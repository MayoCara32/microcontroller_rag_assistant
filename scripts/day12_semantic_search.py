"""Script Didáctico del Día 12: Búsqueda Semántica Vectorial Pura en Microcontrollers RAG Assistant.

Demuestra el flujo básico de recuperación sin generación aumentada con LLM:
Consulta -> Embedding (RETRIEVAL_QUERY) -> ChromaDB -> Top-5 Chunks -> Visualización de Evidencia.
"""
import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from rich.console import Console
from rich.panel import Panel
from configs.settings import get_settings
from src.indexing.embedder import EmbeddingService
from src.indexing.vector_indexer import VectorIndexer


def run_semantic_search_session():
    """Ejecuta una sesión interactiva o de demostración de búsqueda semántica (Día 12)."""
    console = Console()
    settings = get_settings()

    console.print("=" * 65, style="bold cyan")
    console.print("  MICROCONTROLLER RAG ASSISTANT - BÚSQUEDA SEMÁNTICA (DÍA 12)", style="bold green")
    console.print("=" * 65, style="bold cyan")
    console.print(f"[dim]Modelo de Embedding: {settings.DEFAULT_EMBEDDING_MODEL} (task_type: RETRIEVAL_QUERY)[/dim]")
    console.print(f"[dim]Vector Store: ChromaDB ({settings.STORAGE_VECTOR_DIR})[/dim]\n")

    embedder = EmbeddingService()
    indexer = VectorIndexer()

    # Consultas de demostración iniciales
    sample_queries = [
        "¿Cuál es el voltaje máximo de operación del ATmega328P?",
        "¿Cómo funciona el ADC del ESP32?",
        "Configuración del bus I2C y líneas SDA SCL"
    ]

    console.print("[bold yellow]Ejemplos de consultas técnicas disponibles:[/bold yellow]")
    for i, q in enumerate(sample_queries, 1):
        console.print(f"  {i}. {q}")
    console.print("  (O escribe tu propia consulta. Presiona 'q' o 'exit' para salir)\n")

    while True:
        try:
            user_input = console.input("[bold cyan]Pregunta:[/bold cyan] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[green]Sesión finalizada.[/green]")
            break

        if not user_input or user_input.lower() in ["exit", "quit", "q", "salir"]:
            console.print("[green]Saliendo del buscador semántico.[/green]")
            break

        # Permitir seleccionar por número de ejemplo
        if user_input in ["1", "2", "3"]:
            query_text = sample_queries[int(user_input) - 1]
            console.print(f"[bold]Seleccionada:[/bold] {query_text}")
        else:
            query_text = user_input

        console.print(f"\n[bold blue]Consulta:[/bold blue]\n{query_text}\n")

        # 1. Generación de embedding de consulta
        try:
            query_vec = embedder.embed_query(query_text)
        except Exception as e:
            console.print(f"[bold red]Error calculando embedding:[/bold red] {e}")
            continue

        # 2. Recuperación en ChromaDB
        results = indexer.search(query_embedding=query_vec, top_k=5)

        if not results:
            console.print("[yellow]No se encontraron fragmentos en la base vectorial para esta consulta.[/yellow]\n")
            continue

        # 3. Mostrar resultados en el formato didáctico exacto del Día 12
        for rank, res in enumerate(results, 1):
            chunk_id = res.get("chunk_id", "desconocido")
            meta = res.get("metadata", {})
            doc = meta.get("file_name", "Desconocido")
            category = meta.get("category", "N/A")
            component = meta.get("component", "N/A")
            topic = meta.get("topic") or meta.get("section") or "General"
            dist = res.get("distance", 0.0)
            content = res.get("text", "")

            panel_text = (
                f"[bold]Chunk ID:[/bold] {chunk_id}\n"
                f"[bold]Documento:[/bold] {doc}\n"
                f"[bold]Categoría:[/bold] {category}\n"
                f"[bold]Componente:[/bold] {component}\n"
                f"[bold]Tema:[/bold] {topic}\n"
                f"[bold]Distancia L2:[/bold] {dist:.4f}\n\n"
                f"[bold]Fragmento:[/bold]\n{content}"
            )
            console.print(Panel(panel_text, title=f"[bold green]Resultado {rank}[/bold green]", expand=False))
            console.print()


if __name__ == "__main__":
    run_semantic_search_session()
