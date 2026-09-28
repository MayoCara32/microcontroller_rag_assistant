"""Servicio encapsulado de recuperación semántica vectorial para Microcontroller RAG Assistant."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from configs.settings import get_settings
from src.indexing.embedder import EmbeddingService
from src.indexing.vector_indexer import VectorIndexer
from src.retrieval.dense_retriever import DenseRetriever


class RetrievalService:
    """Encapsula la recepción de consultas, generación de embeddings y búsqueda híbrida (semántica y vectorial) en ChromaDB."""

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

        self.dense_retriever = DenseRetriever(embedder=self.embedder, vector_indexer=self.vector_indexer)
        if retriever is not None:
            self.retriever = retriever
        elif use_hybrid:
            from src.retrieval.hybrid_search import HybridSearchEngine
            hybrid_engine = HybridSearchEngine(
                vector_indexer=self.vector_indexer,
                embedder=self.embedder,
                alpha=self.settings.HYBRID_ALPHA
            )
            # Sincronizar índice léxico BM25 con los fragmentos de la base vectorial
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
                    hybrid_engine.fit_lexical_index(corpus)
            except Exception:
                pass
            self.retriever = hybrid_engine
        else:
            self.retriever = self.dense_retriever

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
        - score: score normalizado o fused_score
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

        # 2. Ejecutar la recuperación a través del Retriever
        k = top_k or self.settings.TOP_K_RETRIEVAL
        try:
            # Si existen filtros de metadatos, ejecutar directamente en ChromaDB mediante búsqueda vectorial restringida (where)
            if filters:
                raw_results = self.dense_retriever.retrieve(
                    query=query.strip(),
                    top_k=k,
                    filters=filters
                )
            else:
                raw_results = self.retriever.retrieve(
                    query=query.strip(),
                    top_k=k,
                    filters=None
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
            score = item.get("fused_score") or item.get("score") or (1.0 / (1.0 + float(distancia)))

            formatted_results.append({
                "chunk_id": chunk_id,
                "texto": texto,
                "text": texto,  # alias retrocompatible
                "metadata": metadata,
                "distancia": float(distancia),
                "distance": float(distancia),  # alias retrocompatible
                "score": float(score)
            })

        return formatted_results
