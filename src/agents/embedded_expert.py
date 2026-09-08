"""Especialista en hardware, microcontroladores, electrónica y periféricos."""
from typing import Dict, Any, List


class EmbeddedExpertAgent:
    """Explica conceptos técnicos, conexionados y características eléctricas basándose en fuentes."""

    def __init__(self):
        pass

    def answer_hardware_query(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Genera explicación, ejemplo de conexión, consideraciones técnicas y fuentes."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")

    def generate_pinout_diagram(self, mcu: str, peripheral: str) -> str:
        """Genera diagrama textual/ASCII o tabla pin-a-pin con asignaciones exactas."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")
