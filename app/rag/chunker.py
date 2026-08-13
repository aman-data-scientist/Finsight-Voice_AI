import re
from dataclasses import dataclass
from typing import Any


@dataclass
class Chunk:
    text: str
    metadata: dict[str, Any]


SECTION_PATTERNS = [
    (r"item\s+1a\.?\s+risk factors", "Risk Factors"),
    (r"item\s+7\.?\s+management", "MD&A"),
    (r"consolidated statements of operations", "Consolidated Statements of Operations"),
    (r"consolidated statements of cash flows", "Consolidated Statements of Cash Flows"),
]


def detect_section(text: str) -> str:
    lower = text.lower()
    for pattern, section in SECTION_PATTERNS:
        if re.search(pattern, lower):
            return section
    return "General"


def chunk_pages(
    pages: list[dict[str, int | str]],
    base_metadata: dict[str, Any],
    chunk_size: int = 900,
    overlap: int = 120,
) -> list[Chunk]:
    """Create readable overlapping chunks with page and section metadata."""
    chunks: list[Chunk] = []
    for page in pages:
        text = str(page["text"])
        page_number = int(page["page"])
        section = detect_section(text)
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if len(chunk_text) >= 80:
                metadata = {
                    **base_metadata,
                    "page": page_number,
                    "section": section,
                }
                chunks.append(Chunk(text=chunk_text, metadata=metadata))
            if end == len(text):
                break
            start = max(0, end - overlap)
    return chunks
