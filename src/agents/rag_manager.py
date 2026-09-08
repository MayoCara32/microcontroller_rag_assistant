"""Coordinador del sistema de recuperación RAG."""
from typing import Dict, Any, List


class RAGManagerAgent:
    """Decide qué documentos y estrategias de recuperación usar según la consulta."""

    def __init__(self):
        pass

    def determine_category(self, query: str) -> str:
        """Determina la categoría: Arduino, ESP32, Raspberry, Protocolos, Electrónica o Drivers."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")

    def fetch_verified_context(self, query: str, category: str) -> List[Dict[str, Any]]:
        """Recupera fragmentos relevantes aplicando filtros de metadatos estrictos."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")
