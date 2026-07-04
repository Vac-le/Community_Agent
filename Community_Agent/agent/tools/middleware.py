"""Agent 中间件模块。

职责：
1. 在工具调用前后记录日志。
2. 将 token、RAG 压缩参数等上下文信息注入工具入参。
3. 在模型调用前记录消息情况。
"""

from typing import Callable

from langchain.agents import AgentState
from langchain.agents.middleware import before_model, wrap_tool_call
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command

from utils.logger_handler import logger

# 这组工具依赖登录态 token，但 token 属于运行时上下文，不应依赖模型稳定产出。
# 因此统一在 middleware 注入，避免模型忘填、填错或暴露内部鉴权细节。
TOKEN_INJECT_TOOLS = {
    "query_user_order_history",
    "prepare_food_order",
    "update_food_order_draft",
    "get_pending_food_order",
    "query_all_foods",
    "confirm_food_order",
    "send_agent_chart_email",
    "send_agent_text_email",
    "query_weather_forecast",
}

USER_CONTEXT_INJECT_TOOLS = {
    "send_agent_chart_email",
    "send_agent_text_email",
    "save_user_email_to_memory",
}


def _safe_preview_text(text, max_chars: int = 1200) -> str:
    """将日志中的模型输入内容裁成可读预览，避免控制台过于冗长。"""
    if text is None:
        return ""
    text = str(text)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f" ...[truncated,total={len(text)} chars]"


@wrap_tool_call
def monitor_tool(
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command]
) -> ToolMessage | Command:
    """统一监控工具调用，并注入运行时上下文参数。"""
    logger.info(f"[tool monitor]传入参数:{request.tool_call['args']}")
    # LangChain 先记录的是模型原始 tool_call；真正执行前在这里补系统参数。
    if request.tool_call['name'] in TOKEN_INJECT_TOOLS:
        try:
            if hasattr(request, "runtime"):
                if hasattr(request.runtime, "context"):
                    token = request.runtime.context.get("token")
                    request.tool_call["args"]["token"] = token
                    logger.info("[tool monitor]已注入 token")
        except Exception as e:
            logger.error(f"[tool monitor]获取 token 时发生错误: {str(e)}")

    if request.tool_call['name'] in USER_CONTEXT_INJECT_TOOLS:
        try:
            if hasattr(request, "runtime") and hasattr(request.runtime, "context"):
                request.tool_call["args"]["user_id"] = request.runtime.context.get("user_id")
                request.tool_call["args"]["community_id"] = request.runtime.context.get("community_id")
                logger.info("[tool monitor]已注入 user_id/community_id")
        except Exception as e:
            logger.error(f"[tool monitor]注入用户上下文失败: {str(e)}")

    if request.tool_call["name"] == "rag_summarize":
        try:
            if hasattr(request, "runtime") and hasattr(request.runtime, "context"):
                # RAG 截断长度属于运行时调度参数，会随重试级别动态变化，
                # 因此同样由程序注入而不是写死在工具 description 里。
                rag_doc_chars = request.runtime.context.get("rag_doc_chars")
                if rag_doc_chars:
                    request.tool_call["args"]["max_doc_chars"] = rag_doc_chars
                    logger.info(f"[tool monitor]为 rag_summarize 注入 max_doc_chars={rag_doc_chars}")
        except Exception as e:
            logger.error(f"[tool monitor]注入 RAG 压缩参数失败: {str(e)}")

    logger.info(f"[tool monitor]执行工具:{request.tool_call['name']}")
    logger.info(f"[tool monitor]传入参数:{request.tool_call['args']}")
    try:
        result = handler(request)
        logger.info(f"[tool monitor]执行工具:{request.tool_call['name']} 调用成功")
        logger.info(f"[tool monitor]工具结果预览:{_safe_preview_text(result)}")
        return result
    except Exception as e:
        error_text = str(e)
        tool_name = request.tool_call.get("name", "unknown_tool")
        tool_call_id = request.tool_call.get("id")
        logger.error(f"[tool monitor]工具:{tool_name} 调用失败, 失败原因:{error_text}")
        return ToolMessage(
            content=(
                f"工具 {tool_name} 调用失败。错误信息：{error_text}\n"
                "请根据这个真实错误修正工具参数后重试；如果无法修正，请如实告知用户当前工具调用失败，"
                "不要声称工具已经执行成功。"
            ),
            name=tool_name,
            tool_call_id=tool_call_id,
            status="error",
        )


@before_model
def log_before_model(
        state: AgentState,
        runtime: Runtime,
):
    """模型调用前只记录消息数量与必要摘要，不打印完整历史对话。"""
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    last_role = (
        (getattr(last_message, "type", None) or getattr(last_message, "role", None) or type(last_message).__name__)
        if last_message is not None else "none"
    )
    last_has_tool_calls = bool(getattr(last_message, "tool_calls", None)) if last_message is not None else False
    logger.info(
        f"[log_before_model]即将调用模型，带有:{len(messages)}条消息 "
        f"last_role={last_role} last_has_tool_calls={last_has_tool_calls}"
    )
    return None
