"""Agent 最终回答 Reflection 校验模块。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from utils.config_handler import agent_config
from utils.logger_handler import logger


@dataclass
class ReflectionResult:
    passed: bool
    should_retry: bool
    reason: str = ""
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    missing_tools: list[str] = field(default_factory=list)


@dataclass
class ToolObservation:
    name: str
    content: str


class ReflectionService:
    """只做一致性校验；若不一致则要求模型重试，不直接改写最终输出。"""

    TOOL_CLAIM_PATTERNS = [
        r"我(已经|已|刚刚)?(帮你|为你)?(查询|查找|检索|搜索|调用|查看)了",
        r"(已经|已|刚刚)(查询|查找|检索|搜索|调用|查看)",
        r"根据(查询|检索|搜索|工具|系统|数据库|订单|菜单|资料|公告)(结果|信息)?",
        r"查询结果(显示|如下|为)",
        r"检索结果(显示|如下|为)",
        r"系统(查询|检索|返回|显示)",
        r"我查到",
        r"我为你查",
    ]




    TOOL_INTENT_KEYWORDS = {
        "rag_summarize": ["检索结果", "资料显示", "公告显示", "参考资料显示"],
        "query_all_foods": ["菜单显示", "菜品列表显示", "系统菜品列表"],
        "query_user_order_history": ["历史订单显示", "订单记录显示", "系统订单记录"],
        "prepare_food_order": ["订单草稿已生成", "待确认订单已生成", "已保存订单草稿"],
        "update_food_order_draft": ["订单草稿已更新", "订单草稿已修改", "已更新待确认订单"],
        "get_pending_food_order": ["读取到待确认订单", "查询到待确认订单", "当前待确认订单显示"],
        "confirm_food_order": ["已下单成功", "订单已创建成功", "订单已提交成功"],
    }

    def __init__(self, llm: BaseChatModel, enabled: bool | None = None, max_retry: int | None = None):
        config = agent_config.get("reflection", {})
        self.llm = llm
        self.enabled = config.get("enabled", True) if enabled is None else enabled
        self.max_retry = config.get("max_retry", 1) if max_retry is None else max_retry
        self.use_llm_check = config.get("use_llm_check", True)

    def check(
        self,
        query: str,
        answer: str,
        called_tools: list[str],
        tool_observations: list[ToolObservation] | None = None,
        history_summary: str = "",
        user_memory_context: str = "",
    ) -> ReflectionResult:
        if not self.enabled:
            return ReflectionResult(True, False)

        tools = [tool for tool in called_tools if tool]
        observations = tool_observations or []
        findings = self._collect_findings(query, answer, tools, observations)

        if not self.use_llm_check:
            return self._result_from_findings(findings)

        llm_result = self._reflect_with_llm(query, answer, tools, observations, findings, history_summary, user_memory_context)
        if llm_result is None:
            return self._result_from_findings(findings)

        merged_issues = self._merge_lists(findings["issues"], llm_result.get("issues", []))
        merged_suggestions = self._merge_lists(findings["suggestions"], llm_result.get("suggestions", []))
        merged_missing_tools = self._merge_lists(findings["missing_tools"], llm_result.get("missing_tools", []))
        passed = bool(llm_result.get("passed", not merged_issues)) and not merged_issues
        should_retry = bool(llm_result.get("should_retry", not passed)) and bool(merged_issues or merged_suggestions)
        reason = str(llm_result.get("reason", "")).strip() or (merged_issues[0] if merged_issues else "")
        return ReflectionResult(passed, should_retry, reason, merged_issues, merged_suggestions, merged_missing_tools)

    def build_retry_query(
        self,
        query: str,
        previous_answer: str,
        reflection_result: ReflectionResult,
        tool_observations: list[ToolObservation] | None = None,
        history_summary: str = "",
        user_memory_context: str = "",
    ) -> str:
        issues = "；".join(reflection_result.issues) or reflection_result.reason or "最终回答存在一致性问题"
        suggestions = "；".join(reflection_result.suggestions) or "根据真实工具结果修正结论，并补查缺失信息"
        missing_tools = "、".join(reflection_result.missing_tools) or "无明确缺失工具"
        facts = self._format_tool_observations(tool_observations or [], 3200)
        facts_block = f"\n【本轮真实工具结果】\n{facts}\n" if facts else ""
        history_block = f"\n【最近对话摘要】\n{history_summary}\n" if history_summary else ""
        return (
            f"{query}\n\n【Reflector 复审意见】\n"
            f"发现的问题：{issues}。\n"
            f"建议的修正动作：{suggestions}。\n"
            f"可能需要补充的工具：{missing_tools}。\n"
            "请你作为 Worker 重新完成这次任务，并严格遵守：\n"
            "1. 先判断当前证据是否足够，不足就补充检索或补调工具。\n"
            "2. 所有具体事实必须以真实工具结果为准，不能编造。\n"
            "3. 若 Reflector 指出某个结论证据不足，优先修正结论或补充证据。\n"
            "4. 回答要完整自然，但不要提及 Reflector、复审、上一次回答。\n"
            f"{history_block}{facts_block}\n【上一次初稿】\n{previous_answer}"
        )

    def _collect_findings(
        self,
        query: str,
        answer: str,
        called_tools: list[str],
        tool_observations: list[ToolObservation],
    ) -> dict[str, list[str]]:
        issues: list[str] = []
        suggestions: list[str] = []
        missing_tools: list[str] = []
        text = (answer or "").strip()
        if not text:
            issues.append("当前初稿为空或缺少最终回答")
            suggestions.append("先给出完整回答，再由 Reflector 复审")
            return {"issues": issues, "suggestions": suggestions, "missing_tools": missing_tools}

        if self._claims_tool_usage(text) and not called_tools:
            issues.append("回答声称已经查询、检索或调用系统，但本轮没有任何实际工具调用")
            suggestions.append("删除无依据的系统查询表述，或先补充实际工具调用")

        for tool_name, keywords in self.TOOL_INTENT_KEYWORDS.items():
            if tool_name in called_tools:
                continue
            if self._mentions_tool_result(text, keywords):
                issues.append(f"回答疑似声称使用了 {tool_name} 相关结果，但实际未调用该工具")
                suggestions.append(f"若结论直接依赖 {tool_name}，请先调用该工具再回答")
                missing_tools.append(tool_name)

        if self._claims_tool_usage(text):
            issues.extend(self._unsupported_number_issues(text, tool_observations))
        issues.extend(self._food_order_issues(text, tool_observations))



        if any("foodId" in issue or "菜品" in issue for issue in issues):
            suggestions.append("重新核对菜单映射与订单明细，确保 foodId、菜名、数量一致")
        if any("数字" in issue for issue in issues):
            suggestions.append("所有关键数字尽量在工具结果中找到依据")




        return {
            "issues": self._dedupe(issues),
            "suggestions": self._dedupe(suggestions),
            "missing_tools": self._dedupe(missing_tools),
        }

    def _unsupported_number_issues(self, answer: str, tool_observations: list[ToolObservation]) -> list[str]:
        fact_numbers = self._collect_fact_numbers(tool_observations)
        if not fact_numbers:
            return []
        answer_numbers = {n.replace(",", "") for n in re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", answer)}
        unsupported = sorted(
            n for n in answer_numbers
            if len(n) >= 3 and n not in fact_numbers and n not in {"100", "200", "300", "500", "1000"}
        )
        return [f"回答中出现工具结果里没有支撑的数字: {', '.join(unsupported[:6])}"] if unsupported else []

    def _collect_fact_numbers(self, tool_observations: list[ToolObservation]) -> set[str]:
        fact_numbers: set[str] = set()
        for obs in tool_observations:
            raw_text = (obs.content or "").strip()
            for n in re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", raw_text):
                fact_numbers.add(n.replace(",", ""))
            parsed = self._parse_json(raw_text)
            if parsed is not None:
                self._collect_numbers_from_value(parsed, fact_numbers)
        return fact_numbers

    def _collect_numbers_from_value(self, value: Any, output: set[str]):
        if isinstance(value, dict):
            for item in value.values():
                self._collect_numbers_from_value(item, output)
            return
        if isinstance(value, list):
            for item in value:
                self._collect_numbers_from_value(item, output)
            return
        if isinstance(value, (int, float)):
            output.add(str(value).replace(",", ""))
            return
        if isinstance(value, str):
            for n in re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", value):
                output.add(n.replace(",", ""))

    def _food_order_issues(self, answer: str, tool_observations: list[ToolObservation]) -> list[str]:
        food_catalog = self._extract_food_catalog(tool_observations)
        order_items = self._extract_latest_order_items(tool_observations)
        if not food_catalog or not order_items:
            return []

        issues = []
        valid_names = {item.get("name") for item in food_catalog.values() if item.get("name")}
        for food_name, food_id in self._extract_food_id_pairs(answer):
            catalog_food = food_catalog.get(food_id)
            if catalog_food and catalog_food.get("name") and catalog_food.get("name") != food_name:
                issues.append(f"回答中 foodId:{food_id} 被描述为“{food_name}”，但菜单映射显示该 ID 对应“{catalog_food.get('name')}”")

        answer_food_names = self._extract_food_names(answer, valid_names)
        if answer_food_names:
            order_name_set = set()
            for item in order_items:
                food_id = item.get("foodId")
                if food_id in food_catalog and food_catalog[food_id].get("name"):
                    order_name_set.add(food_catalog[food_id]["name"])
            unsupported_names = sorted(name for name in answer_food_names if name not in order_name_set)
            if unsupported_names:
                issues.append(f"回答提到了订单中不存在的菜品: {', '.join(unsupported_names[:8])}")
        return issues

    def _result_from_findings(self, findings: dict[str, list[str]]) -> ReflectionResult:
        passed = not findings["issues"]
        return ReflectionResult(
            passed=passed,
            should_retry=not passed,
            reason=findings["issues"][0] if findings["issues"] else "",
            issues=findings["issues"],
            suggestions=findings["suggestions"],
            missing_tools=findings["missing_tools"],
        )

    def _reflect_with_llm(
        self,
        query: str,
        answer: str,
        called_tools: list[str],
        tool_observations: list[ToolObservation],
        findings: dict[str, list[str]],
        history_summary: str = "",
        user_memory_context: str = "",
    ) -> dict[str, Any] | None:
        prompt = self._build_reflector_prompt(
            query,
            answer,
            called_tools,
            tool_observations,
            findings,
            history_summary,
            user_memory_context,
        )
        try:
            response = self.llm.invoke([
                SystemMessage(content="你是企业级 Agent Reflector，只负责审稿、找问题、提修改建议，只输出 JSON。"),
                HumanMessage(content=prompt),
            ])
            result = self._parse_json(str(getattr(response, "content", response)))
        except Exception as e:
            logger.warning(f"[Reflection] Reflector 调用失败，回退到规则结果: {e}")
            return None
        return result if isinstance(result, dict) else None

    def _build_reflector_prompt(
        self,
        query: str,
        answer: str,
        called_tools: list[str],
        tool_observations: list[ToolObservation],
        findings: dict[str, list[str]],
        history_summary: str = "",
        user_memory_context: str = "",
    ) -> str:
        issues = "；".join(findings["issues"]) or "无"
        suggestions = "；".join(findings["suggestions"]) or "无"
        missing_tools = "、".join(findings["missing_tools"]) or "无"
        return f"""
