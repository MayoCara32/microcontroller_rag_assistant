"""Pruebas unitarias para el pipeline de ingesta y parseo."""
from pathlib import Path
from src.ingestion.document_cleaner import DocumentCleaner
from src.ingestion.metadata_extractor import MetadataExtractor
from src.indexing.chunker import SemanticHardwareChunker


def test_document_cleaner():
    cleaner = DocumentCleaner()
    raw = "Header noise\n\nPage 1 of 10\n\nATmega2560 operating at 16MHz.\n"
    cleaned = cleaner.clean(raw)
    assert "Page 1 of 10" not in cleaned
    assert "ATmega2560 operating at 16MHz." in cleaned


def test_metadata_extractor_interfaces():
    extractor = MetadataExtractor()
    text = "The ESP32 features I2C, SPI, UART and 12-bit ADC peripherals."
    interfaces = extractor.identify_interfaces(text)
    assert "I2C" in interfaces
    assert "SPI" in interfaces
    assert "UART" in interfaces
    assert "ADC" in interfaces


def test_semantic_hardware_chunker():
    chunker = SemanticHardwareChunker(chunk_size=200, chunk_overlap=20)
    doc_data = {
        "text": "# Section 1\nATmega2560 has 54 digital IO pins.\n\n# Section 2\nESP32 features dual core Xtensa CPU.",
        "file_name": "test_sheet.md",
        "category": "Arduino"
    }
    chunks = chunker.split_document(doc_data)
    assert len(chunks) >= 2
    assert "ATmega2560" in chunks[0]["text"]
