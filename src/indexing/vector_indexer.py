"""Gestor de indexación persistente en base vectorial."""
from pathlib import Path
from typing import List, Dict, Any


class VectorIndexer:
    """Indexa chunks procesados y gestiona colecciones en ChromaDB / Qdrant."""

    def __init__(self, storage_dir: Path, collection_name: str = "microcontrollers_kb"):
        self.storage_dir = storage_dir
        self.collection_name = collection_name

    def create_index(self, chunks: List[Dict[str, Any]]) -> None:
        """Construye y persiste el índice vectorial."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")

    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """Agrega documentos incrementalmente a la colección."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")
