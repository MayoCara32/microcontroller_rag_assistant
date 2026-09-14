"""Interfaz de terminal interactiva para la recuperación de evidencia documental en la base vectorial del proyecto."""
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Asegurar que la raíz del proyecto esté en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.retrieval.retrieval_service import RetrievalService


def print_header() -> None:
    """Muestra el encabezado del sistema."""
    print("================================")
    print("Microcontroller RAG Assistant")
    print("================================\n")


def display_search_results(results: List[Dict[str, Any]]) -> None:
    """Muestra los resultados formateados en la terminal."""
    if not results:
        print("\n[Resultado]: No se encontró información suficiente en la base documental para la consulta solicitada.\n")
        return

    print()
    for index, res in enumerate(results, start=1):
        metadata = res.get("metadata", {})
        doc = metadata.get("file_name") or metadata.get("document") or metadata.get("title") or "Desconocido"
        category = metadata.get("category") or metadata.get("familia") or metadata.get("component") or "General"
        fragmento = res.get("texto") or res.get("text") or ""

        print(f"Resultado {index}\n")
        print("Documento:")
        print(f"{doc}\n")
        print("Categoría:")
        print(f"{category}\n")
        print("Fragmento:")
        print(f"{fragmento}\n")
        print("-" * 32 + "\n")


def run_cli_chat(retrieval_service: Optional[RetrievalService] = None) -> None:
    """Inicia el bucle interactivo de la terminal de consultas."""
    print_header()

    try:
        service = retrieval_service or RetrievalService()
    except Exception as e:
        print(f"[Error al inicializar el servicio de recuperación]: {e}")
        return

    while True:
        try:
            print("Pregunta:")
            user_input = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada por el usuario. Saliendo...")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "q", "salir"]:
            print("Saliendo de Microcontroller RAG Assistant.")
            break

        print("\nSistema:")
        print("- generando embedding...")
        print("- buscando información...")

        try:
            results = service.search(query=user_input)
            display_search_results(results)
        except FileNotFoundError as fnf_err:
            print(f"\n[Error de Base Vectorial]: {fnf_err}\n")
        except RuntimeError as rt_err:
            print(f"\n[Error de Recuperación/Embedding]: {rt_err}\n")
        except Exception as err:
            print(f"\n[Error Inesperado]: {err}\n")


if __name__ == "__main__":
    run_cli_chat()
