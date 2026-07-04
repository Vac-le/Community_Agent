"""通用 Worker 执行逻辑 — 运行子 Agent 并收集工具结果与副产物。"""

from __future__ import annotations

import json
import re
from typing import Any

from agent.graph.state import AgentState
from agent.reflection_service import ToolObservation
from clients.java_backend_client import JavaBackendClient
from utils.logger_handler import logger

_java_client = JavaBackendClient()


def run_worker(agent_executor, state: AgentState, worker_name: str) -> AgentState:
    """运行一个具体业务 Agent，并把收集到的信息写回共享状态。"""
    final_text = ""
    called_tools = list(state.get("called_tools") or [])
    tool_observations = list(state.get("tool_observations") or [])
    chart_outputs = list(state.get("chart_outputs") or [])
    control_outputs = list(state.get("control_outputs") or [])
    emitted_prepare_intent = False
    emitted_order_card = False

    route_messages = list(state.get("route_messages") or state.get("messages") or [])
    route_answers = list(state.get("route_answers") or [])

    stream_agent = agent_executor
    if hasattr(agent_executor, "with_config"):
        stream_agent = agent_executor.with_config({"run_name": worker_name})

    retry_config = state.get("retry_config") or {}
    tool_prompt_max_chars = retry_config.get("tool_prompt_max_chars", 1200)
    rag_doc_chars = retry_config.get("rag_doc_chars", 500)
    retry_level = state.get("retry_level", state.get("reflection_attempt", 0))

    for chunk in stream_agent.stream(
        {"messages": route_messages},
        stream_mode="values",
        context={
            "token": state.get("token"),
            "user_id": state.get("user_id"),
            "community_id": state.get("community_id"),
            "tool_prompt_max_chars": tool_prompt_max_chars,
            "rag_doc_chars": rag_doc_chars,
            "retry_level": retry_level,
        },
    ):
        messages = chunk.get("messages", [])
        if not messages:
            continue

        _collect_called_tools(messages, called_tools)
        _collect_tool_observations(messages, tool_observations)
        _collect_chart_outputs(messages, chart_outputs)

        if not emitted_prepare_intent and _has_order_draft_tool_call(messages):
            emitted_prepare_intent = True
            control_outputs.append("[INTENT:FOOD_CONFIRM]")

        if emitted_prepare_intent and not emitted_order_card:
            if _has_successful_order_draft_result(messages):
                order_card = _load_pending_order_card(state.get("token"))
                if order_card:
                    emitted_order_card = True
                    control_outputs.append({
                        "type": "food_order_card",
                        "intent": "FOOD_CONFIRM",
                        "content": order_card,
                    })
                    state["food_order_card"] = order_card

        last_msg = messages[-1]
        if getattr(last_msg, "type", None) == "ai":
            tool_calls = getattr(last_msg, "tool_calls", None) or []
            text = _extract_text(getattr(last_msg, "content", ""))
            if text and not tool_calls:
                final_text = text

    if final_text.strip():
        route_answers.append({"route": state.get("current_route", ""), "answer": final_text.strip()})
        route_messages = _append_assistant_message(route_messages, final_text.strip())

    state["called_tools"] = called_tools
    state["tool_observations"] = tool_observations
    state["chart_outputs"] = chart_outputs
    state["control_outputs"] = control_outputs
    state["route_messages"] = route_messages
    state["route_answers"] = route_answers
    state["final_answer"] = final_text.strip() if final_text.strip() else state.get("final_answer", "")
    return state


def _append_assistant_message(messages: list[dict[str, str]], answer: str) -> list[dict[str, str]]:
    next_messages = list(messages)
    next_messages.append({"role": "assistant", "content": answer[-1200:]})
    return next_messages[-16:]


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "".join(parts)
    return str(content) if content is not None else ""


def _collect_called_tools(messages, called_tools: list[str]):
    for msg in messages:
        for tc in getattr(msg, "tool_calls", None) or []:
            if isinstance(tc, dict):
                name = tc.get("name")
                if name and name not in called_tools:
                    called_tools.append(name)
        if getattr(msg, "type", None) == "tool":
            name = getattr(msg, "name", None)
            if name and name not in called_tools:
                called_tools.append(name)


def _collect_tool_observations(messages, obs: list[ToolObservation]):
    existing = {(item.name, item.content) for item in obs}
    for msg in messages:
        if getattr(msg, "type", None) != "tool":
            continue
        tool_name = getattr(msg, "name", None)
        content = _extract_text(getattr(msg, "content", ""))
        status = getattr(msg, "status", None)
        if not tool_name or not content:
            continue
        if status == "error" or "Error invoking tool" in content:
            continue
        key = (tool_name, content)
        if key in existing:
            continue
        obs.append(ToolObservation(name=tool_name, content=content))
        existing.add(key)


