"""Interfaz de terminal interactiva para el modo CHAT RAG de Microcontroller RAG Assistant."""
import sys
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any

# Asegurar que la raíz del proyecto esté en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.retrieval.retrieval_service import RetrievalService
from src.retrieval.query_analyzer import QueryAnalyzer
from src.retrieval.filter_builder import MetadataFilterBuilder
from src.generation.response_generator import ResponseGenerator


def print_header(chat_mode: bool = True) -> None:
    """Muestra el encabezado del sistema según el modo."""
    if chat_mode:
        print("========================================")
        print("Microcontroller RAG Assistant")
        print("Asistente técnico basado en documentación")
        print("========================================\n")
    else:
        print("================================")
        print("Microcontroller RAG Assistant")
        print("================================\n")


def display_search_results(results: List[Dict[str, Any]]) -> None:
    """Muestra los resultados formateados en la terminal (modo evidencia pura)."""
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


def display_debug_info(
    question: str,
    results: List[Dict[str, Any]],
    gen_result: Optional[Dict[str, Any]] = None,
    analysis: Optional[Dict[str, Any]] = None,
    filters: Optional[Dict[str, Any]] = None
) -> None:
    """Muestra información detallada y pedagógica de depuración sin exponer claves ni credenciales."""
    import json
    gen_data = gen_result or {}
    print("\n" + "=" * 40)
    print("MODO DEBUG")
    print("=" * 40)
    print(f"\nPREGUNTA:\n{question}\n")

    if analysis is not None:
        hw = analysis.get("hardware_family") or analysis.get("board") or "N/A"
        comp = analysis.get("component") or "N/A"
        print("Análisis:")
        print(f"Hardware:\n{hw}")
        print(f"Componente:\n{comp}")
        print("\nFiltros generados:")
        print(json.dumps(filters or {}, indent=2))
        print(f"\nBúsqueda:\n{len(results)} documentos encontrados.\n")

    print("RESULTADOS RETRIEVAL:")
    if not results:
        print("  (Sin chunks recuperados)")
    else:
        found_docs: List[str] = []
        for r in results:
            meta = r.get("metadata", {})
            doc = meta.get("component") or meta.get("file_name") or meta.get("document") or "Desconocido"
            if doc not in found_docs:
                found_docs.append(doc)

        print("Resultados:")
        for idx, doc in enumerate(found_docs, start=1):
            print(f"{idx}.\n{doc}\n")

        for r in results:
            meta = r.get("metadata", {})
            doc = meta.get("file_name") or meta.get("document") or "Desconocido"
            chunk_id = r.get("chunk_id", "N/A")
            dist = r.get("distancia", r.get("distance", 0.0))
            print(f"Documento: {doc}")
            print(f"Chunk: {chunk_id}")
            print(f"Score / Distancia: {dist:.4f}")
            print("-" * 20)

    print(f"\nCONTEXTO ENVIADO A GEMINI:\n{gen_data.get('context', '(Vacío)')}\n")
    print(f"MODELO UTILIZADO:\n{gen_data.get('model', 'Desconocido')}\n")
    print(f"TEMPERATURA:\n{gen_data.get('temperature', '0.95')}\n")
    print(f"RESPUESTA:\n{gen_data.get('answer', '')}\n")
    print("=" * 40 + "\n")


def run_cli_chat(
    retrieval_service: Optional[RetrievalService] = None,
    response_generator: Optional[ResponseGenerator] = None,
    debug: bool = False,
    chat_mode: Optional[bool] = None
) -> None:
    """Inicia el bucle interactivo de terminal.

    Por defecto ejecuta el modo CHAT RAG completo con Gemini. Si retrieval_service
    se proporciona aislado sin generador y sin especificar chat_mode, preserva
    modo de recuperación pura para compatibilidad hacia atrás.
    """
    if chat_mode is None:
        chat_mode = not (retrieval_service is not None and response_generator is None)

    print_header(chat_mode=chat_mode)

    try:
        retriever = retrieval_service or RetrievalService()
    except Exception as e:
        print(f"[Error al inicializar servicio de recuperación]: {e}")
        return

    analyzer = QueryAnalyzer()
    filter_builder = MetadataFilterBuilder()

    generator: Optional[ResponseGenerator] = None
    if chat_mode:
        try:
            generator = response_generator or ResponseGenerator()
        except Exception as e:
            print(f"[Error al inicializar generador Gemini]: {e}")
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

        if user_input.lower() in ["exit", "salir", "quit", "q"]:
            print("Saliendo de Microcontroller RAG Assistant.")
            break

        # Análisis de intención y construcción de filtros (Día 16)
        analysis = analyzer.analyze(user_input)
        filters = filter_builder.build_from_analysis(analysis)

        if not chat_mode:
            # Modo recuperación pura (Día 12)
            print("\nSistema:")
            print("- generando embedding...")
            print("- buscando información...")
            try:
                results = retriever.search(query=user_input, filters=filters)
                display_search_results(results)
                if debug:
                    display_debug_info(user_input, results, analysis=analysis, filters=filters)
            except FileNotFoundError as fnf_err:
                print(f"\n[Error de Base Vectorial]: {fnf_err}\n")
            except RuntimeError as rt_err:
                print(f"\n[Error de Recuperación/Embedding]: {rt_err}\n")
            except Exception as err:
                print(f"\n[Error Inesperado]: {err}\n")
            continue

        # Modo CHAT RAG con Gemini (Día 13) y Metadata Filtering (Día 16)
        print("\nBuscando información...\n")

        try:
            # 1. Recuperación vectorial con filtros de metadata
            results = retriever.search(query=user_input, filters=filters)

            # Extraer documentos únicos encontrados
            found_docs: List[str] = []
            for res in results:
                meta = res.get("metadata", {})
                doc_name = (
                    meta.get("file_name")
                    or meta.get("document")
                    or meta.get("source")
                    or "Desconocido"
                )
                if doc_name not in found_docs:
                    found_docs.append(doc_name)

            print("Documentos encontrados:")
            if found_docs:
                for idx, doc in enumerate(found_docs, start=1):
                    print(f"{idx}. {doc}")
            else:
                print("Ninguno")

            # 2. Generación de respuesta con Gemini
            print("\nGenerando respuesta...\n")
            assert generator is not None
            gen_result = generator.generate_response(question=user_input, chunks=results)

            # 3. Mostrar respuesta al usuario
            print("Respuesta:")
            print(gen_result.get("answer", ""))
            print()

            sources = gen_result.get("sources", [])
            if sources:
                print("Fuentes:")
                for src in sources:
                    print(f"- {src}")
            else:
                print("Fuentes:")
                print("- Ninguna (información no presente en la documentación)")

            print("\n========================================\n")

            # 4. Modo depuración educativo
            if debug:
                display_debug_info(user_input, results, gen_result=gen_result, analysis=analysis, filters=filters)

        except FileNotFoundError as fnf_err:
            print(f"\n[Error de Base Vectorial]: {fnf_err}\n")
        except RuntimeError as rt_err:
            print(f"\n[Error de Recuperación/Generación]: {rt_err}\n")
        except Exception as err:
            print(f"\n[Error Inesperado]: {err}\n")


def parse_arguments() -> argparse.Namespace:
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Microcontroller RAG Assistant - Terminal Chat"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Habilitar modo de depuración para inspeccionar chunks y contexto enviado"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    run_cli_chat(debug=args.debug, chat_mode=True)
