"""模型工厂模块。

职责：
1. 根据配置创建聊天模型。
2. 根据配置创建向量嵌入模型。
3. 将模型实例集中管理，供 Agent 与 RAG 复用。
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Optional

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from utils.config_handler import agent_config


class BaseModelFactory(ABC):
    """模型工厂抽象基类。"""

    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        """返回具体模型实例。"""


class ChatModelFactory(BaseModelFactory):
    """聊天模型工厂。"""

    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        provider = str(agent_config.get("llm_provider", "tongyi") or "tongyi").strip().lower()
        model_name = agent_config["chat_model_name"]

        if provider == "openai_compatible":
            api_key = (
                os.getenv("MIMO_API_KEY")
                or os.getenv("OPENAI_API_KEY_MIMO")
            )
            if not api_key:
                raise RuntimeError("缺少环境变量 MIMO_API_KEY 或 OPENAI_API_KEY_MIMO，无法初始化 mimo 聊天模型")
            base_url = os.getenv("OPENAI_BASE_URL_MIMO") or os.getenv("OPENAI_BASE_URL") or "https://api.xiaomimimo.com/v1"
            return ChatOpenAI(
                model=model_name,
                temperature=0.0,
                api_key=api_key,
                base_url=base_url,
            )

        return ChatTongyi(model=model_name, temperature=0.0)


class EmbeddingsFactory(BaseModelFactory):
    """Embedding 模型工厂。"""

    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model=agent_config["embedding_model_name"])


# 全局复用的模型实例。
chat_model = ChatModelFactory().generator()
embedding_model = EmbeddingsFactory().generator()
