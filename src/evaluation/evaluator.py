"""Orquestador central de evaluación RAG (Precision, Recall, Faithfulness)."""
from typing import List, Dict, Any, Optional, Union
from src.evaluation.precision import RetrievalPrecisionEvaluator
from src.evaluation.recall import RetrievalRecallEvaluator
from src.evaluation.faithfulness import FaithfulnessEvaluator


class RAGEvaluator:
    """Coordina la evaluación completa de un ciclo RAG: recuperación documental y fidelidad de la respuesta generada."""

    def __init__(
        self,
        precision_evaluator: Optional[RetrievalPrecisionEvaluator] = None,
        recall_evaluator: Optional[RetrievalRecallEvaluator] = None,
        faithfulness_evaluator: Optional[FaithfulnessEvaluator] = None
    ):
        self.precision_evaluator = precision_evaluator or RetrievalPrecisionEvaluator()
        self.recall_evaluator = recall_evaluator or RetrievalRecallEvaluator()
        self.faithfulness_evaluator = faithfulness_evaluator or FaithfulnessEvaluator()

    def evaluate(
        self,
        question: Optional[str] = None,
        expected_documents: Optional[List[str]] = None,
        retrieved_documents: Optional[List[Union[str, Dict[str, Any]]]] = None,
        context: Optional[Union[str, List[Dict[str, Any]]]] = None,
        answer: Optional[str] = None,
        skip_faithfulness: bool = False,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Ejecuta la evaluación integral de un ciclo RAG.

        Parámetros:
            question: Pregunta original formulada.
            expected_documents: Lista de documentos relevantes esperados para la pregunta.
            retrieved_documents: Lista de documentos recuperados (nombres o chunks con metadata).
            context: Contexto textual o chunks enviados al generador.
            answer: Respuesta generada por el LLM.
            skip_faithfulness: Si es True, omite la llamada a Gemini para evaluar faithfulness (útil para pruebas offline).

        Retorna:
            Diccionario estructurado con:
                - precision: resultado de RetrievalPrecisionEvaluator
                - recall: resultado de RetrievalRecallEvaluator
                - faithfulness: resultado de FaithfulnessEvaluator
        """
        # Soporte para paso de diccionario único o kwargs
        q = question or kwargs.get("query", "")
        exp_docs = expected_documents if expected_documents is not None else kwargs.get("expected_docs", [])
        ret_docs = retrieved_documents if retrieved_documents is not None else kwargs.get("retrieved_docs", [])
        ctx = context if context is not None else kwargs.get("chunks", "")
        ans = answer if answer is not None else kwargs.get("generated_answer", "")

        # 1. Retrieval Precision
        precision_result = self.precision_evaluator.evaluate(
            retrieved_documents=ret_docs,
            expected_documents=exp_docs
        )

        # 2. Retrieval Recall
        recall_result = self.recall_evaluator.evaluate(
            retrieved_documents=ret_docs,
            expected_documents=exp_docs
        )

        # 3. Faithfulness
        if skip_faithfulness:
            faithfulness_result = {
                "metric": "faithfulness",
                "faithfulness_score": 0.0,
                "supported_claims": [],
                "unsupported_claims": [],
                "skipped": True
            }
        else:
            faithfulness_result = self.faithfulness_evaluator.evaluate(
                question=q,
                context=ctx,
                answer=ans
            )

        return {
            "precision": precision_result,
            "recall": recall_result,
            "faithfulness": faithfulness_result
        }
