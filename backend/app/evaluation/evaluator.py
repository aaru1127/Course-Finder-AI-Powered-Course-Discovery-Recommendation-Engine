import time
import datetime
import logging
from typing import Dict, Any, List
from backend.app.services.bm25_search import BM25Index
from backend.app.services.vector_search import VectorSearchService
from backend.app.services.hybrid_search import HybridSearchService
from backend.app.services.cache_service import CacheService
from backend.app.evaluation.metrics import precision_at_k, recall_at_k, ndcg_at_k, reciprocal_rank
from backend.app.evaluation.ground_truth import EVALUATION_QUERIES, find_relevant_course_ids

logger = logging.getLogger(__name__)

class SearchEvaluator:
    """
    Automated Quantitative Information Retrieval Evaluator.
    Benchmarks BM25, Semantic Vector Search, and Hybrid RRF against ground-truth queries.
    Measures Precision@K, Recall@K, NDCG@K, MRR, and response latency.
    """

    def __init__(
        self,
        bm25_index: BM25Index,
        vector_service: VectorSearchService,
        hybrid_service: HybridSearchService,
        cache_service: CacheService,
        all_courses: List[Dict[str, Any]]
    ):
        self.bm25_index = bm25_index
        self.vector_service = vector_service
        self.hybrid_service = hybrid_service
        self.cache_service = cache_service
        self.all_courses = all_courses

    def run_benchmark(self, k: int = 10) -> Dict[str, Any]:
        """
        Execute benchmark over all evaluation queries for all three retrieval strategies.
        """
        strategies = ["bm25", "vector", "hybrid"]
        results: Dict[str, Dict[str, float]] = {s: {"p_at_k": 0.0, "r_at_k": 0.0, "ndcg_at_k": 0.0, "mrr": 0.0, "latency_ms": 0.0} for s in strategies}

        num_queries = len(EVALUATION_QUERIES)

        for query_spec in EVALUATION_QUERIES:
            query = query_spec["query"]
            relevant_ids = find_relevant_course_ids(query_spec, self.all_courses)
            if not relevant_ids:
                # If ground truth was overly restrictive, fallback to intent skill match across all courses
                relevant_ids = {c["id"] for c in self.all_courses if any(s.lower() in c["title"].lower() or s.lower() in [sk.lower() for sk in c.get("skills", [])] for s in query_spec.get("intent_skills", []))}

            # 1. BM25 Strategy
            t0 = time.perf_counter()
            bm25_res = self.hybrid_service.search(query=query, top_k=k, mode="keyword")
            t_bm25 = (time.perf_counter() - t0) * 1000
            bm25_ids = [r["id"] for r in bm25_res]

            results["bm25"]["p_at_k"] += precision_at_k(bm25_ids, relevant_ids, k)
            results["bm25"]["r_at_k"] += recall_at_k(bm25_ids, relevant_ids, k)
            results["bm25"]["ndcg_at_k"] += ndcg_at_k(bm25_ids, relevant_ids, k)
            results["bm25"]["mrr"] += reciprocal_rank(bm25_ids, relevant_ids)
            results["bm25"]["latency_ms"] += t_bm25

            # 2. Vector Strategy
            t0 = time.perf_counter()
            vector_res = self.hybrid_service.search(query=query, top_k=k, mode="semantic")
            t_vector = (time.perf_counter() - t0) * 1000
            vec_ids = [r["id"] for r in vector_res]

            results["vector"]["p_at_k"] += precision_at_k(vec_ids, relevant_ids, k)
            results["vector"]["r_at_k"] += recall_at_k(vec_ids, relevant_ids, k)
            results["vector"]["ndcg_at_k"] += ndcg_at_k(vec_ids, relevant_ids, k)
            results["vector"]["mrr"] += reciprocal_rank(vec_ids, relevant_ids)
            results["vector"]["latency_ms"] += t_vector

            # 3. Hybrid RRF Strategy
            t0 = time.perf_counter()
            hybrid_res = self.hybrid_service.search(query=query, top_k=k, mode="hybrid")
            t_hybrid = (time.perf_counter() - t0) * 1000
            hyb_ids = [r["id"] for r in hybrid_res]

            results["hybrid"]["p_at_k"] += precision_at_k(hyb_ids, relevant_ids, k)
            results["hybrid"]["r_at_k"] += recall_at_k(hyb_ids, relevant_ids, k)
            results["hybrid"]["ndcg_at_k"] += ndcg_at_k(hyb_ids, relevant_ids, k)
            results["hybrid"]["mrr"] += reciprocal_rank(hyb_ids, relevant_ids)
            results["hybrid"]["latency_ms"] += t_hybrid

        # Average over total queries
        formatted_strategies = {}
        for s in strategies:
            formatted_strategies[s] = {
                "strategy": s,
                "metrics": {
                    "precision_at_k": round(results[s]["p_at_k"] / num_queries, 4),
                    "recall_at_k": round(results[s]["r_at_k"] / num_queries, 4),
                    "ndcg_at_k": round(results[s]["ndcg_at_k"] / num_queries, 4),
                    "mrr": round(results[s]["mrr"] / num_queries, 4),
                },
                "avg_latency_ms": round(results[s]["latency_ms"] / num_queries, 2)
            }

        # 4. Measure Cache Latency (Miss vs Hit)
        sample_query = "Beginner Node.js backend development"
        cache_key_payload = {"q": sample_query, "k": 10, "mode": "hybrid"}
        
        # Invalidate first to ensure miss
        self.cache_service.clear()
        
        # Measure Miss
        t_start = time.perf_counter()
        miss_res = self.hybrid_service.search(query=sample_query, top_k=10, mode="hybrid")
        self.cache_service.set_search_results(cache_key_payload, miss_res, ttl=300)
        cache_miss_latency = round((time.perf_counter() - t_start) * 1000, 2)

        # Measure Hit
        t_start = time.perf_counter()
        hit_res = self.cache_service.get_search_results(cache_key_payload)
        cache_hit_latency = round((time.perf_counter() - t_start) * 1000, 2)

        cache_benchmark = {
            "cache_miss_latency_ms": cache_miss_latency,
            "cache_hit_latency_ms": max(0.2, cache_hit_latency),
            "speedup_factor": round(cache_miss_latency / max(0.2, cache_hit_latency), 1),
            "backend_in_use": "Redis" if self.cache_service.is_redis_available else "In-Memory LRU (Redis fallback)"
        }

        return {
            "total_queries": num_queries,
            "k": k,
            "strategies": formatted_strategies,
            "redis_cache_benchmark": cache_benchmark,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

