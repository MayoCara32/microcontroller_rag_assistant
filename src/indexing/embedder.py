"""Servicio de cálculo de embeddings densos con soporte para Google Gemini (Día 12) y OpenAI."""
import os
import hashlib
import math
from typing import List, Optional
from configs.settings import get_settings
from src.core.interfaces import BaseEmbedder


class EmbeddingService(BaseEmbedder):
    """Genera representaciones vectoriales densas para consultas y fragmentos documentales."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        dimension: Optional[int] = None,
        api_key: Optional[str] = None,
        allow_test_embeddings: Optional[bool] = None
    ):
        settings = get_settings()
        self.settings = settings
        self.provider = (provider or settings.EMBEDDING_PROVIDER).lower()
        self.model_name = model_name or settings.DEFAULT_EMBEDDING_MODEL
        self.dimension = dimension or settings.EMBEDDING_DIMENSION
        self.api_key = api_key if api_key is not None else (settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY"))
        self.allow_test_embeddings = (
            allow_test_embeddings if allow_test_embeddings is not None else settings.ALLOW_TEST_EMBEDDINGS
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para fragmentos documentales usando modo RETRIEVAL_DOCUMENT."""
        if not texts:
            return []

        if self.provider == "google":
            return self._embed_google(texts, task_type="RETRIEVAL_DOCUMENT")
        elif self.provider == "openai":
            return self._embed_openai(texts)
        else:
            if self.allow_test_embeddings:
                return [self._hash_fallback_embedding(t, self.dimension) for t in texts]
            raise ValueError(f"Proveedor de embeddings '{self.provider}' no soportado.")

    def embed_query(self, query: str) -> List[float]:
        """Genera embedding para una consulta de búsqueda usando modo RETRIEVAL_QUERY."""
        if not query or not query.strip():
            return [0.0] * self.dimension

        if self.provider == "google":
            res = self._embed_google([query], task_type="RETRIEVAL_QUERY")
            return res[0] if res else [0.0] * self.dimension
        elif self.provider == "openai":
            res = self._embed_openai([query])
            return res[0] if res else [0.0] * self.dimension
        else:
            if self.allow_test_embeddings:
                return self._hash_fallback_embedding(query, self.dimension)
            raise ValueError(f"Proveedor de embeddings '{self.provider}' no soportado.")

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Alias retrocompatible para embed_documents."""
        return self.embed_documents(texts)

    def get_query_embedding(self, query: str) -> List[float]:
        """Alias retrocompatible para embed_query."""
        return self.embed_query(query)

    def _embed_google(self, texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> List[List[float]]:
        """Invoca la API de Gemini usando google-genai SDK y parámetros estructurados."""
        api_key = self.api_key
        if not api_key:
            if self.allow_test_embeddings:
                return [self._hash_fallback_embedding(t, self.dimension) for t in texts]
            raise ValueError(
                "GEMINI_API_KEY no configurada. Configure su API key en el archivo .env o en variables de entorno."
            )

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            all_embeddings = []

            # Procesar en lotes de máximo 50 textos para evitar límites de payload
            batch_size = 50
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                config = types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=self.dimension
                )
                response = client.models.embed_content(
                    model=self.model_name,
                    contents=batch,
                    config=config
                )

                if hasattr(response, "embeddings") and response.embeddings:
                    for item in response.embeddings:
                        all_embeddings.append(list(item.values))
                elif hasattr(response, "embedding") and response.embedding:
                    all_embeddings.append(list(response.embedding.values))
                else:
                    raise RuntimeError("La respuesta de Gemini no contiene vectores de embedding.")

            return all_embeddings

        except Exception as e:
            if self.allow_test_embeddings:
                return [self._hash_fallback_embedding(t, self.dimension) for t in texts]
            raise RuntimeError(
                f"Error al generar embeddings con proveedor '{self.provider}' (modelo '{self.model_name}', task '{task_type}'): {str(e)}"
            ) from e

    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """Generador alternativo para OpenAI si está configurado explícitamente."""
        api_key = self.api_key or self.settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            if self.allow_test_embeddings:
                return [self._hash_fallback_embedding(t, self.dimension) for t in texts]
            raise ValueError(
                "OPENAI_API_KEY no configurada. Configure su API key en el archivo .env o en variables de entorno."
            )

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.embeddings.create(
                input=texts,
                model=self.model_name
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            if self.allow_test_embeddings:
                return [self._hash_fallback_embedding(t, self.dimension) for t in texts]
            raise RuntimeError(
                f"Error al generar embeddings con OpenAI (modelo '{self.model_name}'): {str(e)}"
            ) from e

    def _hash_fallback_embedding(self, text: str, dim: int = 768) -> List[float]:
        """Genera un vector determinista pseudo-aleatorio normalizado basado en hash exclusivamente para pruebas locales."""
        val = hashlib.sha256(text.encode("utf-8")).digest()
        vec = []
        for i in range(dim):
            b = val[i % len(val)]
            vec.append((b / 255.0) * 2 - 1)

        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]
