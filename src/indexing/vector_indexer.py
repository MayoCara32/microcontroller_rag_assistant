"""Gestor de indexación persistente en base vectorial utilizando ChromaDB."""
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from configs.settings import get_settings
from src.core.interfaces import BaseVectorIndexer


class VectorIndexer(BaseVectorIndexer):
    """Indexa chunks procesados y gestiona colecciones en ChromaDB."""

    def __init__(self, storage_dir: Optional[Path] = None, collection_name: str = "microcontrollers_kb"):
        settings = get_settings()
        self.storage_dir = Path(storage_dir or settings.STORAGE_VECTOR_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(path=str(self.storage_dir))
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def index_documents(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """Implementación de la interfaz BaseVectorIndexer."""
        if not chunks or not embeddings:
            return

        ids = [c.get("chunk_id", f"chunk_{i}") for i, c in enumerate(chunks)]
        documents = [c.get("text", "") for c in chunks]
        metadatas = [
            {
                "file_name": c.get("file_name", ""),
                "category": c.get("category", ""),
                "component": c.get("component", "")
            }
            for c in chunks
        ]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query_embedding: List[float], top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Implementación de la interfaz BaseVectorIndexer."""
        if not query_embedding:
            return []

        where_filter = filters if filters else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )

        retrieved = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            ids = results["ids"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)

            for d, i, m, dist in zip(docs, ids, metas, distances):
                retrieved.append({
                    "chunk_id": i,
                    "text": d,
                    "metadata": m,
                    "score": 1.0 / (1.0 + dist)  # Convertir distancia L2 a score de similitud
                })

        return retrieved

    def create_index(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """Construye y persiste el índice vectorial."""
        self.index_documents(chunks, embeddings)

    def add_documents(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """Agrega documentos incrementalmente a la colección."""
        self.index_documents(chunks, embeddings)
