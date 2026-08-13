import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.agents.tools import calculate, parse_receipt_fields
from app.rag.retriever import retrieve_documents


def evaluate_calculator() -> None:
    cases = json.loads((PROJECT_ROOT / "data/evaluation/calculation_questions.json").read_text())
    passed = 0
    for case in cases:
        actual = calculate(case["expression"])
        if abs(actual - case["expected_approx"]) < 0.1:
            passed += 1
    print(f"Calculator: {passed}/{len(cases)} close matches")


def evaluate_receipt_parser() -> None:
    cases = json.loads((PROJECT_ROOT / "data/evaluation/receipt_cases.json").read_text())
    passed = 0
    for case in cases:
        parsed = parse_receipt_fields(case["ocr_text"])
        if parsed["vendor"] == case["expected_vendor"] and parsed["total"] == case["expected_total"]:
            passed += 1
    print(f"Receipt parser: {passed}/{len(cases)} field matches")


def evaluate_rag_retrieval() -> None:
    cases = json.loads((PROJECT_ROOT / "data/evaluation/rag_questions.json").read_text())
    passed = 0
    for case in cases:
        results = retrieve_documents(case["question"], top_k=4)
        if any(r["metadata"].get("company") == case["expected_company"] for r in results):
            passed += 1
    print(f"RAG retrieval: {passed}/{len(cases)} company matches")


if __name__ == "__main__":
    evaluate_calculator()
    evaluate_receipt_parser()
    try:
        evaluate_rag_retrieval()
    except FileNotFoundError as exc:
        print(f"RAG retrieval skipped: {exc}")
