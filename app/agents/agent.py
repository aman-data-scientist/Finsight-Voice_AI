import logging
import re
from dataclasses import dataclass, field
from typing import Any

from app.agents.tools import calculate, explain_finance_concept, search_financial_documents, try_extract_revenue_growth

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    answer: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)


def run_agent(query: str) -> AgentResponse:
    """Single simple router: choose RAG, calculator, or concept explanation."""
    query = query.strip()
    if not query:
        return AgentResponse(answer="Please enter a financial question.", trace=["Empty query"])

    lower = query.lower()
    trace: list[str] = ["Agent received query"]

    if _looks_like_concept(lower):
        topic = _extract_concept(query)
        trace.extend(["Finance concept detected", "Tool: explain_finance_concept"])
        return AgentResponse(answer=explain_finance_concept(topic), trace=trace)

    if _looks_like_financial_report_question(lower):
        trace.extend(["Company financial question detected", "Tool: search_financial_documents"])
        result = search_financial_documents(query, company=_extract_company(query))
        sources = result["sources"]
        trace.append(f"Retrieved: {len(sources)} relevant chunks")
        if _needs_calculation(lower):
            trace.append("Tool: calculate")
            years = _extract_years(lower)
            if len(years) >= 2:
                growth = try_extract_revenue_growth(sources, min(years), max(years))
                if growth:
                    result["answer"] += (
                        f"\n\nCalculator check: revenue growth from {min(years)} to {max(years)} is "
                        f"{growth['growth_percent']:.2f}% based on extracted values "
                        f"{growth['start_value']:,.0f} and {growth['end_value']:,.0f}."
                    )
                else:
                    trace.append("Calculator skipped: numeric values were not reliably extractable")
        trace.append("Final answer generated")
        return AgentResponse(answer=result["answer"], sources=sources, trace=trace)

    if _is_math_expression(query):
        trace.append("Tool: calculate")
        try:
            value = calculate(query)
            return AgentResponse(answer=str(value), trace=trace)
        except ValueError:
            return AgentResponse(answer="I could not calculate that expression safely.", trace=trace)

    trace.append("General fallback")
    return AgentResponse(
        answer="Ask a question about the indexed financial reports, a finance concept, or a calculation.",
        trace=trace,
    )


def _extract_company(query: str) -> str | None:
    for company in ("Apple", "Microsoft", "Tesla", "Google"):
        if company.lower() in query.lower():
            return company
    return None


def _looks_like_concept(query: str) -> bool:
    return query.startswith("what is ") and any(term in query for term in ["cash flow", "ebitda", "working capital", "margin"])


def _extract_concept(query: str) -> str:
    topic = re.sub(r"(?i)^what is |[?.]", "", query).strip()
    return topic


def _looks_like_financial_report_question(query: str) -> bool:
    companies = ["apple", "microsoft", "tesla", "google", "alphabet"]
    finance_terms = ["revenue", "cash flow", "income", "growth", "risk", "margin", "10-k", "compare"]
    return any(company in query for company in companies) and any(term in query for term in finance_terms)


def _needs_calculation(query: str) -> bool:
    return any(term in query for term in ["growth", "percentage", "percent", "change", "compare"])


def _is_math_expression(query: str) -> bool:
    return bool(re.fullmatch(r"[\d\s+\-*/().]+", query))


def _extract_years(query: str) -> list[int]:
    return [int(match) for match in re.findall(r"\b(20\d{2})\b", query)]
