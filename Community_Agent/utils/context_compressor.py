"""上下文压缩工具模块。

职责：
1. 估算消息列表 token 并选择压缩档位。
2. 按滑动窗口 + 历史摘要策略构建 Agent 输入消息。
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from models.dto import ChatHistoryMessage
from models.factory import chat_model
from utils.logger_handler import logger
from utils.retry_handler import ContextRetryHandler
from utils.token_utils import estimate_messages_tokens


class ContextCompressor:
    """多 Agent / 单 Agent 共用的上下文压缩器。"""

    def __init__(self, retry_handler: ContextRetryHandler | None = None):
        self.retry_handler = retry_handler or ContextRetryHandler()

    def resolve_retry_level(
        self,
        query: str,
        chat_history: list[ChatHistoryMessage] | None,
        user_memory_context: str = "",
    ) -> int:
        """根据 token 估算结果选择压缩档位，最多升到 max_retry。"""
        for retry_level in range(self.retry_handler.max_retry + 1):
            retry_config = self.retry_handler.get_retry_level_config(retry_level)
            messages = self.build_messages(
                query,
                chat_history,
                user_memory_context,
                retry_level,
                retry_config,
            )
            estimated_tokens = estimate_messages_tokens(messages)
            if not self.retry_handler.should_compress(estimated_tokens):
                logger.info(
                    f"[ContextCompressor] retry_level={retry_level} estimated_tokens={estimated_tokens}"
                )
                return retry_level
            logger.warning(
                f"[ContextCompressor] token 达到阈值，升级到下一档压缩: "
                f"retry_level={retry_level} estimated_tokens={estimated_tokens}"
            )
        return self.retry_handler.max_retry

    def build_messages(
        self,
        query: str,
        chat_history: list[ChatHistoryMessage] | None,
        user_memory_context: str = "",
        retry_level: int = 0,
        retry_config: dict | None = None,
    ) -> list[dict[str, str]]:
        """构建压缩后的 Agent 消息列表。"""
        retry_config = retry_config or self.retry_handler.get_retry_level_config(retry_level)
        max_chars = retry_config["single_message_max_chars"]
        normalized_history = self._normalize_history(chat_history, max_chars)
        compressed_query = self._compress_content(query, max_chars)

        if retry_level <= 0:
            messages: list[dict[str, str]] = []
            if user_memory_context:
                messages.append({"role": "system", "content": user_memory_context})
            messages.extend(normalized_history[-12:])
            messages.append({"role": "user", "content": compressed_query})
            return messages

        summary_message = self._build_history_summary_message(normalized_history, retry_config)
        recent_history = normalized_history[-retry_config["recent_rounds"] * 2 :]

        messages = []
        if user_memory_context:
            messages.append({"role": "system", "content": user_memory_context})
        if summary_message:
            messages.append({"role": "system", "content": summary_message})
        messages.extend(recent_history)
        messages.append({"role": "user", "content": compressed_query})
        return messages

    def _normalize_history(
        self,
        chat_history: list[ChatHistoryMessage] | None,
        max_chars: int,
    ) -> list[dict[str, str]]:
        normalized_history: list[dict[str, str]] = []
        for history_message in chat_history or []:
            role = self._normalize_role(history_message.role)
            content = self._clean_history_content(role, (history_message.content or "").strip())
            content = self._compress_content(content, max_chars)
            if role and content:
                normalized_history.append({"role": role, "content": content})
        return normalized_history

    def _build_history_summary_message(
        self,
        normalized_history: list[dict[str, str]],
        retry_config: dict,
    ) -> str:
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
            summary = str(getattr(response, "content", response) or "").strip()
            return self._compress_content(summary, max_chars)
        except Exception as e:
            logger.warning(f"[ContextCompressor] 历史摘要失败，回退规则截断: {e}")
            return self._compress_content(history_text.replace("\n", "；"), max_chars)

    def _clean_history_content(self, role: str | None, content: str) -> str:
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
        if not content:
            return ""
        content = content.strip()
        if len(content) <= max_chars:
            return content
        return content[:max_chars] + "..."

    def _normalize_role(self, role: str | None) -> str | None:
        if role in {"assistant", "user"}:
            return role
        return None