你现在不是 Worker，而是 Reflector。你的职责是审查 Worker 当前初稿是否可靠，并决定是否要求 Worker 再做一轮。

请重点检查：
1. 初稿是否和真实工具调用、真实工具结果存在明显事实冲突。
2. 初稿是否存在严重幻觉，例如虚构工具结果、虚构订单创建、虚构明确数字统计。
3. 对于一般性归纳、保守表述、常识性总结，不要过度苛责，也不要因为表达不够严谨就一律要求重做。
4. 只有在明显事实错误、缺失关键工具调用、强证据冲突时，才建议重试。
5. 你不要直接代替 Worker 重写答案，只做审稿和指导。
6. 用户在当前问题、最近对话摘要或长期记忆中明确提供的输入侧事实（如邮箱、地址、联系电话、口味偏好），若未与工具结果冲突，可被 Worker 在最终回答中引用，不要求工具结果再次回显确认。
7. 若邮件发送工具成功返回，Worker 可以保守表述“已发送到您指定的邮箱”或“已发送到 xxx@qq.com”；但不能据此编造邮件正文细节、图表时间范围、统计口径或额外业务事实。

请只输出 JSON：
{{
  "passed": true,
  "should_retry": false,
  "reason": "",
  "issues": [],
  "suggestions": [],
  "missing_tools": []
}}

