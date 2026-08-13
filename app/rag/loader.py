import logging
import re
from html.parser import HTMLParser
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "ix:header"}:
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "ix:header"}:
            self._skip = False
        if tag.lower() in {"p", "div", "tr", "br", "table"}:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            cleaned = data.strip()
            if cleaned:
                self._parts.append(cleaned)

    def text(self) -> str:
        return clean_text(" ".join(self._parts))


def extract_pdf_pages(pdf_path: Path) -> list[dict[str, int | str]]:
    """Extract page text from a PDF while preserving page numbers."""
    import fitz

    pages: list[dict[str, int | str]] = []
    with fitz.open(pdf_path) as doc:
        for index, page in enumerate(doc, start=1):
            text = clean_text(page.get_text("text"))
            if text:
                pages.append({"page": index, "text": text})
    return pages


def extract_html_pages(html_path: Path, chars_per_page: int = 3500) -> list[dict[str, int | str]]:
    """Extract text from an SEC HTML filing and create approximate pages.

    SEC primary filings are usually HTML, not PDF. Approximate page numbers keep
    citations honest when the source does not provide PDF page numbers.
    """
    parser = _HTMLTextExtractor()
    parser.feed(html_path.read_text(encoding="utf-8", errors="ignore"))
    text = parser.text()
    pages: list[dict[str, int | str]] = []
    for start in range(0, len(text), chars_per_page):
        page_text = text[start : start + chars_per_page].strip()
        if page_text:
            pages.append({"page": len(pages) + 1, "text": page_text})
    return pages


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def download_sec_document(url: str, output_path: Path, user_agent: str) -> Path:
    """Download one SEC filing with a descriptive User-Agent."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading SEC document to %s", output_path)
    response = requests.get(url, headers={"User-Agent": user_agent}, timeout=30)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path