def _collect_chart_outputs(messages, chart_outputs: list[dict]):
    existing_urls = {item.get("content", {}).get("imageUrl") for item in chart_outputs}
    for msg in messages:
        if getattr(msg, "type", None) != "tool":
            continue
        tool_name = getattr(msg, "name", "") or ""
        if not _is_viz_tool(tool_name):
            continue
        content = _extract_text(getattr(msg, "content", ""))
        status = getattr(msg, "status", None)
        if not content or status == "error":
            continue
        image_url = _extract_chart_url(content)
        if not image_url or image_url in existing_urls:
            continue
        chart_outputs.append({
            "type": "chart",
            "intent": "CHART",
            "content": {
                "imageUrl": image_url,
                "toolName": tool_name,
                "title": _extract_chart_title(content, tool_name),
            },
        })
        existing_urls.add(image_url)
        logger.info(f"[MCP图表] worker={tool_name} url={image_url}")


def _is_viz_tool(name: str) -> bool:
    if not name.startswith("generate_"):
        return False
    suffixes = {"_chart", "_diagram", "_graph", "_map", "_tree"}
    return any(name.endswith(s) for s in suffixes)


def _extract_chart_url(content: str) -> str | None:
    parsed = _try_json(content)
    if isinstance(parsed, dict):
        for k in ("imageUrl", "image_url", "url", "src"):
            v = parsed.get(k)
            if isinstance(v, str) and v.startswith("http"):
                return v
    md = re.search(r"!\[[^\]]*\]\((https?://[^\s)]+)\)", content)
    if md:
        return md.group(1)
    url = re.search(r"https?://[^\s)\]}\"']+", content)
    return url.group(0) if url else None


def _extract_chart_title(content: str, tool_name: str) -> str:
    parsed = _try_json(content)
    if isinstance(parsed, dict):
        for k in ("title", "name"):
            v = parsed.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
    readable = tool_name.replace("generate_", "").replace("_", " ").strip()
    return readable.title() if readable else "AI 生成可视化"


def _try_json(content: str):
    try:
        return json.loads(content)
    except Exception:
        return None


def _has_order_draft_tool_call(messages) -> bool:
    draft_tools = {"prepare_food_order", "update_food_order_draft"}
    for msg in reversed(messages):
        if getattr(msg, "type", None) == "ai":
            for tc in getattr(msg, "tool_calls", None) or []:
                if isinstance(tc, dict) and tc.get("name") in draft_tools:
                    return True
        if getattr(msg, "type", None) == "tool":
            if getattr(msg, "name", None) in draft_tools:
                return True
    return False


def _has_successful_order_draft_result(messages) -> bool:
    draft_tools = {"prepare_food_order", "update_food_order_draft"}
    for msg in reversed(messages):
        if getattr(msg, "type", None) != "tool":
            continue
        if getattr(msg, "name", None) not in draft_tools:
            continue
        content = _extract_text(getattr(msg, "content", ""))
        if getattr(msg, "status", None) == "error":
            continue
        try:
            payload = json.loads(content)
            if isinstance(payload, dict) and payload.get("code") == 200:
                return True
        except json.JSONDecodeError:
            return bool(content.strip())
    return False


def _load_pending_order_card(token: str | None) -> dict | None:
    if not token:
        return None
    try:
        result = _java_client.get_current_food_order_draft(token)
        foods_result = _java_client.get_food_list(token)
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
    food_map = _build_food_map(foods_result)
    return _build_order_card(data, food_map)


def _build_food_map(foods_result: Any) -> dict[int, dict]:
    foods = []
    if isinstance(foods_result, dict):
        data = foods_result.get("data")
        if isinstance(data, list):
            foods = data
        elif isinstance(foods_result.get("rows"), list):
            foods = foods_result.get("rows") or []
    return {
        int(item.get("id")): item
        for item in foods
        if isinstance(item, dict) and item.get("id") is not None
    }


def _build_order_card(order_data: dict, food_map: dict[int, dict]) -> dict:
    order_items = order_data.get("orderItems") or order_data.get("items") or []
    normalized_items = []
    for item in order_items:
        if not isinstance(item, dict):
            continue
        food_id = item.get("foodId") or item.get("id")
        try:
            food_id_int = int(food_id)
        except (TypeError, ValueError):
            food_id_int = None
        food_info = food_map.get(food_id_int, {}) if food_id_int is not None else {}
        normalized_items.append({
            "id": food_id_int or item.get("id"),
            "foodId": food_id_int or item.get("foodId") or item.get("id"),
            "name": item.get("name") or food_info.get("name") or "未命名菜品",
            "price": item.get("price") or food_info.get("price") or 0,
            "quantity": item.get("quantity") or 1,
            "image": item.get("image") or food_info.get("img") or "",
            "description": item.get("description") or food_info.get("description") or "",
        })
    return {
        "sessionId": order_data.get("sessionId") or "",
        "amount": order_data.get("amount") or 0,
        "deliveryAddress": order_data.get("deliveryAddress") or "",
        "deliveryPhone": order_data.get("deliveryPhone") or "",
        "remark": order_data.get("remark") or "",
        "recommendSummary": order_data.get("recommendSummary") or "",
        "items": normalized_items,
    }
