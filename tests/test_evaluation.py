"""Tests unitarios para el módulo de evaluación RAG (Precision, Recall, Faithfulness, Evaluator, Report)."""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from src.evaluation.precision import RetrievalPrecisionEvaluator
from src.evaluation.recall import RetrievalRecallEvaluator
from src.evaluation.faithfulness import FaithfulnessEvaluator
from src.evaluation.evaluator import RAGEvaluator
from src.evaluation.evaluation_report import EvaluationReport


# ==============================================================================
# Tests para Retrieval Precision
# ==============================================================================

def test_precision_perfect_match():
    evaluator = RetrievalPrecisionEvaluator()
    retrieved = ["esp32_datasheet_en.pdf"]
    expected = ["esp32_datasheet_en.pdf"]
    res = evaluator.evaluate(retrieved, expected)

    assert res["metric"] == "precision"
    assert res["value"] == 1.0
    assert res["relevant_documents"] == ["esp32_datasheet_en.pdf"]
    assert res["irrelevant_documents"] == []


def test_precision_partial_match():
    evaluator = RetrievalPrecisionEvaluator()
    retrieved = ["esp32_datasheet_en.pdf", "A000066-datasheet.pdf"]
    expected = ["esp32_datasheet_en.pdf"]
    res = evaluator.evaluate(retrieved, expected)

    assert res["value"] == 0.5
    assert len(res["relevant_documents"]) == 1
    assert len(res["irrelevant_documents"]) == 1


def test_precision_no_match():
    evaluator = RetrievalPrecisionEvaluator()
    retrieved = ["A000066-datasheet.pdf", "A000067-datasheet.pdf"]
    expected = ["esp32_datasheet_en.pdf"]
    res = evaluator.evaluate(retrieved, expected)

    assert res["value"] == 0.0
    assert len(res["relevant_documents"]) == 0
    assert len(res["irrelevant_documents"]) == 2


def test_precision_empty_retrieved():
    evaluator = RetrievalPrecisionEvaluator()
    res = evaluator.evaluate([], ["esp32_datasheet_en.pdf"])
    assert res["value"] == 0.0
    assert res["relevant_documents"] == []


def test_precision_with_metadata_dicts():
    evaluator = RetrievalPrecisionEvaluator()
    retrieved = [
        {"metadata": {"file_name": "UM10204.pdf"}},
        {"metadata": {"file_name": "kb-canbus-en.pdf"}}
    ]
    expected = ["um10204.pdf"]
    res = evaluator.evaluate(retrieved, expected)

    assert res["value"] == 0.5
    assert res["relevant_documents"] == ["UM10204.pdf"]


# ==============================================================================
# Tests para Retrieval Recall
# ==============================================================================

def test_recall_perfect_match():
    evaluator = RetrievalRecallEvaluator()
    retrieved = ["esp32_datasheet_en.pdf", "other.pdf"]
    expected = ["esp32_datasheet_en.pdf"]
    res = evaluator.evaluate(retrieved, expected)

    assert res["metric"] == "recall"
    assert res["value"] == 1.0
    assert res["found_documents"] == ["esp32_datasheet_en.pdf"]
    assert res["missing_documents"] == []


def test_recall_partial_match():
    evaluator = RetrievalRecallEvaluator()
    retrieved = ["A000066-datasheet.pdf"]
    expected = ["A000066-datasheet.pdf", "atmega328ds.pdf"]
    res = evaluator.evaluate(retrieved, expected)

    assert res["value"] == 0.5
    assert res["found_documents"] == ["A000066-datasheet.pdf"]
    assert res["missing_documents"] == ["atmega328ds.pdf"]


def test_recall_zero_match():
    evaluator = RetrievalRecallEvaluator()
    retrieved = ["esp32_datasheet_en.pdf"]
    expected = ["UM10204.pdf"]
    res = evaluator.evaluate(retrieved, expected)

    assert res["value"] == 0.0
    assert res["found_documents"] == []
    assert res["missing_documents"] == ["UM10204.pdf"]


def test_recall_empty_expected():
    evaluator = RetrievalRecallEvaluator()
    res = evaluator.evaluate(["esp32_datasheet_en.pdf"], [])
    assert res["value"] == 0.0


# ==============================================================================
# Tests para Faithfulness
# ==============================================================================

def test_faithfulness_fallback_deterministic():
    evaluator = FaithfulnessEvaluator()
    res = evaluator.evaluate(
        question="¿Cuál es el pinout?",
        context="",
        answer="No encontré información suficiente en la documentación disponible para responder esta pregunta."
    )
    assert res["metric"] == "faithfulness"
    assert res["faithfulness_score"] == 1.0
    assert len(res["supported_claims"]) > 0
    assert len(res["unsupported_claims"]) == 0


