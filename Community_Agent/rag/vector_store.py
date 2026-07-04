"""RAG 向量库服务模块。

职责：
1. 初始化 Milvus Lite 向量库。
2. 负责知识文档切分、去重、入库。
3. 提供检索器与相似度搜索能力。
4. 为混合召回补齐稳定的 chunk 元数据。
"""

from __future__ import annotations

import hashlib
import os
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymilvus import DataType, MilvusClient

from models.factory import embedding_model
from utils.config_handler import rag_config, vector_store_config
from utils.file_handler import get_file_md5_hex, listdir_with_allowed_type, pdf_loader, txt_loader
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


class _SimpleRetriever:
    def __init__(self, service: "VectorStoreService", k: int):
        self.service = service
        self.k = k

    def invoke(self, query: str) -> list[Document]:
        return self.service.similarity_search(query, k=self.k)


class VectorStoreService:
    """向量库服务。"""

    def __init__(self):
        store_config = vector_store_config.get("store", {}) or {}
        chunking_config = vector_store_config.get("chunking", {}) or {}

        persist_directory = get_abs_path(store_config["persist_directory"])
        os.makedirs(persist_directory, exist_ok=True)
        lite_db_path = os.path.join(persist_directory, "milvus_lite.db")

        self.store_config = store_config
        self.chunking_config = chunking_config
        self.collection_name = store_config["collection_name"]
        self.vector_dim = self._detect_vector_dim()
        self.client = MilvusClient(uri=lite_db_path)
        self._ensure_collection()
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chunking_config["chunk_size"],
            chunk_overlap=chunking_config["chunk_overlap"],
            separators=chunking_config["separators"],
            length_function=len,
        )

    def _detect_vector_dim(self) -> int:
        sample = embedding_model.embed_query("test")
        if not sample:
            raise RuntimeError("embedding_model 返回空向量，无法初始化 Milvus 集合")
        return len(sample)

    def _ensure_collection(self):
        existing = set(self.client.list_collections())
        if self.collection_name in existing:
            return

        schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=True)
        schema.add_field(field_name="pk", datatype=DataType.VARCHAR, is_primary=True, max_length=128)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self.vector_dim)

        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="AUTOINDEX",
            metric_type="COSINE",
            index_name="vector_index",
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params,
        )

    def get_retriever(self, k: int | None = None):
        """返回简单 retriever 适配器。"""
        top_k = k or rag_config.get("retrieval", {}).get("top_k") or self.store_config["k"]
        return _SimpleRetriever(self, top_k)

    def similarity_search(self, query: str, k: int | None = None) -> list[Document]:
        """执行相似度检索，返回候选文档。"""
        top_k = k or rag_config.get("retrieval", {}).get("top_k") or self.store_config["k"]
        query_vector = embedding_model.embed_query(query)
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            anns_field="vector",
            search_params={"metric_type": "COSINE"},
            limit=top_k,
            output_fields=["text", "source", "parent_doc_id", "chunk_index", "chunk_id", "source_file_name"],
        )

        docs: list[Document] = []
        for item in (results[0] if results else []):
            entity = item.get("entity") or {}
            text = entity.get("text") or ""
            metadata = {
                "source": entity.get("source"),
                "parent_doc_id": entity.get("parent_doc_id"),
                "chunk_index": entity.get("chunk_index"),
                "chunk_id": entity.get("chunk_id"),
                "source_file_name": entity.get("source_file_name"),
                "dense_score": item.get("distance"),
                "recall_source": "dense",
            }
            docs.append(Document(page_content=text, metadata=metadata))
        return docs

    def _normalize_source(self, file_path: str) -> str:
        return os.path.abspath(file_path).replace("\\", "/")

    def _build_parent_doc_id(self, file_path: str) -> str:
        source = self._normalize_source(file_path)
        return hashlib.md5(source.encode("utf-8")).hexdigest()

    def _enrich_chunk_metadata(self, docs: list[Document], file_path: str) -> list[Document]:
        """为 chunk 增加稳定标识，支持多路召回去重与父文档折叠。"""
        enriched_docs: list[Document] = []
        source = self._normalize_source(file_path)
        parent_doc_id = self._build_parent_doc_id(file_path)

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

    def _build_insert_rows(self, docs: list[Document]) -> list[dict[str, Any]]:
        texts = [doc.page_content for doc in docs]
        vectors = embedding_model.embed_documents(texts)
        rows: list[dict[str, Any]] = []
        for doc, vector in zip(docs, vectors):
            metadata = dict(doc.metadata or {})
            rows.append({
                "pk": metadata["chunk_id"],
                "text": doc.page_content,
                "vector": vector,
                "source": metadata.get("source", ""),
                "parent_doc_id": metadata.get("parent_doc_id", ""),
                "chunk_index": metadata.get("chunk_index", 0),
                "chunk_id": metadata.get("chunk_id", ""),
                "source_file_name": metadata.get("source_file_name", ""),
            })
        return rows

    def load_document(self):
        """加载 data 目录知识文件，并切分后写入向量库。"""

        def check_md5_hex(md5_for_check: str):
            md5_store_path = get_abs_path(self.store_config["md5_hex_store"])
            if not os.path.exists(md5_store_path):
                open(md5_store_path, "w", encoding="utf-8").close()
                return False
            with open(md5_store_path, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True
                return False

        def save_md5_hex(md5_for_check: str):
            with open(get_abs_path(self.store_config["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(read_path: str):
            if read_path.endswith(".txt"):
                return txt_loader(read_path)
            if read_path.endswith(".pdf"):
                return pdf_loader(read_path)
            return []

        allowed_files_path: list[str] = listdir_with_allowed_type(
            get_abs_path(self.store_config["data_path"]),
            tuple(self.store_config["allowed_knowledge_file_type"]),
        )

        for file_path in allowed_files_path:
            md5_hex = get_file_md5_hex(file_path)
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{file_path}已经存在")
                continue
            try:
                documents: list[Document] = get_file_documents(file_path)

                if not documents:
                    logger.warning(f"[加载知识库]{file_path}内无有效内容")
                    continue

                spliter_document: list[Document] = self.spliter.split_documents(documents)
                spliter_document = self._enrich_chunk_metadata(spliter_document, file_path)

                if not spliter_document:
                    logger.warning(f"[加载知识库]{file_path}分片后没有有效内容")
                    continue

                rows = self._build_insert_rows(spliter_document)
                self.client.upsert(collection_name=self.collection_name, data=rows)
                save_md5_hex(md5_hex)
                logger.info(f"[加载知识库]{file_path}内容加载成功")
            except Exception as e:
                logger.error(f"[加载知识库]{file_path}加载失败：{str(e)}", exc_info=True)
                continue


if __name__ == "__main__":
    vs = VectorStoreService()
    vs.load_document()
    retriever = vs.get_retriever()
    res = retriever.invoke("物业管理条例")
    for doc in res:
        print(doc.page_content)
        print("---------------------------------------------")
