"""Extracción y enriquecimiento de metadatos de microcontroladores y periféricos."""
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional


class MetadataExtractor:
    """Extrae metadatos jerárquicos (fabricante, familia, modelo, periféricos, interfaces)."""

    COMMON_INTERFACES = ["I2C", "SPI", "UART", "USART", "CAN", "ADC", "DAC", "PWM", "GPIO", "USB", "I2S"]

    def extract_metadata(self, document_content: str, filename: str, metadata_file_path: Optional[Path] = None) -> Dict[str, Any]:
        """Genera el esquema de metadatos RAG estándar cargando JSON existente o infiriendo datos."""
        if metadata_file_path and metadata_file_path.exists():
            try:
                with open(metadata_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # Inferencia básica por palabras clave
        category = "General Embebidos"
        if re.search(r'\barduino\b', filename + " " + document_content[:1000], re.IGNORECASE):
            category = "Arduino"
        elif re.search(r'\besp32\b|\besp8266\b', filename + " " + document_content[:1000], re.IGNORECASE):
            category = "ESP32"
        elif re.search(r'\braspberry\s+pi\s+pico\b|\brp2040\b|\brp2350\b', filename + " " + document_content[:1000], re.IGNORECASE):
            category = "Raspberry Pi Pico"

        interfaces = self.identify_interfaces(document_content)

        return {
            "file_name": filename,
            "category": category,
            "interfaces": interfaces,
            "keywords": [category] + interfaces
        }

    def identify_interfaces(self, text: str) -> List[str]:
        """Detecta protocolos e interfaces presentes (I2C, SPI, UART, CAN, ADC, PWM)."""
        found = []
        for iface in self.COMMON_INTERFACES:
            pattern = r'\b' + re.escape(iface) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found.append(iface)
        return found
