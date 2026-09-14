"""Pruebas de integración para la interacción de terminal del sistema RAG (Día 13)."""
import pytest
from unittest.mock import MagicMock, patch
from src.retrieval.retrieval_service import RetrievalService
from src.cli_chat import run_cli_chat, display_search_results
from src.cli.terminal_interface import TerminalRAGInterface


def test_cli_chat_successful_retrieval(capsys):
    """Verifica que el flujo de terminal muestre chunks formateados sin generación LLM."""
    mock_service = MagicMock(spec=RetrievalService)
    mock_service.search.return_value = [
        {
            "chunk_id": "atmega_pin_01",
            "texto": "El microcontrolador ATmega328P cuenta con 14 pines de E/S digital (de los cuales 6 pueden usarse como salidas PWM).",
            "metadata": {
                "file_name": "ATmega328P_Datasheet.pdf",
                "category": "Microcontroladores",
                "component": "ATmega328P"
            },
            "distancia": 0.115
        }
    ]

    with patch("builtins.input", side_effect=["¿Cuántos pines digitales tiene Arduino UNO?", "salir"]):
        run_cli_chat(retrieval_service=mock_service)

    output = capsys.readouterr().out

    # Validar flujo y formato estricto
    assert "Microcontroller RAG Assistant" in output
    assert "generando embedding..." in output
    assert "buscando información..." in output
    assert "Resultado 1" in output
    assert "Documento:\nATmega328P_Datasheet.pdf" in output
    assert "Categoría:\nMicrocontroladores" in output
    assert "Fragmento:\nEl microcontrolador ATmega328P cuenta con 14 pines de E/S digital" in output
    # Confirmar que no hay síntesis conversacional generada por LLM
    assert "Hola" not in output
    assert "Como modelo de lenguaje" not in output


def test_cli_chat_no_results(capsys):
    """Verifica que ante cero resultados se muestre el mensaje estándar sin alucinación."""
    mock_service = MagicMock(spec=RetrievalService)
    mock_service.search.return_value = []

    with patch("builtins.input", side_effect=["Consulta inexistente o sin datos", "exit"]):
        run_cli_chat(retrieval_service=mock_service)

    output = capsys.readouterr().out
    assert "No se encontró información suficiente en la base documental para la consulta solicitada." in output


def test_terminal_rag_interface_with_retrieval_service():
    """Verifica que TerminalRAGInterface interactúe correctamente con RetrievalService."""
    mock_service = MagicMock(spec=RetrievalService)
    mock_service.search.return_value = [
        {
            "chunk_id": "esp32_adc_01",
            "texto": "El convertidor analógico a digital (ADC) del ESP32 integra hasta 18 canales de 12 bits.",
            "metadata": {"file_name": "ESP32_TRM.pdf", "category": "ESP32", "component": "ESP32"},
            "distancia": 0.089
        }
    ]

    interface = TerminalRAGInterface(retrieval_service=mock_service)
    results = interface.process_query("¿Cómo funciona ADC?")

    mock_service.search.assert_called_once_with(query="¿Cómo funciona ADC?", top_k=None)
    assert len(results) == 1
    assert results[0]["chunk_id"] == "esp32_adc_01"
