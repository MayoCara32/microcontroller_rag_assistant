"""Índice BM25 para búsqueda léxica basada en coincidencia exacta de términos."""
import re
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi


class BM25Index:
    """Gestiona la tokenización e indexación textual BM25 de los chunks documentales."""

    def __init__(self):
        self.corpus_chunks: List[Dict[str, Any]] = []
        self.bm25: Optional[BM25Okapi] = None

    def tokenize(self, text: str) -> List[str]:
        """Tokenizador adaptado a términos técnicos (registros, pines, hexadecimales, modelos)."""
        if not text:
            return []
        return re.findall(r'\w+|0x[0-9a-fA-F]+', text.lower())

    def fit(self, chunks: List[Dict[str, Any]]) -> None:
        """Construye el índice BM25 a partir de una lista de chunks."""
        self.corpus_chunks = chunks
        tokenized_corpus = [self.tokenize(c.get("text") or c.get("texto", "")) for c in chunks]
        if tokenized_corpus:
            self.bm25 = BM25Okapi(tokenized_corpus)
        else:
            self.bm25 = None

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Busca coincidencias textuales utilizando BM25 y retorna chunks anotados con score."""
        if not self.bm25 or not self.corpus_chunks:
            return []

        tokenized_query = self.tokenize(query)
        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)
        query_set = set(tokenized_query)

        # Filtrar candidatos con score > 0 o coincidencia directa de token
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            chunk = self.corpus_chunks[idx]
            chunk_tokens = set(self.tokenize(chunk.get("text") or chunk.get("texto", "")))

            # Incluir si el score de BM25 es mayor a cero o si contiene al menos un token coincidente
            if score > 0 or bool(query_set & chunk_tokens):
                chunk_id = chunk.get("chunk_id") or chunk.get("id") or f"bm25_{idx}"
                text = chunk.get("text") or chunk.get("texto", "")
                meta = chunk.get("metadata") or {}

                results.append({
                    "chunk_id": str(chunk_id),
                    "id": str(chunk_id),
                    "text": text,
                    "texto": text,
                    "document": text,
                    "metadata": meta,
                    "score": score if score > 0 else 0.1,
                    "distance": 0.0,
                    "distancia": 0.0
                })

            if len(results) >= top_k:
                break

        return results
