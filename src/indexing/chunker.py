"""Fragmentador semántico adaptado a documentación de hardware y hojas de datos técnicas."""
import re
from typing import List, Dict, Any, Optional
from src.core.interfaces import BaseChunker


class SemanticHardwareChunker(BaseChunker):
    """Divide documentos técnicos preservando la integridad de tablas, secciones y overlap continuo."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap debe ser estrictamente menor que chunk_size.")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Implementación de la interfaz BaseChunker."""
        doc_data = {"text": text, "file_name": metadata.get("file_name", "doc") if metadata else "doc"}
        if metadata:
            doc_data.update(metadata)
        return self.split_document(doc_data)

    def split_document(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera chunks con contexto de cabecera, metadatos enriquecidos y overlap verificable."""
        content = document_data.get("text", "")
        if not content or not content.strip():
            return []

        file_name = document_data.get("file_name", "unknown")
        category = document_data.get("category", "Microcontrollers")
        component = document_data.get("component", file_name)

        # Extraer metadatos adicionales preservando trazabilidad
        extra_meta = {
            k: v for k, v in document_data.items()
            if k not in ["text", "raw_text", "file_name", "category", "component"]
        }

        sections = self._split_by_tables_and_sections(content)
        chunks = []
        chunk_id = 0

        header_context = f"[Componente: {component} | Categoría: {category}]\n"

        for sec in sections:
            sec_text = sec.strip()
            if not sec_text:
                continue

            # Preservar tablas Markdown completas si se ajustan a un margen técnico razonable (1.5x)
            is_table = "|---" in sec_text or "| ---" in sec_text
            max_limit = int(self.chunk_size * 1.5) if is_table else self.chunk_size

            if len(sec_text) <= max_limit:
                chunks.append({
                    "chunk_id": f"{file_name}_{chunk_id}",
                    "text": header_context + sec_text,
                    "raw_text": sec_text,
                    "file_name": file_name,
                    "category": category,
                    "component": component,
                    **extra_meta
                })
                chunk_id += 1
            else:
                # Ventana deslizante con ajuste a límites de palabras y overlap verificable
                start = 0
                sec_len = len(sec_text)
                while start < sec_len:
                    end = min(start + self.chunk_size, sec_len)

                    # Si no es el final de la sección, ajustar al último salto de línea o espacio
                    if end < sec_len:
                        half_point = start + (self.chunk_size // 2)
                        boundary = sec_text.rfind("\n", half_point, end)
                        if boundary == -1:
                            boundary = sec_text.rfind(" ", half_point, end)
                        if boundary != -1 and boundary > start:
                            end = boundary + 1

                    piece = sec_text[start:end].strip()
                    if piece:
                        chunks.append({
                            "chunk_id": f"{file_name}_{chunk_id}",
                            "text": header_context + piece,
                            "raw_text": piece,
                            "file_name": file_name,
                            "category": category,
                            "component": component,
                            **extra_meta
                        })
                        chunk_id += 1

                    if end >= sec_len:
                        break

                    # Calcular siguiente inicio a partir del final real menos el overlap
                    next_start = end - self.chunk_overlap

                    # Ajustar next_start al siguiente espacio para no cortar palabras al inicio
                    if start < next_start < end:
                        space_pos = sec_text.find(" ", next_start, end)
                        if space_pos != -1:
                            next_start = space_pos + 1

                    # Garantizar avance hacia adelante para prevenir bucles infinitos
                    if next_start <= start:
                        next_start = end

                    start = next_start

        return chunks

    def _split_by_tables_and_sections(self, content: str) -> List[str]:
        """Aísla tablas y encabezados Markdown (#, ##, ###) para evitar su fragmentación abrupta."""
        pattern = r'(?=\n#{1,4}\s+|\n---\s+Página\s+\d+)'
        raw_sections = [s.strip() for s in re.split(pattern, content) if s.strip()]

        sections = []
        i = 0
        while i < len(raw_sections):
            curr = raw_sections[i]
            lines = [l.strip() for l in curr.splitlines() if l.strip()]
            # Unir encabezados huérfanos sin cuerpo con la siguiente sección
            if len(lines) == 1 and lines[0].startswith("#") and i + 1 < len(raw_sections):
                sections.append(curr + "\n\n" + raw_sections[i + 1])
                i += 2
            else:
                sections.append(curr)
                i += 1

        return sections
