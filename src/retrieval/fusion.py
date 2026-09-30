"""Estrategias de fusión de resultados para búsqueda híbrida (Día 17)."""
from typing import List, Dict, Any, Optional
from configs.settings import get_settings


class WeightedScoreFusion:
    """Implementa Weighted Score Fusion normalizando y combinando resultados densos y léxicos."""

    def __init__(
        self,
        dense_weight: Optional[float] = None,
        keyword_weight: Optional[float] = None
    ):
        settings = get_settings()
        self.dense_weight = dense_weight if dense_weight is not None else settings.DENSE_WEIGHT
        self.keyword_weight = keyword_weight if keyword_weight is not None else settings.KEYWORD_WEIGHT

    def _min_max_normalize(self, scores: List[float]) -> List[float]:
        """Normaliza una lista de scores al rango [0, 1]."""
        if not scores:
            return []
        min_s = min(scores)
        max_s = max(scores)
        if max_s == min_s:
            return [1.0 if max_s > 0 else 0.0 for _ in scores]
        return [(s - min_s) / (max_s - min_s) for s in scores]

    def fuse(
        self,
        dense_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Combina y ordena resultados densos y por palabras clave usando pesos configurables."""
        chunks_map: Dict[str, Dict[str, Any]] = {}
        dense_scores_map: Dict[str, float] = {}
        keyword_scores_map: Dict[str, float] = {}

        # 1. Mapear resultados densos
        if dense_results:
            d_raw_scores = [float(item.get("score", 0.0)) for item in dense_results]
            d_norm_scores = self._min_max_normalize(d_raw_scores)
            for item, norm_s in zip(dense_results, d_norm_scores):
                cid = str(item.get("chunk_id") or item.get("id"))
                chunks_map[cid] = item
                dense_scores_map[cid] = norm_s

        # 2. Mapear resultados léxicos (keyword/BM25)
        if keyword_results:
            k_raw_scores = [float(item.get("score", 0.0)) for item in keyword_results]
            k_norm_scores = self._min_max_normalize(k_raw_scores)
            for item, norm_s in zip(keyword_results, k_norm_scores):
                cid = str(item.get("chunk_id") or item.get("id"))
                if cid not in chunks_map:
                    chunks_map[cid] = item
                keyword_scores_map[cid] = norm_s

        # 3. Calcular Weighted Hybrid Score
        fused_list: List[Dict[str, Any]] = []
        all_cids = set(dense_scores_map.keys()) | set(keyword_scores_map.keys())

        for cid in all_cids:
            d_score = dense_scores_map.get(cid, 0.0)
            k_score = keyword_scores_map.get(cid, 0.0)

            hybrid_score = (self.dense_weight * d_score) + (self.keyword_weight * k_score)

            item = dict(chunks_map[cid])
            item["dense_score"] = d_score
            item["keyword_score"] = k_score
            item["hybrid_score"] = hybrid_score
            item["score"] = hybrid_score  # compatibilidad con interfaz genérica

            fused_list.append(item)

        # 4. Ordenar descendente por hybrid_score
        fused_list.sort(key=lambda x: x["hybrid_score"], reverse=True)

        return fused_list[:top_k]
