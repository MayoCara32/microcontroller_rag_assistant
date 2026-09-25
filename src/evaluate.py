"""CLI ejecutable para la evaluación integral del pipeline RAG de Microcontroller Assistant."""
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Asegurar que la raíz del proyecto esté en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from configs.settings import get_settings
from src.retrieval.retrieval_service import RetrievalService
from src.generation.response_generator import ResponseGenerator
from src.evaluation.evaluator import RAGEvaluator
from src.evaluation.evaluation_report import EvaluationReport


def extract_doc_names(results: List[Dict[str, Any]]) -> List[str]:
    """Extrae la lista de nombres únicos de documentos presentes en los chunks recuperados."""
    docs: List[str] = []
    for res in results:
        meta = res.get("metadata", {})
        doc = (
            meta.get("file_name")
            or meta.get("document")
            or meta.get("source")
            or ""
        )
        if doc and doc not in docs:
            docs.append(doc)
    return docs


def run_evaluation(
    questions_path: Path,
    output_path: Path,
    limit: Optional[int] = None,
    skip_faithfulness: bool = False,
    verbose: bool = True,
    top_k: Optional[int] = None,
    delay: float = 0.0
) -> Dict[str, Any]:
    """Ejecuta el ciclo completo de evaluación RAG sobre el conjunto de preguntas."""
    if not questions_path.exists():
        raise FileNotFoundError(f"Archivo de preguntas no encontrado en: {questions_path}")

    with open(questions_path, "r", encoding="utf-8") as f:
        questions_data = json.load(f)

    if not isinstance(questions_data, list):
        raise ValueError("El archivo de preguntas debe contener una lista JSON de objetos.")

    if limit is not None and limit > 0:
        questions_data = questions_data[:limit]

    # Inicializar componentes del pipeline existente
    settings = get_settings()
    retriever = RetrievalService()
    generator = ResponseGenerator()
    evaluator = RAGEvaluator()
    report = EvaluationReport(output_path=output_path)

    total_q = len(questions_data)
    if verbose:
        print(f"\nIniciando evaluación RAG ({total_q} preguntas)...")
        print(f"Dataset: {questions_path}")
        print(f"Almacenamiento del reporte: {output_path}\n")

    for idx, item in enumerate(questions_data, start=1):
        q_id = item.get("id", idx)
        category = item.get("category", "General")
        question = item.get("question", "").strip()
        expected_docs = item.get("expected_documents", [])

        if verbose:
            print(f"[{idx}/{total_q}] ({category}) {question[:65]}...")

        # 1. Retrieval
        try:
            results = retriever.search(query=question, top_k=top_k)
        except Exception as e:
            if verbose:
                print(f"  [Error en Retrieval]: {e}")
            results = []

        retrieved_docs = extract_doc_names(results)

        # 2. Generation (solo cuando se evalúa faithfulness)
        answer = ""
        context = ""
        if not skip_faithfulness:
            import time
            max_gen_retries = 4
            for attempt in range(max_gen_retries):
                try:
                    gen_res = generator.generate_response(question=question, chunks=results)
                    answer = gen_res.get("answer", "")
                    context = gen_res.get("context", "")
                    break
                except Exception as e:
                    err_str = str(e)
                    if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str) and attempt < max_gen_retries - 1:
                        time.sleep(15.0 * (attempt + 1))
                        continue
                    elif ("503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str) and attempt < max_gen_retries - 1:
                        time.sleep(2.0 * (attempt + 1))
                        continue
                    if verbose:
                        print(f"  [Error en Generación]: {e}")
                    answer = f"Error en generación: {e}"
                    context = ""
                    break
        else:
            answer = "Generación omitida (modo evaluación de recuperación)."
            context = ""

        # 3. Evaluation
        try:
            eval_metrics = evaluator.evaluate(
                question=question,
                expected_documents=expected_docs,
                retrieved_documents=retrieved_docs,
                context=context,
                answer=answer,
                skip_faithfulness=skip_faithfulness
            )
        except Exception as e:
            if verbose:
                print(f"  [Error en Evaluación]: {e}")
            eval_metrics = {
                "precision": {"value": 0.0, "error": str(e)},
                "recall": {"value": 0.0, "error": str(e)},
                "faithfulness": {"faithfulness_score": 0.0, "error": str(e)}
            }

        p_val = eval_metrics["precision"].get("value", 0.0)
        r_val = eval_metrics["recall"].get("value", 0.0)
        f_val = eval_metrics["faithfulness"].get("faithfulness_score", 0.0)

        if verbose:
            print(f"   -> Precision: {p_val:.2f} | Recall: {r_val:.2f} | Faithfulness: {f_val:.2f}")

        # 4. Guardar registro
        report.add_record(
            question=question,
            retrieval_precision=p_val,
            retrieval_recall=r_val,
            faithfulness=f_val,
            expected_documents=expected_docs,
            retrieved_documents=retrieved_docs,
            answer=answer,
            details=eval_metrics,
            category=category,
            question_id=q_id
        )

        if delay > 0 and idx < total_q and not skip_faithfulness:
            import time
            time.sleep(delay)

    # Persistir reporte JSON
    saved_path = report.save_json(output_path)
    summary = report.compute_summary()

    if verbose:
        print(f"\nReporte guardado exitosamente en: {saved_path}\n")

    # Mostrar salida en consola según formato requerido
    print("========================")
    print("RAG Evaluation\n")
    print("Precision:")
    print(f"{summary['mean_precision']:.2f}\n")
    print("Recall:")
    print(f"{summary['mean_recall']:.2f}\n")
    print("Faithfulness:")
    print(f"{summary['mean_faithfulness']:.2f}")
    print("========================\n")

    return {
        "summary": summary,
        "report_path": str(saved_path),
        "total_evaluated": total_q
    }


def parse_arguments() -> argparse.Namespace:
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Microcontroller RAG Assistant - Evaluación Integral (Precision, Recall, Faithfulness)"
    )
    parser.add_argument(
        "--questions",
        type=str,
        default=str(BASE_DIR / "evaluation" / "questions.json"),
        help="Ruta al archivo JSON de preguntas de evaluación"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(BASE_DIR / "evaluation" / "results" / "report.json"),
        help="Ruta donde se guardará el reporte JSON generado"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Límite máximo de preguntas a evaluar (útil para pruebas rápidas)"
    )
    parser.add_argument(
        "--skip-faithfulness",
        action="store_true",
        help="Omitir la evaluación de fidelidad con Gemini (solo evaluar retrieval)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        help="Número de fragmentos a recuperar en cada consulta"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Pausa en segundos entre preguntas para regular cuota de API (ej. 3.0)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Silenciar los logs de progreso intermedios"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    run_evaluation(
        questions_path=Path(args.questions),
        output_path=Path(args.output),
        limit=args.limit,
        skip_faithfulness=args.skip_faithfulness,
        verbose=not args.quiet,
        top_k=args.top_k,
        delay=args.delay
    )
