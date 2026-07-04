"""RAG 重排模块。

职责：
1. 对向量检索返回的候选文档进行二次排序。
2. 优先使用通义 DashScope rerank 模型。
3. 模型不可用或调用失败时，降级到本地关键词排序。
"""

from http import HTTPStatus

import dashscope
from langchain_core.documents import Document

from utils.config_handler import rag_config
from utils.logger_handler import logger


class RerankerService:
    """文档重排服务。"""

    def __init__(self):
        rerank_config = rag_config.get("rerank", {}) or {}
        self.enabled = rerank_config.get("enabled", True)
        self.provider = rerank_config.get("provider", "simple")
        self.model_name = rerank_config.get("model_name", "gte-rerank-v2")
        self.fallback_enabled = rerank_config.get("fallback_enabled", True)

    def rerank(self, query: str, docs: list[Document], top_k: int) -> list[Document]:
        """对候选文档进行重排。"""
        if not docs:
            return []

        if not self.enabled:
            logger.info("[RAG][Rerank] rerank 未启用，直接返回向量召回结果")
            return docs[:top_k]

        if self.provider == "dashscope":
            return self._dashscope_rerank(query, docs, top_k)

        logger.info(f"[RAG][Rerank] 使用本地关键词重排 provider={self.provider}")
        return self._keyword_rerank(query, docs, top_k)

    def _dashscope_rerank(self, query: str, docs: list[Document], top_k: int) -> list[Document]:
        """使用通义 DashScope TextReRank 对候选文档重排。"""
        documents = [doc.page_content or "" for doc in docs]
        try:
            response = dashscope.TextReRank.call(
                model=self.model_name,
                query=query,
                documents=documents,
                top_n=top_k,
                return_documents=False,
            )

            status_code = getattr(response, "status_code", None)
            if status_code != HTTPStatus.OK:
                message = getattr(response, "message", "")
                code = getattr(response, "code", "")
                raise RuntimeError(f"DashScope rerank failed status={status_code} code={code} message={message}")

            results = self._extract_dashscope_results(response)
            if not results:
                raise RuntimeError("DashScope rerank 返回结果为空")

            ranked_docs: list[Document] = []
            for item in results:
                index = item.get("index")
                score = item.get("relevance_score")
                if not isinstance(index, int) or index < 0 or index >= len(docs):
                    logger.warning(f"[RAG][Rerank] 忽略非法 rerank index={index}")
                    continue

                doc = docs[index]
                metadata = dict(doc.metadata or {})
                metadata["rerank_score"] = score
                metadata["rerank_model"] = self.model_name
                ranked_docs.append(Document(page_content=doc.page_content, metadata=metadata))

            if not ranked_docs:
                raise RuntimeError("DashScope rerank 未产生有效文档")

            logger.info(
                f"[RAG][Rerank] 通义重排成功 model={self.model_name} input_docs={len(docs)} output_docs={len(ranked_docs)}"
            )
            return ranked_docs[:top_k]
        except Exception as e:
            logger.warning(f"[RAG][Rerank] 通义重排失败，将尝试降级: {str(e)}")
            if not self.fallback_enabled:
                raise
            return self._keyword_rerank(query, docs, top_k)

    def _extract_dashscope_results(self, response) -> list[dict]:
        """兼容 DashScope SDK 不同响应对象的结果结构。"""
        output = getattr(response, "output", None)
        if isinstance(output, dict):
            results = output.get("results", [])
        else:
            results = getattr(output, "results", []) if output is not None else []

        normalized_results = []
        for item in results or []:
            if isinstance(item, dict):
                normalized_results.append(item)
            else:
                normalized_results.append({
                    "index": getattr(item, "index", None),
                    "relevance_score": getattr(item, "relevance_score", None),
                })
        return normalized_results

    def _keyword_rerank(self, query: str, docs: list[Document], top_k: int) -> list[Document]:
        """按 query 命中情况执行本地兜底排序。"""
        normalized_terms = [term.strip().lower() for term in query.split() if term.strip()]

        def score(doc: Document) -> tuple[int, int]:
            text = (doc.page_content or "").lower()
            hit_count = sum(1 for term in normalized_terms if term and term in text)
            text_length = len(text)
            return hit_count, -text_length

        sorted_docs = sorted(docs, key=score, reverse=True)
        logger.info(f"[RAG][Rerank] 使用本地关键词降级重排 input_docs={len(docs)} output_docs={min(top_k, len(sorted_docs))}")
        return sorted_docs[:top_k]
