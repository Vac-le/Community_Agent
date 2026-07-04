"""上下文超窗重试策略模块。

职责：
1. 判断异常是否属于上下文超限类错误。
2. 根据重试级别给出不同的裁剪配置。
3. 为 Agent 的自动降级重试提供统一策略入口。
"""

from __future__ import annotations

from utils.config_handler import rag_config


class ContextRetryHandler:
    """上下文重试策略管理器。"""

    def __init__(self, max_retry: int | None = None):
        retry_config = rag_config.get("retry", {})
        self.max_retry = max_retry if max_retry is not None else retry_config.get("max_retry", 3)
        self.max_context_tokens = retry_config.get("max_context_tokens", 32000)
        self.trigger_ratio = retry_config.get("trigger_ratio", 0.8)
        self.recent_rounds = retry_config.get("recent_rounds", 2)
        self.summary_max_chars = retry_config.get("summary_max_chars", [200, 150, 100, 50])
        self.single_message_max_chars = retry_config.get("single_message_max_chars", [600, 500, 400, 300])
        self.rag_doc_chars = retry_config.get("rag_doc_chars", [500, 300, 200, 150])
        self.tool_prompt_max_chars = retry_config.get("tool_prompt_max_chars", [1200, 800, 500, 300])

    def should_retry(self, error: Exception) -> bool:
        """判断异常是否值得按超窗策略重试。"""
        message = str(error).lower()
        return any(
            keyword in message
            for keyword in [
                "context",
                "token",
                "maximum context length",
                "context length exceeded",
                "prompt is too long",
                "input is too long",
            ]
        )

    def should_compress(self, estimated_tokens: int) -> bool:
        """当估算 token 达到上下文窗口阈值时触发裁剪。"""
        return estimated_tokens >= int(self.max_context_tokens * self.trigger_ratio)

    def get_retry_level_config(self, retry_index: int) -> dict:
        """根据重试次数返回对应的上下文压缩配置。"""
        return {
            "recent_rounds": self.recent_rounds,
            "summary_max_chars": self.summary_max_chars[min(retry_index, len(self.summary_max_chars) - 1)],
            "single_message_max_chars": self.single_message_max_chars[min(retry_index, len(self.single_message_max_chars) - 1)],
            "rag_doc_chars": self.rag_doc_chars[min(retry_index, len(self.rag_doc_chars) - 1)],
            "tool_prompt_max_chars": self.tool_prompt_max_chars[min(retry_index, len(self.tool_prompt_max_chars) - 1)],
        }
