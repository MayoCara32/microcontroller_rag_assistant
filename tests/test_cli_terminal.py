"""Pruebas unitarias para la interfaz de terminal (TerminalRAGInterface)."""
from unittest.mock import MagicMock
from src.cli.terminal_interface import TerminalRAGInterface


def test_terminal_display_results_with_chunks():
    """Valida que la interfaz renderice correctamente los paneles cuando hay chunks recuperados."""
    mock_retriever = MagicMock()
    mock_console = MagicMock()

    app = TerminalRAGInterface(retriever=mock_retriever, console=mock_console)

    sample_results = [
        {
            "chunk_id": "chunk_001",
            "text": "Tensión recomendada de 1.8V a 5.5V para el microcontrolador ATmega328P.",
            "metadata": {
                "file_name": "ATmega328P_Datasheet.pdf",
                "category": "Microcontroladores",
                "component": "ATmega328P",
                "topic": "Electrical Characteristics"
            },
            "distance": 0.123
        }
    ]

    app.display_results("Voltaje ATmega328P", sample_results)

    # Verificar que console.print fue llamado varias veces para imprimir paneles
    assert mock_console.print.call_count >= 2


def test_terminal_display_no_results_message():
    """Valida que ante cero resultados se imprima el mensaje formal de ausencia documental."""
    mock_retriever = MagicMock()
    mock_console = MagicMock()

    app = TerminalRAGInterface(retriever=mock_retriever, console=mock_console)
    app.display_results("Consulta inexistente", [])

    # Obtener los textos impresos en la consola mockeada
    printed_texts = []
    for call in mock_console.print.call_args_list:
        if call.args:
            arg = call.args[0]
            if hasattr(arg, "renderable"):
                printed_texts.append(str(arg.renderable))
            else:
                printed_texts.append(str(arg))
    combined_output = " ".join(printed_texts)

    assert "No se encontró información suficiente en la base documental" in combined_output



def test_terminal_process_query_shortcut_mapping():
    """Valida que un atajo numérico '1' invoque la consulta correspondiente de la lista de ejemplos."""
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [{"chunk_id": "c1", "text": "sample"}]

    app = TerminalRAGInterface(retriever=mock_retriever)
    results = app.process_query("1")

    expected_query = app.sample_queries[0]
    mock_retriever.retrieve.assert_called_once_with(query=expected_query, top_k=None)
    assert len(results) == 1
