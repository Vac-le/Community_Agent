"""RAG 总结服务模块。

职责：
1. 先从向量库粗召回候选文档。
2. 对候选文档做 rerank。
3. 将最终证据拼成上下文，交给大模型生成总结回答。
"""

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from models.factory import chat_model
from rag.hybrid_retriever import HybridRetrieverService
from rag.reranker import RerankerService
from rag.vector_store import VectorStoreService
from utils.config_handler import rag_config
from utils.logger_handler import logger
from utils.prompt_loader import load_rag_prompt


def print_prompt(prompt):
    """调试时打印最终 prompt 内容。"""
    print("=" * 20)
    print(prompt.to_string())
    print("=" * 20)
    return prompt


class RagSummarizeService(object):
    """RAG 总结服务。"""

    def __init__(self):
        self.vector_store = None
        self.hybrid_retriever = None
        self.reranker = None
        self.prompt_text = load_rag_prompt()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()
        self.top_k = rag_config.get("retrieval", {}).get("top_k", 10)
        self.final_k = rag_config.get("retrieval", {}).get("final_k", 3)
        self.max_doc_chars = rag_config.get("context", {}).get("max_doc_chars", 500)

    def _ensure_initialized(self):
        if self.vector_store is None:
            self.vector_store = VectorStoreService()
        if self.hybrid_retriever is None:
            self.hybrid_retriever = HybridRetrieverService(self.vector_store)
        if self.reranker is None:
            self.reranker = RerankerService()

    def _init_chain(self):
        """初始化 RAG 总结链。"""
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain

    def retrieve_candidates(self, query: str) -> list[Document]:
        """先做 Dense + BM25 混合粗召回。"""
        self._ensure_initialized()
        docs = self.hybrid_retriever.retrieve(query)
        logger.info(f"[RAG] query={query} 混合粗召回文档数={len(docs)}")
        return docs

    def rerank_docs(self, query: str, docs: list[Document]) -> list[Document]:
        """对粗召回结果做二次重排。"""
        final_docs = self.reranker.rerank(query, docs, top_k=self.final_k)
        logger.info(f"[RAG] query={query} rerank后文档数={len(final_docs)}")
        return final_docs

    def build_context(self, docs: list[Document], max_doc_chars: int | None = None) -> str:
        """将最终证据文档拼接成模型可用上下文。"""
        doc_char_limit = max_doc_chars or self.max_doc_chars
        context_parts: list[str] = []
        for idx, doc in enumerate(docs, start=1):
            content = (doc.page_content or "")[:doc_char_limit]
            context_parts.append(
                f"[参考资料{idx}]: 参考资料:{content} | 参考元数据 : {doc.metadata}"
            )
        return "\n".join(context_parts)

    def retriever_docs(self, query: str) -> list[Document]:
        """执行完整检索流程并返回最终文档。"""
        candidate_docs = self.retrieve_candidates(query)
        return self.rerank_docs(query, candidate_docs)

    def rag_summarize(self, query: str, max_doc_chars: int | None = None) -> str:
        """执行 RAG 总结，返回面向用户的文本回答。"""
        context_docs = self.retriever_docs(query)
        context = self.build_context(context_docs, max_doc_chars=max_doc_chars)
        return self.chain.invoke(
            {
                "input": query,
                "context": context,
            }
        )


if __name__ == "__main__":
    rag = RagSummarizeService()
    print(rag.rag_summarize("社区现在有什么活动"))
