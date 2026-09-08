"""Servicio de cálculo de embeddings densos para texto técnico."""
from typing import List


class EmbeddingService:
    """Genera representaciones vectoriales densas para consultas y chunks documentales."""

    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name

    def embed_text(self, text: str) -> List[float]:
        """Calcula el vector para un único texto."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Calcula vectores en lote."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")
