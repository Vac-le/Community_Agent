"""召回评估脚本。

说明：
1. 直接复用当前项目已有 Chroma 向量库，不重建索引。
2. 对照评估 dense_only 与 hybrid_with_bm25 两种方案。
3. 以 chunk 级命中为主：只有 chunk 内容命中 expected_chunk_keywords 才算命中。
4. 将详细结果和汇总指标保存到 retrieval_eval/results/ 下。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.hybrid_retriever import BM25RetrieverService
from rag.rag_service import RagSummarizeService
from rag.vector_store import VectorStoreService

CASES_PATH = BASE_DIR / "cases.json"
RESULTS_DIR = BASE_DIR / "results"


def _doc_source_name(doc: Document) -> str:
    metadata = doc.metadata or {}
    source_file_name = metadata.get("source_file_name")
    if source_file_name:
        return str(source_file_name)
    source = metadata.get("source", "")
    return Path(str(source)).name if source else "unknown"


def _doc_preview(doc: Document, limit: int = 120) -> str:
    text = (doc.page_content or "").replace("\n", " ").strip()
    return text[:limit] + ("..." if len(text) > limit else "")


def _chunk_hit(doc: Document, expected_chunk_keywords: list[str]) -> bool:
    text = (doc.page_content or "")
    if not expected_chunk_keywords:
        return False
    return any(keyword in text for keyword in expected_chunk_keywords)


def _doc_hit(doc: Document, expected_sources: list[str], expected_chunk_keywords: list[str]) -> bool:
    """主口径：chunk 命中；source 仅作参考，不作为主命中条件。"""
    return _chunk_hit(doc, expected_chunk_keywords)


def _stage_metrics(docs: list[Document], expected_sources: list[str], expected_chunk_keywords: list[str], ks: list[int]) -> dict[str, Any]:
    hits = [_doc_hit(doc, expected_sources, expected_chunk_keywords) for doc in docs]
    metrics: dict[str, Any] = {
        "hit_at_k": any(hits),
        "hit_count": sum(1 for item in hits if item),
        "mrr": 0.0,
    }
    for rank, is_hit in enumerate(hits, start=1):
        if is_hit:
            metrics["mrr"] = round(1.0 / rank, 4)
            break
    for k in ks:
        metrics[f"recall_at_{k}"] = any(hits[:k])
    return metrics


def _serialize_docs(docs: list[Document], expected_sources: list[str], expected_chunk_keywords: list[str]) -> list[dict[str, Any]]:
    serialized = []
    for rank, doc in enumerate(docs, start=1):
        metadata = dict(doc.metadata or {})
        serialized.append(
            {
                "rank": rank,
                "source_file_name": _doc_source_name(doc),
                "chunk_id": metadata.get("chunk_id"),
                "parent_doc_id": metadata.get("parent_doc_id"),
                "recall_sources": metadata.get("recall_sources"),
                "fusion_score": metadata.get("fusion_score"),
                "bm25_score": metadata.get("bm25_score"),
                "rerank_score": metadata.get("rerank_score"),
                "chunk_hit": _chunk_hit(doc, expected_chunk_keywords),
                "source_match": _doc_source_name(doc) in expected_sources if expected_sources else False,
                "preview": _doc_preview(doc),
            }
        )
    return serialized


def _aggregate(case_results: list[dict[str, Any]], stage_names: list[str], ks: list[int]) -> dict[str, Any]:
    summary: dict[str, Any] = {"case_count": len(case_results), "systems": {}}
    for stage in stage_names:
        hit_cases = 0
        total_mrr = 0.0
        total_hits = 0
        recall_hits = {k: 0 for k in ks}
        for case in case_results:
            metrics = case["systems"][stage]["metrics"]
            hit_cases += 1 if metrics["hit_at_k"] else 0
            total_mrr += metrics["mrr"]
            total_hits += metrics["hit_count"]
            for k in ks:
                recall_hits[k] += 1 if metrics[f"recall_at_{k}"] else 0
        count = max(len(case_results), 1)
        stage_summary = {
            "hit_rate": round(hit_cases / count, 4),
            "avg_mrr": round(total_mrr / count, 4),
            "avg_hit_count": round(total_hits / count, 4),
        }
        for k in ks:
            stage_summary[f"recall_at_{k}"] = round(recall_hits[k] / count, 4)
        summary["systems"][stage] = stage_summary
    return summary


def main():
    if not CASES_PATH.exists():
        raise FileNotFoundError(f"测试用例文件不存在: {CASES_PATH}")

    with CASES_PATH.open("r", encoding="utf-8") as f:
        cases = json.load(f)

    vector_store = VectorStoreService()
    bm25 = BM25RetrieverService()
    rag_service = RagSummarizeService()
    hybrid = rag_service.hybrid_retriever
    reranker = rag_service.reranker
    final_k = rag_service.final_k
    ks = [1, 3, 5]

    case_results: list[dict[str, Any]] = []
    for case in cases:
        query = case["query"]
        expected_sources = case.get("expected_sources", [])
        expected_chunk_keywords = case.get("expected_chunk_keywords", [])

        dense_docs = vector_store.similarity_search(query, k=hybrid.dense_top_k)
        dense_rerank_docs = reranker.rerank(query, dense_docs, top_k=final_k)

        bm25_docs = bm25.search(query, k=hybrid.bm25_top_k)
        fused_docs = hybrid._rrf_fuse(dense_docs, bm25_docs)
        collapsed_docs = hybrid._collapse_docs(fused_docs, hybrid.fused_top_k)
        hybrid_rerank_docs = reranker.rerank(query, collapsed_docs, top_k=final_k)

        systems = {
            "dense_only_recall": dense_docs,
            "dense_only_rerank": dense_rerank_docs,
            "hybrid_with_bm25_recall": collapsed_docs,
            "hybrid_with_bm25_rerank": hybrid_rerank_docs,
        }

        case_result = {
            "name": case.get("name") or query,
            "query": query,
            "expected_sources": expected_sources,
            "expected_chunk_keywords": expected_chunk_keywords,
            "systems": {},
        }

        for system_name, docs in systems.items():
            case_result["systems"][system_name] = {
                "metrics": _stage_metrics(docs, expected_sources, expected_chunk_keywords, ks),
                "docs": _serialize_docs(docs, expected_sources, expected_chunk_keywords),
            }
        case_results.append(case_result)

    stage_names = [
        "dense_only_recall",
        "dense_only_rerank",
        "hybrid_with_bm25_recall",
        "hybrid_with_bm25_rerank",
    ]
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "vector_store_reused": True,
        "evaluation_mode": "chunk_level_hit",
        "cases_path": str(CASES_PATH),
        "summary": _aggregate(case_results, stage_names, ks),
        "cases": case_results,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = RESULTS_DIR / f"retrieval_eval_{timestamp}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"评估完成，结果已保存到: {output_path}")


if __name__ == "__main__":
    main()
