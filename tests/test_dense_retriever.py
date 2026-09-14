"""Pruebas unitarias para el recuperador semántico denso (DenseRetriever)."""
from unittest.mock import MagicMock
from src.retrieval.dense_retriever import DenseRetriever


def test_dense_retriever_retrieve_success():
    """Valida el flujo estándar: Consulta -> Embedding -> k-NN search en VectorIndexer."""
    mock_embedder = MagicMock()
    mock_embedder.embed_query.return_value = [0.1, 0.2, 0.3]

    mock_indexer = MagicMock()
    mock_results = [
        {
            "chunk_id": "chunk_esp32_adc_01",
            "text": "El ESP32 integra dos convertidores analógico-digitales ADC1 y ADC2 de 12 bits.",
            "metadata": {
                "file_name": "esp32_technical_reference.pdf",
                "category": "Microcontroladores",
                "component": "ESP32",
                "topic": "ADC"
            },
            "distance": 0.245,
            "score": 0.803
        }
    ]
    mock_indexer.search.return_value = mock_results

    retriever = DenseRetriever(embedder=mock_embedder, vector_indexer=mock_indexer)
    results = retriever.retrieve(query="¿Cómo funciona el ADC del ESP32?", top_k=3)

    # Verificaciones
    mock_embedder.embed_query.assert_called_once_with("¿Cómo funciona el ADC del ESP32?")
    mock_indexer.search.assert_called_once_with(
        query_embedding=[0.1, 0.2, 0.3],
        top_k=3,
        filters=None
    )
    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk_esp32_adc_01"
    assert results[0]["metadata"]["component"] == "ESP32"


def test_dense_retriever_empty_query():
    """Valida que consultas vacías o de puros espacios no invoquen el servicio de embeddings."""
    mock_embedder = MagicMock()
    mock_indexer = MagicMock()

    retriever = DenseRetriever(embedder=mock_embedder, vector_indexer=mock_indexer)
    
    assert retriever.retrieve("") == []
    assert retriever.retrieve("   ") == []
    mock_embedder.embed_query.assert_not_called()
    mock_indexer.search.assert_not_called()


def test_dense_retriever_filters_forwarding():
    """Valida que los filtros de metadatos se transmitan correctamente al almacén vectorial."""
    mock_embedder = MagicMock()
    mock_embedder.embed_query.return_value = [0.0] * 768
    mock_indexer = MagicMock()
    mock_indexer.search.return_value = []

    retriever = DenseRetriever(embedder=mock_embedder, vector_indexer=mock_indexer)
    filters = {"component": "ATmega328P"}
    
    results = retriever.retrieve(query="Voltaje de operación", top_k=5, filters=filters)

    mock_indexer.search.assert_called_once_with(
        query_embedding=[0.0] * 768,
        top_k=5,
        filters=filters
    )
    assert results == []
