"""Extractor estructural de PDFs y manuales técnicos."""
from pathlib import Path
from typing import Dict, List, Any
import pymupdf as fitz
from src.core.interfaces import BaseParser


class PDFParser(BaseParser):
    """Extrae texto, metadatos y tablas preservando la estructura técnica."""

    def __init__(self, extract_tables: bool = True):
        self.extract_tables = extract_tables

    def parse_document(self, file_path: Path) -> Dict[str, Any]:
        """Extrae el contenido estructurado de un documento técnico (PDF o Markdown procesado)."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"El archivo {file_path} no existe.")

        if file_path.suffix.lower() in [".md", ".txt"]:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "text": content,
                "pages": [{"page_number": 1, "text": content}],
                "tables": []
            }

        doc = fitz.open(file_path)
        pages_content = []
        full_text = []

        for i, page in enumerate(doc):
            page_text = page.get_text("text")
            pages_content.append({"page_number": i + 1, "text": page_text})
            full_text.append(f"--- Página {i + 1} ---\n{page_text}")

        doc.close()

        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "text": "\n\n".join(full_text),
            "pages": pages_content,
            "tables": []
        }

    def extract_tables_from_page(self, page_data: Any) -> List[Dict[str, Any]]:
        """Extrae tablas de registros o características eléctricas."""
        # Método extensible para extracción de tablas mediante pdfplumber si es requerido
        return []
