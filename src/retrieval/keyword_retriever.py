"""Módulo de recuperación textual/léxica utilizando BM25 (Día 17)."""
from typing import List, Dict, Any, Optional
from src.core.interfaces import BaseRetriever
from src.retrieval.bm25_index import BM25Index


class KeywordRetriever(BaseRetriever):
    """Recuperador léxico basado en coincidencias exactas de texto con BM25."""

    def __init__(self, bm25_index: Optional[BM25Index] = None):
        self.bm25_index = bm25_index or BM25Index()

    def fit(self, chunks: List[Dict[str, Any]]) -> None:
        """Inicializa/sincroniza el índice BM25 con los fragmentos del corpus."""
        self.bm25_index.fit(chunks)

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Ejecuta la búsqueda léxica BM25 filtrando opcionalmente por metadatos."""
        if not query or not query.strip():
            return []

        k = top_k or 10
        raw_results = self.bm25_index.search(query.strip(), top_k=k * 2)

        # Aplicar filtrado por metadata en memoria si se proveen filtros
        filtered_results = []
        for item in raw_results:
            meta = item.get("metadata", {})
            match = True
            if filters:
                for fk, fv in filters.items():
                    if meta.get(fk) != fv:
                        match = False
                        break
            if match:
                filtered_results.append(item)

        return filtered_results[:k]
