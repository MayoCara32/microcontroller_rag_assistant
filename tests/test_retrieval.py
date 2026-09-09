"""Pruebas unitarias para la búsqueda híbrida y reordenamiento."""
from src.retrieval.hybrid_search import HybridSearchEngine
from src.retrieval.reranker import CrossEncoderReranker


def test_hybrid_search_bm25_tokenization():
    engine = HybridSearchEngine()
    chunks = [
        {"chunk_id": "c1", "text": "ATmega2560 register TWCR controls I2C bus.", "file_name": "mega.md"},
        {"chunk_id": "c2", "text": "ESP32 GPIO16 supports PWM output.", "file_name": "esp32.md"}
    ]
    engine.fit_lexical_index(chunks)
    results = engine.search("TWCR", top_k=2)
    assert len(results) > 0
    assert results[0]["chunk_id"] == "c1"


def test_cross_encoder_reranker():
    reranker = CrossEncoderReranker()
    docs = [
        {"chunk_id": "d1", "text": "General info about Arduino.", "fused_score": 0.5},
        {"chunk_id": "d2", "text": "ATmega2560 maximum current per IO pin is 40mA.", "fused_score": 0.8}
    ]
    reranked = reranker.rerank("maximum current ATmega2560", docs, top_n=1)
    assert len(reranked) == 1
