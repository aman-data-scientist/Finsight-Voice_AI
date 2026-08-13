import json

import numpy as np
import pytest

from app.rag import retriever

faiss = pytest.importorskip("faiss")


def test_retrieve_documents_from_tiny_index(tmp_path, monkeypatch):
    vector_dir = tmp_path / "vectorstore"
    vector_dir.mkdir()
    index = faiss.IndexFlatIP(2)
    index.add(np.array([[1.0, 0.0]], dtype="float32"))
    faiss.write_index(index, str(vector_dir / "index.faiss"))
    (vector_dir / "chunks.json").write_text(
        json.dumps([{"text": "Apple revenue evidence", "metadata": {"company": "Apple"}}]),
        encoding="utf-8",
    )

    settings = retriever.get_settings()
    monkeypatch.setattr(settings, "vectorstore_dir", vector_dir)
    monkeypatch.setattr(settings, "retrieval_min_score", 0.0)
    monkeypatch.setattr(retriever, "embed_texts", lambda texts: np.array([[1.0, 0.0]], dtype="float32"))

    results = retriever.retrieve_documents("Apple revenue")
    assert results[0]["metadata"]["company"] == "Apple"
