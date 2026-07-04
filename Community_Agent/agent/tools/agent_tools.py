"""Agent 本地业务工具集合。

职责：
1. 将 RAG 检索总结能力封装为 Agent 工具。
2. 将 Java 后端餐饮订单能力封装为 Agent 工具。
3. 保持工具入参与主提示词、middleware 注入逻辑一致。
"""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.tools import tool

from clients.java_backend_client import JavaBackendClient
from memory.user_long_memory_service import UserLongMemoryService
from rag.rag_service import RagSummarizeService
from utils.logger_handler import logger

_rag_service: RagSummarizeService | None = None
_java_client = JavaBackendClient()
_user_memory_service = UserLongMemoryService()


def _get_rag_service() -> RagSummarizeService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RagSummarizeService()
    return _rag_service


def _to_json_text(payload: Any) -> str:
    """将工具返回统一转为 JSON 字符串，便于模型读取。"""
    return json.dumps(payload, ensure_ascii=False)


def _extract_email(text: str | None) -> str | None:
    """从用户输入中提取邮箱。"""
    if not text:
        return None
    match = re.search(r"[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+", text)
    return match.group(0) if match else None


@tool
def save_user_email_to_memory(email: str, user_id: int | None = None, community_id: int | None = None) -> str:
    """当用户明确提供邮箱时，将邮箱保存到长期记忆，供后续发送图表或分析报告邮件使用。"""
    try:
        result = _user_memory_service.save_user_email(user_id, community_id, email)
        return _to_json_text({"code": 200 if result.get("saved") or result.get("email") else 1, "message": result.get("reason", "邮箱已保存"), "data": result})
    except Exception as e:
        logger.error(f"[AgentTool] save_user_email_to_memory 调用失败: {e}")
        return _to_json_text({"code": 500, "message": str(e), "data": None})


@tool
def send_agent_chart_email(
    chart_url: str,
    agent_message: str,
    subject: str = "社区助手图表分析结果",
    chart_title: str = "Agent 生成图表",
    to_email: str | None = None,
    user_email_from_message: str | None = None,
    token: str | None = None,
    user_id: int | None = None,
    community_id: int | None = None,
) -> str:
    """把 Agent 生成的图表图片链接和分析说明发送到用户邮箱；若没有邮箱，返回 need_email 要求先询问用户邮箱。"""
    if not token:
        return _to_json_text({"code": 401, "message": "缺少登录 token，无法发送邮件", "data": None})

    email = _extract_email(to_email) or _extract_email(user_email_from_message)
    if email:
        _user_memory_service.save_user_email(user_id, community_id, email)
    else:
        email = _user_memory_service.get_user_email(user_id, community_id)

    if not email:
        return _to_json_text({
            "code": 422,
            "message": "当前不知道用户邮箱，请先询问用户用于接收图表的邮箱。用户提供邮箱后，先调用 save_user_email_to_memory 保存，再重新调用本工具发送邮件。",
            "data": {"need_email": True},
        })

    email_data = {
        "toEmail": email,
        "subject": subject,
        "agentMessage": agent_message,
        "chartUrl": chart_url,
        "chartTitle": chart_title,
    }
    try:
        result = _java_client.send_chart_email(token, email_data)
        if isinstance(result, dict) and result.get("code") == 200:
            result = {
                "code": 200,
                "message": result.get("message", "邮件发送成功"),
                "data": {
                    "toEmail": email,
                    "subject": subject,
                    "chartTitle": chart_title,
                    "status": "SENT",
                },
            }
        return _to_json_text(result)
    except Exception as e:
        logger.error(f"[AgentTool] send_agent_chart_email 调用失败: {e}")
        return _to_json_text({"code": 500, "message": str(e), "data": None})


@tool
def send_agent_text_email(
    agent_message: str,
    subject: str = "社区助手结果通知",
    to_email: str | None = None,
    user_email_from_message: str | None = None,
    token: str | None = None,
    user_id: int | None = None,
    community_id: int | None = None,
) -> str:
    """把 Agent 生成的通用文本结果发送到用户邮箱，适用于订单推荐摘要、服务结果说明等非图表场景。"""
    if not token:
        return _to_json_text({"code": 401, "message": "缺少登录 token，无法发送邮件", "data": None})

    email = _extract_email(to_email) or _extract_email(user_email_from_message)
    if email:
        _user_memory_service.save_user_email(user_id, community_id, email)
    else:
        email = _user_memory_service.get_user_email(user_id, community_id)

    if not email:
        return _to_json_text({
            "code": 422,
            "message": "当前不知道用户邮箱，请先询问用户用于接收结果的邮箱。用户提供邮箱后，先调用 save_user_email_to_memory 保存，再重新调用本工具发送邮件。",
            "data": {"need_email": True},
        })

    email_data = {
        "toEmail": email,
        "subject": subject,
        "agentMessage": agent_message,
    }
    try:
        result = _java_client.send_agent_email(token, email_data)
        if isinstance(result, dict) and result.get("code") == 200:
            result = {
                "code": 200,
                "message": result.get("message", "邮件发送成功"),
                "data": {
                    "toEmail": email,
                    "subject": subject,
                    "status": "SENT",
                },
            }
        return _to_json_text(result)
    except Exception as e:
        logger.error(f"[AgentTool] send_agent_text_email 调用失败: {e}")
        return _to_json_text({"code": 500, "message": str(e), "data": None})


