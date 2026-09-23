"""Generador y persistidor de reportes de evaluación RAG en formato JSON."""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime


class EvaluationReport:
    """Acumula evaluaciones por pregunta, calcula promedios y persiste el reporte JSON."""

    DEFAULT_REPORT_PATH = Path(__file__).resolve().parent.parent.parent / "evaluation" / "results" / "report.json"

    def __init__(self, output_path: Optional[Union[str, Path]] = None):
        self.output_path = Path(output_path) if output_path else self.DEFAULT_REPORT_PATH
        self.records: List[Dict[str, Any]] = []

    def add_record(
        self,
        question: str,
        retrieval_precision: float,
        retrieval_recall: float,
        faithfulness: float,
        expected_documents: Optional[List[str]] = None,
        retrieved_documents: Optional[List[str]] = None,
        answer: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
        question_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Registra el resultado de evaluar una consulta individual."""
        record: Dict[str, Any] = {
            "id": question_id,
            "category": category or "General",
            "question": question,
            "retrieval_precision": round(float(retrieval_precision), 4),
            "retrieval_recall": round(float(retrieval_recall), 4),
            "faithfulness": round(float(faithfulness), 4),
            "expected_documents": expected_documents or [],
            "retrieved_documents": retrieved_documents or [],
            "answer": answer or "",
            "details": details or {}
        }
        self.records.append(record)
        return record

    def compute_summary(self) -> Dict[str, Any]:
        """Calcula promedios globales sobre los registros evaluados."""
        total = len(self.records)
        if total == 0:
            return {
                "total_questions": 0,
                "mean_precision": 0.0,
                "mean_recall": 0.0,
                "mean_faithfulness": 0.0
            }

        sum_precision = sum(r.get("retrieval_precision", 0.0) for r in self.records)
        sum_recall = sum(r.get("retrieval_recall", 0.0) for r in self.records)
        sum_faithfulness = sum(r.get("faithfulness", 0.0) for r in self.records)

        return {
            "total_questions": total,
            "mean_precision": round(sum_precision / total, 4),
            "mean_recall": round(sum_recall / total, 4),
            "mean_faithfulness": round(sum_faithfulness / total, 4)
        }

    def generate_report_dict(self) -> Dict[str, Any]:
        """Estructura el documento final del reporte con metadata, resumen y lista de resultados."""
        summary = self.compute_summary()
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "results": self.records
        }

    def save_json(self, target_path: Optional[Union[str, Path]] = None) -> Path:
        """Serializa y guarda el reporte en disco en la ruta especificada."""
        path = Path(target_path) if target_path else self.output_path
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = self.generate_report_dict()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        return path
