"""Pruebas unitarias para VectorIndexer y ChromaDB (Sección 27)."""
import pytest
from src.indexing.vector_indexer import VectorIndexer


def test_chromadb_insert_and_query_top_k(tmp_path):
    """Valida inserción de chunks pequeños, persistencia local y recuperación top-k con distancias."""
    indexer = VectorIndexer(storage_dir=tmp_path / "test_chroma", collection_name="test_collection")

    test_chunks = [
        {
            "chunk_id": "test_chunk_01",
            "text": "El convertidor ADC del ATmega328P posee 10 bits de resolución.",
            "file_name": "atmega328.md",
            "category": "Arduino",
            "component": "ATmega328P"
        },
        {
            "chunk_id": "test_chunk_02",
            "text": "El microcontrolador ESP32 opera a 240MHz con Wi-Fi integrado.",
            "file_name": "esp32.md",
            "category": "ESP32",
            "component": "ESP32"
        },
        {
            "chunk_id": "test_chunk_03",
            "text": "Raspberry Pi Pico utiliza el procesador dual-core RP2040.",
            "file_name": "pico.md",
            "category": "Raspberry Pi",
            "component": "RP2040"
        }
    ]

    # Vectores sintéticos simples de prueba (dim=4 para prueba unitaria ligera)
    test_embeddings = [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0]
    ]

    # 1. Inserción en ChromaDB
    indexer.index_documents(test_chunks, test_embeddings)

    # 2. Consultar con vector cercano al primer chunk
    query_vec = [0.9, 0.1, 0.0, 0.0]
    results = indexer.search(query_vec, top_k=2)

    assert len(results) == 2
    # El primer resultado debe ser test_chunk_01
    assert results[0]["chunk_id"] == "test_chunk_01"
    assert results[0]["metadata"]["component"] == "ATmega328P"
    assert "distance" in results[0]
    assert isinstance(results[0]["distance"], float)
    assert results[0]["distance"] >= 0.0


def test_chromadb_persistence_reload(tmp_path):
    """Valida que los datos indexados persistan al recargar la colección desde disco."""
    storage_dir = tmp_path / "persistent_chroma"

    # Primera instancia: indexar
    indexer_1 = VectorIndexer(storage_dir=storage_dir, collection_name="persistent_coll")
    chunk = [{
        "chunk_id": "persist_01",
        "text": "Prueba de persistencia de datos.",
        "file_name": "persist.md"
    }]
    emb = [[0.5, 0.5]]
    indexer_1.index_documents(chunk, emb)

    # Segunda instancia independiente apuntando al mismo directorio
    indexer_2 = VectorIndexer(storage_dir=storage_dir, collection_name="persistent_coll")
    res = indexer_2.search([0.5, 0.5], top_k=1)

    assert len(res) == 1
    assert res[0]["chunk_id"] == "persist_01"
    assert res[0]["text"] == "Prueba de persistencia de datos."
