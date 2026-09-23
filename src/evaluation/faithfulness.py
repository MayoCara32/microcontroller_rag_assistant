"""Evaluador de fidelidad (Faithfulness) de respuestas generadas contra contexto documental."""
import re
import json
from typing import List, Dict, Any, Optional, Union
from src.generation.gemini_client import GeminiClient
from src.generation.prompt_builder import PromptBuilder


class FaithfulnessEvaluator:
    """Evalúa si las afirmaciones presentes en la respuesta generada están respaldadas por el contexto recuperado.

    Utiliza Gemini como evaluador independiente para clasificar afirmaciones en:
    - SUPPORTED: Completamente respaldada por el contexto.
    - UNSUPPORTED: No presente en el contexto o inventada.
    - PARTIALLY_SUPPORTED: Parcialmente respaldada o ambigua.
    """

    NO_CONTEXT_FALLBACK = (
        "No encontré información suficiente en la documentación disponible para responder esta pregunta."
    )

    SYSTEM_PROMPT = (
        "Eres un evaluador riguroso de respuestas de sistemas Retrieval-Augmented Generation (RAG).\n"
        "Tu única tarea es comparar la respuesta generada contra el contexto proporcionado y verificar su fidelidad factual.\n"
        "REGLAS CRÍTICAS:\n"
        "1. NO respondas la pregunta bajo ninguna circunstancia.\n"
        "2. Evalúa únicamente si la respuesta generada se basa de forma estricta en el contexto proporcionado.\n"
        "3. Desglosa la respuesta generada en afirmaciones fácticas individuales.\n"
        "4. Clasifica cada afirmación en una de estas categorías:\n"
        "   - SUPPORTED: La afirmación está directamente respaldada por el contexto.\n"
        "   - UNSUPPORTED: La afirmación no aparece en el contexto o contradice el contexto.\n"
        "   - PARTIALLY_SUPPORTED: Solo una parte de la afirmación tiene respaldo explícito.\n"
        "5. Calcula el faithfulness_score de 0.0 a 1.0:\n"
        "   faithfulness_score = (número de SUPPORTED + 0.5 * número de PARTIALLY_SUPPORTED) / total_afirmaciones.\n"
        "   Si no hay afirmaciones técnicas evaluables o el sistema indicó honestamente que no hay información, el score es 1.0.\n"
        "6. Tu respuesta DEBE ser un objeto JSON válido sin texto adicional antes o después."
    )

    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        model: Optional[str] = None,
        temperature: float = 0.0
    ):
        self.gemini_client = gemini_client or GeminiClient(
            model_name=model,
            temperature=temperature
        )

    def _build_evaluation_prompt(self, question: str, context: str, answer: str) -> str:
        """Construye el prompt de evaluación en formato estricto."""
        return (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"PREGUNTA DEL USUARIO:\n{question.strip()}\n\n"
            f"CONTEXTO RECUPERADO:\n{context.strip() if context.strip() else '(Sin contexto documental)'}\n\n"
            f"RESPUESTA GENERADA A EVALUAR:\n{answer.strip()}\n\n"
            "FORMATO DE SALIDA REQUERIDO (JSON ÚNICAMENTE):\n"
            "{\n"
            '  "faithfulness_score": 0.85,\n'
            '  "supported_claims": [\n'
            '    "afirmación 1 respaldada"\n'
            "  ],\n"
            '  "unsupported_claims": [\n'
            '    "afirmación 2 no encontrada en el contexto"\n'
            "  ],\n"
            '  "partially_supported_claims": []\n'
            "}"
        )

    @staticmethod
    def _parse_json_response(raw_text: str) -> Dict[str, Any]:
        """Extrae y parsea de forma segura el bloque JSON devuelto por Gemini."""
        if not raw_text or not raw_text.strip():
            raise ValueError("Respuesta vacía del evaluador LLM.")

        # Intentar parseo directo
        cleaned = raw_text.strip()
        # Remover bloques de código markdown ```json ... ```
        if "```" in cleaned:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
            if match:
                cleaned = match.group(1).strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        # Búsqueda por delimitadores {}
        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            sub = cleaned[first_brace : last_brace + 1]
            try:
                parsed = json.loads(sub)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass

        raise ValueError(f"No fue posible parsear JSON en la respuesta del evaluador: {raw_text[:200]}")

    def evaluate(
        self,
        question: str,
        context: Union[str, List[Dict[str, Any]]],
        answer: str
    ) -> Dict[str, Any]:
        """Evalúa la fidelidad (faithfulness) de una respuesta generada contra su contexto.

        Parámetros:
            question: Pregunta original formulada.
            context: Texto con el contexto documental o lista de chunks recuperados.
            answer: Respuesta generada por el pipeline RAG.

        Retorna:
            Diccionario estructurado con:
                - metric: "faithfulness"
                - faithfulness_score: float entre 0.0 y 1.0
                - supported_claims: lista de afirmaciones respaldadas
                - unsupported_claims: lista de afirmaciones no respaldadas
                - partially_supported_claims: lista de afirmaciones parcialmente respaldadas
        """
        # Normalizar contexto a cadena
        if isinstance(context, list):
            context_str, _ = PromptBuilder.format_context_from_chunks(context)
        else:
            context_str = str(context or "").strip()

        clean_answer = str(answer or "").strip()

        # Caso determinista: Si el generador respondió con la frase de no contexto
        if not clean_answer or self.NO_CONTEXT_FALLBACK.lower() in clean_answer.lower():
            return {
                "metric": "faithfulness",
                "faithfulness_score": 1.0,
                "supported_claims": ["El sistema indicó honestamente ausencia de información."],
                "unsupported_claims": [],
                "partially_supported_claims": []
            }

        # Construir prompt y consultar a Gemini
        eval_prompt = self._build_evaluation_prompt(
            question=question,
            context=context_str,
            answer=clean_answer
        )

        import time
        max_retries = 4
        last_error = None

        for attempt in range(max_retries):
            try:
                raw_response = self.gemini_client.generate(prompt=eval_prompt)
                parsed = self._parse_json_response(raw_response)

                score = float(parsed.get("faithfulness_score", 0.0))
                score = max(0.0, min(1.0, round(score, 4)))

                supported = list(parsed.get("supported_claims", []))
                unsupported = list(parsed.get("unsupported_claims", []))
                partially = list(parsed.get("partially_supported_claims", []))

                return {
                    "metric": "faithfulness",
                    "faithfulness_score": score,
                    "supported_claims": supported,
                    "unsupported_claims": unsupported,
                    "partially_supported_claims": partially
                }
            except Exception as e:
                last_error = e
                err_str = str(e)
                if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str) and attempt < max_retries - 1:
                    # Espera mayor para reset de ventana de cuota por minuto
                    wait_time = 15.0 * (attempt + 1)
                    time.sleep(wait_time)
                    continue
                elif ("503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str) and attempt < max_retries - 1:
                    time.sleep(2.0 * (attempt + 1))
                    continue
                break

        return {
            "metric": "faithfulness",
            "faithfulness_score": 0.0,
            "supported_claims": [],
            "unsupported_claims": [f"Fallo en la evaluación de fidelidad: {str(last_error)}"],
            "partially_supported_claims": [],
            "error": str(last_error)
        }
