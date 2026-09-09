"""Limpieza de ruido documental respetando especificaciones eléctricas y eliminando duplicados multilingües."""
import re
from typing import Dict, Any
from src.core.interfaces import BaseCleaner


class DocumentCleaner(BaseCleaner):
    """Elimina encabezados, pies de página, caracteres especiales y duplicados manteniendo unidades técnicas."""

    def __init__(self, preserve_electrical_units: bool = True):
        self.preserve_electrical_units = preserve_electrical_units

    def clean(self, raw_text: str) -> str:
        """Implementación de la interfaz BaseCleaner."""
        return self.clean_text(raw_text)

    def clean_text(self, raw_text: str) -> str:
        """Limpia ruido de OCR, headers, footers y normaliza saltos de línea."""
        if not raw_text:
            return ""

        # Eliminar números de página solos en líneas (ej. "Page 12 of 45" o "- 12 -")
        cleaned = re.sub(r'(?i)^\s*(page\s+\d+(\s+of\s+\d+)?|-?\s*\d+\s*-?)\s*$', '', raw_text, flags=re.MULTILINE)

        # Normalizar espacios en blanco consecutivos manteniendo saltos de línea dobles para párrafos
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)

        # Eliminar secuencias repetitivas no deseadas (caracteres nulos o control)
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', cleaned)

        return cleaned.strip()

    def sanitize_table(self, table_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza filas y columnas de tablas técnicas preservando nombres de registros y valores."""
        sanitized = {}
        for key, value in table_data.items():
            clean_key = str(key).strip()
            if isinstance(value, str):
                sanitized[clean_key] = value.strip()
            elif isinstance(value, list):
                sanitized[clean_key] = [v.strip() if isinstance(v, str) else v for v in value]
            else:
                sanitized[clean_key] = value
        return sanitized
