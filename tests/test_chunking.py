from app.rag.chunker import chunk_pages


def test_chunk_pages_preserves_metadata():
    pages = [{"page": 3, "text": "Consolidated Statements of Operations " + "revenue " * 200}]
    chunks = chunk_pages(pages, {"company": "Apple", "year": 2024, "filing_type": "10-K"})
    assert chunks
    assert chunks[0].metadata["company"] == "Apple"
    assert chunks[0].metadata["page"] == 3
    assert chunks[0].metadata["section"] == "Consolidated Statements of Operations"
