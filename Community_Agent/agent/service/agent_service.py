"""Agent 业务服务层。

职责：
1. 接收 API 层传入的聊天请求。
2. 调用 ReactAgent 执行具体推理与工具调用。
3. 将底层输出封装为前端可消费的结构化 SSE 事件。
4. 使用 Java 侧透传的短期会话历史。
"""

import json
from typing import Iterator

from agent.graph.executor import MultiAgentExecutor
from clients.java_backend_client import JavaBackendClient
from models.dto import AgentChatRequest


class AgentService:
    """Agent 服务层实现。"""

    def __init__(self):
        """初始化服务依赖。"""
        self.java_client = JavaBackendClient()
        self.react_client = MultiAgentExecutor()

    def chat_stream(self, request: AgentChatRequest) -> Iterator[str]:
        """以结构化 SSE 方式处理一轮 Agent 聊天。"""
        intent = "CHAT"
        references = []
        final_answer = ""
        final_emitted = False
        last_phase = ""

        session_history = request.chatHistory or []
        history_text = " ".join([(msg.content or "") for msg in session_history])
        combined_text = f"{history_text} {request.currentMessage}".strip()

        if any(keyword in combined_text for keyword in ["下单", "帮我下单", "根据我的历史订单下单"]):
            intent = "FOOD_PREVIEW"

        for payload in (
            self._build_status_payload(request.sessionId, intent, phase="received", message="已收到你的请求", stage="started", progress=5),
            self._build_status_payload(request.sessionId, intent, phase="understanding", message="正在理解你的需求", stage="routing", progress=15),
            self._build_status_payload(request.sessionId, intent, phase="planning", message="正在规划处理步骤", stage="routing", progress=25),
        ):
            last_phase = payload["phase"]
            yield self._to_sse(payload)

        try:
            for chunk in self.react_client.execute_stream(
                request.currentMessage,
                token=request.token,
                session_id=request.sessionId,
                chat_history=session_history,
                user_id=request.userId,
                community_id=request.communityId,
            ):
                if isinstance(chunk, str):
                    next_intent, text_content = self._parse_stream_text(chunk, intent)
                    if next_intent != intent:
                        intent = next_intent
                    if not text_content:
                        continue
                    final_answer = text_content.strip()
                    if final_answer:
                        if last_phase != "summarizing":
                            payload = self._build_status_payload(
                                request.sessionId,
                                intent,
                                phase="summarizing",
                                message="正在整理最终结果",
                                stage="validating",
                                progress=92,
                            )
                            last_phase = payload["phase"]
                            yield self._to_sse(payload)
                        final_emitted = True
                        yield self._to_sse({
                            "type": "final",
                            "sessionId": request.sessionId,
                            "intent": intent,
                            "content": final_answer,
                            "references": references,
                        })
                    continue

                if not isinstance(chunk, dict):
                    continue

                chunk_type = chunk.get("type")

                if chunk_type == "chart" and isinstance(chunk.get("content"), dict):
                    intent = "CHART"
                    yield self._to_sse({
                        "type": "chart",
                        "sessionId": request.sessionId,
                        "intent": intent,
                        "content": chunk.get("content"),
                    })
                    continue

                refs = chunk.get("references", [])
                if refs:
                    references.extend(refs)
                    yield self._to_sse({
                        "type": "reference",
                        "sessionId": request.sessionId,
                        "intent": intent,
                        "references": refs,
                    })
                    continue

                card_intent = chunk.get("intent")
                card_content = chunk.get("content")
                if card_intent == "FOOD_CONFIRM" and isinstance(card_content, dict):
                    intent = "FOOD_CONFIRM"
                    yield self._to_sse({
                        "type": "food_order_card",
                        "sessionId": request.sessionId,
                        "intent": intent,
                        "content": card_content,
                    })
                    continue

                if chunk_type == "status":
                    payload = self._normalize_status_payload(chunk, request.sessionId, intent)
                    phase = payload.get("phase") or ""
                    if phase == last_phase and payload.get("message") == "正在处理中":
                        continue
                    last_phase = phase
                    yield self._to_sse(payload)
                    continue

            completed_message = "处理完成" if final_emitted else "处理完成，但没有生成文本答案"
            payload = self._build_status_payload(
                request.sessionId,
                intent,
                phase="completed",
                message=completed_message,
                stage="completed",
                progress=100,
            )
            yield self._to_sse(payload)

            done_payload = {
                "type": "done",
                "sessionId": request.sessionId,
                "intent": intent,
                "references": references,
                "hasFinal": final_emitted,
            }
            yield self._to_sse(done_payload)

        except Exception as e:
            error_payload = {
                "type": "error",
                "sessionId": request.sessionId,
                "intent": intent,
                "phase": "error",
                "message": str(e),
            }
            yield self._to_sse(error_payload)

    def _to_sse(self, payload: dict) -> str:
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    def _parse_stream_text(self, chunk: str, current_intent: str) -> tuple[str, str]:
        """解析最终文本片段，并识别特殊控制标记。"""
        if not chunk:
            return current_intent, ""

        text = chunk.strip()
        if text == "[INTENT:FOOD_CONFIRM]":
            return "FOOD_CONFIRM", ""

        return current_intent, chunk

    def _normalize_status_payload(self, chunk: dict, session_id: str | None, intent: str) -> dict:
        phase = chunk.get("phase") or self._map_stage_to_phase(chunk.get("stage"))
        message = chunk.get("message") or self._default_message_for_phase(phase)
        payload = self._build_status_payload(
            session_id,
            intent,
            phase=phase,
            message=message,
            stage=chunk.get("stage") or phase,
            progress=chunk.get("progress") or self._default_progress_for_phase(phase),
        )
        if chunk.get("node"):
            payload["node"] = chunk.get("node")
        if chunk.get("details"):
            payload["details"] = chunk.get("details")
        return payload

    def _build_status_payload(self, session_id: str | None, intent: str, phase: str, message: str, stage: str, progress: int | None = None) -> dict:
        payload = {
            "type": "status",
            "sessionId": session_id,
            "intent": intent,
            "phase": phase,
            "stage": stage,
            "message": message,
        }
        if progress is not None:
            payload["progress"] = progress
        return payload

    def _map_stage_to_phase(self, stage: str | None) -> str:
        stage_to_phase = {
            "started": "received",
            "routing": "planning",
            "running": "retrieving",
            "retrieving": "retrieving",
            "tool_calling": "tool_calling",
            "generating": "generating",
            "reflecting": "summarizing",
            "validating": "summarizing",
            "completed": "completed",
            "error": "error",
        }
        return stage_to_phase.get(stage or "", "running")

    def _default_message_for_phase(self, phase: str) -> str:
        messages = {
            "received": "已收到你的请求",
            "understanding": "正在理解你的需求",
            "planning": "正在规划处理步骤",
            "retrieving": "正在检索相关资料",
            "tool_calling": "正在调用系统能力",
            "generating": "正在生成回答内容",
            "summarizing": "正在整理最终结果",
            "completed": "处理完成",
            "error": "处理时出现问题",
            "running": "正在处理中",
        }
        return messages.get(phase, "正在处理中")

    def _default_progress_for_phase(self, phase: str) -> int | None:
        progress_map = {
            "received": 5,
            "understanding": 15,
            "planning": 25,
            "retrieving": 45,
            "tool_calling": 60,
            "generating": 80,
            "summarizing": 92,
            "completed": 100,
            "error": 100,
            "running": 50,
        }
        return progress_map.get(phase)

