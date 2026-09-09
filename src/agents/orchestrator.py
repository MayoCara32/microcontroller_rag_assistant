"""Coordinador principal del sistema Microcontrollers AI Copilot."""
from typing import Dict, Any, List, Optional
from src.retrieval.hybrid_search import HybridSearchEngine
from src.retrieval.reranker import CrossEncoderReranker
from src.agents.embedded_expert import EmbeddedExpertAgent
from src.agents.code_reviewer import EmbeddedCodeReviewerAgent
from src.validation.safety_guardrails import ElectricalSafetyGuardrails
from src.validation.citation_validator import CitationSourceValidator


class RAGOrchestrator:
    """Orquestador central: clasifica consultas, coordina agentes y consolida respuestas con citas."""

    def __init__(
        self,
        retriever: Optional[HybridSearchEngine] = None,
        reranker: Optional[CrossEncoderReranker] = None,
        hardware_expert: Optional[EmbeddedExpertAgent] = None,
        code_reviewer: Optional[EmbeddedCodeReviewerAgent] = None,
        guardrails: Optional[ElectricalSafetyGuardrails] = None,
        citation_validator: Optional[CitationSourceValidator] = None
    ):
        self.retriever = retriever or HybridSearchEngine()
        self.reranker = reranker or CrossEncoderReranker()
        self.hardware_expert = hardware_expert or EmbeddedExpertAgent()
        self.code_reviewer = code_reviewer or EmbeddedCodeReviewerAgent()
        self.guardrails = guardrails or ElectricalSafetyGuardrails()
        self.citation_validator = citation_validator or CitationSourceValidator()

    def route_query(self, user_query: str) -> str:
        """Clasifica la consulta del usuario para determinar la ruta de ejecución."""
        query_lower = user_query.lower()
        if any(w in query_lower for w in ["código", "code", "void loop", "setup()", "sketch", "firmware", "función"]):
            return "code_review"
        return "hardware_query"

    def execute_workflow(self, user_query: str, target_mcu: str = "Arduino", code_snippet: Optional[str] = None) -> Dict[str, Any]:
        """Ejecuta el flujo completo: análisis -> recuperación -> delegación a agentes -> guardrails -> citas."""
        route = self.route_query(user_query)

        # 1. Recuperación Híbrida y Reranking
        raw_chunks = self.retriever.retrieve(user_query, top_k=10)
        reranked_chunks = self.reranker.rerank(user_query, raw_chunks, top_n=5)

        # 2. Delegación a Agentes Especializados
        if route == "code_review" and code_snippet:
            agent_result = self.code_reviewer.review_code(code_snippet, target_mcu, reranked_chunks)
            base_response = agent_result.get("report", "")
        else:
            agent_result = self.hardware_expert.answer_hardware_query(user_query, reranked_chunks)
            base_response = agent_result.get("answer", "")

        # 3. Auditoría de Seguridad Eléctrica
        safety_warnings = self.guardrails.audit_hardware_plan(user_query + " " + base_response)
        if safety_warnings:
            base_response += "\n\n⚠️ **ALERTAS DE SEGURIDAD ELÉCTRICA DETECTADAS:**\n" + "\n".join([f"- {w}" for w in safety_warnings])

        # 4. Validar Citas y Referencias
        citation_result = self.citation_validator.validate_citations(base_response, reranked_chunks)
        final_response = citation_result.get("validated_response", base_response)

        return {
            "query": user_query,
            "route": route,
            "response": final_response,
            "chunks_retrieved": len(reranked_chunks),
            "safety_warnings": safety_warnings,
            "sources": citation_result.get("sources", [])
        }
