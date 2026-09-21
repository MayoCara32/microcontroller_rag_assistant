"""Constructor de prompts para el sistema RAG de microcontroladores."""
from typing import List, Dict, Any, Tuple, Optional


class PromptBuilder:
    """Construye prompts estructurados para Gemini con contexto técnico y reglas estrictas."""

    SYSTEM_INSTRUCTION = "Eres un asistente experto en microcontroladores y sistemas embebidos."

    RULES = (
        "- Responde únicamente utilizando el contexto proporcionado.\n"
        "- No inventes información.\n"
        "- Si la información no aparece en el contexto, indícalo explícitamente.\n"
        "- Mantén precisión técnica."
    )

    INSTRUCTIONS = (
        "Genera una respuesta clara.\n"
        "Incluye las fuentes utilizadas al final bajo la sección 'Fuentes:'."
    )

    @classmethod
    def format_context_from_chunks(cls, chunks: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
        """Convierte una lista de chunks recuperados en una cadena de contexto y lista de fuentes únicas."""
        if not chunks:
            return "", []

        context_blocks = []
        sources = []

        for index, chunk in enumerate(chunks, start=1):
            metadata = chunk.get("metadata", {})
            doc = (
                metadata.get("file_name")
                or metadata.get("document")
                or metadata.get("source")
                or metadata.get("title")
                or f"Documento_{index}"
            )
            text = chunk.get("texto") or chunk.get("text", "").strip()
            category = metadata.get("category") or metadata.get("familia") or metadata.get("component") or "General"

            if doc not in sources:
                sources.append(doc)

            context_blocks.append(
                f"--- Documento [{index}]: {doc} (Categoría: {category}) ---\n{text}"
            )

        context_str = "\n\n".join(context_blocks)
        return context_str, sources

    @classmethod
    def build_prompt(cls, question: str, context: str) -> str:
        """Construye el prompt completo para Gemini según la estructura requerida."""
        clean_question = question.strip() if question else ""
        clean_context = context.strip() if context else "No se proporcionó contexto."

        prompt = (
            f"SYSTEM:\n"
            f"{cls.SYSTEM_INSTRUCTION}\n\n"
            f"REGLAS:\n"
            f"{cls.RULES}\n\n"
            f"CONTEXTO:\n"
            f"{clean_context}\n\n"
            f"PREGUNTA:\n"
            f"{clean_question}\n\n"
            f"INSTRUCCIONES:\n"
            f"{cls.INSTRUCTIONS}"
        )
        return prompt
