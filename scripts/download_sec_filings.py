import logging
import json
import sys
import time
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.config import get_settings
from app.rag.loader import download_sec_document
from app.rag.sources import SEC_COMPANIES, SEC_DOCUMENTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _build_sec_document(company_key: str, filing_date: str, accession: str, primary_doc: str) -> dict[str, str | int]:
    company = SEC_COMPANIES[company_key]
    cik = company["cik"]
    year = int(filing_date[:4])
    accession_no_dash = accession.replace("-", "")
    source_url = (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
        f"{accession_no_dash}/{primary_doc}"
    )
    return {
        "company": company["company"],
        "ticker": company["ticker"],
        "filing_type": "10-K",
        "year": year,
        "document_id": f"{company_key}_{year}_10k",
        "source_url": source_url,
    }


def _append_10ks_from_filings(company_key: str, filings: dict, documents: list[dict[str, str | int]], limit: int) -> None:
    seen_ids = {doc["document_id"] for doc in documents}
    for form, filing_date, accession, primary_doc in zip(
        filings["form"],
        filings["filingDate"],
        filings["accessionNumber"],
        filings["primaryDocument"],
    ):
        if form != "10-K":
            continue
        doc = _build_sec_document(company_key, filing_date, accession, primary_doc)
        if doc["document_id"] in seen_ids:
            continue
        documents.append(doc)
        seen_ids.add(doc["document_id"])
        if len(documents) == limit:
            return


def discover_latest_10ks(company_key: str, limit: int = 10) -> list[dict[str, str | int]]:
    """Discover recent and archived 10-K filings from SEC submissions metadata."""
    settings = get_settings()
    company = SEC_COMPANIES[company_key]
    cik = company["cik"]
    submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(
        submissions_url,
        headers={"User-Agent": settings.sec_user_agent},
        timeout=30,
    )
    response.raise_for_status()
    docs: list[dict[str, str | int]] = []
    payload = response.json()
    _append_10ks_from_filings(company_key, payload["filings"]["recent"], docs, limit)

    for archive in payload["filings"].get("files", []):
        if len(docs) >= limit:
            break
        archive_url = f"https://data.sec.gov/submissions/{archive['name']}"
        archive_response = requests.get(
            archive_url,
            headers={"User-Agent": settings.sec_user_agent},
            timeout=30,
        )
        archive_response.raise_for_status()
        _append_10ks_from_filings(company_key, archive_response.json(), docs, limit)
        time.sleep(0.2)

    if len(docs) < limit:
        logger.warning("Only found %s 10-K filings for %s", len(docs), company["company"])
    return docs


def write_manifest(documents: list[dict[str, str | int]]) -> None:
    settings = get_settings()
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = settings.processed_dir / "document_manifest.json"
    manifest_path.write_text(json.dumps(documents, indent=2), encoding="utf-8")
    logger.info("Wrote manifest with %s documents to %s", len(documents), manifest_path)


def download_small_sec_corpus() -> None:
    """Download the tiny curated SEC corpus as HTML files."""
    settings = get_settings()
    for doc in SEC_DOCUMENTS:
        company_folder = str(doc["company"]).lower()
        output_path = settings.raw_data_dir / company_folder / f"{doc['year']}_10k.html"
        if output_path.exists():
            logger.info("Already exists: %s", output_path)
            continue
        download_sec_document(str(doc["source_url"]), output_path, settings.sec_user_agent)
        time.sleep(0.2)


def download_sec_corpus(companies: list[str], per_company: int) -> None:
    """Download recent SEC annual filings for selected companies."""
    settings = get_settings()
    documents: list[dict[str, str | int]] = []
    for company_key in companies:
        discovered = discover_latest_10ks(company_key, limit=per_company)
        documents.extend(discovered)
        for doc in discovered:
            company_folder = str(doc["company"]).lower()
            output_path = settings.raw_data_dir / company_folder / f"{doc['year']}_10k.html"
            if output_path.exists():
                logger.info("Already exists: %s", output_path)
                continue
            download_sec_document(str(doc["source_url"]), output_path, settings.sec_user_agent)
            time.sleep(0.2)
    write_manifest(documents)


if __name__ == "__main__":
    download_sec_corpus(["apple", "microsoft", "tesla", "google"], per_company=10)
    print("Downloaded SEC filings into data/raw and wrote data/processed/document_manifest.json.")
