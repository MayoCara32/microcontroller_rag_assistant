"""Coordinador principal del sistema Microcontroller RAG Assistant con Metadata Filtering."""
from typing import Dict, Any, List, Optional
from configs.settings import get_settings
from src.indexing.embedder import EmbeddingService
from src.indexing.vector_indexer import VectorIndexer
from src.retrieval.retrieval_service import RetrievalService
from src.retrieval.query_analyzer import QueryAnalyzer
from src.retrieval.filter_builder import MetadataFilterBuilder
from src.generation.prompt_builder import PromptBuilder
from src.generation.response_generator import ResponseGenerator


class RAGOrchestrator:
    """Orquestador central: coordina análisis de consulta, filtrado de metadatos, recuperación y generación.

    Mantiene estrictamente desacopladas las responsabilidades:
    - Retrieval: encuentra y filtra información documental relevante.
    - Generation: sintetiza y explica fundamentándose exclusivamente en el contexto.
    - Evaluation: mide la fidelidad y precisión del sistema.
    """

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        query_analyzer: Optional[QueryAnalyzer] = None,
        filter_builder: Optional[MetadataFilterBuilder] = None,
        response_generator: Optional[ResponseGenerator] = None,
        vector_indexer: Optional[VectorIndexer] = None,
        embedder: Optional[EmbeddingService] = None,
    ):
        settings = get_settings()
        self.settings = settings
        self.embedder = embedder or EmbeddingService()
        self.vector_indexer = vector_indexer or VectorIndexer()
        self.retrieval_service = retrieval_service or RetrievalService(
            embedder=self.embedder,
            vector_indexer=self.vector_indexer,
            use_hybrid=False  # Priorizar recuperación densa con filtrado en Día 16
        )
        self.query_analyzer = query_analyzer or QueryAnalyzer()
        self.filter_builder = filter_builder or MetadataFilterBuilder()
        self.response_generator = response_generator

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
        filters: Optional[Dict[str, Any]] = None,
        apply_automatic_filters: bool = True
    ) -> Dict[str, Any]:
        """Ejecuta el flujo RAG con Metadata Filtering:

        Pregunta -> Query Analyzer -> Metadata Filter Builder -> Retrieval Service (ChromaDB) -> Top-K Chunks.
        """
        k = top_k or self.settings.TOP_K_RETRIEVAL
        route = self.route_query(user_query)

        # 1. Análisis de intención y extracción de entidades técnicas
        analysis = self.query_analyzer.analyze(user_query) if apply_automatic_filters else {}

        # 2. Construcción de filtros para ChromaDB
        built_filter = None
        if apply_automatic_filters and analysis:
            built_filter = self.filter_builder.build_from_analysis(analysis)

        # Priorizar filtros explícitos si fueron suministrados
        effective_filter = filters if filters is not None else built_filter

        # 3. Búsqueda vectorial con filtro de metadata en ChromaDB
        retrieved_chunks = self.retrieval_service.search(
            query=user_query,
            top_k=k,
            filters=effective_filter
        )

        return {
            "query": user_query,
            "route": route,
            "target_mcu": target_mcu,
            "analysis": analysis,
            "filters_applied": effective_filter,
            "chunks_retrieved": len(retrieved_chunks),
            "results": retrieved_chunks,
            "status": "Recuperación con Metadata Filtering completada exitosamente."
        }

    def execute_generation_workflow(
        self,
        user_query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Flujo completo de generación aumentada:

        Pregunta -> Query Analysis -> Filter Builder -> Retrieval -> Context Builder -> Gemini Response.
        """
        # 1. Recuperar chunks mediante el flujo filtrado
        retrieval_res = self.execute_workflow(user_query=user_query, top_k=top_k, filters=filters)
        chunks = retrieval_res["results"]

        # 2. Instanciar generador si no fue inyectado
        generator = self.response_generator or ResponseGenerator()

        # 3. Generar respuesta fundamentada con Gemini
        gen_output = generator.generate_response(question=user_query, chunks=chunks)

        return {
            **retrieval_res,
            "answer": gen_output.get("answer", ""),
            "sources": gen_output.get("sources", []),
            "prompt": gen_output.get("prompt", ""),
            "model": gen_output.get("model", ""),
            "temperature": gen_output.get("temperature", 0.95)
        }