@tool
def query_weather_forecast(token: str | None = None) -> str:
    """查询天气预报信息，当前固定查询 cityId=2250 的 15 日天气。"""
    if not token:
        return _to_json_text({"code": 401, "message": "缺少登录 token，无法查询天气", "data": None})
    try:
        return _to_json_text(_java_client.get_weather(token, city_id=2250))
    except Exception as e:
        logger.error(f"[AgentTool] query_weather_forecast 调用失败: {e}")
        return _to_json_text({"code": 500, "message": str(e), "data": None})


@tool
def rag_summarize(query: str, max_doc_chars: int | None = None) -> str:
    """检索社区公告、社区服务知识库，并返回总结后的自然语言答案。"""
    return _get_rag_service().rag_summarize(query, max_doc_chars=max_doc_chars)


@tool
def query_all_foods(token: str | None = None) -> str:
    """查询当前社区全部菜品信息，包括菜品名称、价格、描述、图片和分类。"""
    if not token:
        return _to_json_text({"code": 401, "message": "缺少登录 token，无法查询菜品", "data": None})
    try:
        return _to_json_text(_java_client.get_food_list(token))
    except Exception as e:
        logger.error(f"[AgentTool] query_all_foods 调用失败: {e}")
        return _to_json_text({"code": 500, "message": str(e), "data": None})


@tool
def query_user_order_history(token: str | None = None) -> str:
    """查询当前登录用户的历史餐饮订单。"""
    if not token:
        return _to_json_text({"code": 401, "message": "缺少登录 token，无法查询历史订单", "data": None})
    try:
        return _to_json_text(_java_client.get_user_order_history(token))
    except Exception as e:
        logger.error(f"[AgentTool] query_user_order_history 调用失败: {e}")
        return _to_json_text({"code": 500, "message": str(e), "data": None})


@tool
def prepare_food_order(
    session_id: str,
    delivery_address: str,
    delivery_phone: str,
    order_items: list[dict[str, Any]],
    amount: int,
    recommend_summary: str,
    remark: str = "",
    token: str | None = None,
) -> str:
    """保存一份待确认的餐饮订单草稿，不会真实下单。"""
    if not token:
        return _to_json_text({"code": 401, "message": "缺少登录 token，无法保存订单草稿", "data": None})
    draft_data = {
        "sessionId": session_id,
        "deliveryAddress": delivery_address,
        "deliveryPhone": delivery_phone,
        "orderItems": order_items,
        "amount": amount,
        "recommendSummary": recommend_summary,
        "remark": remark or "",
    }
    try:
        return _to_json_text(_java_client.save_food_order_draft(token, draft_data))
    except Exception as e:
        logger.error(f"[AgentTool] prepare_food_order 调用失败: {e}")
        return _to_json_text({"code": 500, "message": str(e), "data": None})


@tool
def update_food_order_draft(
    session_id: str,
    delivery_address: str,
    delivery_phone: str,
    order_items: list[dict[str, Any]],
    amount: int,
    recommend_summary: str,
    remark: str = "",
    token: str | None = None,
) -> str:
    """更新当前用户的待确认餐饮订单草稿。"""
    if not token:
        return _to_json_text({"code": 401, "message": "缺少登录 token，无法更新订单草稿", "data": None})
    draft_data = {
        "sessionId": session_id,
        "deliveryAddress": delivery_address,
        "deliveryPhone": delivery_phone,
        "orderItems": order_items,
        "amount": amount,
        "recommendSummary": recommend_summary,
        "remark": remark or "",
    }
    try:
        return _to_json_text(_java_client.update_food_order_draft(token, draft_data))
    except Exception as e:
        logger.error(f"[AgentTool] update_food_order_draft 调用失败: {e}")
        return _to_json_text({"code": 500, "message": str(e), "data": None})


@tool
def get_pending_food_order(token: str | None = None) -> str:
    """获取当前用户待确认的餐饮订单草稿。"""
    if not token:
        return _to_json_text({"code": 401, "message": "缺少登录 token，无法查询待确认订单", "data": None})
    try:
        return _to_json_text(_java_client.get_current_food_order_draft(token))
    except Exception as e:
        logger.error(f"[AgentTool] get_pending_food_order 调用失败: {e}")
        return _to_json_text({"code": 500, "message": str(e), "data": None})


@tool
def confirm_food_order(session_id: str, token: str | None = None) -> str:
    """确认当前待确认餐饮订单草稿，并创建正式订单。"""
    if not token:
        return _to_json_text({"code": 401, "message": "缺少登录 token，无法确认订单", "data": None})
    try:
        return _to_json_text(_java_client.confirm_food_order(token, session_id))
    except Exception as e:
        logger.error(f"[AgentTool] confirm_food_order 调用失败: {e}")
        return _to_json_text({"code": 500, "message": str(e), "data": None})
