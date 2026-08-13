import argparse
import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.config import get_settings
from app.rag.chunker import Chunk, chunk_pages
from app.rag.loader import extract_html_pages, extract_pdf_pages
from app.rag.retriever import build_vector_index
from app.rag.sources import SEC_DOCUMENTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_document_manifest() -> list[dict[str, str | int]]:
    settings = get_settings()
    manifest_path = settings.processed_dir / "document_manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return SEC_DOCUMENTS


def ingest_local_pdfs() -> int:
    settings = get_settings()
    all_chunks: list[Chunk] = []
    for doc in load_document_manifest():
        company_folder = str(doc["company"]).lower()
        pdf_path = settings.raw_data_dir / company_folder / f"{doc['year']}_10k.pdf"
        annual_pdf_path = settings.raw_data_dir / company_folder / f"{doc['year']}_annual_report.pdf"
        html_path = settings.raw_data_dir / company_folder / f"{doc['year']}_10k.html"
        htm_path = settings.raw_data_dir / company_folder / f"{doc['year']}_10k.htm"
        if pdf_path.exists():
            pages = extract_pdf_pages(pdf_path)
        elif annual_pdf_path.exists():
            pages = extract_pdf_pages(annual_pdf_path)
        elif html_path.exists():
            pages = extract_html_pages(html_path)
        elif htm_path.exists():
            pages = extract_html_pages(htm_path)
        else:
            logger.warning(
                "Missing %s, %s, or %s. Download the filing from %s",
                pdf_path,
                annual_pdf_path,
                html_path,
                doc["source_url"],
            )
            continue
        chunks = chunk_pages(pages, doc)
        all_chunks.extend(chunks)

    if not all_chunks:
        raise SystemExit("No local PDFs found. See README data ingestion instructions.")
    return build_vector_index(all_chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the small FinSight FAISS index.")
    parser.parse_args()
    count = ingest_local_pdfs()
    print(f"Indexed {count} chunks.")
