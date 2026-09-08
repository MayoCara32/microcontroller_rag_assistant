"""Extractor estructural de PDFs y manuales técnicos."""
from pathlib import Path
from typing import Dict, List, Any


class PDFParser:
    """Extrae texto, metadatos y tablas preservando la estructura técnica."""

    def __init__(self, extract_tables: bool = True):
        self.extract_tables = extract_tables

    def parse_document(self, file_path: Path) -> Dict[str, Any]:
        """Extrae el contenido estructurado de un documento técnico."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")

    def extract_tables_from_page(self, page_data: Any) -> List[Dict[str, Any]]:
        """Extrae tablas de registros o características eléctricas."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")
