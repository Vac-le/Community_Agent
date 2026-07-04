"""BM25 与混合召回模块。

职责：
1. 读取与向量库一致的数据源并切分 chunk。
2. 使用 rank_bm25 对 chunk 建立关键词检索索引。
3. 执行 Dense + BM25 多路召回、去重、父文档折叠和 RRF 融合。
"""

from __future__ import annotations

import hashlib
import os
import re
from collections import Counter

import jieba
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi

from utils.config_handler import rag_config, vector_store_config
from utils.file_handler import listdir_with_allowed_type, pdf_loader, txt_loader
from utils.logger_handler import logger
from utils.path_tool import get_abs_path

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]+")
_STOPWORDS = {
    "我们", "你们", "请问", "一下", "这个", "那个", "可以", "是否", "怎么", "如何", "什么", "哪些", "有关", "根据", "关于",
    "多少", "是不是", "是否可以", "一下子", "里面", "现在", "目前", "一下", "规定", "要求"
}


class KeywordExtractor:
    """基于 jieba 的中文关键词提取。"""

    def _tokenize(self, text: str) -> list[str]:
        raw_tokens = list(jieba.cut(text or "", cut_all=False))
        normalized_tokens: list[str] = []
        for token in raw_tokens:
            token = token.strip().lower()
            if not token:
                continue
            if _TOKEN_PATTERN.fullmatch(token) is None:
                continue
            if token in _STOPWORDS:
                continue
            if len(token) == 1 and not token.isdigit() and not token.isalpha():
                continue
            normalized_tokens.append(token)
        return normalized_tokens

    def extract(self, query: str, max_terms: int = 8) -> list[str]:
        tokens = self._tokenize(query)
        if not tokens:
            return [query.strip()] if query and query.strip() else []

        counts = Counter(tokens)
        ranked = sorted(counts.items(), key=lambda item: (-item[1], -len(item[0]), item[0]))
        return [term for term, _ in ranked[:max_terms]]


class BM25RetrieverService:
    """基于 rank_bm25 的 BM25 检索器。"""

    def __init__(self):
        chunking_config = vector_store_config.get("chunking", {}) or {}
        self.store_config = vector_store_config.get("store", {}) or {}
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunking_config["chunk_size"],
            chunk_overlap=chunking_config["chunk_overlap"],
            separators=chunking_config["separators"],
            length_function=len,
        )
        self.keyword_extractor = KeywordExtractor()
        bm25_config = rag_config.get("bm25", {}) or {}
        self.k1 = float(bm25_config.get("k1", 1.5))
        self.b = float(bm25_config.get("b", 0.75))
        self.documents = self._load_documents()
        self.tokenized_docs = [self._tokenize(doc.page_content or "") for doc in self.documents]
        self.bm25 = BM25Okapi(self.tokenized_docs, k1=self.k1, b=self.b) if self.tokenized_docs else None
        logger.info(f"[RAG][BM25] rank_bm25 索引文档块数量={len(self.documents)}")

    def _normalize_source(self, file_path: str) -> str:
        return os.path.abspath(file_path).replace("\\", "/")

    def _build_parent_doc_id(self, file_path: str) -> str:
        source = self._normalize_source(file_path)
        return hashlib.md5(source.encode("utf-8")).hexdigest()

    def _load_raw_documents(self, file_path: str) -> list[Document]:
        if file_path.endswith(".txt"):
            return txt_loader(file_path)
        if file_path.endswith(".pdf"):
            return pdf_loader(file_path)
        return []

    def _enrich_chunk_metadata(self, docs: list[Document], file_path: str) -> list[Document]:
        source = self._normalize_source(file_path)
        parent_doc_id = self._build_parent_doc_id(file_path)
        enriched_docs: list[Document] = []
        for chunk_index, doc in enumerate(docs):
            content = (doc.page_content or "").strip()
            if not content:
                continue
            metadata = dict(doc.metadata or {})
            metadata.setdefault("source", source)
            metadata["parent_doc_id"] = parent_doc_id
            metadata["chunk_index"] = chunk_index
            metadata["chunk_id"] = f"{parent_doc_id}#{chunk_index}"
            metadata["source_file_name"] = os.path.basename(file_path)
            enriched_docs.append(Document(page_content=content, metadata=metadata))
        return enriched_docs

    def _load_documents(self) -> list[Document]:
        docs: list[Document] = []
        allowed_files_path = listdir_with_allowed_type(
            get_abs_path(self.store_config["data_path"]),
            tuple(self.store_config["allowed_knowledge_file_type"]),
        )
        for file_path in allowed_files_path:
            raw_docs = self._load_raw_documents(file_path)
            if not raw_docs:
                continue
            chunked = self.splitter.split_documents(raw_docs)
            docs.extend(self._enrich_chunk_metadata(chunked, file_path))
        return docs

    def _tokenize(self, text: str) -> list[str]:
        return self.keyword_extractor._tokenize(text)

    def search(self, query: str, k: int = 10) -> list[Document]:
        query_terms = self.keyword_extractor.extract(query)
        if not query_terms or self.bm25 is None:
            return []

        scores = self.bm25.get_scores(query_terms)
        scored_docs: list[tuple[float, int]] = [
            (float(score), idx) for idx, score in enumerate(scores) if float(score) > 0
        ]
        scored_docs.sort(key=lambda item: item[0], reverse=True)

        docs: list[Document] = []
        for score, idx in scored_docs[:k]:
            doc = self.documents[idx]
            metadata = dict(doc.metadata or {})
            metadata["bm25_score"] = score
            metadata["bm25_terms"] = query_terms
            docs.append(Document(page_content=doc.page_content, metadata=metadata))

        logger.info(f"[RAG][BM25] query={query} terms={query_terms} recall_docs={len(docs)}")
        return docs


