"""Extracción y enriquecimiento de metadatos de microcontroladores y periféricos."""
from typing import Dict, Any


class MetadataExtractor:
    """Extrae metadatos jerárquicos (fabricante, familia, modelo, periféricos, interfaces)."""

    def extract_metadata(self, document_content: str, filename: str) -> Dict[str, Any]:
        """Genera el esquema de metadatos RAG estándar para sistemas embebidos."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")

    def identify_interfaces(self, text: str) -> list[str]:
        """Detecta protocolos e interfaces presentes (I2C, SPI, UART, CAN, ADC, PWM)."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")
