"""Módulo de recuperación semántica vectorial densa (Día 12)."""
from typing import Dict, Any, List, Optional
from configs.settings import get_settings
from src.core.interfaces import BaseRetriever, BaseEmbedder, BaseVectorIndexer
from src.indexing.embedder import EmbeddingService
from src.indexing.vector_indexer import VectorIndexer


class DenseRetriever(BaseRetriever):
    """Recuperador semántico que transforma consultas en embeddings y busca en ChromaDB."""

    def __init__(
        self,
        embedder: Optional[BaseEmbedder] = None,
        vector_indexer: Optional[BaseVectorIndexer] = None,
    ):
        settings = get_settings()
        self.settings = settings
        self.embedder = embedder or EmbeddingService()
        self.vector_indexer = vector_indexer or VectorIndexer()

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Recupera los fragmentos más relevantes para una consulta técnica usando búsqueda vectorial.

        Flujo obligatorio (Día 12):
        Consulta -> Embedding RETRIEVAL_QUERY -> k-NN ChromaDB -> Chunks estructurados.
        """
        if not query or not query.strip():
            return []

        k = top_k or self.settings.TOP_K_RETRIEVAL

        # 1. Generación del embedding de consulta (task_type=RETRIEVAL_QUERY)
        query_embedding = self.embedder.embed_query(query.strip())

        # 2. Búsqueda de los vecinos más cercanos en el almacén vectorial
        results = self.vector_indexer.search(
            query_embedding=query_embedding,
            top_k=k,
            filters=filters
        )

        return results
