"""Motor de búsqueda híbrida combinando similitud densa y BM25 léxico."""
import re
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from configs.settings import get_settings
from src.core.interfaces import BaseRetriever
from src.indexing.embedder import EmbeddingService
from src.indexing.vector_indexer import VectorIndexer


class HybridSearchEngine(BaseRetriever):
    """Ejecuta consultas duales (Vector + BM25) para capturar semántica y nombres de pines/registros exactos."""

    def __init__(self, alpha: Optional[float] = None, vector_indexer: Optional[VectorIndexer] = None, embedder: Optional[EmbeddingService] = None):
        settings = get_settings()
        self.alpha = alpha if alpha is not None else settings.HYBRID_ALPHA
        self.vector_indexer = vector_indexer or VectorIndexer()
        self.embedder = embedder or EmbeddingService()

        # Índice BM25 en memoria
        self.corpus_chunks: List[Dict[str, Any]] = []
        self.bm25: Optional[BM25Okapi] = None

    def fit_lexical_index(self, chunks: List[Dict[str, Any]]) -> None:
        """Construye el índice BM25 a partir de los chunks documentales."""
        self.corpus_chunks = chunks
        tokenized_corpus = [self._tokenize(c.get("text", "")) for c in chunks]
        if tokenized_corpus:
            self.bm25 = BM25Okapi(tokenized_corpus)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenizador adaptado a términos técnicos (registros, pines, hexadecimale, etc.)."""
        return re.findall(r'\w+|0x[0-9a-fA-F]+', text.lower())

    def retrieve(self, query: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Implementación de la interfaz BaseRetriever."""
        return self.search(query, filters=filters, top_k=top_k)

    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Realiza la búsqueda híbrida y aplica Fusión de Rangos Recíprocos (RRF)."""
        # 1. Búsqueda Densa (Vectorial)
        query_vec = self.embedder.get_query_embedding(query)
        dense_results = self.vector_indexer.search(query_vec, top_k=top_k * 2, filters=filters)

        # 2. Búsqueda Léxica (BM25)
        bm25_results = []
        if self.bm25 and self.corpus_chunks:
            tokenized_query = self._tokenize(query)
            query_set = set(tokenized_query)
            scores = self.bm25.get_scores(tokenized_query)
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k * 2]
            for idx in top_indices:
                chunk_tokens = set(self._tokenize(self.corpus_chunks[idx].get("text", "")))
                # Incluir si el score de BM25 es > 0 o si contiene coincidencia exacta de token
                if scores[idx] > 0 or bool(query_set & chunk_tokens):
                    bm25_results.append({
                        "chunk_id": self.corpus_chunks[idx].get("chunk_id", f"bm25_{idx}"),
                        "text": self.corpus_chunks[idx].get("text", ""),
                        "metadata": {
                            "file_name": self.corpus_chunks[idx].get("file_name", ""),
                            "category": self.corpus_chunks[idx].get("category", "")
                        },
                        "score": float(scores[idx]) if scores[idx] > 0 else 0.1
                    })

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = {}
        chunks_by_id: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(dense_results):
            cid = item["chunk_id"]
            chunks_by_id[cid] = item
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (self.alpha / (60.0 + rank + 1))

        for rank, item in enumerate(bm25_results):
            cid = item["chunk_id"]
            chunks_by_id[cid] = item
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + ((1.0 - self.alpha) / (60.0 + rank + 1))

        sorted_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        fused_results = []
        for cid in sorted_ids[:top_k]:
            item = chunks_by_id[cid]
            item["fused_score"] = rrf_scores[cid]
            fused_results.append(item)

        return fused_results
