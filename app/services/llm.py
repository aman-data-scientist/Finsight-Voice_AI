import logging

import requests
from openai import OpenAI

from app.config import get_settings
from app.rag.prompts import RAG_SYSTEM_PROMPT, format_context

logger = logging.getLogger(__name__)


def generate_grounded_answer(query: str, evidence: list[dict]) -> str:
    """Generate an answer grounded in retrieved evidence, or a safe fallback."""
    if not evidence:
        return "I could not find sufficient evidence in the indexed financial reports to answer this reliably."

    settings = get_settings()
    context = format_context(evidence)
    if not settings.api_key:
        return _extractive_fallback(evidence, "no LLM API key is configured")

    try:
        provider = settings.llm_provider.lower().strip()
        if provider in {"google", "gemini"}:
            return _generate_gemini_answer(query, context)
        if provider == "openai":
            return _generate_openai_answer(query, context)
        return _extractive_fallback(evidence, f"unsupported LLM provider '{settings.llm_provider}'")
    except Exception as exc:
        logger.exception("LLM API failed: %s", exc)
        return _extractive_fallback(evidence, f"the LLM API call failed: {exc}")


def _generate_openai_answer(query: str, context: str) -> str:
    settings = get_settings()
    client = OpenAI(api_key=settings.api_key)
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question: {query}\n\nEvidence:\n{context}\n\nAnswer with a short Sources section.",
            },
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content or ""


def _generate_gemini_answer(query: str, context: str) -> str:
    settings = get_settings()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.llm_model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": RAG_SYSTEM_PROMPT}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"Question: {query}\n\nEvidence:\n{context}\n\nAnswer with a short Sources section."
                    }
                ],
            }
        ],
        "generationConfig": {"temperature": 0.1},
    }
    response = requests.post(url, params={"key": settings.api_key}, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _extractive_fallback(evidence: list[dict], reason: str) -> str:
    first = evidence[0]
    metadata = first["metadata"]
    snippet = first["text"][:700].strip()
    source = (
        f"{metadata.get('company')} {metadata.get('year')} {metadata.get('filing_type')} - "
        f"{metadata.get('section')} - page {metadata.get('page')}"
    )
    return (
        f"I found relevant evidence, but {reason}, so here is the most relevant excerpt.\n\n"
        f"Evidence excerpt:\n{snippet}\n\nSources:\n1. {source}"
    )
