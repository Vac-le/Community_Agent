"""LangGraph 多 Agent 状态定义。"""

from __future__ import annotations

from typing import Any, TypedDict

from agent.reflection_service import ToolObservation
from models.dto import ChatHistoryMessage


class AgentState(TypedDict, total=False):
    """多 Agent 编排共享状态。"""

    query: str
    original_query: str
    token: str | None
    session_id: str | None
    chat_history: list[ChatHistoryMessage] | None
    user_id: int | None
    community_id: int | None
    user_memory_context: str

    routes: list[str]
    current_route_index: int
    current_route: str
    current_worker: str

    messages: list[dict[str, str]]
    route_messages: list[dict[str, str]]
    route_answers: list[dict[str, str]]

    called_tools: list[str]
    tool_observations: list[ToolObservation]
    chart_outputs: list[dict]
    control_outputs: list[Any]
    status_events: list[dict[str, Any]]
    food_order_card: dict | None

    final_answer: str
    reflection_attempt: int
    reflection_result: dict[str, Any]
    should_retry: bool
    done: bool

    retry_level: int
    retry_config: dict[str, Any]
