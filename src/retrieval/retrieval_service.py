"""Servicio encapsulado de recuperación semántica vectorial para Microcontroller RAG Assistant."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from configs.settings import get_settings
from src.indexing.embedder import EmbeddingService
from src.indexing.vector_indexer import VectorIndexer
from src.retrieval.dense_retriever import DenseRetriever


class RetrievalService:
    """Encapsula la recepción de consultas, generación de embeddings y búsqueda en ChromaDB."""

    def __init__(
        self,
        embedder: Optional[EmbeddingService] = None,
        vector_indexer: Optional[VectorIndexer] = None,
        retriever: Optional[DenseRetriever] = None
    ):
        self.settings = get_settings()
        if retriever is not None:
            self.retriever = retriever
        else:
            emb = embedder or EmbeddingService()
            vec = vector_indexer or VectorIndexer()
            self.retriever = DenseRetriever(embedder=emb, vector_indexer=vec)

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Ejecuta la búsqueda semántica vectorial y retorna fragmentos relevantes.

        Devuelve una lista de diccionarios con las claves:
        - chunk_id: identificador único del fragmento
        - texto: contenido textual del fragmento
        - metadata: diccionarios con metadatos asociados
        - distancia: distancia L2 respecto a la consulta
        """
        if not query or not query.strip():
            return []

        # 1. Verificar si existe el directorio de la base vectorial
        storage_dir = Path(self.settings.STORAGE_VECTOR_DIR)
        if not storage_dir.exists():
            raise FileNotFoundError(
                f"La base de datos vectorial ChromaDB no existe en la ruta: {storage_dir}. "
                "Ejecute primero el pipeline de indexación para generar los vectores."
            )

        # 2. Ejecutar la recuperación a través del DenseRetriever
        try:
            raw_results = self.retriever.retrieve(
                query=query.strip(),
                top_k=top_k,
                filters=filters
            )
        except Exception as e:
            raise RuntimeError(
                f"Falla durante la generación de embedding o búsqueda en ChromaDB: {str(e)}"
            ) from e

        # 3. Formatear y estructurar resultados con los campos requeridos
        formatted_results: List[Dict[str, Any]] = []
        for item in raw_results:
            chunk_id = item.get("chunk_id", "")
            texto = item.get("text") or item.get("texto", "")
            metadata = item.get("metadata", {})
            distancia = item.get("distance") if "distance" in item else item.get("distancia", 0.0)

            formatted_results.append({
                "chunk_id": chunk_id,
                "texto": texto,
                "text": texto,  # alias retrocompatible
                "metadata": metadata,
                "distancia": float(distancia),
                "distance": float(distancia)  # alias retrocompatible
            })

        return formatted_results
