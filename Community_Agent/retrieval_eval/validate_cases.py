"""校验 retrieval_eval/cases.json 中的 expected_chunk_keywords 是否真实存在于知识库原文。"""

from __future__ import annotations

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
CASES_PATH = BASE_DIR / "cases.json"
RESULT_PATH = BASE_DIR / "results" / "cases_keyword_validation.json"


def load_knowledge_texts() -> dict[str, str]:
    texts: dict[str, str] = {}
    for path in DATA_DIR.glob("*.txt"):
        texts[path.name] = path.read_text(encoding="utf-8")
    return texts


def main() -> None:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    knowledge_texts = load_knowledge_texts()

    report: list[dict] = []
    missing_count = 0
    missing_in_expected_sources_count = 0
    for case in cases:
        expected_sources = case.get("expected_sources", [])
        keywords = case.get("expected_chunk_keywords", [])
        keyword_results = []
        for keyword in keywords:
            matched_sources = [name for name, text in knowledge_texts.items() if keyword in text]
            source_restricted_matches = [name for name in expected_sources if keyword in knowledge_texts.get(name, "")]
            found = bool(matched_sources)
            found_in_expected_sources = bool(source_restricted_matches)
            if not found:
                missing_count += 1
            if found and not found_in_expected_sources:
                missing_in_expected_sources_count += 1
            keyword_results.append(
                {
                    "keyword": keyword,
                    "found": found,
                    "matched_sources": matched_sources,
                    "found_in_expected_sources": found_in_expected_sources,
                    "source_restricted_matches": source_restricted_matches,
                }
            )
        report.append(
            {
                "name": case.get("name"),
                "query": case.get("query"),
                "expected_sources": expected_sources,
                "keyword_results": keyword_results,
            }
        )

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(
            {
                "case_count": len(cases),
                "missing_keyword_count": missing_count,
                "missing_in_expected_sources_count": missing_in_expected_sources_count,
                "cases": report,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"校验完成，结果已保存到: {RESULT_PATH}")


if __name__ == "__main__":
    main()