def test_faithfulness_with_mocked_gemini():
    mock_client = MagicMock()
    mock_client.generate.return_value = json.dumps({
        "faithfulness_score": 0.75,
        "supported_claims": ["El ADC del ESP32 tiene 12 bits de resolución."],
        "unsupported_claims": ["El ESP32 opera a 5V nativos."],
        "partially_supported_claims": []
    })

    evaluator = FaithfulnessEvaluator(gemini_client=mock_client)
    res = evaluator.evaluate(
        question="¿Cuántos bits tiene el ADC?",
        context="El ESP32 incluye dos convertidores ADC de 12 bits.",
        answer="El ADC del ESP32 tiene 12 bits de resolución y opera a 5V nativos."
    )

    assert res["metric"] == "faithfulness"
    assert res["faithfulness_score"] == 0.75
    assert len(res["supported_claims"]) == 1
    assert len(res["unsupported_claims"]) == 1
    assert mock_client.generate.called


def test_faithfulness_markdown_json_parsing():
    mock_client = MagicMock()
    mock_client.generate.return_value = """```json
    {
      "faithfulness_score": 1.0,
      "supported_claims": ["Afirmación válida."],
      "unsupported_claims": [],
      "partially_supported_claims": []
    }
    ```"""

    evaluator = FaithfulnessEvaluator(gemini_client=mock_client)
    res = evaluator.evaluate(
        question="Pregunta test",
        context="Contexto test",
        answer="Respuesta test"
    )

    assert res["faithfulness_score"] == 1.0
    assert res["supported_claims"] == ["Afirmación válida."]


# ==============================================================================
# Tests para RAGEvaluator y EvaluationReport
# ==============================================================================

def test_rag_evaluator_coordination():
    mock_faith = MagicMock()
    mock_faith.evaluate.return_value = {
        "metric": "faithfulness",
        "faithfulness_score": 0.9,
        "supported_claims": ["Dato verificado"],
        "unsupported_claims": []
    }

    evaluator = RAGEvaluator(faithfulness_evaluator=mock_faith)
    res = evaluator.evaluate(
        question="¿Cuál es el voltaje?",
        expected_documents=["A000066-datasheet.pdf"],
        retrieved_documents=["A000066-datasheet.pdf", "other.pdf"],
        context="El voltaje recomendado es 7-12V",
        answer="El voltaje recomendado es 7-12V"
    )

    assert "precision" in res
    assert "recall" in res
    assert "faithfulness" in res
    assert res["precision"]["value"] == 0.5
    assert res["recall"]["value"] == 1.0
    assert res["faithfulness"]["faithfulness_score"] == 0.9


def test_evaluation_report_summary_and_save(tmp_path):
    report_file = tmp_path / "test_report.json"
    report = EvaluationReport(output_path=report_file)

    report.add_record(
        question="Pregunta 1",
        retrieval_precision=1.0,
        retrieval_recall=1.0,
        faithfulness=1.0,
        expected_documents=["doc1.pdf"],
        retrieved_documents=["doc1.pdf"]
    )
    report.add_record(
        question="Pregunta 2",
        retrieval_precision=0.5,
        retrieval_recall=0.8,
        faithfulness=0.9,
        expected_documents=["doc2.pdf"],
        retrieved_documents=["doc2.pdf", "doc3.pdf"]
    )

    summary = report.compute_summary()
    assert summary["total_questions"] == 2
    assert summary["mean_precision"] == 0.75
    assert summary["mean_recall"] == 0.9
    assert summary["mean_faithfulness"] == 0.95

    saved = report.save_json()
    assert saved.exists()

    with open(saved, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["summary"]["total_questions"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["question"] == "Pregunta 1"


# ==============================================================================
# Tests para el Dataset evaluation/questions.json
# ==============================================================================

def test_questions_dataset_structure_and_counts():
    questions_path = Path(__file__).resolve().parent.parent / "evaluation" / "questions.json"
    assert questions_path.exists(), "El archivo evaluation/questions.json debe existir."

    with open(questions_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    assert len(dataset) >= 20, f"Debe haber al menos 20 preguntas (encontradas {len(dataset)})."

    categories = {}
    for item in dataset:
        assert "id" in item
        assert "question" in item
        assert "expected_documents" in item
        assert len(item["expected_documents"]) > 0
        cat = item.get("category", "Desconocido")
        categories[cat] = categories.get(cat, 0) + 1

    assert categories.get("Arduino", 0) >= 5, "Debe haber mínimo 5 preguntas de Arduino."
    assert categories.get("ESP32", 0) >= 5, "Debe haber mínimo 5 preguntas de ESP32."
    assert categories.get("Raspberry", 0) >= 3, "Debe haber mínimo 3 preguntas de Raspberry."
    assert categories.get("Protocolos", 0) >= 4, "Debe haber mínimo 4 preguntas de Protocolos."
    assert categories.get("Drivers", 0) >= 3, "Debe haber mínimo 3 preguntas de Drivers."
