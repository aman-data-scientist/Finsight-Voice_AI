from functools import lru_cache
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "FinSight Voice"
    data_dir: Path = Field(default=Path("data"))
    raw_data_dir: Path = Field(default=Path("data/raw"))
    processed_dir: Path = Field(default=Path("data/processed"))
    vectorstore_dir: Path = Field(default=Path("data/vectorstore"))
    upload_max_mb: int = 10

    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    api_key: str | None = None

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    retrieval_top_k: int = 4
    retrieval_min_score: float = 0.2

    sec_user_agent: str = "FinSightVoicePortfolio/0.1 contact@example.com"

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if not settings.api_key:
        settings.api_key = (
            os.getenv("OPENAI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )
    return settings
