"""Definición y carga centralizada de configuraciones del sistema."""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuraciones globales del Asistente RAG para Microcontroladores (Día 12)."""

    # Raíz del proyecto
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Directorios de datos
    DATA_RAW_DIR: Path = BASE_DIR / "data" / "raw"
    DATA_PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
    DATA_METADATA_DIR: Path = BASE_DIR / "data" / "metadata"

    # Directorios de almacenamiento persistente
    STORAGE_VECTOR_DIR: Path = BASE_DIR / "storage" / "vector_store"
    STORAGE_LEXICAL_DIR: Path = BASE_DIR / "storage" / "lexical_index"

    # Proveedor y Modelo de Embeddings (Día 12)
    EMBEDDING_PROVIDER: str = "google"
    DEFAULT_EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIMENSION: int = 768
    GEMINI_API_KEY: Optional[str] = None

    # Control de seguridad de pruebas: en producción debe ser False
    ALLOW_TEST_EMBEDDINGS: bool = False

    # Parámetros de Fragmentación (Chunking) y Recuperación
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    TOP_K_RETRIEVAL: int = 5

    # Parámetros y modelos reservados para fases futuras (Día 13+)
    LLM_PROVIDER: str = "google"
    OPENAI_API_KEY: Optional[str] = None
    DEFAULT_LLM_MODEL: str = "gemini-2.0-flash"
    TOP_K_RERANKED: int = 5
    SIMILARITY_THRESHOLD: float = 0.75
    HYBRID_ALPHA: float = 0.5
    ENFORCE_STRICT_ELECTRICAL_CHECK: bool = True
    ENFORCE_CITATION_VALIDATION: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


def get_settings() -> Settings:
    """Devuelve una instancia singleton o fresca de Settings."""
    return Settings()
