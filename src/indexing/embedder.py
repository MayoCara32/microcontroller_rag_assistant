"""Servicio de cálculo de embeddings densos para texto técnico con soporte multimodelo (Google GenAI / OpenAI / Fallback)."""
import os
from typing import List
from configs.settings import get_settings
from src.core.interfaces import BaseEmbedder


class EmbeddingService(BaseEmbedder):
    """Genera representaciones vectoriales densas para consultas y chunks documentales."""

    def __init__(self, provider: str = None, model_name: str = None):
        settings = get_settings()
        self.provider = provider or settings.EMBEDDING_PROVIDER
        self.model_name = model_name or settings.DEFAULT_EMBEDDING_MODEL
        self.settings = settings

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Implementación de la interfaz BaseEmbedder."""
        return self.embed_batch(texts)

    def get_query_embedding(self, query: str) -> List[float]:
        """Implementación de la interfaz BaseEmbedder."""
        return self.embed_text(query)

    def embed_text(self, text: str) -> List[float]:
        """Calcula el vector para un único texto."""
        res = self.embed_batch([text])
        return res[0] if res else []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Calcula vectores en lote."""
        if not texts:
            return []

        # Intento de generación con Google GenAI SDK
        if self.provider == "google" and (self.settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")):
            try:
                from google import genai
                client = genai.Client(api_key=self.settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY"))
                response = client.models.embed_content(
                    model=self.model_name,
                    contents=texts
                )
                return [e.values for e in response.embeddings]
            except Exception:
                pass

        # Intento de generación con OpenAI SDK
        if self.provider == "openai" and (self.settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY"))
                response = client.embeddings.create(
                    input=texts,
                    model=self.model_name
                )
                return [item.embedding for item in response.data]
            except Exception:
                pass

        # Fallback local determinista para testing y entornos offline
        return [self._hash_fallback_embedding(t) for t in texts]

    def _hash_fallback_embedding(self, text: str, dim: int = 768) -> List[float]:
        """Genera un vector determinista pseudo-aleatorio normalizado basado en hash para pruebas en entorno offline."""
        import hashlib
        import math

        val = hashlib.sha256(text.encode("utf-8")).digest()
        vec = []
        for i in range(dim):
            b = val[i % len(val)]
            vec.append((b / 255.0) * 2 - 1)

        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]
