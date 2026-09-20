"""Central configuration management for AeroCX AI.

All settings are read from environment variables (see .env.example).
No secrets are hard-coded.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings loaded from the environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: str = "mock"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    hf_sentiment_model: str = "distilbert-base-uncased-finetuned-sst-2-english"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    database_url: str = "postgresql+psycopg2://aerocx:aerocx@localhost:5432/aerocx"
    model_path: str = "models"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    random_seed: int = 42
    log_level: str = "INFO"

    # RAG relevance gate: minimum cosine similarity for retrieved context to
    # count as grounded. Calibrated on the TF-IDF fallback backend
    # (see docs/architecture.md). Tunable per deployment.
    rag_min_similarity: float = 0.10


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


def model_dir() -> Path:
    """Absolute path to the directory holding trained artefacts."""
    s = get_settings()
    p = Path(s.model_path)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return p
