"""Pruebas unitarias para la interfaz interactiva de chat RAG cli_chat.py."""
from unittest.mock import MagicMock, patch
from src.cli_chat import run_cli_chat, display_debug_info


def test_display_debug_info_formatting_and_no_secrets(capsys):
    """Valida que display_debug_info muestre la estructura de depuración sin filtrar secretos."""
    sample_results = [
        {
            "chunk_id": "esp32_c1",
            "texto": "El módulo ADC2 es usado internamente por el Wi-Fi.",
            "metadata": {
                "file_name": "ESP32_Technical_Reference_Manual.pdf",
                "category": "ESP32"
            },
            "distancia": 0.2255
        }
    ]
    gen_result = {
        "answer": "El ADC2 tiene limitaciones cuando el Wi-Fi está encendido.",
        "context": "Contexto técnico de prueba",
        "model": "gemini-2.0-flash"
    }

    display_debug_info(
        question="¿Puedo usar ADC2 con Wi-Fi?",
        results=sample_results,
        gen_result=gen_result
    )
    captured = capsys.readouterr().out

    assert "MODO DEBUG" in captured
    assert "PREGUNTA:" in captured
    assert "¿Puedo usar ADC2 con Wi-Fi?" in captured
    assert "RESULTADOS RETRIEVAL:" in captured
    assert "ESP32_Technical_Reference_Manual.pdf" in captured
    assert "esp32_c1" in captured
    assert "0.2255" in captured
    assert "CONTEXTO ENVIADO A GEMINI:" in captured
    assert "Contexto técnico de prueba" in captured
    assert "MODELO UTILIZADO:" in captured
    assert "gemini-2.0-flash" in captured
    assert "RESPUESTA:" in captured
    # Verificar que no expone texto de clave falsa
    assert "AIza" not in captured
    assert "API_KEY" not in captured


def test_run_cli_chat_flow_multiple_questions(capsys):
    """Valida el bucle de interacción de run_cli_chat simulando múltiples preguntas y salida."""
    mock_retriever = MagicMock()
    mock_retriever.search.side_effect = [
        [
            {
                "chunk_id": "c1",
                "texto": "Características eléctricas del ADC.",
                "metadata": {"file_name": "ESP32_Datasheet.pdf"},
                "distancia": 0.1
            }
        ],
        [
            {
                "chunk_id": "c2",
                "texto": "ATmega328P opera a 16MHz.",
                "metadata": {"file_name": "ATmega328P_Datasheet.pdf"},
                "distancia": 0.05
            }
        ]
    ]

    mock_generator = MagicMock()
    mock_generator.generate_response.side_effect = [
        {
            "answer": "El ADC del ESP32 tiene 12 bits.",
            "sources": ["ESP32_Datasheet.pdf"],
            "context": "Características eléctricas del ADC.",
            "model": "gemini-2.0-flash"
        },
        {
            "answer": "El ATmega328P funciona a 16MHz en Arduino Uno.",
            "sources": ["ATmega328P_Datasheet.pdf"],
            "context": "ATmega328P opera a 16MHz.",
            "model": "gemini-2.0-flash"
        }
    ]

    # Simular dos preguntas seguidas y luego "salir"
    inputs = [
        "¿Cómo funciona el ADC del ESP32?",
        "¿A qué frecuencia corre el ATmega328P?",
        "salir"
    ]

    with patch("builtins.input", side_effect=inputs):
        run_cli_chat(retrieval_service=mock_retriever, response_generator=mock_generator)

    captured = capsys.readouterr().out

    assert "Microcontroller RAG Assistant" in captured
    assert "Asistente técnico basado en documentación" in captured
    assert "Buscando información..." in captured
    assert "Documentos encontrados:" in captured
    assert "1. ESP32_Datasheet.pdf" in captured
    assert "Generando respuesta..." in captured
    assert "El ADC del ESP32 tiene 12 bits." in captured
    assert "Fuentes:" in captured
    assert "- ESP32_Datasheet.pdf" in captured
    assert "1. ATmega328P_Datasheet.pdf" in captured
    assert "El ATmega328P funciona a 16MHz en Arduino Uno." in captured
    assert "Saliendo de Microcontroller RAG Assistant." in captured


def test_run_cli_chat_debug_flag(capsys):
    """Valida que la opción debug active la visualización extendida sin fallar."""
    mock_retriever = MagicMock()
    mock_retriever.search.return_value = [
        {
            "chunk_id": "chunk_debug_1",
            "texto": "Texto técnico",
            "metadata": {"file_name": "Datasheet_Debug.pdf"},
            "distancia": 0.15
        }
    ]

    mock_generator = MagicMock()
    mock_generator.generate_response.return_value = {
        "answer": "Respuesta en modo debug",
        "sources": ["Datasheet_Debug.pdf"],
        "context": "Texto técnico",
        "model": "gemini-2.0-flash"
    }

    inputs = ["Consulta técnica", "exit"]

    with patch("builtins.input", side_effect=inputs):
        run_cli_chat(
            retrieval_service=mock_retriever,
            response_generator=mock_generator,
            debug=True
        )

    captured = capsys.readouterr().out
    assert "MODO DEBUG" in captured
    assert "PREGUNTA:" in captured
    assert "chunk_debug_1" in captured
    assert "MODELO UTILIZADO:" in captured


def test_run_cli_chat_handles_runtime_error(capsys):
    """Valida que run_cli_chat reporte mensajes de error claros sin romperse."""
    mock_retriever = MagicMock()
    mock_retriever.search.side_effect = RuntimeError("Falla de API key de Gemini")

    inputs = ["Consulta fallida", "exit"]

    with patch("builtins.input", side_effect=inputs):
        run_cli_chat(retrieval_service=mock_retriever, response_generator=MagicMock())

    captured = capsys.readouterr().out
    assert "[Error de Recuperación/Generación]: Falla de API key de Gemini" in captured
