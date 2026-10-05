"""Configuration settings for the clinical intelligence system."""

from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8501"]

    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "google/gemini-2.5-flash-lite"
    OPENROUTER_MAX_TOKENS: int = 2048
    OPENROUTER_TEMPERATURE: float = 0.0
    OPENROUTER_SEED: Optional[int] = 42

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CROSS_ENCODER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    NLI_MODEL: str = "cross-encoder/nli-deberta-v3-small"
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    FAISS_DIM: int = 384

    RAG_K_RETRIEVE: int = 20
    RAG_K_RERANK: int = 8

    MAX_TEXT_INPUT_LENGTH: int = 5000
    ABSTAIN_CONFIDENCE_THRESHOLD: float = 0.45

    REPLAY: bool = False
    LLM_CACHE_DIR: str = "./data/llm_cache"
    CORPUS_PATH: str = "./data/corpus.jsonl"

    ENTREZ_EMAIL: str = "dev@example.com"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
