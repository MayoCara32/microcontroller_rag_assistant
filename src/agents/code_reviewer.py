"""Especialista en revisión y corrección de firmware embebido."""
from typing import Dict, Any, List


class EmbeddedCodeReviewerAgent:
    """Evalúa errores lógicos, bloqueos por delays, uso de memoria y problemas de timers/ISR."""

    def __init__(self):
        pass

    def review_code(
        self,
        code_snippet: str,
        target_mcu: str,
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Sigue el flujo: explica problema -> causa -> propone solución -> fragmento corregido."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")
