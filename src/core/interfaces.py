"""Definición de interfaces abstractas para la arquitectura desacoplada de Microcontrollers AI Copilot."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional


class BaseParser(ABC):
    """Interfaz base para extractores de documentos técnicos (PDF, MD, HTML)."""

    @abstractmethod
    def parse_document(self, file_path: Path) -> Dict[str, Any]:
        """Extrae el contenido estructurado y metadatos de un archivo."""
        pass


class BaseCleaner(ABC):
    """Interfaz base para limpiadores de texto y eliminación de ruido."""

    @abstractmethod
    def clean(self, raw_text: str) -> str:
        """Limpia el texto eliminando ruido, duplicados o caracteres no deseados."""
        pass


class BaseChunker(ABC):
    """Interfaz base para algoritmos de fragmentación semántica/estructurada."""

    @abstractmethod
    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fragmenta el texto en chunks optimizados con metadatos técnicos."""
        pass


class BaseEmbedder(ABC):
    """Interfaz base para generadores de vectores de características."""

    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings vectoriales para una lista de textos."""
        pass

    @abstractmethod
    def get_query_embedding(self, query: str) -> List[float]:
        """Genera el embedding vectorial para una consulta de búsqueda."""
        pass


class BaseVectorIndexer(ABC):
    """Interfaz base para la gestión e indexación en almacenes vectoriales."""

    @abstractmethod
    def index_documents(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """Almacena fragmentos y sus correspondientes vectores en la base de datos."""
        pass

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Ejecuta una búsqueda vectorial k-NN."""
        pass


class BaseRetriever(ABC):
    """Interfaz base para estrategias de búsqueda (densa, léxica o híbrida)."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Recupera los fragmentos más relevantes para una consulta dada."""
        pass


class BaseAgent(ABC):
    """Interfaz base para agentes especializados del sistema."""

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la tarea asignada al agente especializado."""
        pass
