SEC_COMPANIES: dict[str, dict[str, str]] = {
    "apple": {"company": "Apple", "ticker": "AAPL", "cik": "0000320193"},
    "microsoft": {"company": "Microsoft", "ticker": "MSFT", "cik": "0000789019"},
    "tesla": {"company": "Tesla", "ticker": "TSLA", "cik": "0001318605"},
    "google": {"company": "Google", "ticker": "GOOGL", "cik": "0001652044"},
}


SEC_DOCUMENTS: list[dict[str, str | int]] = [
    {
        "company": "Apple",
        "ticker": "AAPL",
        "filing_type": "10-K",
        "year": 2024,
        "document_id": "apple_2024_10k",
        "source_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm",
    },
    {
        "company": "Apple",
        "ticker": "AAPL",
        "filing_type": "10-K",
        "year": 2023,
        "document_id": "apple_2023_10k",
        "source_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm",
    },
    {
        "company": "Microsoft",
        "ticker": "MSFT",
        "filing_type": "10-K",
        "year": 2024,
        "document_id": "microsoft_2024_10k",
        "source_url": "https://www.sec.gov/Archives/edgar/data/789019/000095017024087843/msft-20240630.htm",
    },
    {
        "company": "Microsoft",
        "ticker": "MSFT",
        "filing_type": "10-K",
        "year": 2023,
        "document_id": "microsoft_2023_10k",
        "source_url": "https://www.sec.gov/Archives/edgar/data/789019/000095017023035122/msft-20230630.htm",
    },
    {
        "company": "Tesla",
        "ticker": "TSLA",
        "filing_type": "10-K",
        "year": 2024,
        "document_id": "tesla_2024_10k",
        "source_url": "https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231.htm",
    },
    {
        "company": "Tesla",
        "ticker": "TSLA",
        "filing_type": "10-K",
        "year": 2023,
        "document_id": "tesla_2023_10k",
        "source_url": "https://www.sec.gov/Archives/edgar/data/1318605/000162828024002390/tsla-20231231.htm",
    },
]
