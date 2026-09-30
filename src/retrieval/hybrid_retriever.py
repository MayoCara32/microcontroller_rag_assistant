"""Coordinador del sistema de Recuperación Híbrida (Dense + BM25) (Día 17)."""
from typing import List, Dict, Any, Optional
from src.core.interfaces import BaseRetriever
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.keyword_retriever import KeywordRetriever
from src.retrieval.fusion import WeightedScoreFusion


class HybridRetriever(BaseRetriever):
    """Integra y coordina Dense Retrieval y Keyword Retrieval aplicando fusión de scores."""

    def __init__(
        self,
        dense_retriever: Optional[DenseRetriever] = None,
        keyword_retriever: Optional[KeywordRetriever] = None,
        fusion_engine: Optional[WeightedScoreFusion] = None
    ):
        self.dense_retriever = dense_retriever or DenseRetriever()
        self.keyword_retriever = keyword_retriever or KeywordRetriever()
        self.fusion_engine = fusion_engine or WeightedScoreFusion()

    def fit_keyword_index(self, chunks: List[Dict[str, Any]]) -> None:
        """Inicializa el índice BM25 con el corpus de chunks."""
        self.keyword_retriever.fit(chunks)

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Ejecuta búsquedas densa y textual, fusiona resultados y elimina duplicados."""
        if not query or not query.strip():
            return []

        k = top_k or 10

        # 1. Búsqueda semántica densa
        dense_results = self.dense_retriever.retrieve(query=query, top_k=k * 2, filters=filters)

        # 2. Búsqueda por palabras clave (BM25)
        keyword_results = self.keyword_retriever.retrieve(query=query, top_k=k * 2, filters=filters)

        # 3. Fusión de resultados (Weighted Score Fusion) y ordenamiento
        fused_results = self.fusion_engine.fuse(
            dense_results=dense_results,
            keyword_results=keyword_results,
            top_k=k
        )

        return fused_results
