"""Coordinador de generación de respuestas técnicas basadas en contexto documental."""
from typing import Dict, Any, List, Optional, Union, Tuple
from configs.settings import get_settings
from src.generation.gemini_client import GeminiClient
from src.generation.prompt_builder import PromptBuilder


class ResponseGenerator:
    """Coordina la construcción del prompt RAG y la invocación al cliente Gemini."""

    NO_CONTEXT_FALLBACK = (
        "No encontré información suficiente en la documentación disponible para responder esta pregunta."
    )

    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        prompt_builder: Optional[PromptBuilder] = None
    ):
        self.settings = get_settings()
        self.client = gemini_client or GeminiClient()
        self.prompt_builder = prompt_builder or PromptBuilder()

    def generate_response(
        self,
        question: str,
        context: Optional[Union[str, List[Dict[str, Any]]]] = None,
        chunks: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """Genera una respuesta fundamentada utilizando el contexto documental provisto.

        Parámetros:
            question: Pregunta técnica formulada por el usuario.
            context: Cadena de texto con el contexto o lista de chunks recuperados.
            chunks: Lista opcional de fragmentos recuperados desde ChromaDB.
            model: Nombre opcional del modelo LLM a utilizar.
            temperature: Temperatura opcional para la generación.

        Retorna un diccionario con:
            - text / answer: Respuesta textual generada.
            - sources: Lista de fuentes documentales identificadas.
            - prompt: Prompt completo enviado a Gemini (para depuración/auditoría).
            - model: Modelo utilizado para la inferencia.
            - temperature: Temperatura utilizada.
        """
        if not question or not question.strip():
            raise ValueError("La pregunta no puede estar vacía.")

        # 1. Normalizar contexto y fuentes
        context_str = ""
        sources: List[str] = []

        if chunks is not None:
            context_str, sources = self.prompt_builder.format_context_from_chunks(chunks)
        elif isinstance(context, list):
            context_str, sources = self.prompt_builder.format_context_from_chunks(context)
        elif isinstance(context, str):
            context_str = context.strip()
            if context_str:
                sources = ["Documentación proporcionada"]

        # 2. Si no existe contexto suficiente, responder con corte determinista
        target_model = model or self.client.model_name
        target_temp = temperature if temperature is not None else self.client.temperature

        if not context_str:
            return {
                "answer": self.NO_CONTEXT_FALLBACK,
                "text": self.NO_CONTEXT_FALLBACK,
                "sources": [],
                "prompt": "",
                "model": target_model,
                "temperature": target_temp
            }

        # 3. Construir prompt RAG
        prompt = self.prompt_builder.build_prompt(question=question, context=context_str)

        # 4. Enviar a Gemini (manejo explícito de excepciones)
        try:
            generated_text = self.client.generate(
                prompt=prompt,
                model=target_model,
                temperature=target_temp
            )
        except Exception as e:
            # Nunca ocultar errores
            raise RuntimeError(f"Falla en la generación de respuesta con Gemini: {str(e)}") from e

        return {
            "answer": generated_text,
            "text": generated_text,
            "sources": sources,
            "prompt": prompt,
            "context": context_str,
            "model": target_model,
            "temperature": target_temp
        }