class HybridRetrieverService:
    """混合召回：Dense + BM25，支持去重与 chunk 级折叠。"""

    def __init__(self, vector_store_service):
        retrieval_config = rag_config.get("retrieval", {}) or {}
        self.vector_store = vector_store_service
        self.bm25 = BM25RetrieverService()
        self.dense_top_k = int(retrieval_config.get("dense_top_k", retrieval_config.get("top_k", 10)))
        self.bm25_top_k = int(retrieval_config.get("bm25_top_k", retrieval_config.get("top_k", 10)))
        self.fused_top_k = int(retrieval_config.get("fused_top_k", max(self.dense_top_k, self.bm25_top_k)))
        self.collapse_by_parent = bool(retrieval_config.get("collapse_by_parent", True))
        self.rrf_k = int(retrieval_config.get("rrf_k", 60))

    def _doc_key(self, doc: Document) -> str:
        metadata = doc.metadata or {}
        return str(metadata.get("chunk_id") or metadata.get("source") or (doc.page_content or "")[:120])

    def _parent_key(self, doc: Document) -> str:
        metadata = doc.metadata or {}
        return str(metadata.get("parent_doc_id") or metadata.get("chunk_id") or self._doc_key(doc))

    def _merge_doc(self, base: Document, extra: Document, score: float, source_name: str) -> Document:
        metadata = dict(base.metadata or {})
        recall_sources = set(metadata.get("recall_sources", []))
        if not recall_sources:
            original_source = metadata.get("recall_source")
            if original_source:
                recall_sources.add(str(original_source))
        recall_sources.add(source_name)
        metadata["recall_sources"] = sorted(recall_sources)
        metadata[f"{source_name}_rrf_score"] = score
        return Document(page_content=base.page_content, metadata=metadata)

    def _rrf_fuse(self, dense_docs: list[Document], bm25_docs: list[Document]) -> list[Document]:
        doc_map: dict[str, Document] = {}
        score_map: dict[str, float] = {}

        for source_name, docs in (("dense", dense_docs), ("bm25", bm25_docs)):
            for rank, doc in enumerate(docs, start=1):
                key = self._doc_key(doc)
                rrf_score = 1.0 / (self.rrf_k + rank)
                if key not in doc_map:
                    metadata = dict(doc.metadata or {})
                    metadata["recall_sources"] = [source_name]
                    metadata[f"{source_name}_rrf_score"] = rrf_score
                    doc_map[key] = Document(page_content=doc.page_content, metadata=metadata)
                    score_map[key] = 0.0
                else:
                    doc_map[key] = self._merge_doc(doc_map[key], doc, rrf_score, source_name)
                score_map[key] += rrf_score

        ranked = sorted(score_map.items(), key=lambda item: item[1], reverse=True)
        fused_docs: list[Document] = []
        for key, score in ranked:
            doc = doc_map[key]
            metadata = dict(doc.metadata or {})
            metadata["fusion_score"] = score
            fused_docs.append(Document(page_content=doc.page_content, metadata=metadata))
        return fused_docs

    def _collapse_docs(self, docs: list[Document], limit: int) -> list[Document]:
        if not self.collapse_by_parent:
            return docs[:limit]

        collapsed: list[Document] = []
        seen_parents: set[str] = set()
        for doc in docs:
            parent_key = self._parent_key(doc)
            if parent_key in seen_parents:
                continue
            seen_parents.add(parent_key)
            collapsed.append(doc)
            if len(collapsed) >= limit:
                break
        return collapsed

    def retrieve(self, query: str) -> list[Document]:
        dense_docs = self.vector_store.similarity_search(query, k=self.dense_top_k)
        bm25_docs = self.bm25.search(query, k=self.bm25_top_k)
        fused_docs = self._rrf_fuse(dense_docs, bm25_docs)
        collapsed_docs = self._collapse_docs(fused_docs, self.fused_top_k)
        logger.info(f"[RAG][Hybrid] dense={len(dense_docs)} bm25={len(bm25_docs)} fused={len(fused_docs)} final={len(collapsed_docs)}")
        return collapsed_docs
