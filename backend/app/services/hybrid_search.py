import logging
from typing import List, Dict, Any, Optional
from backend.app.services.bm25_search import BM25Index
from backend.app.services.vector_search import VectorSearchService

logger = logging.getLogger(__name__)

class HybridSearchService:
    """
    Hybrid Retrieval Engine combining Lexical (BM25) and Semantic (Dense Vector) search
    using Reciprocal Rank Fusion (RRF).

    Formula:
        RRF_Score(d) = sum_{m in {bm25, vector}} ( w_m / (k + rank_m(d)) )
    where:
        k = 60 (standard smoothing constant)
        rank_m(d) is 1-based index in model m's retrieved list
    """

    def __init__(
        self,
        bm25_index: BM25Index,
        vector_service: VectorSearchService,
        rrf_k: int = 60,
        bm25_weight: float = 1.0,
        vector_weight: float = 1.0
    ):
        self.bm25_index = bm25_index
        self.vector_service = vector_service
        self.rrf_k = rrf_k
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight

    def search(
        self,
        query: str,
        query_embedding: Optional[Any] = None,
        top_k: int = 10,
        difficulty: Optional[str] = None,
        category: Optional[str] = None,
        max_duration: Optional[float] = None,
        min_duration: Optional[float] = None,
        provider: Optional[str] = None,
        free_only: bool = False,
        mode: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        Execute search according to mode: 'hybrid', 'semantic', or 'keyword'.
        """
        # Mode: Pure BM25 Keyword Search
        if mode == "keyword":
            results = self.bm25_index.search(
                query=query,
                top_k=top_k,
                difficulty=difficulty,
                category=category,
                max_duration=max_duration,
                min_duration=min_duration,
                provider=provider,
                free_only=free_only
            )
            # Calibrate BM25 scores to 0.0 - 1.0 range based on top result
            if results:
                max_s = max(r["score"] for r in results) or 1.0
                for r in results:
                    r["score"] = round(min(0.99, max(0.40, (r["score"] / max_s) * 0.95)), 3)
            return results

        # Mode: Pure Semantic Vector Search
        if mode == "semantic":
            return self.vector_service.search(
                query=query,
                query_embedding=query_embedding,
                top_k=top_k,
                difficulty=difficulty,
                category=category,
                max_duration=max_duration,
                min_duration=min_duration,
                provider=provider,
                free_only=free_only
            )

        # Mode: Hybrid Search with RRF Fusion
        candidate_k = max(top_k * 3, 30)

        # 1. Lexical retrieval
        bm25_results = self.bm25_index.search(
            query=query,
            top_k=candidate_k,
            difficulty=difficulty,
            category=category,
            max_duration=max_duration,
            min_duration=min_duration,
            provider=provider,
            free_only=free_only
        )

        # 2. Semantic retrieval
        vector_results = self.vector_service.search(
            query=query,
            query_embedding=query_embedding,
            top_k=candidate_k,
            difficulty=difficulty,
            category=category,
            max_duration=max_duration,
            min_duration=min_duration,
            provider=provider,
            free_only=free_only
        )

        # 3. Fuse with Reciprocal Rank Fusion (RRF)
        # Store metadata and calculate accumulated RRF scores
        rrf_scores: Dict[str, float] = {}
        course_data: Dict[str, Dict[str, Any]] = {}
        bm25_ranks: Dict[str, int] = {}
        vector_ranks: Dict[str, int] = {}
        matched_skills_map: Dict[str, set] = {}

        # Process BM25 rankings
        for rank, item in enumerate(bm25_results, start=1):
            cid = item["id"]
            course_data[cid] = item
            bm25_ranks[cid] = rank
            rrf_score = self.bm25_weight / (self.rrf_k + rank)
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + rrf_score
            matched_skills_map.setdefault(cid, set()).update(item.get("matched_skills", []))

        # Process Vector rankings
        for rank, item in enumerate(vector_results, start=1):
            cid = item["id"]
            if cid not in course_data:
                course_data[cid] = item
            vector_ranks[cid] = rank
            rrf_score = self.vector_weight / (self.rrf_k + rank)
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + rrf_score
            matched_skills_map.setdefault(cid, set()).update(item.get("matched_skills", []))

        # 4. Sort courses by fused RRF score descending
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        # Maximum theoretical RRF score when a course ranks #1 in both retrievals:
        max_possible_rrf = (self.bm25_weight / (self.rrf_k + 1)) + (self.vector_weight / (self.rrf_k + 1))

        final_results = []
        for cid in sorted_cids[:top_k]:
            base_course = course_data[cid]
            raw_rrf = rrf_scores[cid]
            
            # Calibrated relevance score (percentage between 0.0 and 1.0)
            # High agreement (in both #1 ranks) yields 95-98%
            # Moderate agreement yields 80-92%
            # Single source lower rank scales down accurately
            calibrated_score = round(min(0.98, max(0.50, (raw_rrf / max_possible_rrf) * 0.95 + 0.05)), 3)

            sources = []
            if cid in bm25_ranks:
                sources.append(f"BM25 (Rank {bm25_ranks[cid]})")
            if cid in vector_ranks:
                sources.append(f"Semantic (Rank {vector_ranks[cid]})")

            final_results.append({
                **base_course,
                "score": calibrated_score,
                "raw_rrf_score": round(raw_rrf, 5),
                "matched_skills": list(matched_skills_map.get(cid, set()))[:5],
                "retrieval_sources": sources,
                "rank": len(final_results) + 1
            })

        return final_results

