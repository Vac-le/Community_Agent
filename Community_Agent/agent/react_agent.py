"""ReAct Agent 主流程模块。

职责：
1. 创建 LangChain Agent。
2. 组装用户消息与历史消息。
3. 在流式输出过程中处理工具调用副产物。
4. 当上下文过长时，执行自动压缩与重试。
"""

import json
import re
import threading

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage

from agent.reflection_service import ReflectionService, ToolObservation
from agent.tools.agent_tools import (
    confirm_food_order,
    get_pending_food_order,
    prepare_food_order,
    query_all_foods,
    query_user_order_history,
    query_weather_forecast,
    rag_summarize,
    save_user_email_to_memory,
    send_agent_chart_email,
    update_food_order_draft,
)
from agent.tools.middleware import log_before_model, monitor_tool
from clients.java_backend_client import JavaBackendClient
from models.dto import ChatHistoryMessage
from memory.user_long_memory_service import UserLongMemoryService
from models.factory import chat_model
from utils.logger_handler import logger
from utils.prompt_loader import load_system_prompt
from utils.mcp_tool_loader import load_mcp_tools_sync
from utils.retry_handler import ContextRetryHandler
from utils.token_utils import estimate_messages_tokens, estimate_text_tokens


class ReactAgent:
    """项目内核心 Agent 执行器。"""

    CONTEXT_EXCEEDED_MESSAGE = "当前对话轮数过多，请新开窗口"

    def __init__(self):
        # create_agent 负责把“模型 + 工具 + 中间件”组装成统一执行器。
        # 当前所有问题统一走同一条 Agent 路径，是否调用 RAG 由 LLM 结合提示词与工具定义自主决断。
        # 这里保留一份 Java 客户端，主要用于在流式过程中补拉订单草稿卡片等副产物。
        local_tools = [
            rag_summarize,
            query_all_foods,
            query_user_order_history,
            query_weather_forecast,
            prepare_food_order,
            update_food_order_draft,
            get_pending_food_order,
            confirm_food_order,
            save_user_email_to_memory,
            send_agent_chart_email,
        ]
        mcp_tools = load_mcp_tools_sync()
        all_tools = local_tools + mcp_tools
        logger.info(f"[MCP] Agent 注册工具数量: local={len(local_tools)} mcp={len(mcp_tools)} total={len(all_tools)}")
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompt(),
            tools=all_tools,
            middleware=[monitor_tool, log_before_model],
        )
        # 客户端
        self.java_client = JavaBackendClient()
        # 上下文重试机制
        self.retry_handler = ContextRetryHandler()
        # 最终回答一致性校验机制
        self.reflection_service = ReflectionService(chat_model)
        # 用户长期记忆机制
        self.user_memory_service = UserLongMemoryService()

    def execute_stream(
        self,
        query: str,
        token: str | None = None,
        session_id: str | None = None,
        chat_history: list[ChatHistoryMessage] | None = None,
        user_id: int | None = None,
        community_id: int | None = None,
    ):
        """执行一轮流式推理，并在超窗时自动降级重试。"""
        logger.info(f"[Agent决策] unified_agent query={self._preview_text(query, 800)}")
        yield from self._execute_agent_stream(query, token, session_id, chat_history, user_id, community_id)

    def _execute_agent_stream(
        self,
        query: str,
        token: str | None = None,
        session_id: str | None = None,
        chat_history: list[ChatHistoryMessage] | None = None,
        user_id: int | None = None,
        community_id: int | None = None,
    ):
        """统一走 LangChain Agent 工具链，由 LLM 自主决定是否调用 RAG 或订餐工具。"""
        last_error: Exception | None = None
        user_memory_context = self.user_memory_service.build_memory_context(user_id, community_id)

        for retry_level in range(self.retry_handler.max_retry + 1):
            retry_config = self.retry_handler.get_retry_level_config(retry_level)
            current_query = query

            for reflection_attempt in range(self.reflection_service.max_retry + 1):
                current_query = self._maybe_summarize_current_query(current_query, retry_config, retry_level)
                history_summary = self._build_recent_history_summary(chat_history, retry_config["recent_rounds"])
                messages = self._build_messages(current_query, chat_history, retry_config, retry_level, user_memory_context)
                estimated_tokens = estimate_messages_tokens(messages)
                logger.info(
                    f"[Agent重试] retry_level={retry_level} reflection_attempt={reflection_attempt} "
                    f"recent_rounds={retry_config['recent_rounds']} estimated_tokens={estimated_tokens}"
                )

                if self.retry_handler.should_compress(estimated_tokens):
                    if retry_level >= self.retry_handler.max_retry:
                        logger.warning(
                            f"[Agent重试] 已达到最大裁剪次数，estimated_tokens={estimated_tokens}，直接返回超限提示"
                        )
                        yield self.CONTEXT_EXCEEDED_MESSAGE
                        return
                    logger.warning(
                        f"[Agent重试] 估算 token 达到阈值，提前进入下一档裁剪: retry_level={retry_level} estimated_tokens={estimated_tokens}"
                    )
                    break

                self._log_request_snapshot(messages, retry_level, retry_config, estimated_tokens)

                emitted_prepare_intent = False
                emitted_order_card = False
                emitted_control_outputs = []
                final_text_parts = []
                called_tools = []
                tool_observations: list[ToolObservation] = []
                chart_outputs = []
                input_dic = {"messages": messages}

                try:
                    for chunk in self.agent.stream(
                        input_dic,
                        stream_mode="values",
                        context={
                            "token": token,
                            "user_id": user_id,
                            "community_id": community_id,
                            "tool_prompt_max_chars": retry_config["tool_prompt_max_chars"],
                            "rag_doc_chars": retry_config["rag_doc_chars"],
                            "retry_level": retry_level,
                        },
                    ):
                        messages = chunk.get("messages", [])
                        if not messages:
                            continue

                        self._log_chunk_trace(messages)
                        self._collect_called_tools(messages, called_tools)
                        self._collect_tool_observations(messages, tool_observations)
                        self._collect_chart_outputs(messages, chart_outputs)

                        if not emitted_prepare_intent and self._has_order_draft_tool_call(messages):
                            emitted_prepare_intent = True
                            logger.info("[Agent轨迹] 检测到订单草稿相关工具调用，切换到 FOOD_CONFIRM 阶段")
                            # 先缓存控制标记，最终回答通过 Reflection 后再发给上层 SSE。
                            emitted_control_outputs.append("[INTENT:FOOD_CONFIRM]")

                        if emitted_prepare_intent and not emitted_order_card and self._has_successful_order_draft_tool_result(messages):
                            order_card = self._load_pending_order_card(token)
                            if order_card:
                                emitted_order_card = True
                                logger.info(f"[Agent轨迹] 读取到待确认订单卡片: {self._preview_text(order_card, 1200)}")
                                # 订单卡片不是模型直接吐出的内容，而是工具成功后的业务副产物，
                                # 这里通过补拉后端草稿把结构化数据提前送给前端渲染。
                                emitted_control_outputs.append({
                                    "type": "food_order_card",
                                    "intent": "FOOD_CONFIRM",
                                    "content": order_card,
                                })

                        last_msg = messages[-1]
                        if hasattr(last_msg, "type") and last_msg.type == "ai":
                            tool_calls = getattr(last_msg, "tool_calls", None) or []
                            text = self._extract_text(last_msg.content)
                            if text:
                                logger.info(f"[Agent输出] 模型文本片段: {self._preview_text(text, 1000)}")
                                if not tool_calls:
                                    final_text_parts = [text]

                    final_answer = "".join(final_text_parts).strip()
                    reflection_result = self.reflection_service.check(
                        query,
                        final_answer,
                        called_tools,
                        tool_observations,
                        history_summary,
                        user_memory_context,
                    )
                    logger.info(
                        f"[Reflection] passed={reflection_result.passed} should_retry={reflection_result.should_retry} "
                        f"called_tools={called_tools} issues={reflection_result.issues} "
                        f"suggestions={reflection_result.suggestions} missing_tools={reflection_result.missing_tools}"
                    )

                    if reflection_result.should_retry and reflection_attempt < self.reflection_service.max_retry:
                        current_query = self.reflection_service.build_retry_query(
                            query,
                            final_answer,
                            reflection_result,
                            tool_observations,
                            history_summary,
                        )
                        logger.warning(
                            f"[Reflection] Reflector 要求 Worker 重试: reason={reflection_result.reason} "
                            f"issues={reflection_result.issues} suggestions={reflection_result.suggestions}"
                        )
                        continue

                    self._update_user_long_memory(user_id, community_id, query, final_answer)
                    for output in emitted_control_outputs:
                        yield output
                    for chart_output in chart_outputs:
                        yield chart_output
                    if final_answer:
                        yield final_answer
                    return
                except Exception as e:
                    last_error = e
                    logger.warning(f"[Agent重试] retry_level={retry_level} 失败: {str(e)}")
                    if not self.retry_handler.should_retry(e):
                        raise
                    if retry_level >= self.retry_handler.max_retry:
                        yield self.CONTEXT_EXCEEDED_MESSAGE
                        return
                    break

        if last_error:
            if self.retry_handler.should_retry(last_error):
                yield self.CONTEXT_EXCEEDED_MESSAGE
                return
            raise last_error

    def _log_request_snapshot(self, messages: list[dict[str, str]], retry_level: int, retry_config: dict, estimated_tokens: int):
        """打印本轮真正准备发给模型的输入摘要。"""
        last_role = messages[-1].get("role") if messages else "unknown"
        context_mode = "summary_compressed" if retry_level > 0 else "full_history"
        logger.info(
            f"[Agent输入快照] retry_level={retry_level} context_mode={context_mode} recent_rounds={retry_config['recent_rounds']} "
            f"summary_max_chars={retry_config['summary_max_chars']} single_message_max_chars={retry_config['single_message_max_chars']} "
            f"rag_doc_chars={retry_config['rag_doc_chars']} tool_prompt_max_chars={retry_config['tool_prompt_max_chars']} "
            f"message_count={len(messages)} last_role={last_role} estimated_tokens={estimated_tokens}"
        )

    def _log_chunk_trace(self, messages):
        """打印当前 Agent 可见执行轨迹。"""
        last_msg = messages[-1]
        msg_type = getattr(last_msg, "type", type(last_msg).__name__)
        logger.info(f"[Agent轨迹] 当前最后一条消息类型: {msg_type}")

        tool_calls = getattr(last_msg, "tool_calls", None) or []
        if tool_calls:
            logger.info(f"[Agent轨迹] 当前消息包含工具调用: {tool_calls}")

    def _collect_called_tools(self, messages, called_tools: list[str]):
        """从 Agent 消息轨迹中收集本轮实际出现过的工具调用名称。"""
        for msg in messages:
            tool_calls = getattr(msg, "tool_calls", None) or []
            for tool_call in tool_calls:
                if isinstance(tool_call, dict):
                    tool_name = tool_call.get("name")
                    if tool_name and tool_name not in called_tools:
                        called_tools.append(tool_name)

            if getattr(msg, "type", None) == "tool":
                tool_name = getattr(msg, "name", None)
                if tool_name and tool_name not in called_tools:
                    called_tools.append(tool_name)

    def _collect_tool_observations(self, messages, tool_observations: list[ToolObservation]):
        """收集本轮成功工具的真实结果，供最终答案事实约束使用。"""
        existing = {(item.name, item.content) for item in tool_observations}
        for msg in messages:
            if getattr(msg, "type", None) != "tool":
                continue
            tool_name = getattr(msg, "name", None)
            content = self._extract_text(getattr(msg, "content", ""))
            status = getattr(msg, "status", None)
            if not tool_name or not content:
                continue
            if status == "error" or "Error invoking tool" in content:
                continue
            key = (tool_name, content)
            if key in existing:
                continue
            tool_observations.append(ToolObservation(name=tool_name, content=content))
            existing.add(key)

    def _collect_chart_outputs(self, messages, chart_outputs: list[dict]):
        """从 AntV MCP 可视化工具结果中提取图片 URL，供前端渲染。"""
        existing_urls = {item.get("content", {}).get("imageUrl") for item in chart_outputs}
        for msg in messages:
            if getattr(msg, "type", None) != "tool":
                continue

            tool_name = getattr(msg, "name", "") or ""
            if not self._is_visualization_tool(tool_name):
                continue

            status = getattr(msg, "status", None)
            content = self._extract_text(getattr(msg, "content", ""))
            if not content or status == "error" or "Error invoking tool" in content:
                continue

            image_url = self._extract_chart_image_url(content)
            if not image_url or image_url in existing_urls:
                continue

            chart_output = {
                "type": "chart",
                "intent": "CHART",
                "content": {
                    "imageUrl": image_url,
                    "toolName": tool_name,
                    "title": self._extract_chart_title(content, tool_name),
                },
            }
            chart_outputs.append(chart_output)
            existing_urls.add(image_url)
            logger.info(f"[MCP图表] 捕获可视化图片: tool={tool_name} image_url={image_url}")

    def _extract_chart_image_url(self, content: str) -> str | None:
        """兼容 JSON、Markdown、纯文本中的图片 URL。"""
        parsed = self._try_parse_json(content)
        url = self._find_url_in_value(parsed) if parsed is not None else None
        if url:
            return url

        markdown_match = re.search(r"!\[[^\]]*\]\((https?://[^\s)]+)\)", content)
        if markdown_match:
            return markdown_match.group(1)

        url_match = re.search(r"https?://[^\s)\]}\"']+", content)
        if url_match:
            return url_match.group(0)
        return None

    def _extract_chart_title(self, content: str, tool_name: str = "") -> str:
        """从工具结果中尽量提取标题，失败时返回基于工具名的默认标题。"""
        parsed = self._try_parse_json(content)
        if isinstance(parsed, dict):
            for key in ["title", "name"]:
                value = parsed.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return self._default_visualization_title(tool_name)

    def _default_visualization_title(self, tool_name: str) -> str:
        if not tool_name:
            return "AI 生成可视化"
        readable = tool_name.replace("generate_", "").replace("_", " ").strip()
        return readable.title() if readable else "AI 生成可视化"

    def _is_visualization_tool(self, tool_name: str) -> bool:
        if not tool_name.startswith("generate_"):
            return False
        visualization_suffixes = {
            "_chart",
            "_diagram",
            "_graph",
            "_map",
            "_tree",
            "_mind_map",
            "_flow_diagram",
            "_organization_chart",
            "_network_graph",
        }
        return any(tool_name.endswith(suffix) for suffix in visualization_suffixes)

    def _try_parse_json(self, content: str):
        """尝试解析 JSON 文本。"""
        try:
            return json.loads(content)
        except Exception:
            return None

    def _find_url_in_value(self, value) -> str | None:
        """递归查找 JSON 结构中的图片 URL。"""
        image_keys = {"imageUrl", "image_url", "url", "src", "href", "downloadUrl", "download_url"}
        if isinstance(value, dict):
            for key in image_keys:
                item = value.get(key)
                if isinstance(item, str) and self._is_chart_image_url(item):
                    return item
            for item in value.values():
                found = self._find_url_in_value(item)
                if found:
                    return found
        if isinstance(value, list):
            for item in value:
                found = self._find_url_in_value(item)
                if found:
                    return found
        if isinstance(value, str) and self._is_chart_image_url(value):
            return value
        return None

    def _is_chart_image_url(self, value: str) -> bool:
        """判断字符串是否像可展示的图表 URL。"""
        if not value.startswith(("http://", "https://")):
            return False
        lower_value = value.lower()
        return any(marker in lower_value for marker in [".png", ".jpg", ".jpeg", ".webp", ".svg", "oss", "dashscope", "aliyun"])

    def _preview_text(self, content, max_chars: int = 1000) -> str:
        """生成控制台可读的内容预览。"""
        if content is None:
            return ""
        content_str = str(content)
        if len(content_str) <= max_chars:
            return content_str
        return content_str[:max_chars] + f" ...[truncated,total={len(content_str)} chars]"

    def _has_order_draft_tool_call(self, messages) -> bool:
        """判断当前 Agent 是否已经触发了订单草稿保存或修改工具。"""
        draft_tool_names = {"prepare_food_order", "update_food_order_draft"}
        for msg in reversed(messages):
            msg_type = getattr(msg, "type", None)
            if msg_type == "ai":
                tool_calls = getattr(msg, "tool_calls", None) or []
                for tool_call in tool_calls:
                    if isinstance(tool_call, dict) and tool_call.get("name") in draft_tool_names:
                        return True

            if msg_type == "tool":
                tool_name = getattr(msg, "name", None)
                if tool_name in draft_tool_names:
                    return True

                additional_kwargs = getattr(msg, "additional_kwargs", None) or {}
                if isinstance(additional_kwargs, dict):
                    if additional_kwargs.get("name") in draft_tool_names:
                        return True
                    tool_call_id = additional_kwargs.get("tool_call_id")
                    if tool_call_id and self._match_tool_call_id(messages, tool_call_id, draft_tool_names):
                        return True
        return False

    def _match_tool_call_id(self, messages, tool_call_id: str, draft_tool_names: set[str]) -> bool:
        """根据 tool_call_id 回溯对应的 AI tool_call，兼容不同消息结构。"""
        for msg in reversed(messages):
            if getattr(msg, "type", None) != "ai":
                continue
            tool_calls = getattr(msg, "tool_calls", None) or []
            for tool_call in tool_calls:
                if not isinstance(tool_call, dict):
                    continue
                if tool_call.get("id") == tool_call_id and tool_call.get("name") in draft_tool_names:
                    return True
        return False

    def _has_successful_order_draft_tool_result(self, messages) -> bool:
        """判断订单草稿保存/更新工具是否已经成功返回。"""
        draft_tool_names = {"prepare_food_order", "update_food_order_draft"}
        for msg in reversed(messages):
            if getattr(msg, "type", None) != "tool":
                continue

            tool_name = getattr(msg, "name", None)
            if tool_name not in draft_tool_names:
                additional_kwargs = getattr(msg, "additional_kwargs", None) or {}
                tool_call_id = additional_kwargs.get("tool_call_id") if isinstance(additional_kwargs, dict) else None
                if not tool_call_id or not self._match_tool_call_id(messages, tool_call_id, draft_tool_names):
                    continue

            status = getattr(msg, "status", None)
            content = self._extract_text(getattr(msg, "content", ""))
            if status == "error" or "Error invoking tool" in content:
                continue

            try:
                payload = json.loads(content)
            except json.JSONDecodeError:
                return bool(content.strip())

            if isinstance(payload, dict):
                if payload.get("code") == 200:
                    return True
                data = payload.get("data")
                if isinstance(data, dict) and data.get("status") == "PENDING_CONFIRM":
                    return True
        return False

    def _load_pending_order_card(self, token: str | None):
        """从 Java 后端读取当前待确认的订单草稿卡片。"""
        if not token:
            return None

        try:
            result = self.java_client.get_current_food_order_draft(token)
            foods_result = self.java_client.get_food_list(token)
        except Exception:
            return None

        if not isinstance(result, dict):
            return None

        data = result.get("data") if isinstance(result.get("data"), dict) else result
        if not isinstance(data, dict):
            return None

        order_items = data.get("orderItems") or data.get("items") or []
        if not isinstance(order_items, list) or not order_items:
            return None

        food_map = self._build_food_map(foods_result)
        return self._build_order_card(data, food_map)

    def _build_food_map(self, foods_result: dict | None) -> dict:
        """把菜品列表转成按 foodId 索引的字典，用于补齐订单明细展示信息。"""
        if not isinstance(foods_result, dict):
            return {}
        foods = foods_result.get("data")
        if not isinstance(foods, list):
            return {}
        return {food.get("id"): food for food in foods if isinstance(food, dict) and food.get("id") is not None}

    def _build_order_card(self, data: dict, food_map: dict | None = None):
        """将 Java 返回的订单草稿转换为前端卡片结构。"""
        food_map = food_map or {}
        items = []
        for index, item in enumerate(data.get("orderItems") or data.get("items") or []):
            food = item.get("food") if isinstance(item.get("food"), dict) else {}
            food_id = item.get("foodId") or food.get("id") or item.get("id") or index
            catalog_food = food_map.get(food_id, {})
            name = item.get("name") or food.get("name") or item.get("foodName") or catalog_food.get("name") or f"菜品{index + 1}"
            price = item.get("price")
            if price is None:
                price = food.get("price")
            if price is None:
                price = catalog_food.get("price")
            if price is None:
                price = item.get("amount")
            quantity = item.get("quantity") or item.get("count") or 1
            items.append({
                "id": food_id,
                "foodId": food_id,
                "name": name,
                "price": price or 0,
                "quantity": quantity,
                "image": item.get("image") or food.get("img") or catalog_food.get("img") or "",
                "description": item.get("description") or food.get("description") or catalog_food.get("description") or "",
            })

        amount = data.get("amount")
        if amount is None:
            amount = sum((item.get("price") or 0) * (item.get("quantity") or 0) for item in items)

        return {
            "sessionId": data.get("sessionId") or data.get("session_id") or "",
            "items": items,
            "deliveryAddress": data.get("deliveryAddress") or data.get("delivery_address") or "",
            "deliveryPhone": data.get("deliveryPhone") or data.get("delivery_phone") or "",
            "remark": data.get("remark") or "",
            "amount": amount or 0,
            "recommendSummary": data.get("recommendSummary") or data.get("recommend_summary") or "",
            "fromHistory": True,
        }

    def _extract_text(self, content) -> str:
        """从模型消息内容中提取纯文本。"""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return "".join(text_parts)
        return str(content) if content is not None else ""

    def _build_recent_history_summary(
        self,
        chat_history: list[ChatHistoryMessage] | None = None,
        recent_rounds: int = 2,
        max_chars: int = 1600,
    ) -> str:
        """为 Reflection 构建最近 N 轮历史摘要，避免其脱离上下文做审稿。"""
        if not chat_history or recent_rounds <= 0:
            return ""

        normalized_history: list[str] = []
        for history_message in chat_history:
            role = self._normalize_role(history_message.role)
            content = self._clean_history_content(role, (history_message.content or "").strip())
            content = self._compress_content(content)
            if not role or not content:
                continue
            normalized_history.append(f"{role}: {content}")

        recent_messages = normalized_history[-recent_rounds * 2:]
        summary_parts: list[str] = []
        total = 0
        for index, item in enumerate(recent_messages, start=1):
            line = f"[{index}] {self._preview_text(item, 280)}"
            projected = total + len(line) + (1 if summary_parts else 0)
            if projected > max_chars:
                remaining = max_chars - total
                if remaining > 40:
                    summary_parts.append(line[:remaining] + "...")
                break
            summary_parts.append(line)
            total = projected
        return "\n".join(summary_parts)

    def _maybe_summarize_current_query(self, query: str, retry_config: dict, retry_level: int) -> str:
        """当当前问题单体已接近上下文阈值时，优先先摘要当前问题。"""
        if not query:
            return ""

        query_tokens = estimate_text_tokens(query)
        threshold_tokens = int(self.retry_handler.max_context_tokens * self.retry_handler.trigger_ratio)
        if query_tokens < threshold_tokens:
            return query

        target_chars = max(120, retry_config["single_message_max_chars"])
        logger.warning(
            f"[Agent重试] 当前问题单体过长，先摘要当前问题: retry_level={retry_level} "
            f"query_tokens={query_tokens} threshold_tokens={threshold_tokens} target_chars={target_chars}"
        )
        summarized_query = self._summarize_current_query(query, target_chars)
        return summarized_query or self._compress_content(query, target_chars)

    def _summarize_current_query(self, query: str, max_chars: int) -> str:
        """将超长当前问题压缩成保留诉求与约束的短问题。"""
        prompt = (
            f"请将下面这个超长用户问题压缩为一个更短但语义完整的问题。"
            f"必须保留核心任务、关键约束、明确要求和必要背景。"
            f"不要编造，不要分点，控制在{max_chars}字以内。\n\n原问题：\n{query}"
        )
        try:
            response = chat_model.invoke([
                SystemMessage(content="你是用户问题压缩器，只输出压缩后的问题正文。"),
                HumanMessage(content=prompt),
            ])
            summary = self._extract_text(getattr(response, "content", response)).strip()
            return self._compress_content(summary, max_chars)
        except Exception as e:
            logger.warning(f"[CurrentQuerySummary] 模型摘要失败，回退规则截断: {e}")
            return self._compress_content(query, max_chars)

    def _build_messages(
        self,
        query: str,
        chat_history: list[ChatHistoryMessage] | None = None,
        retry_config: dict | None = None,
        retry_level: int = 0,
        user_memory_context: str = "",
    ) -> list[dict[str, str]]:
        """构建发送给 Agent 的消息列表。

        默认模式保留当前问题 + 最近 6 轮历史；
        只有进入上下文重试后，才启用“摘要 + 最近 2 轮 + 当前问题”的压缩模式。
        """
        retry_config = retry_config or self.retry_handler.get_retry_level_config(0)
        max_chars = retry_config["single_message_max_chars"]
        normalized_history = self._normalize_history(chat_history, max_chars)

        if retry_level <= 0:
            history_messages = normalized_history[-12:]
            messages: list[dict[str, str]] = []
            if user_memory_context:
                messages.append({"role": "system", "content": user_memory_context})
            messages.extend(history_messages)
            chart_instruction = self._build_chart_instruction(query)
            if chart_instruction:
                messages.append({"role": "system", "content": chart_instruction})
            messages.append({"role": "user", "content": self._compress_content(query, max_chars)})
            return messages

        summary_message = self._build_history_summary_message(normalized_history, retry_config)
        recent_history = self._pick_recent_history(normalized_history, retry_config["recent_rounds"])

        messages: list[dict[str, str]] = []
        if user_memory_context:
            messages.append({"role": "system", "content": user_memory_context})
        if summary_message:
            messages.append({"role": "system", "content": summary_message})
        chart_instruction = self._build_chart_instruction(query)
        if chart_instruction:
            messages.append({"role": "system", "content": chart_instruction})
        messages.extend(recent_history)
        messages.append({"role": "user", "content": self._compress_content(query, max_chars)})
        return messages

    def _update_user_long_memory(
        self,
        user_id: int | None,
        community_id: int | None,
        query: str,
        final_answer: str,
    ) -> None:
        """最终回答通过后，后台异步沉淀用户长期记忆，不阻塞主响应。"""
        def _worker():
            try:
                result = self.user_memory_service.update_from_query(user_id, community_id, query, final_answer)
                logger.info(f"[UserMemory] update_result={result}")
            except Exception as e:
                logger.warning(f"[UserMemory] 更新用户长期记忆失败，不影响主流程: {e}")

        try:
            threading.Thread(target=_worker, daemon=True, name="user-memory-update").start()
        except Exception as e:
            logger.warning(f"[UserMemory] 后台线程启动失败，跳过长期记忆更新: {e}")

    def _build_chart_instruction(self, query: str) -> str:
        """图表请求时追加更强的工具调用指令。"""
        chart_keywords = ["图表", "可视化", "统计图", "柱状图", "条形图", "折线图", "饼图", "雷达图", "词云", "趋势图", "看板"]
        if not any(keyword in (query or "") for keyword in chart_keywords):
            return ""
        return (
            "用户当前请求包含图表/可视化需求。你必须调用一个具体的 AntV MCP 图表工具完成生成，"
            "例如 generate_bar_chart、generate_column_chart、generate_line_chart、generate_pie_chart、"
            "generate_radar_chart 或 generate_word_cloud_chart。禁止只输出表格、统计文字或声称已经生成图表。"
            "若需要业务数据，先调用业务查询工具，再把整理后的真实数据传入 generate_*_chart 工具。"
        )

    def _normalize_history(self, chat_history: list[ChatHistoryMessage] | None, max_chars: int) -> list[dict[str, str]]:
        """标准化历史消息，并对单条内容做截断。"""
        normalized_history: list[dict[str, str]] = []
        if not chat_history:
            return normalized_history

        for history_message in chat_history:
            role = self._normalize_role(history_message.role)
            content = self._clean_history_content(role, (history_message.content or "").strip())
            content = self._compress_content(content, max_chars)
            if not role or not content:
                continue
            normalized_history.append({"role": role, "content": content})
        return normalized_history

    def _pick_recent_history(self, normalized_history: list[dict[str, str]], recent_rounds: int) -> list[dict[str, str]]:
        """保留最近若干轮完整对话。"""
        if recent_rounds <= 0:
            return []
        return normalized_history[-recent_rounds * 2:]

    def _build_history_summary_message(self, normalized_history: list[dict[str, str]], retry_config: dict) -> str:
        """把较早历史压缩为一段摘要，供模型理解上下文。"""
        recent_count = retry_config["recent_rounds"] * 2
        early_history = normalized_history[:-recent_count] if recent_count > 0 else normalized_history
        if not early_history:
            return ""

        source_lines = [
            f"{item['role']}: {item['content']}"
            for item in early_history
            if item.get("role") and item.get("content")
        ]
        if not source_lines:
            return ""

        summary = self._summarize_history("\n".join(source_lines), retry_config["summary_max_chars"])
        if not summary:
            return ""
        return f"以下是更早历史对话摘要，请结合其与最近对话继续回答：{summary}"

    def _summarize_history(self, history_text: str, max_chars: int) -> str:
        """使用当前模型把较早历史压缩成短摘要，失败时退化为规则摘要。"""
        if not history_text:
            return ""

        prompt = (
            f"请将下面较早的多轮对话压缩为一段连续上下文摘要，保留用户诉求、已确认事实、未完成任务、关键偏好。"
            f"不要编造，不要分点，控制在{max_chars}字以内。\n\n对话内容：\n{history_text}"
        )
        try:
            response = chat_model.invoke([
                SystemMessage(content="你是对话历史压缩器，只输出摘要正文。"),
                HumanMessage(content=prompt),
            ])
            summary = self._extract_text(getattr(response, "content", response)).strip()
            return self._compress_content(summary, max_chars)
        except Exception as e:
            logger.warning(f"[HistorySummary] 模型摘要失败，回退规则摘要: {e}")
            return self._fallback_history_summary(history_text, max_chars)

    def _fallback_history_summary(self, history_text: str, max_chars: int) -> str:
        """当模型摘要失败时，退化为规则截断摘要。"""
        cleaned = history_text.replace("\n", "；")
        return self._compress_content(cleaned, max_chars)

    def _clean_history_content(self, role: str | None, content: str) -> str:
        """清洗历史消息，assistant 历史只保留最终用户可见答案。"""
        if role != "assistant" or not content:
            return content

        final_markers = [
            "已为您",
            "已为你",
            "太好了！",
            "订单详情如下",
            "更新后的订单详情如下",
            "这份订单",
            "目前资料中",
        ]
        best_index = -1
        for marker in final_markers:
            index = content.rfind(marker)
            if index > best_index:
                best_index = index

        if best_index > 0:
            return content[best_index:].strip()
        return content.strip()

    def _compress_content(self, content: str, max_chars: int = 600) -> str:
        """对超长单条消息做基础截断。"""
        if not content:
            return ""
        content = content.strip()
        if len(content) <= max_chars:
            return content
        return content[:max_chars] + "..."

    def _normalize_role(self, role: str | None) -> str | None:
        """将历史消息角色标准化为 Agent 可识别角色。"""
        if role == "assistant":
            return "assistant"
        if role == "user":
            return "user"
        return None


if __name__ == "__main__":
    agent = ReactAgent()
    for chunk in agent.execute_stream("帮我下单"):
        print(chunk, end="", flush=True)
