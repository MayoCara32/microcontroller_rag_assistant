"""Interfaz de línea de comandos (CLI) enriquecida para interacción con Microcontrollers AI Copilot."""
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from configs.settings import get_settings
from src.ingestion.pdf_parser import PDFParser
from src.ingestion.document_cleaner import DocumentCleaner
from src.ingestion.metadata_extractor import MetadataExtractor
from src.indexing.chunker import SemanticHardwareChunker
from src.indexing.embedder import EmbeddingService
from src.indexing.vector_indexer import VectorIndexer
from src.retrieval.hybrid_search import HybridSearchEngine
from src.agents.orchestrator import RAGOrchestrator

app = typer.Typer(help="Microcontrollers AI Copilot - CLI RAG especializado en ingeniería de sistemas embebidos.")
console = Console()


@app.command()
def ingest(
    processed_dir: Path = typer.Option(Path("data/processed"), help="Directorio de documentos procesados/MD"),
    metadata_dir: Path = typer.Option(Path("data/metadata"), help="Directorio de metadatos JSON")
):
    """Indexa documentos y metadatos de hojas de datos en el sistema RAG."""
    console.print("[bold green]Iniciando proceso de ingesta e indexación...[/bold green]")
    settings = get_settings()
    parser = PDFParser()
    cleaner = DocumentCleaner()
    metadata_extractor = MetadataExtractor()
    chunker = SemanticHardwareChunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    embedder = EmbeddingService()
    vector_indexer = VectorIndexer()

    all_chunks = []

    # Buscar archivos .md en data/processed
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

    console.print(f"Generando embeddings para [bold]{len(all_chunks)}[/bold] fragmentos...")
    texts = [c["text"] for c in all_chunks]
    embeddings = embedder.get_embeddings(texts)

    console.print("Almacenando en base vectorial ChromaDB...")
    vector_indexer.index_documents(all_chunks, embeddings)
    console.print(f"[bold green]✔ Ingesta completada con éxito: {len(all_chunks)} chunks indexados.[/bold green]")


@app.command()
def query(
    user_query: str = typer.Argument(..., help="Consulta sobre microcontroladores, pines o firmware"),
    mcu: str = typer.Option("Arduino", help="Microcontrolador objetivo (ej. Arduino, ESP32, RP2040)")
):
    """Realiza una consulta técnica al sistema RAG."""
    console.print(f"[bold blue]Consultando Copilot para:[/bold blue] '{user_query}' ({mcu})")
    orchestrator = RAGOrchestrator()
    result = orchestrator.execute_workflow(user_query=user_query, target_mcu=mcu)

    response_md = Markdown(result["response"])
    console.print(Panel(response_md, title="[bold green]Respuesta de Microcontrollers AI Copilot[/bold green]", expand=False))


def run_cli() -> None:
    """Punto de entrada para ejecución interactiva por consola."""
    app()


if __name__ == "__main__":
    run_cli()
