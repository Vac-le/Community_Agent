"""Token 估算工具模块。

职责：
1. 粗略估算文本 token 数。
2. 粗略估算消息列表的 token 数。

说明：
当前实现是轻量估算版，主要用于上下文压缩和超窗重试，
并非精确 tokenizer 结果。
"""

from __future__ import annotations


def estimate_text_tokens(text: str) -> int:
    """按字符长度粗略估算文本 token 数。"""
    if not text:
        return 0
    return max(1, len(text) // 2)


def estimate_messages_tokens(messages: list[dict[str, str]]) -> int:
    """估算消息列表的总 token 数。"""
    total = 0
    for message in messages:
        total += estimate_text_tokens(message.get("content", "")) + 8
    return total
