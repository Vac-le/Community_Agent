"""Agent HTTP 接口层。

职责：
1. 对外暴露流式聊天接口。
2. 接收 Java 侧透传的 token。
3. 将服务层返回的内容以 SSE 形式输出。
"""

from fastapi import APIRouter, Header
from starlette.responses import StreamingResponse

from agent.service.agent_service import AgentService
from models.dto import AgentChatRequest

router = APIRouter(prefix="/agent", tags=["agent"])
service = AgentService()

# uvicorn main:app --reload --host 0.0.0.0 --port 9000
@router.post("/chat/stream")
def chat_stream(request: AgentChatRequest, token: str | None = Header(default=None)):
    """Agent 流式聊天接口。"""
    request.token = token
    return StreamingResponse(
        service.chat_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
