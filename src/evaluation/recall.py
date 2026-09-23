"""Evaluador de exhaustividad para la etapa de recuperación documental (Retrieval Recall)."""
from pathlib import Path
from typing import List, Dict, Any, Union


class RetrievalRecallEvaluator:
    """Calcula el recall del módulo de recuperación comparando documentos esperados contra recuperados.

    Recall = (Documentos esperados encontrados) / (Total de documentos esperados)
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
        """Calcula la métrica de exhaustividad (recall) de recuperación.

        Parámetros:
            retrieved_documents: Lista de nombres de archivos recuperados o diccionarios con metadata.
            expected_documents: Lista de nombres de archivos considerados relevantes por el dataset.

        Retorna:
            Diccionario estructurado con:
                - metric: "recall"
                - value: float entre 0.0 y 1.0
                - found_documents: lista de documentos esperados que sí fueron recuperados
                - missing_documents: lista de documentos esperados que no fueron recuperados
        """
        if not expected_documents:
            return {
                "metric": "recall",
                "value": 0.0,
                "found_documents": [],
                "missing_documents": []
            }

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

        retrieved_normalized = {
            self._normalize_name(d): d for d in extracted_retrieved if d
        }

        found_docs: List[str] = []
        missing_docs: List[str] = []

        for exp in expected_documents:
            norm = self._normalize_name(exp)
            if norm in retrieved_normalized:
                found_docs.append(exp)
            else:
                missing_docs.append(exp)

        total_expected = len(expected_documents)
        recall_value = round(len(found_docs) / total_expected, 4) if total_expected > 0 else 0.0

        return {
            "metric": "recall",
            "value": recall_value,
            "found_documents": found_docs,
            "missing_documents": missing_docs
        }
