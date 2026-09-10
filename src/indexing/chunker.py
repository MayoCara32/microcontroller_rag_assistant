"""Fragmentador semántico adaptado a documentación de hardware."""
import re
from typing import List, Dict, Any, Optional
from src.core.interfaces import BaseChunker


class SemanticHardwareChunker(BaseChunker):
    """Divide documentos técnicos preservando la integridad de tablas y secciones operativas."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Implementación de la interfaz BaseChunker."""
        doc_data = {"text": text, "file_name": metadata.get("file_name", "doc") if metadata else "doc"}
        if metadata:
            doc_data.update(metadata)
        return self.split_document(doc_data)

    def split_document(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera chunks optimizados con contexto autocontenido y metadatos."""
        content = document_data.get("text", "")
        file_name = document_data.get("file_name", "unknown")
        category = document_data.get("category", "Microcontrollers")
        component = document_data.get("component", file_name)

        sections = self._split_by_tables_and_sections(content)
        chunks = []
        chunk_id = 0

        header_context = f"[Componente: {component} | Categoría: {category}]\n"

        for sec in sections:
            sec_text = sec.strip()
            if not sec_text:
                continue

            # Preservar tablas Markdown completas si se ajustan a un margen técnico razonable
            is_table = "|---" in sec_text or "| ---" in sec_text
            max_limit = int(self.chunk_size * 1.5) if is_table else self.chunk_size

            if len(sec_text) <= max_limit:
                chunks.append({
                    "chunk_id": f"{file_name}_{chunk_id}",
                    "text": header_context + sec_text,
                    "raw_text": sec_text,
                    "file_name": file_name,
                    "category": category,
                    "component": component
                })
                chunk_id += 1
            else:
                # Sliding window split para secciones extensas
                start = 0
                while start < len(sec_text):
                    end = start + self.chunk_size
                    piece = sec_text[start:end]

                    # Ajustar al último salto de línea o espacio
                    if end < len(sec_text):
                        last_space = piece.rfind("\n")
                        if last_space == -1:
                            last_space = piece.rfind(" ")
                        if last_space > self.chunk_size // 2:
                            end = start + last_space + 1
                            piece = sec_text[start:end]

                    chunks.append({
                        "chunk_id": f"{file_name}_{chunk_id}",
                        "text": header_context + piece.strip(),
                        "raw_text": piece.strip(),
                        "file_name": file_name,
                        "category": category,
                        "component": component
                    })
                    chunk_id += 1
                    start += (self.chunk_size - self.chunk_overlap)

        return chunks

    def _split_by_tables_and_sections(self, content: str) -> List[str]:
        """Aísla tablas y encabezados Markdown (#, ##, ###) para evitar su fragmentación abrupta."""
        # Dividir por encabezados de Markdown o divisores de página
        pattern = r'(?=\n#{1,4}\s+|\n---\s+Página\s+\d+)'
        raw_sections = [s.strip() for s in re.split(pattern, content) if s.strip()]

        # Unir encabezados huérfanos sin cuerpo con la siguiente sección
        sections = []
        i = 0
        while i < len(raw_sections):
            curr = raw_sections[i]
            lines = [l.strip() for l in curr.splitlines() if l.strip()]
            if len(lines) == 1 and lines[0].startswith("#") and i + 1 < len(raw_sections):
                sections.append(curr + "\n\n" + raw_sections[i + 1])
                i += 2
            else:
                sections.append(curr)
                i += 1

        return sections
