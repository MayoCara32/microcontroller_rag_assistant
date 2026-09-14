"""Coordinador principal del sistema Microcontroller RAG Assistant (Día 12)."""
from typing import Dict, Any, List, Optional
from configs.settings import get_settings
from src.indexing.embedder import EmbeddingService
from src.indexing.vector_indexer import VectorIndexer


class RAGOrchestrator:
    """Orquestador central: coordina la ingesta y la búsqueda semántica vectorial (Día 12).

    Nota pedagógica: La generación final aumentada (RAG con LLM), búsqueda híbrida BM25,
    re-ranking y guardrails eléctricos están aislados para fases futuras (Día 13+).
    """

    def __init__(
        self,
        vector_indexer: Optional[VectorIndexer] = None,
        embedder: Optional[EmbeddingService] = None,
    ):
        settings = get_settings()
        self.settings = settings
        self.vector_indexer = vector_indexer or VectorIndexer()
        self.embedder = embedder or EmbeddingService()

    def route_query(self, user_query: str) -> str:
        """Clasifica la consulta del usuario para el pipeline activo."""
        query_lower = user_query.lower()
        if any(w in query_lower for w in ["código", "code", "void loop", "setup()", "sketch", "firmware"]):
            return "firmware_query"
        return "hardware_query"

    def execute_workflow(
        self,
        user_query: str,
        target_mcu: str = "Arduino",
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ejecuta el flujo correspondiente al Día 12:

        Consulta -> Embedding RETRIEVAL_QUERY -> Búsqueda vectorial ChromaDB -> Top-K Chunks con Metadatos.
        El flujo se detiene en la entrega de fragmentos recuperados sin invocar LLM de generación final.
        """
        k = top_k or self.settings.TOP_K_RETRIEVAL
        route = self.route_query(user_query)

        # 1. Generación de embedding de consulta (task_type=RETRIEVAL_QUERY)
        query_embedding = self.embedder.embed_query(user_query)

        # 2. Búsqueda vectorial determinista en ChromaDB
        retrieved_chunks = self.vector_indexer.search(
            query_embedding=query_embedding,
            top_k=k,
            filters=filters
        )

        return {
            "query": user_query,
            "route": route,
            "target_mcu": target_mcu,
            "chunks_retrieved": len(retrieved_chunks),
            "results": retrieved_chunks,
            "status": "Día 12: Búsqueda vectorial completada (sin generación final)."
        }

    # =========================================================================
    # COMPONENTES AISLADOS PARA SESIONES FUTURAS (DÍA 13+)
    # =========================================================================
    def execute_future_generation_workflow(
        self,
        user_query: str,
        target_mcu: str = "Arduino",
        code_snippet: Optional[str] = None
    ) -> Dict[str, Any]:
        """Flujo reservado para fases posteriores del curso (RAG aumentado con LLM).

        No participa en el pipeline activo de Día 12.
        """
        raise NotImplementedError(
            "La generación RAG aumentada con LLM está reservada para sesiones posteriores (Día 13+)."
        )
