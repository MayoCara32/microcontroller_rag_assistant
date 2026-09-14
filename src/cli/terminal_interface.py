"""Interfaz interactiva de consola para consultas técnicas al Microcontroller RAG Assistant.

Permite a los usuarios consultar la documentación técnica de microcontroladores
mostrando exclusivamente la evidencia recuperada sin síntesis LLM.
"""
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from configs.settings import get_settings
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.retrieval_service import RetrievalService


class TerminalRAGInterface:
    """Gestiona la sesión interactiva en terminal y el formateo de evidencia documental."""

    def __init__(
        self,
        retriever: Optional[DenseRetriever] = None,
        retrieval_service: Optional[RetrievalService] = None,
        console: Optional[Console] = None
    ):
        self.settings = get_settings()
        self.console = console or Console()
        self.retrieval_service = retrieval_service
        if retrieval_service is not None:
            self.service = retrieval_service
            self.retriever = getattr(retrieval_service, "retriever", retriever or DenseRetriever())
        elif retriever is not None:
            self.retriever = retriever
            self.service = RetrievalService(retriever=retriever)
        else:
            self.service = RetrievalService()
            self.retriever = self.service.retriever

        self.sample_queries = [
            "¿Cuál es el voltaje máximo de operación del ATmega328P?",
            "¿Cómo funciona el ADC del ESP32?",
            "Configuración del bus I2C y líneas SDA SCL"
        ]

    def display_header(self) -> None:
        """Imprime el encabezado técnico del sistema en la consola."""
        self.console.print("=" * 70, style="bold cyan")
        self.console.print("  MICROCONTROLLER RAG ASSISTANT - TERMINAL DE CONSULTAS TÉCNICAS", style="bold green")
        self.console.print("=" * 70, style="bold cyan")
        self.console.print(f"[dim]Modelo de Embeddings: {self.settings.DEFAULT_EMBEDDING_MODEL} (RETRIEVAL_QUERY)[/dim]")
        self.console.print(f"[dim]Almacén Vectorial: ChromaDB ({self.settings.STORAGE_VECTOR_DIR})[/dim]")
        self.console.print("[dim]Modo: Recuperación de Evidencia Pura (Sin Generación LLM)[/dim]\n")

    def display_sample_queries(self) -> None:
        """Muestra ejemplos sugeridos para el usuario."""
        self.console.print("[bold yellow]Consultas técnicas de ejemplo:[/bold yellow]")
        for i, q in enumerate(self.sample_queries, 1):
            self.console.print(f"  {i}. {q}")
        self.console.print("  (Escribe tu pregunta o selecciona 1-3. Escribe 'q' o 'exit' para salir)\n")

    def format_chunk_panel(self, rank: int, chunk: Dict[str, Any]) -> Panel:
        """Formatea un fragmento recuperado con sus metadatos técnicos en un panel estilizado."""
        chunk_id = chunk.get("chunk_id", "desconocido")
        meta = chunk.get("metadata", {})
        doc = meta.get("file_name", "Desconocido")
        category = meta.get("category", "N/A")
        component = meta.get("component", "N/A")
        topic = meta.get("topic") or meta.get("section") or "General"
        dist = chunk.get("distance", 0.0)
        content = chunk.get("text", "")

        panel_text = (
            f"[bold cyan]Chunk ID:[/bold cyan] {chunk_id}\n"
            f"[bold cyan]Documento Fuente:[/bold cyan] {doc}\n"
            f"[bold cyan]Categoría:[/bold cyan] {category}\n"
            f"[bold cyan]Componente:[/bold cyan] {component}\n"
            f"[bold cyan]Tema / Sección:[/bold cyan] {topic}\n"
            f"[bold cyan]Distancia L2:[/bold cyan] {dist:.4f}\n\n"
            f"[bold yellow]Contenido del Fragmento:[/bold yellow]\n{content}"
        )
        return Panel(panel_text, title=f"[bold green]Evidencia Recuperada #{rank}[/bold green]", expand=False)

    def display_results(self, query: str, results: List[Dict[str, Any]]) -> None:
        """Renderiza los resultados recuperados o el mensaje de ausencia de contexto."""
        self.console.print(f"\n[bold blue]Consulta Procesada:[/bold blue] {query}\n")

        if not results:
            self.console.print(
                Panel(
                    "[yellow]No se encontró información suficiente en la base documental para la consulta solicitada.[/yellow]",
                    title="[bold red]Sin Coincidencias[/bold red]",
                    expand=False
                )
            )
            self.console.print()
            return

        self.console.print(f"[bold green]Se recuperaron {len(results)} fragmentos relevantes:[/bold green]\n")
        for rank, res in enumerate(results, 1):
            panel = self.format_chunk_panel(rank, res)
            self.console.print(panel)
            self.console.print()

    def process_query(self, query_text: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Procesa una consulta técnica y ejecuta la recuperación semántica."""
        if not query_text or not query_text.strip():
            return []

        clean_query = query_text.strip()
        # Mapeo de atajos numéricos
        if clean_query in ["1", "2", "3"] and int(clean_query) <= len(self.sample_queries):
            clean_query = self.sample_queries[int(clean_query) - 1]

        try:
            if self.retrieval_service is not None:
                results = self.retrieval_service.search(query=clean_query, top_k=top_k)
            else:
                results = self.retriever.retrieve(query=clean_query, top_k=top_k)
            return results
        except Exception as e:
            self.console.print(f"[bold red]Error durante la recuperación vectorial:[/bold red] {e}")
            return []

    def run_interactive_loop(self) -> None:
        """Inicia el bucle interactivo de terminal."""
        self.display_header()
        self.display_sample_queries()

        while True:
            try:
                user_input = self.console.input("[bold cyan]Pregunta técnica > [/bold cyan]").strip()
            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[green]Sesión finalizada por el usuario.[/green]")
                break

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q", "salir"]:
                self.console.print("[green]Saliendo del asistente de consultas técnicas. ¡Hasta pronto![/green]")
                break

            # Resolver consulta si es selección rápida
            query_to_execute = user_input
            if user_input in ["1", "2", "3"]:
                query_to_execute = self.sample_queries[int(user_input) - 1]

            results = self.process_query(query_to_execute)
            self.display_results(query_to_execute, results)
