import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from app.config import get_settings
from app.rag.chunker import Chunk
from app.rag.embeddings import embed_texts

logger = logging.getLogger(__name__)


INDEX_FILE = "index.faiss"
CHUNKS_FILE = "chunks.json"


def build_vector_index(chunks: list[Chunk], output_dir: Path | None = None) -> int:
    """Embed chunks and persist a FAISS cosine-similarity index."""
    settings = get_settings()
    output_dir = output_dir or settings.vectorstore_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    if not chunks:
        raise ValueError("No chunks provided for indexing.")

    import faiss

    vectors = embed_texts([chunk.text for chunk in chunks])
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(output_dir / INDEX_FILE))

    payload = [{"text": chunk.text, "metadata": chunk.metadata} for chunk in chunks]
    (output_dir / CHUNKS_FILE).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info("Indexed %s chunks", len(chunks))
    return len(chunks)


def retrieve_documents(query: str, top_k: int | None = None) -> list[dict[str, Any]]:
    """Return top semantic matches from the local FAISS index."""
    settings = get_settings()
    top_k = top_k or settings.retrieval_top_k
    index_path = settings.vectorstore_dir / INDEX_FILE
    chunks_path = settings.vectorstore_dir / CHUNKS_FILE
    if not index_path.exists() or not chunks_path.exists():
        raise FileNotFoundError("Vector index is missing. Run scripts/ingest.py first.")

    import faiss

    index = faiss.read_index(str(index_path))
    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    query_vector = embed_texts([query])
    scores, ids = index.search(np.asarray(query_vector, dtype="float32"), top_k)

    results: list[dict[str, Any]] = []
    for score, chunk_id in zip(scores[0], ids[0]):
        if chunk_id < 0:
            continue
        item = chunks[int(chunk_id)]
        result = {
            "text": item["text"],
            "score": float(score),
            "metadata": item["metadata"],
        }
        if result["score"] >= settings.retrieval_min_score:
            results.append(result)
    logger.info("Retrieved %s chunks for query", len(results))
    return results
