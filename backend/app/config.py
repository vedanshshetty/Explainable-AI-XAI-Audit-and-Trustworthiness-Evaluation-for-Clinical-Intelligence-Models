"""Configuration settings for the clinical intelligence system."""

from functools import lru_cache
from pathlib import Path
from typing import Any, List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Absolute project root, derived from this file rather than the working
# directory. Relative paths in settings ("./data/corpus.jsonl") are resolved
# against this, so the app behaves identically no matter where it is launched
# from. Without this, starting uvicorn inside backend/ silently loads nothing.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# .env is looked up next to the project root so it is found from any cwd.
ENV_FILE = PROJECT_ROOT / ".env"


def resolve_path(value: str) -> str:
    """Return an absolute path, anchoring relative paths to the project root."""
    path = Path(value).expanduser()
    if path.is_absolute():
        return str(path)
    return str((PROJECT_ROOT / path).resolve())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
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

    # Citation rendering
    CITATION_TOP_K: int = 5
    CITATION_MAX_EXCERPT_CHARS: int = 900

    # Data source: Europe PMC REST API (scripts/download_data.py).
    # The local corpus stays the primary source; these only drive an optional refresh.
    EUROPE_PMC_BASE_URL: str = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    EUROPE_PMC_SEARCH_PATH: str = "search"
    EUROPE_PMC_EMAIL: str = "dev@example.com"
    EUROPE_PMC_PAGE_SIZE: int = 100
    EUROPE_PMC_MAX_RETRIES: int = 3
    EUROPE_PMC_TIMEOUT: int = 30
    EUROPE_PMC_REQUEST_DELAY: float = 1.0

    # Deprecated: NCBI eutils is no longer used for downloads.
    ENTREZ_EMAIL: str = "dev@example.com"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator(
        "FAISS_INDEX_PATH", "LLM_CACHE_DIR", "CORPUS_PATH", mode="after"
    )
    @classmethod
    def anchor_paths(cls, v: Any) -> Any:
        """Anchor filesystem settings to the project root.

        Without this the data files are looked up relative to the process
        working directory, so running uvicorn from backend/ finds an empty
        corpus and the retrieval pipeline returns nothing.
        """
        return resolve_path(v) if isinstance(v, str) else v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
