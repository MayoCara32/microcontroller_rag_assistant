"""Pruebas unitarias para EmbeddingService según especificaciones del Día 12 (Sección 26)."""
from unittest.mock import patch, MagicMock
import pytest
from src.indexing.embedder import EmbeddingService


def test_embed_methods_exist():
    """Valida que embed_documents y embed_query existan en la interfaz del servicio."""
    service = EmbeddingService(dimension=768)
    assert hasattr(service, "embed_documents")
    assert callable(service.embed_documents)
    assert hasattr(service, "embed_query")
    assert callable(service.embed_query)


def test_embed_dimensions_and_task_types():
    """Valida dimensionalidad 768 y diferenciación de task_type (RETRIEVAL_DOCUMENT vs RETRIEVAL_QUERY)."""
    mock_client = MagicMock()

    # Configurar respuesta simulada de Gemini con 768 dimensiones
    doc_embedding = MagicMock()
    doc_embedding.values = [0.1] * 768
    query_embedding = MagicMock()
    query_embedding.values = [0.2] * 768

    mock_doc_response = MagicMock(embeddings=[doc_embedding, doc_embedding])
    mock_query_response = MagicMock(embeddings=[query_embedding])

    mock_client.models.embed_content.side_effect = [mock_doc_response, mock_query_response]

    service = EmbeddingService(
        provider="google",
        model_name="gemini-embedding-001",
        dimension=768,
        api_key="test-fake-key",
        allow_test_embeddings=False
    )

    with patch("google.genai.Client", return_value=mock_client):
        # 1. Probar embed_documents
        doc_vectors = service.embed_documents(["Texto 1", "Texto 2"])
        assert len(doc_vectors) == 2
        assert len(doc_vectors[0]) == 768

        first_call_config = mock_client.models.embed_content.call_args_list[0].kwargs["config"]
        assert first_call_config.task_type == "RETRIEVAL_DOCUMENT"
        assert first_call_config.output_dimensionality == 768

        # 2. Probar embed_query
        query_vector = service.embed_query("¿Cómo se configura el I2C?")
        assert len(query_vector) == 768

        second_call_config = mock_client.models.embed_content.call_args_list[1].kwargs["config"]
        assert second_call_config.task_type == "RETRIEVAL_QUERY"
        assert second_call_config.output_dimensionality == 768


def test_api_error_raises_explicit_exception():
    """Valida que un fallo de la API no quede oculto silenciosamente y lance RuntimeError."""
    mock_client = MagicMock()
    mock_client.models.embed_content.side_effect = ConnectionError("Google API quota exceeded / network failure")

    service = EmbeddingService(
        provider="google",
        model_name="gemini-embedding-001",
        api_key="test-fake-key",
        allow_test_embeddings=False
    )

    with patch("google.genai.Client", return_value=mock_client):
        with pytest.raises(RuntimeError) as exc_info:
            service.embed_documents(["Texto para indexar"])

        err_msg = str(exc_info.value)
        assert "Error al generar embeddings con proveedor 'google'" in err_msg
        assert "gemini-embedding-001" in err_msg


def test_fallback_does_not_activate_in_production():
    """Valida que el fallback sintético NO se active si allow_test_embeddings es False y no hay API key."""
    service = EmbeddingService(
        provider="google",
        api_key="",
        allow_test_embeddings=False
    )
    with pytest.raises(ValueError) as exc_info:
        service.embed_documents(["Texto de prueba"])

    assert "GEMINI_API_KEY no configurada" in str(exc_info.value)


def test_fallback_activates_only_when_explicitly_allowed():
    """Valida que el fallback sintético hash se active ÚNICAMENTE cuando allow_test_embeddings es True."""
    service = EmbeddingService(
        provider="google",
        api_key="",
        allow_test_embeddings=True,
        dimension=768
    )
    vecs = service.embed_documents(["Texto de prueba"])
    assert len(vecs) == 1
    assert len(vecs[0]) == 768
    # Comprobar que sea determinista
    vecs2 = service.embed_documents(["Texto de prueba"])
    assert vecs[0] == vecs2[0]
