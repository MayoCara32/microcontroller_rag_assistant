"""Pruebas unitarias para el servicio de recuperación (RetrievalService)."""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.retrieval.retrieval_service import RetrievalService


def test_retrieval_service_search_returns_expected_structure():
    """Verifica que RetrievalService formatee y retorne chunk_id, texto, metadata y distancia."""
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [
        {
            "chunk_id": "chunk_esp32_01",
            "text": "El ADC del ESP32 cuenta con una resolución de 12 bits.",
            "metadata": {"file_name": "ESP32_TRM.pdf", "category": "ESP32"},
            "distance": 0.15
        }
    ]

    service = RetrievalService(retriever=mock_retriever)

    # Forzar que Path.exists devuelva True para STORAGE_VECTOR_DIR
    with patch.object(Path, "exists", return_value=True):
        results = service.search("ADC ESP32")

    assert len(results) == 1
    res = results[0]
    assert res["chunk_id"] == "chunk_esp32_01"
    assert res["texto"] == "El ADC del ESP32 cuenta con una resolución de 12 bits."
    assert res["metadata"] == {"file_name": "ESP32_TRM.pdf", "category": "ESP32"}
    assert res["distancia"] == pytest.approx(0.15)


def test_retrieval_service_missing_vector_store():
    """Valida que si la base vectorial no existe se lance FileNotFoundError."""
    mock_retriever = MagicMock()
    service = RetrievalService(retriever=mock_retriever)

    with patch.object(Path, "exists", return_value=False):
        with pytest.raises(FileNotFoundError, match="ChromaDB no existe"):
            service.search("Consulta de prueba")


def test_retrieval_service_embedding_or_chroma_failure():
    """Valida que las fallas de embedding o ChromaDB se capturen en RuntimeError con mensaje claro."""
    mock_retriever = MagicMock()
    mock_retriever.retrieve.side_effect = Exception("Falla de conexion con Gemini API")

    service = RetrievalService(retriever=mock_retriever)

    with patch.object(Path, "exists", return_value=True):
        with pytest.raises(RuntimeError, match="Falla durante la generación de embedding"):
            service.search("Consulta con error")


def test_retrieval_service_empty_query():
    """Valida que consultas vacías retornen una lista vacía de inmediato."""
    mock_retriever = MagicMock()
    service = RetrievalService(retriever=mock_retriever)
    assert service.search("") == []
    assert service.search("   ") == []
