from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "CourseFinder API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/coursefinder"
    SQLITE_FALLBACK_PATH: str = str(BASE_DIR / "data" / "coursefinder_local.db")
    USE_SQLITE_IF_POSTGRES_UNAVAILABLE: bool = True

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_DEFAULT_TTL: int = 600  # 10 minutes
    REDIS_ENABLED: bool = True

    # Information Retrieval & Embedding Parameters
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    BM25_K1: float = 1.5
    BM25_B: float = 0.75
    RRF_K: int = 60  # Standard Reciprocal Rank Fusion constant

    # Dataset file
    DATASET_PATH: str = str(BASE_DIR / "data" / "courses_dataset.json")
    EMBEDDINGS_CACHE_PATH: str = str(BASE_DIR / "data" / "courses_embeddings.npy")

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
