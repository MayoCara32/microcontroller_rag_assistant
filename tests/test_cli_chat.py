"""Pruebas unitarias para la interfaz cli_chat.py."""
from unittest.mock import MagicMock, patch
from src.cli_chat import run_cli_chat, display_search_results


def test_display_search_results_formatting(capsys):
    """Valida la salida con formato especifico requerida por el prompt para los resultados."""
    sample_results = [
        {
            "chunk_id": "c1",
            "texto": "El módulo ADC2 es usado internamente por el Wi-Fi.",
            "metadata": {
                "file_name": "ESP32 Technical Reference Manual",
                "category": "ESP32"
            },
            "distancia": 0.22
        }
    ]

    display_search_results(sample_results)
    captured = capsys.readouterr().out

    assert "Resultado 1" in captured
    assert "Documento:" in captured
    assert "ESP32 Technical Reference Manual" in captured
    assert "Categoría:" in captured
    assert "ESP32" in captured
    assert "Fragmento:" in captured
    assert "El módulo ADC2 es usado internamente por el Wi-Fi." in captured


def test_run_cli_chat_flow(capsys):
    """Valida el bucle de interaccion de run_cli_chat simulando entrada de usuario."""
    mock_service = MagicMock()
    mock_service.search.return_value = [
        {
            "chunk_id": "c1",
            "texto": "Características eléctricas del ADC.",
            "metadata": {"file_name": "ESP32 Manual", "category": "ESP32"},
            "distancia": 0.1
        }
    ]

    # Simular una pregunta y luego la orden de salir
    inputs = ["¿Cómo funciona el ADC del ESP32?", "salir"]

    with patch("builtins.input", side_effect=inputs):
        run_cli_chat(retrieval_service=mock_service)

    captured = capsys.readouterr().out

    assert "Microcontroller RAG Assistant" in captured
    assert "Pregunta:" in captured
    assert "generando embedding..." in captured
    assert "buscando información..." in captured
    assert "Resultado 1" in captured
    assert "ESP32 Manual" in captured


def test_run_cli_chat_handles_error(capsys):
    """Valida que run_cli_chat reporte mensajes de error claros sin romperse."""
    mock_service = MagicMock()
    mock_service.search.side_effect = RuntimeError("Falla de API key de Gemini")

    inputs = ["Consulta fallida", "exit"]

    with patch("builtins.input", side_effect=inputs):
        run_cli_chat(retrieval_service=mock_service)

    captured = capsys.readouterr().out
    assert "[Error de Recuperación/Embedding]: Falla de API key de Gemini" in captured
