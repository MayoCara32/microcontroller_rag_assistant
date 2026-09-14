import sys
from pathlib import Path
from typing import Optional

# Asegurar que la raíz del proyecto esté en sys.path para ejecuciones directas
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from configs.settings import get_settings
from src.ingestion.pdf_parser import PDFParser
from src.ingestion.document_cleaner import DocumentCleaner
from src.ingestion.metadata_extractor import MetadataExtractor
from src.indexing.chunker import SemanticHardwareChunker
from src.indexing.embedder import EmbeddingService
from src.indexing.vector_indexer import VectorIndexer
from src.agents.orchestrator import RAGOrchestrator

app = typer.Typer(help="Microcontroller RAG Assistant - CLI de Ingesta y Búsqueda Semántica Vectorial (Día 12).")
console = Console()


@app.command()
def ingest(
    processed_dir: Path = typer.Option(Path("data/processed"), help="Directorio de documentos procesados/MD"),
    metadata_dir: Path = typer.Option(Path("data/metadata"), help="Directorio de metadatos JSON")
):
    """Indexa documentos y metadatos de hojas de datos en ChromaDB (Día 12)."""
    console.print("[bold green]Iniciando proceso de ingesta e indexación vectorial (Día 12)...[/bold green]")
    settings = get_settings()
    parser = PDFParser()
    cleaner = DocumentCleaner()
    metadata_extractor = MetadataExtractor()
    chunker = SemanticHardwareChunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    embedder = EmbeddingService()
    vector_indexer = VectorIndexer()

    all_chunks = []

    # Buscar archivos .md y .txt en data/processed
    if processed_dir.exists():
        md_files = list(processed_dir.glob("**/*.md")) + list(processed_dir.glob("**/*.txt"))
        for md_file in md_files:
            console.print(f"Procesando: [cyan]{md_file.name}[/cyan]")
            doc_data = parser.parse_document(md_file)
            cleaned_text = cleaner.clean(doc_data["text"])

            meta_file = metadata_dir / md_file.parent.name / (md_file.stem + ".json")
            meta = metadata_extractor.extract_metadata(cleaned_text, md_file.name, meta_file)

            chunks = chunker.chunk(cleaned_text, metadata=meta)
            all_chunks.extend(chunks)

    if not all_chunks:
        console.print("[bold yellow]No se encontraron documentos en data/processed para indexar.[/bold yellow]")
        return

    console.print(f"Generando embeddings ({settings.DEFAULT_EMBEDDING_MODEL}) para [bold]{len(all_chunks)}[/bold] fragmentos...")
    texts = [c["text"] for c in all_chunks]
    embeddings = embedder.embed_documents(texts)

    console.print("Almacenando en base vectorial ChromaDB...")
    vector_indexer.index_documents(all_chunks, embeddings)
    console.print(f"[bold green]✔ Ingesta completada con éxito: {len(all_chunks)} chunks indexados en ChromaDB.[/bold green]")


@app.command()
def query(
    user_query: str = typer.Argument(..., help="Consulta técnica sobre microcontroladores, pines o registros"),
    mcu: str = typer.Option("Arduino", help="Microcontrolador objetivo"),
    top_k: int = typer.Option(5, help="Número de fragmentos vectoriales a recuperar")
):
    """Ejecuta una búsqueda semántica vectorial en ChromaDB y muestra los Top-K chunks recuperados."""
    console.print(f"[bold blue]Recuperación Vectorial para:[/bold blue] '{user_query}'")
    orchestrator = RAGOrchestrator()
    result = orchestrator.execute_workflow(user_query=user_query, target_mcu=mcu, top_k=top_k)

    chunks = result.get("results", [])
    if not chunks:
        console.print("[yellow]No se encontraron fragmentos relevantes en la base vectorial.[/yellow]")
        return

    table = Table(title=f"Top {len(chunks)} Chunks Recuperados (Día 12 - Sin Generación LLM)")
    table.add_column("#", justify="center", style="bold cyan")
    table.add_column("Chunk ID", style="bold")
    table.add_column("Documento", style="green")
    table.add_column("Componente", style="magenta")
    table.add_column("Distancia L2", justify="right", style="yellow")

    for idx, c in enumerate(chunks, 1):
        meta = c.get("metadata", {})
        table.add_row(
            str(idx),
            str(c.get("chunk_id", "")),
            str(meta.get("file_name", "Desconocido")),
            str(meta.get("component", "N/A")),
            f"{c.get('distance', 0.0):.4f}"
        )

    console.print(table)

    for idx, c in enumerate(chunks, 1):
        meta = c.get("metadata", {})
        panel_content = (
            f"[bold green]Documento:[/bold green] {meta.get('file_name')} | "
            f"[bold green]Componente:[/bold green] {meta.get('component')} | "
            f"[bold yellow]Distancia:[/bold yellow] {c.get('distance', 0.0):.4f}\n\n"
            f"{c.get('text', '')}"
        )
        console.print(Panel(panel_content, title=f"Resultado {idx}: {c.get('chunk_id')}", expand=False))


def run_cli() -> None:
    """Punto de entrada para ejecución interactiva por consola."""
    app()


if __name__ == "__main__":
    run_cli()
