"""Script de inicio para la interacción por terminal con el Microcontroller RAG Assistant.

Permite realizar consultas técnicas interactivas y recuperar evidencia documental
utilizando búsqueda semántica vectorial pura (Día 12).
"""
import sys
from pathlib import Path

# Asegurar que la raíz del proyecto esté en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.cli.terminal_interface import TerminalRAGInterface


def main():
    """Punto de entrada principal para la terminal de consultas RAG."""
    app = TerminalRAGInterface()
    app.run_interactive_loop()


if __name__ == "__main__":
    main()
