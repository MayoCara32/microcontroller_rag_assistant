"""Evaluador de precisión para la etapa de recuperación documental (Retrieval Precision)."""
from pathlib import Path
from typing import List, Dict, Any, Union


class RetrievalPrecisionEvaluator:
    """Calcula la precisión del módulo de recuperación comparando documentos recuperados contra esperados.

    Precision = (Documentos relevantes recuperados) / (Total de documentos recuperados)
    """

    @staticmethod
    def _normalize_name(doc_name: str) -> str:
        """Normaliza el nombre de archivo a minúsculas y sin ruta para comparación confiable."""
        if not doc_name:
            return ""
        return Path(doc_name.strip()).name.lower()

    def evaluate(
        self,
        retrieved_documents: List[Union[str, Dict[str, Any]]],
        expected_documents: List[str]
    ) -> Dict[str, Any]:
        """Calcula la métrica de precisión de recuperación.

        Parámetros:
            retrieved_documents: Lista de nombres de archivos recuperados o diccionarios con metadata.
            expected_documents: Lista de nombres de archivos considerados relevantes por el dataset.

        Retorna:
            Diccionario estructurado con:
                - metric: "precision"
                - value: float entre 0.0 y 1.0
                - relevant_documents: lista de documentos recuperados que eran esperados
                - irrelevant_documents: lista de documentos recuperados que no eran esperados
        """
        # Extraer nombres si vienen como diccionarios de chunks o metadatas
        extracted_retrieved: List[str] = []
        for item in retrieved_documents:
            if isinstance(item, str):
                name = item.strip()
            elif isinstance(item, dict):
                meta = item.get("metadata", item)
                name = (
                    meta.get("file_name")
                    or meta.get("document")
                    or meta.get("source")
                    or item.get("file_name", "")
                )
            else:
                name = str(item)
            if name and name not in extracted_retrieved:
                extracted_retrieved.append(name)

        if not extracted_retrieved:
            return {
                "metric": "precision",
                "value": 0.0,
                "relevant_documents": [],
                "irrelevant_documents": []
            }

        # Conjunto de esperados normalizados
        expected_normalized = {
            self._normalize_name(d): d for d in expected_documents if d
        }

        relevant_docs: List[str] = []
        irrelevant_docs: List[str] = []

        for doc in extracted_retrieved:
            norm = self._normalize_name(doc)
            if norm in expected_normalized:
                relevant_docs.append(doc)
            else:
                irrelevant_docs.append(doc)

        total_retrieved = len(extracted_retrieved)
        precision_value = round(len(relevant_docs) / total_retrieved, 4) if total_retrieved > 0 else 0.0

        return {
            "metric": "precision",
            "value": precision_value,
            "relevant_documents": relevant_docs,
            "irrelevant_documents": irrelevant_docs
        }
