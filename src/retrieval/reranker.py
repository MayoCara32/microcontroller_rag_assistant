"""[COMPONENTE AISLADO - RESERVADO PARA DÍA 13+]
Reordenamiento contextual de alta precisión mediante FlashRank / Cross-Encoder.
No participa en el pipeline activo de Día 12.
"""
from typing import List, Dict, Any


class CrossEncoderReranker:
    """Reordena los candidatos para priorizar chunks con datos eléctricos críticos y tablas de mapeo."""

    def __init__(self, model_name: str = "ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """Aplica cross-encoding/FlashRank y devuelve los top_n fragmentos más relevantes."""
        if not documents:
            return []

        try:
            from flashrank import Ranker, RerankRequest
            ranker = Ranker(model_name="ms-marco-MiniLM-L-6-v2")
            passages = [{"id": d.get("chunk_id", str(i)), "text": d.get("text", "")} for i, d in enumerate(documents)]
            rerank_req = RerankRequest(query=query, passages=passages)
            results = ranker.rerank(rerank_req)

            res_map = {r["id"]: r.get("score", 0.0) for r in results}
            for doc in documents:
                cid = doc.get("chunk_id", "")
                if cid in res_map:
                    doc["rerank_score"] = res_map[cid]

            sorted_docs = sorted(documents, key=lambda x: x.get("rerank_score", x.get("fused_score", 0.0)), reverse=True)
            return sorted_docs[:top_n]
        except Exception:
            # Fallback a conservacion de ranking de fusion si flashrank no esta disponible localmente
            return documents[:top_n]
