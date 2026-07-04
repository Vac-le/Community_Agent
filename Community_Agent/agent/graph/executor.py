"""LangGraph 多 Agent 主执行器 — 工程化显式 worker 节点版本。"""

from __future__ import annotations

import json
import threading

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from agent.graph.agents import (
    create_knowledge_agent,
    create_order_agent,
    create_report_agent,
    create_weather_agent,
)
from agent.graph.state import AgentState
from agent.graph.supervisor import supervisor_route
from agent.graph.worker import run_worker
from agent.reflection_service import ReflectionService
from memory.user_long_memory_service import UserLongMemoryService
from models.dto import ChatHistoryMessage
from models.factory import chat_model
from utils.context_compressor import ContextCompressor
from utils.logger_handler import logger
from utils.retry_handler import ContextRetryHandler

ROUTE_LABELS = {
    "knowledge": "知识问答",
    "order": "订餐订单",
    "report": "数据分析",
    "weather": "天气查询",
}

ROUTE_TO_NODE = {
    "knowledge": "knowledge_worker",
    "order": "order_worker",
    "report": "report_worker",
    "weather": "weather_worker",
}


class MultiAgentExecutor:
    def __init__(self):
        self.knowledge_agent = create_knowledge_agent()
        self.order_agent = create_order_agent()
        self.report_agent = create_report_agent()
        self.weather_agent = create_weather_agent()
        self.reflection_service = ReflectionService(chat_model)
        self.user_memory_service = UserLongMemoryService()
        self.retry_handler = ContextRetryHandler()
        self.context_compressor = ContextCompressor(self.retry_handler)
        self.graph = self._build_graph().compile()

    def execute_stream(self, query: str, token: str | None = None, session_id: str | None = None, chat_history: list[ChatHistoryMessage] | None = None, user_id: int | None = None, community_id: int | None = None):
        logger.info(f"[MultiAgent] query={query[:200]}")
        user_memory_context = self.user_memory_service.build_memory_context(user_id, community_id)
        retry_level = self.context_compressor.resolve_retry_level(query, chat_history, user_memory_context)
        retry_config = self.retry_handler.get_retry_level_config(retry_level)
        base_messages = self.context_compressor.build_messages(
            query, chat_history, user_memory_context, retry_level, retry_config
        )
        state: AgentState = {"query": query, "original_query": query, "token": token, "session_id": session_id, "chat_history": chat_history, "user_id": user_id, "community_id": community_id, "user_memory_context": user_memory_context, "routes": [], "current_route_index": 0, "current_route": "", "current_worker": "", "messages": base_messages, "route_messages": base_messages, "route_answers": [], "called_tools": [], "tool_observations": [], "chart_outputs": [], "control_outputs": [], "status_events": [], "food_order_card": None, "final_answer": "", "reflection_attempt": 0, "should_retry": False, "done": False, "retry_level": retry_level, "retry_config": retry_config}
        emitted_chart_urls: set[str] = set()
        emitted_control_keys: set[str] = set()
        emitted_status_keys: set[str] = set()
        confirmed_answer = ""
        for chunk in self.graph.stream(state, stream_mode="updates"):
            for node_name, node_state in chunk.items():
                for status in (node_state.get("status_events") or []):
                    status_key = json.dumps(status, ensure_ascii=False, sort_keys=True)
                    if status_key not in emitted_status_keys:
                        emitted_status_keys.add(status_key)
                        yield status
                for chart in (node_state.get("chart_outputs") or []):
                    url = (chart.get("content") or {}).get("imageUrl", "")
                    if url and url not in emitted_chart_urls:
                        emitted_chart_urls.add(url)
                        yield chart
                for ctrl in (node_state.get("control_outputs") or []):
                    key = str(ctrl)
                    if key not in emitted_control_keys:
                        emitted_control_keys.add(key)
                        yield ctrl
                if node_name == "reflector":
                    if node_state.get("should_retry", False):
                        yield {"type": "status", "phase": "planning", "stage": "reflecting", "message": "发现结果需要修正，正在根据反思意见重新执行", "node": node_name, "progress": 70}
                    else:
                        confirmed_answer = node_state.get("final_answer") or confirmed_answer
                if node_name == "memory_updater":
                    final_answer = node_state.get("final_answer") or confirmed_answer
                    self._async_update_memory(user_id, community_id, query, final_answer)
                    if final_answer:
                        yield final_answer

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("supervisor", self._supervisor_node)
        graph.add_node("knowledge_worker", self._knowledge_worker_node)
        graph.add_node("order_worker", self._order_worker_node)
        graph.add_node("report_worker", self._report_worker_node)
        graph.add_node("weather_worker", self._weather_worker_node)
        graph.add_node("final_summarizer", self._final_summarizer_node)
        graph.add_node("reflector", self._reflector_node)
        graph.add_node("memory_updater", self._memory_updater_node)
        graph.set_entry_point("supervisor")
        graph.add_conditional_edges("supervisor", self._next_worker_from_state, {"knowledge_worker": "knowledge_worker", "order_worker": "order_worker", "report_worker": "report_worker", "weather_worker": "weather_worker", "final_summarizer": "final_summarizer", "reflector": "reflector"})
        for worker_node in ROUTE_TO_NODE.values():
            graph.add_conditional_edges(worker_node, self._after_worker_decision, {"knowledge_worker": "knowledge_worker", "order_worker": "order_worker", "report_worker": "report_worker", "weather_worker": "weather_worker", "final_summarizer": "final_summarizer", "reflector": "reflector"})
        graph.add_edge("final_summarizer", "reflector")
        graph.add_conditional_edges("reflector", self._after_reflector_decision, {"supervisor": "supervisor", "memory_updater": "memory_updater"})
        graph.add_edge("memory_updater", END)
        return graph

    def _supervisor_node(self, state: AgentState) -> AgentState:
        routing_query = state.get("query") or state.get("original_query") or ""
        history_summary = self._build_history_hint(state.get("chat_history"))
        routes = supervisor_route(routing_query, history_summary)
        retry_instruction = ""
        current_query = state.get("query", "")
        original_query = state.get("original_query") or routing_query
        if state.get("reflection_attempt", 0) > 0 and current_query and current_query != original_query:
            retry_instruction = current_query
        base_messages = self._build_base_messages(
            routing_query,
            state.get("chat_history"),
            state.get("user_memory_context", ""),
            state.get("retry_level", 0),
            state.get("retry_config"),
        )
        if retry_instruction:
            base_messages.insert(1 if base_messages and base_messages[0]["role"] == "system" else 0, {"role": "system", "content": retry_instruction})
        state["routes"] = routes
        state["current_route_index"] = 0
        state["current_route"] = routes[0] if routes else ""
        state["current_worker"] = ROUTE_TO_NODE.get(state["current_route"], "")
        state["messages"] = base_messages
        state["route_messages"] = base_messages
        state["route_answers"] = []
        state["final_answer"] = ""
        state["status_events"] = [self._status_event(phase="planning", stage="routing", message=self._planning_message_for_routes(routes, state.get("reflection_attempt", 0)), node="supervisor", progress=30, details={"routes": routes})]
        logger.info(f"[Supervisor] routes={routes} retry_attempt={state.get('reflection_attempt', 0)}")
        return state

    def _knowledge_worker_node(self, state: AgentState) -> AgentState:
        state["current_route"] = "knowledge"
        state["current_worker"] = "knowledge_worker"
        state["status_events"] = [self._status_event(phase="retrieving", stage="retrieving", message="正在检索社区知识库", node="knowledge_worker", progress=45, details={"route": "knowledge"})]
        return self._advance_route_index(run_worker(self.knowledge_agent, state, "knowledge_agent"))

    def _order_worker_node(self, state: AgentState) -> AgentState:
        state["current_route"] = "order"
        state["current_worker"] = "order_worker"
        state["status_events"] = [self._status_event(phase="tool_calling", stage="tool_calling", message="正在处理订餐相关请求", node="order_worker", progress=60, details={"route": "order"})]
        return self._advance_route_index(run_worker(self.order_agent, state, "order_agent"))

    def _report_worker_node(self, state: AgentState) -> AgentState:
        state["current_route"] = "report"
        state["current_worker"] = "report_worker"
        state["status_events"] = [self._status_event(phase="retrieving", stage="retrieving", message="正在分析数据并生成图表", node="report_worker", progress=50, details={"route": "report"})]
        return self._advance_route_index(run_worker(self.report_agent, state, "report_agent"))

    def _weather_worker_node(self, state: AgentState) -> AgentState:
        state["current_route"] = "weather"
        state["current_worker"] = "weather_worker"
        state["status_events"] = [self._status_event(phase="retrieving", stage="retrieving", message="正在查询天气信息", node="weather_worker", progress=45, details={"route": "weather"})]
        return self._advance_route_index(run_worker(self.weather_agent, state, "weather_agent"))

    def _advance_route_index(self, state: AgentState) -> AgentState:
        routes = state.get("routes") or []
        next_index = state.get("current_route_index", 0) + 1
        if next_index < len(routes):
            next_route = routes[next_index]
            state["current_route_index"] = next_index
            state["current_route"] = next_route
            state["current_worker"] = ROUTE_TO_NODE.get(next_route, "")
            base_messages = self._build_base_messages(
                state.get("query") or state.get("original_query", ""),
                state.get("chat_history"),
                state.get("user_memory_context", ""),
                state.get("retry_level", 0),
                state.get("retry_config"),
            )
            prior_context = self._build_prior_agents_context(state.get("route_answers") or [])
            if prior_context:
                insert_pos = next((i for i, m in enumerate(base_messages) if m.get("role") == "user"), len(base_messages))
                base_messages.insert(insert_pos, {"role": "system", "content": prior_context})
            state["messages"] = base_messages
            state["route_messages"] = base_messages
        else:
            state["current_worker"] = ""
        return state

    def _build_prior_agents_context(self, route_answers: list[dict]) -> str:
        parts = []
        labels = {"knowledge": "知识问答", "order": "订单", "report": "数据分析与图表", "weather": "天气"}
        for item in route_answers:
            answer = (item.get("answer") or "").strip()
            if answer:
                label = labels.get(item.get("route", ""), item.get("route", ""))
                parts.append(f"【{label} Agent 已完成的结果】\n{answer[:800]}")
        return "以下是本次请求中前置 Agent 已完成的任务结果，你可以直接引用这些信息，无需重复查询相同数据：\n\n" + "\n\n".join(parts) if parts else ""

    def _next_worker_from_state(self, state: AgentState) -> str:
        worker = state.get("current_worker")
        return worker if worker in ROUTE_TO_NODE.values() else ("final_summarizer" if len(state.get("routes") or []) > 1 else "reflector")

    def _after_worker_decision(self, state: AgentState) -> str:
        worker = state.get("current_worker")
        return worker if worker in ROUTE_TO_NODE.values() else ("final_summarizer" if len(state.get("routes") or []) > 1 else "reflector")

    def _final_summarizer_node(self, state: AgentState) -> AgentState:
        status_events = list(state.get("status_events") or [])
        status_events.append(self._status_event(phase="generating", stage="generating", message="正在整合多个子任务的结果", node="final_summarizer", progress=80))
        state["status_events"] = status_events
        route_answers = state.get("route_answers") or []
        if len(route_answers) <= 1:
            if route_answers and not state.get("final_answer"):
                state["final_answer"] = (route_answers[0].get("answer") or "").strip()
            return state
        parts = []
        labels = {"knowledge": "知识问答", "order": "订单处理", "report": "数据分析", "weather": "天气"}
        for item in route_answers:
            answer = (item.get("answer") or "").strip()
            if answer:
                label = labels.get(item.get("route", ""), item.get("route", "") or "Agent")
                parts.append(f"【{label}结果】\n{answer}")
        if not parts:
            return state
        history_summary = self._build_history_hint(state.get("chat_history"))
        joined = "\n\n".join(parts)
        prompt = (
            "你是最终答复整合器。请基于多个子 Agent 的结果，输出一份直接面向用户的最终答案。\n"
            "要求：1.只输出一个最终答案；2.合并重复信息；3.自然整合依赖关系；4.不要编造事实；5.不要暴露多Agent过程。\n\n"
            f"【用户原始问题】\n{state.get('original_query', '')}\n\n"
            f"【最近对话摘要】\n{history_summary or '无'}\n\n"
            f"【多个子 Agent 的结果】\n{joined}"
        )
        try:
            response = chat_model.invoke([SystemMessage(content="你负责将多个子结果整合成一个最终用户答案。"), HumanMessage(content=prompt)])
            final_answer = self._extract_message_text(getattr(response, "content", response)).strip()
            if final_answer:
                state["final_answer"] = final_answer
        except Exception as e:
            logger.warning(f"[FinalSummarizer] 总结失败，回退到顺序拼接答案: {e}")
            state["final_answer"] = "\n\n".join(parts).strip()
        return state

    def _reflector_node(self, state: AgentState) -> AgentState:
        status_events = list(state.get("status_events") or [])
        status_events.append(self._status_event(phase="summarizing", stage="reflecting", message="正在校验最终回答的一致性", node="reflector", progress=90))
        state["status_events"] = status_events
        history_summary = self._build_history_hint(state.get("chat_history"))
        result = self.reflection_service.check(state.get("original_query", state.get("query", "")), state.get("final_answer", ""), state.get("called_tools", []), state.get("tool_observations", []), history_summary, state.get("user_memory_context", ""))
        logger.info(f"[Reflector] passed={result.passed} should_retry={result.should_retry} attempt={state.get('reflection_attempt', 0)} issues={result.issues}")
        if result.should_retry and state.get("reflection_attempt", 0) < self.reflection_service.max_retry:
            state["should_retry"] = True
            state["reflection_attempt"] = state.get("reflection_attempt", 0) + 1
            retry_query = self.reflection_service.build_retry_query(state.get("original_query", ""), state.get("final_answer", ""), result, state.get("tool_observations", []), history_summary, state.get("user_memory_context", ""))
            state["query"] = retry_query
            rebuilt_messages = self._build_base_messages(
                retry_query,
                state.get("chat_history"),
                state.get("user_memory_context", ""),
                state.get("retry_level", 0),
                state.get("retry_config"),
            )
            state["messages"] = rebuilt_messages
            state["route_messages"] = rebuilt_messages
        else:
            state["should_retry"] = False
            state["done"] = True
        return state

    def _after_reflector_decision(self, state: AgentState) -> str:
        return "supervisor" if state.get("should_retry") else "memory_updater"

    def _memory_updater_node(self, state: AgentState) -> AgentState:
        state["done"] = True
        return state

    def _build_base_messages(
        self,
        query: str,
        chat_history: list[ChatHistoryMessage] | None,
        user_memory_context: str,
        retry_level: int = 0,
        retry_config: dict | None = None,
    ) -> list[dict[str, str]]:
        return self.context_compressor.build_messages(
            query,
            chat_history,
            user_memory_context,
            retry_level,
            retry_config or self.retry_handler.get_retry_level_config(retry_level),
        )

    def _extract_message_text(self, content) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(str(getattr(item, "text", "") or ""))
            return "".join(parts)
        return str(content) if content is not None else ""

    def _async_update_memory(self, user_id, community_id, query, final_answer):
        def _worker():
            try:
                result = self.user_memory_service.update_from_query(user_id, community_id, query, final_answer)
                logger.info(f"[UserMemory] update_result={result}")
            except Exception as e:
                logger.warning(f"[UserMemory] update failed: {e}")
        threading.Thread(target=_worker, daemon=True).start()

    def _build_history_hint(self, chat_history: list[ChatHistoryMessage] | None) -> str:
        if not chat_history:
            return ""
        parts = []
        for msg in chat_history[-6:]:
            if getattr(msg, "content", None):
                parts.append(f"{'用户' if msg.role == 'user' else '助手'}: {msg.content[:120]}")
        return "\n".join(parts)


    def _planning_message_for_routes(self, routes: list[str], reflection_attempt: int) -> str:
        if reflection_attempt > 0:
            return "正在根据反思意见重新规划处理步骤"
        if not routes:
            return "正在分析你的需求"
        if len(routes) == 1:
            return f"已识别需求，将交给{ROUTE_LABELS.get(routes[0], routes[0])}处理"
        route_labels = "、".join(ROUTE_LABELS.get(route, route) for route in routes)
        return f"已识别复合需求，将依次交给{route_labels}处理"

    def _status_event(self, phase: str, stage: str, message: str, node: str, progress: int | None = None, details: dict | None = None) -> dict:
        payload = {"type": "status", "phase": phase, "stage": stage, "message": message, "node": node}
        if progress is not None:
            payload["progress"] = progress
        if details:
            payload["details"] = details
        return payload
