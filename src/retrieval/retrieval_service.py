"""Servicio encapsulado de recuperación semántica vectorial para Microcontroller RAG Assistant."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from configs.settings import get_settings
from src.indexing.embedder import EmbeddingService
from src.indexing.vector_indexer import VectorIndexer
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.keyword_retriever import KeywordRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.fusion import WeightedScoreFusion


class RetrievalService:
    """Encapsula la recepción de consultas, búsqueda semántica, léxica e híbrida con soporte de filtros."""

    def __init__(
        self,
        embedder: Optional[EmbeddingService] = None,
        vector_indexer: Optional[VectorIndexer] = None,
        retriever: Optional[Any] = None,
        use_hybrid: bool = True
    ):
        self.settings = get_settings()
        self.embedder = embedder or EmbeddingService()
        self.vector_indexer = vector_indexer or VectorIndexer()
        self.use_hybrid = use_hybrid
        self.custom_retriever = retriever

        self.dense_retriever = DenseRetriever(embedder=self.embedder, vector_indexer=self.vector_indexer)
        self.keyword_retriever = KeywordRetriever()
        self.fusion_engine = WeightedScoreFusion(
            dense_weight=self.settings.DENSE_WEIGHT,
            keyword_weight=self.settings.KEYWORD_WEIGHT
        )
        self.hybrid_retriever = HybridRetriever(
            dense_retriever=self.dense_retriever,
            keyword_retriever=self.keyword_retriever,
            fusion_engine=self.fusion_engine
        )

        self._sync_lexical_index()

        if retriever is not None:
            self.retriever = retriever
        else:
            self.retriever = self.hybrid_retriever if use_hybrid else self.dense_retriever

    def _sync_lexical_index(self) -> None:
        """Sincroniza el corpus en memoria de BM25 cargando fragmentos desde ChromaDB."""
        try:
            all_data = self.vector_indexer.collection.get()
            if all_data and all_data.get("ids"):
                corpus = []
                for cid, doc, meta in zip(
                    all_data["ids"],
                    all_data["documents"],
                    all_data.get("metadatas") or [{}] * len(all_data["ids"])
                ):
                    corpus.append({
                        "chunk_id": cid,
                        "text": doc,
                        "file_name": (meta or {}).get("file_name", ""),
                        "category": (meta or {}).get("category", ""),
                        "metadata": meta or {}
                    })
                self.keyword_retriever.fit(corpus)
        except Exception:
            pass

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        mode: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """Ejecuta la búsqueda (dense, keyword o hybrid) y retorna fragmentos relevantes."""
        if not query or not query.strip():
            return []

        storage_dir = Path(self.settings.STORAGE_VECTOR_DIR)
        if not storage_dir.exists():
            raise FileNotFoundError(
                f"La base de datos vectorial ChromaDB no existe en la ruta: {storage_dir}. "
                "Ejecute primero el pipeline de indexación para generar los vectores."
            )

        k = top_k or self.settings.TOP_K_RETRIEVAL

        try:
            if self.custom_retriever is not None:
                raw_results = self.custom_retriever.retrieve(
                    query=query.strip(),
                    top_k=k,
                    filters=filters
                )
            elif mode == "dense":
                raw_results = self.dense_retriever.retrieve(
                    query=query.strip(),
                    top_k=k,
                    filters=filters
                )
            elif mode == "keyword":
                raw_results = self.keyword_retriever.retrieve(
                    query=query.strip(),
                    top_k=k,
                    filters=filters
                )
            elif mode == "hybrid":
                raw_results = self.hybrid_retriever.retrieve(
                    query=query.strip(),
                    top_k=k,
                    filters=filters
                )
            else:
                raw_results = self.retriever.retrieve(
                    query=query.strip(),
                    top_k=k,
                    filters=filters
                )
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise e
            raise RuntimeError(
                f"Falla durante la generación de embedding o búsqueda en ChromaDB: {str(e)}"
            ) from e

        formatted_results: List[Dict[str, Any]] = []
        for item in raw_results:
            chunk_id = item.get("chunk_id") or item.get("id", "")
            texto = item.get("text") or item.get("texto", "")
            metadata = item.get("metadata", {})
            distancia = item.get("distance") if "distance" in item else item.get("distancia", 0.0)
            score = item.get("hybrid_score") or item.get("fused_score") or item.get("score") or (1.0 / (1.0 + float(distancia)))

            formatted_results.append({
                "chunk_id": str(chunk_id),
                "texto": texto,
                "text": texto,
                "metadata": metadata,
                "distancia": float(distancia),
                "distance": float(distancia),
                "score": float(score),
                "dense_score": float(item.get("dense_score", 0.0)),
                "keyword_score": float(item.get("keyword_score", 0.0)),
                "hybrid_score": float(score)
            })

        return formatted_results
