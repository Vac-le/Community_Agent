"""数据传输对象定义模块。

职责：
1. 定义前后端之间的请求/响应结构。
2. 为 Agent、订餐相关能力提供统一的 Pydantic 模型。
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ChatHistoryMessage(BaseModel):
    """单条历史消息。"""

    role: Optional[str] = None
    content: Optional[str] = None
    intent: Optional[str] = None
    timestamp: Optional[int] = None


class AgentChatRequest(BaseModel):
    """Agent 聊天请求体。"""

    userId: int
    communityId: int
    sessionId: str
    currentMessage: str
    chatHistory: List[ChatHistoryMessage] = Field(default_factory=list)
    token: Optional[str] = None


class AgentChatResponse(BaseModel):
    """Agent 非流式响应结构预留模型。"""

    sessionId: str
    answer: str
    intent: str
    references: List[str] = []


class FoodRecommendRequest(BaseModel):
    """订餐推荐请求。"""

    maxCalories: Optional[int] = None
    preference: Optional[str] = None


class CreateFoodOrderRequest(BaseModel):
    """创建餐饮订单请求。"""

    sessionId: str
    deliveryAddress: str
    deliveryPhone: str
    remark: Optional[str] = None
    orderItems: List[dict[str, Any]]


class PrepareFoodOrderDraftRequest(BaseModel):
    """创建待确认订单草稿请求。"""

    sessionId: str
    deliveryAddress: str
    deliveryPhone: str
    remark: Optional[str] = None
    amount: int
    orderItems: List[dict[str, Any]]
    recommendSummary: str
