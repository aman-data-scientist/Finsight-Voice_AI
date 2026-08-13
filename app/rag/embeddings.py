from functools import lru_cache

import numpy as np

from app.config import get_settings


@lru_cache
def get_embedding_model():
    settings = get_settings()
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_embedding_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return np.asarray(vectors, dtype="float32")