【用户问题】
{query}

【最近对话摘要】
{history_summary or "无"}

【Worker 当前初稿】
{answer}

【实际调用工具】
{', '.join(called_tools) if called_tools else '无'}

【真实工具结果】
{self._format_tool_observations(tool_observations, 6000)}

【系统规则预检查发现的问题】
{issues}

【系统规则预检查建议】
{suggestions}

【系统推测可能缺失的工具】
{missing_tools}
"""

    def _claims_tool_usage(self, text: str) -> bool:
        return any(re.search(pattern, text) for pattern in self.TOOL_CLAIM_PATTERNS)

    def _mentions_tool_result(self, text: str, keywords: list[str]) -> bool:
        claim_words = ["查询结果", "检索结果", "系统显示", "系统返回", "工具返回", "资料显示", "公告显示", "已下单成功", "订单已创建"]
        return any(keyword in text for keyword in keywords) and any(word in text for word in claim_words)

    def _extract_food_catalog(self, tool_observations: list[ToolObservation]) -> dict[int, dict[str, Any]]:
        catalog: dict[int, dict[str, Any]] = {}
        for obs in tool_observations:
            if obs.name != "query_all_foods":
                continue
            payload = self._parse_json(obs.content)
            if not isinstance(payload, dict):
                continue
            foods = payload.get("data")
            if not isinstance(foods, list):
                continue
            for food in foods:
                if not isinstance(food, dict):
                    continue
                food_id = self._to_int(food.get("id"))
                if food_id is None:
                    continue
                catalog[food_id] = {"name": str(food.get("name") or "").strip(), "price": food.get("price")}
        return catalog

    def _extract_latest_order_items(self, tool_observations: list[ToolObservation]) -> list[dict[str, Any]]:
        latest_items: list[dict[str, Any]] = []
        for obs in tool_observations:
            if obs.name not in {"get_pending_food_order", "prepare_food_order", "update_food_order_draft"}:
                continue
            payload = self._parse_json(obs.content)
            if not isinstance(payload, dict):
                continue
            data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
            if not isinstance(data, dict):
                continue
            order_items = data.get("orderItems") or data.get("items") or []
            if not isinstance(order_items, list):
                continue
            normalized = []
            for item in order_items:
                if not isinstance(item, dict):
                    continue
                food_id = self._to_int(item.get("foodId") or item.get("id"))
                quantity = self._to_int(item.get("quantity") or item.get("count") or 1)
                if food_id is None:
                    continue
                normalized.append({"foodId": food_id, "quantity": quantity or 1})
            if normalized:
                latest_items = normalized
        return latest_items

    def _extract_food_id_pairs(self, answer: str) -> list[tuple[str, int]]:
        pairs: list[tuple[str, int]] = []
        pattern = re.compile(r"([\u4e00-\u9fa5A-Za-z0-9]+)\s*[（(]\s*foodId\s*[:：]\s*(\d+)", re.IGNORECASE)
        for name, raw_id in pattern.findall(answer or ""):
            food_id = self._to_int(raw_id)
            if food_id is not None:
                pairs.append((name.strip("*•- \t\n\r"), food_id))
        return pairs

    def _extract_food_names(self, answer: str, valid_names: set[str]) -> set[str]:
        text = answer or ""
        return {name for name in valid_names if name and name in text}

    def _to_int(self, value: Any) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            try:
                return int(float(value))
            except (TypeError, ValueError):
                return None

    def _merge_lists(self, first: list[str], second: list[str]) -> list[str]:
        return self._dedupe([item for item in [*first, *second] if item])

    def _dedupe(self, items: list[str]) -> list[str]:
        return list(dict.fromkeys(item.strip() for item in items if isinstance(item, str) and item.strip()))

    def _format_tool_observations(self, tool_observations: list[ToolObservation], max_chars: int = 6000) -> str:
        if not tool_observations:
            return ""
        blocks = []
        for idx, obs in enumerate(tool_observations, start=1):
            block = f"[{idx}] tool={obs.name}\n{self._compact_tool_content(obs.content)}"
            blocks.append(block)
        return "\n\n".join(blocks)

    def _compact_tool_content(self, content: str) -> str:
        return (content or "").strip()
    def _simplify(self, value: Any) -> Any:
        if isinstance(value, dict):
            keys = [
                "code", "message", "status", "answer", "summary", "result", "data",
                "sessionId", "deliveryAddress", "deliveryPhone", "remark", "amount",
                "recommendSummary", "orderItems", "items", "references", "content",
                "name", "price", "quantity", "foodId", "id", "title",
            ]
            picked = {k: self._simplify(value[k]) for k in keys if k in value}
            return picked or {k: self._simplify(v) for k, v in list(value.items())[:12]}
        if isinstance(value, list):
            total = len(value)
            shown_items = [self._simplify(item) for item in value[:12]]
            if total > 12:
                return {
                    "_type": "list_preview",
                    "total": total,
                    "shown": len(shown_items),
                    "items": shown_items,
                    "note": f"仅展示前{len(shown_items)}条，原始列表共有{total}条。",
                }
            return shown_items
        return value

    def _parse_json(self, content: str) -> dict | list | None:
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text).strip()
            text = re.sub(r"```$", "", text).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            for left, right in (("{", "}"), ("[", "]")):
                start = text.find(left)
                end = text.rfind(right)
                if start >= 0 and end > start:
                    try:
                        return json.loads(text[start:end + 1])
                    except json.JSONDecodeError:
                        pass
        return None
