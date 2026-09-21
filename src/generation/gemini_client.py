"""Cliente de comunicación con la API de Google Gemini para generación de texto."""
import os
from typing import Optional, Any
from configs.settings import get_settings


class GeminiClient:
    """Encapsula la comunicación con la API de Gemini mediante el SDK google-genai."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        client: Optional[Any] = None
    ):
        settings = get_settings()
        self.settings = settings
        self.api_key = (
            api_key
            if api_key is not None
            else (settings.resolved_gemini_api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
        )
        self.model_name = (
            model_name
            if model_name is not None
            else (settings.resolved_llm_model or os.environ.get("GEMINI_MODEL") or os.environ.get("MODEL_NAME") or "gemini-2.0-flash")
        )
        self.temperature = (
            temperature
            if temperature is not None
            else settings.resolved_temperature
        )

        if client is not None:
            self.client = client
        else:
            self.client = self._init_client()

    def _init_client(self) -> Any:
        """Inicializa el cliente oficial google-genai."""
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY no configurada. Configure su API key en el archivo .env o en variables de entorno."
            )

        try:
            from google import genai
            return genai.Client(api_key=self.api_key)
        except Exception as e:
            raise RuntimeError(f"Error al inicializar cliente genai.Client: {str(e)}") from e

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Envía un prompt a Gemini y retorna el texto de la respuesta generada.

        Lanza excepciones explícitas si ocurre un error de red, autenticación o respuesta vacía.
        """
        if not prompt or not prompt.strip():
            raise ValueError("El prompt no puede estar vacío.")

        target_model = model or self.model_name
        target_temp = temperature if temperature is not None else self.temperature

        try:
            from google.genai import types
            config = types.GenerateContentConfig(temperature=target_temp)
            response = self.client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=config
            )
        except Exception as e:
            raise RuntimeError(
                f"Error al generar respuesta con Gemini (modelo '{target_model}'): {str(e)}"
            ) from e

        if not response or not hasattr(response, "text") or response.text is None:
            raise RuntimeError("La API de Gemini devolvió una respuesta vacía o sin contenido de texto.")

        return response.text.strip()
