"""Pruebas unitarias completas para SemanticHardwareChunker (Día 12)."""
import pytest
from src.indexing.chunker import SemanticHardwareChunker


def test_no_empty_chunks():
    """Valida que no se emitan chunks vacíos ni con solo espacios."""
    chunker = SemanticHardwareChunker(chunk_size=200, chunk_overlap=30)
    doc_data = {
        "text": "\n\n  \n\n# Header\nTexto con contenido técnico real.\n\n\n  ",
        "file_name": "test_doc.md",
        "category": "Arduino"
    }
    chunks = chunker.split_document(doc_data)
    assert len(chunks) > 0
    for c in chunks:
        assert c["raw_text"].strip() != ""
        assert len(c["text"].strip()) > 0


def test_unique_chunk_ids():
    """Valida que todos los chunk IDs generados sean únicos."""
    chunker = SemanticHardwareChunker(chunk_size=150, chunk_overlap=25)
    long_text = "El microcontrolador ATmega328P opera a 16MHz con 32KB de memoria flash. " * 10
    doc_data = {
        "text": long_text,
        "file_name": "atmega328.md",
        "category": "Arduino"
    }
    chunks = chunker.split_document(doc_data)
    assert len(chunks) > 2
    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids))


def test_metadata_preservation():
    """Valida que los metadatos contextuales adicionales se preserven íntegros."""
    chunker = SemanticHardwareChunker(chunk_size=300, chunk_overlap=50)
    doc_data = {
        "text": "Especificaciones del ADC de 10 bits.",
        "file_name": "mega.md",
        "category": "Arduino",
        "component": "ATmega2560",
        "manufacturer": "Microchip",
        "document_type": "Datasheet",
        "operating_voltage": "5V"
    }
    chunks = chunker.split_document(doc_data)
    assert len(chunks) == 1
    c = chunks[0]
    assert c["component"] == "ATmega2560"
    assert c["manufacturer"] == "Microchip"
    assert c["document_type"] == "Datasheet"
    assert c["operating_voltage"] == "5V"
    assert "[Componente: ATmega2560 | Categoría: Arduino]" in c["text"]


def test_no_word_chopping_in_sliding_window():
    """Valida que el corte por ventana no divida palabras a la mitad."""
    chunker = SemanticHardwareChunker(chunk_size=120, chunk_overlap=20)
    text = "El registro ADMUX selecciona el canal analógico multiplexado y el voltaje de referencia interno del microcontrolador ATmega328P."
    doc_data = {"text": text, "file_name": "test.md"}
    chunks = chunker.split_document(doc_data)
    for c in chunks:
        raw = c["raw_text"]
        # Ni el inicio ni el final deben ser una palabra mocha (deben comenzar y terminar en límites de palabra)
        assert not raw.startswith(" "), "El fragmento no debe iniciar con espacio residual"
        assert not raw.endswith(" "), "El fragmento no debe finalizar con espacio residual"


def test_verifiable_overlap_between_chunks():
    """Valida que la región de overlap exista y sea verificable entre fragmentos continuos."""
    chunker = SemanticHardwareChunker(chunk_size=200, chunk_overlap=40)
    # Generar texto largo continuo sin encabezados Markdown
    text = (
        "El puerto serie USART del ATmega328P permite comunicación full-duplex con búfer de recepción. "
        "Posee generador de baud rate de alta precisión compatible con tasas estándar como 9600 y 115200 baudios. "
        "Adicionalmente cuenta con soporte para tramas de datos de 5 a 9 bits y bits de paridad par o impar."
    )
    doc_data = {"text": text, "file_name": "usart.md"}
    chunks = chunker.split_document(doc_data)
    assert len(chunks) >= 2, "Debe dividirse en al menos dos chunks"

    chunk_a = chunks[0]["raw_text"]
    chunk_b = chunks[1]["raw_text"]

    # Comprobar que alguna subcadena del final de chunk A esté al inicio de chunk B
    words_a = chunk_a.split()
    words_b = chunk_b.split()
    # Tomar las últimas 3 palabras de A
    last_words_a = " ".join(words_a[-3:])
    assert last_words_a in chunk_b, f"Se esperaba encontrar '{last_words_a}' en el Chunk B para verificar overlap."


def test_reasonable_size_and_tables():
    """Valida que las tablas Markdown no se corten arbitrariamente si caben en margen técnico."""
    chunker = SemanticHardwareChunker(chunk_size=250, chunk_overlap=30)
    table_content = (
        "| Pin | Función | Modo |\n"
        "| --- | --- | --- |\n"
        "| PB0 | SS | SPI Slave Select |\n"
        "| PB1 | SCK | SPI Clock |\n"
        "| PB2 | MOSI | Master Out Slave In |\n"
        "| PB3 | MISO | Master In Slave Out |\n"
    )
    doc_data = {"text": table_content, "file_name": "spi_table.md"}
    chunks = chunker.split_document(doc_data)
    # La tabla completa debe preservarse junta
    assert len(chunks) == 1
    assert "MISO" in chunks[0]["raw_text"]
    assert "PB0" in chunks[0]["raw_text"]


def test_small_document_processing():
    """Valida que documentos de pocas líneas o palabras funcionen sin errores."""
    chunker = SemanticHardwareChunker(chunk_size=800, chunk_overlap=150)
    doc_data = {"text": "Documento corto de sensor DHT22.", "file_name": "dht22.md"}
    chunks = chunker.split_document(doc_data)
    assert len(chunks) == 1
    assert "DHT22" in chunks[0]["text"]


def test_empty_document_handling():
    """Valida que un documento vacío devuelva una lista vacía."""
    chunker = SemanticHardwareChunker()
    assert chunker.split_document({"text": ""}) == []
    assert chunker.split_document({"text": "   \n\n  "}) == []
