"""Pruebas unitarias para el módulo de generación con Gemini (Día 13 / Modo Chat)."""
import pytest
from unittest.mock import MagicMock, patch
from configs.settings import Settings
from src.generation.gemini_client import GeminiClient
from src.generation.prompt_builder import PromptBuilder
from src.generation.response_generator import ResponseGenerator


def test_api_key_loading_from_settings():
    """Valida que la clave de API se resuelva desde GEMINI_API_KEY o GOOGLE_API_KEY."""
    s1 = Settings(GEMINI_API_KEY="test-gemini-key", _env_file=None)
    assert s1.resolved_gemini_api_key == "test-gemini-key"

    s2 = Settings(GEMINI_API_KEY=None, GOOGLE_API_KEY="test-google-key", _env_file=None)
    assert s2.resolved_gemini_api_key == "test-google-key"

    s3 = Settings(GEMINI_MODEL="gemini-2.0-flash-exp", _env_file=None)
    assert s3.resolved_llm_model == "gemini-2.0-flash-exp"


def test_gemini_client_missing_api_key_raises_error():
    """Valida que GeminiClient lance ValueError explícito si no hay API key configurada."""
    with patch("src.generation.gemini_client.get_settings") as mock_settings:
        mock_settings.return_value = Settings(GEMINI_API_KEY=None, GOOGLE_API_KEY=None)
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY no configurada"):
                GeminiClient(api_key=None)


def test_gemini_client_generate_success():
    """Valida la llamada a generate_content mediante el cliente mockeado."""
    mock_genai_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "El microcontrolador ATmega328P opera entre 1.8V y 5.5V."
    mock_genai_client.models.generate_content.return_value = mock_response

    client = GeminiClient(api_key="fake-key-12345", client=mock_genai_client)
    result = client.generate("¿Cuál es el voltaje del ATmega328P?")

    assert result == "El microcontrolador ATmega328P opera entre 1.8V y 5.5V."
    mock_genai_client.models.generate_content.assert_called_once()


def test_gemini_client_handles_api_error():
    """Valida que GeminiClient propague RuntimeError sin ocultar errores de API."""
    mock_genai_client = MagicMock()
    mock_genai_client.models.generate_content.side_effect = Exception("Rate limit exceeded 429")

    client = GeminiClient(api_key="fake-key-12345", client=mock_genai_client)
    with pytest.raises(RuntimeError, match="Rate limit exceeded 429"):
        client.generate("Consulta de prueba")


def test_gemini_client_empty_response():
    """Valida que GeminiClient detecte respuestas nulas o vacías de la API."""
    mock_genai_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = None
    mock_genai_client.models.generate_content.return_value = mock_response

    client = GeminiClient(api_key="fake-key-12345", client=mock_genai_client)
    with pytest.raises(RuntimeError, match="respuesta vacía"):
        client.generate("Consulta de prueba")


def test_prompt_builder_format_chunks():
    """Valida la extracción de fuentes y estructuración de contexto documental."""
    chunks = [
        {
            "chunk_id": "esp32_c1",
            "texto": "El ESP32 integra dos convertidores SAR ADC de 12 bits.",
            "metadata": {"file_name": "ESP32_Datasheet.pdf", "category": "ESP32"}
        },
        {
            "chunk_id": "esp32_c2",
            "texto": "ADC2 no debe usarse mientras el módulo Wi-Fi esté activo.",
            "metadata": {"file_name": "ESP32_TRM.pdf", "category": "ESP32"}
        },
        {
            "chunk_id": "esp32_c3",
            "texto": "Los canales ADC1 están en GPIO32 a GPIO39.",
            "metadata": {"file_name": "ESP32_Datasheet.pdf", "category": "ESP32"}
        }
    ]

    context, sources = PromptBuilder.format_context_from_chunks(chunks)

    assert "ESP32_Datasheet.pdf" in sources
    assert "ESP32_TRM.pdf" in sources
    assert len(sources) == 2  # Debe deduplicar
    assert "El ESP32 integra dos convertidores SAR ADC" in context
    assert "ADC2 no debe usarse mientras el módulo Wi-Fi esté activo" in context


def test_prompt_builder_structure():
    """Valida que el prompt incluya SYSTEM, REGLAS, CONTEXTO, PREGUNTA e INSTRUCCIONES."""
    prompt = PromptBuilder.build_prompt(
        question="¿Cómo configuro el pin D13 como salida?",
        context="pinMode(13, OUTPUT) configura el pin D13 como salida digital."
    )

    assert "SYSTEM:" in prompt
    assert "Eres un asistente experto en microcontroladores" in prompt
    assert "REGLAS:" in prompt
    assert "Responde únicamente utilizando el contexto proporcionado" in prompt
    assert "CONTEXTO:" in prompt
    assert "pinMode(13, OUTPUT)" in prompt
    assert "PREGUNTA:" in prompt
    assert "¿Cómo configuro el pin D13 como salida?" in prompt
    assert "INSTRUCCIONES:" in prompt
    assert "Incluye las fuentes utilizadas" in prompt


def test_response_generator_without_context():
    """Valida que ante ausencia de contexto, ResponseGenerator corte sin llamar al LLM."""
    mock_client = MagicMock()
    generator = ResponseGenerator(gemini_client=mock_client)

    result = generator.generate_response(question="¿Cuál es la frecuencia del ESP32?", chunks=[])

    assert result["answer"] == ResponseGenerator.NO_CONTEXT_FALLBACK
    assert result["sources"] == []
    mock_client.generate.assert_not_called()


def test_response_generator_success():
    """Valida el flujo normal de ResponseGenerator con chunks válidos."""
    mock_client = MagicMock()
    mock_client.model_name = "gemini-2.0-flash"
    mock_client.generate.return_value = "El ESP32 opera a un reloj de hasta 240 MHz."

    generator = ResponseGenerator(gemini_client=mock_client)
    chunks = [
        {
            "chunk_id": "c1",
            "texto": "Frecuencia de CPU: 80 MHz, 160 MHz o 240 MHz.",
            "metadata": {"file_name": "ESP32_Datasheet.pdf"}
        }
    ]

    res = generator.generate_response(
        question="¿A qué frecuencia opera el ESP32?",
        chunks=chunks
    )

    assert res["answer"] == "El ESP32 opera a un reloj de hasta 240 MHz."
    assert "ESP32_Datasheet.pdf" in res["sources"]
    assert "Frecuencia de CPU" in res["context"]
    assert res["model"] == "gemini-2.0-flash"
    mock_client.generate.assert_called_once()


def test_no_secrets_exposed_in_generation():
    """Valida que no se filtren claves de API en prompts o respuestas generadas."""
    secret_key = "AIzaSySecretApiKey1234567890"
    mock_client = MagicMock()
    mock_client.api_key = secret_key
    mock_client.model_name = "gemini-2.0-flash"
    mock_client.generate.return_value = "Respuesta técnica fundamentada."

    generator = ResponseGenerator(gemini_client=mock_client)
    res = generator.generate_response(
        question="¿Qué voltaje soporta el pin VCC?",
        context="Voltaje máximo absoluto: 6.0V."
    )

    # El prompt y la respuesta no deben contener la clave
    assert secret_key not in res["prompt"]
    assert secret_key not in res["answer"]
    assert secret_key not in res["context"]
