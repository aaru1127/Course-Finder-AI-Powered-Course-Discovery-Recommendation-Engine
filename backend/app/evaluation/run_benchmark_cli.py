"""
CLI runner for quantitative information retrieval evaluation.
Outputs Precision@10, Recall@10, NDCG@10, MRR, and response latency comparison.
"""
import json
import logging
from pathlib import Path
from backend.app.config import settings
from backend.app.services.bm25_search import BM25Index
from backend.app.services.vector_search import VectorSearchService
from backend.app.services.hybrid_search import HybridSearchService
from backend.app.services.cache_service import CacheService
from backend.app.evaluation.evaluator import SearchEvaluator

logging.basicConfig(level=logging.INFO)

def main():
    with open(settings.DATASET_PATH, "r", encoding="utf-8") as f:
        courses = json.load(f)

    bm25 = BM25Index()
    bm25.index_courses(courses)

    vector = VectorSearchService(cache_path=settings.EMBEDDINGS_CACHE_PATH)
    vector.index_courses(courses)

    hybrid = HybridSearchService(bm25_index=bm25, vector_service=vector)
    cache = CacheService()

    evaluator = SearchEvaluator(bm25, vector, hybrid, cache, courses)
    print("=" * 65)
    print("  CourseFinder Quantitative Information Retrieval Benchmark")
    print("=" * 65)

    report = evaluator.run_benchmark(k=10)

    print(f"\nEvaluated on {report['total_queries']} ground-truth test queries @ K={report['k']}:\n")
    print(f"{'Retrieval Strategy':<20} | {'P@10':<8} | {'R@10':<8} | {'NDCG@10':<8} | {'MRR':<8} | {'Latency':<10}")
    print("-" * 72)
    for strat, data in report["strategies"].items():
        m = data["metrics"]
        print(f"{strat.upper():<20} | {m['precision_at_k']:<8.4f} | {m['recall_at_k']:<8.4f} | {m['ndcg_at_k']:<8.4f} | {m['mrr']:<8.4f} | {data['avg_latency_ms']:<6.1f} ms")

    cb = report["redis_cache_benchmark"]
    print("\n" + "=" * 65)
    print("  Redis Caching & Latency Profiling (Cache-Aside Pattern)")
    print("=" * 65)
    print(f"  Backend in Use:         {cb['backend_in_use']}")
    print(f"  Cache Miss Latency:     {cb['cache_miss_latency_ms']} ms")
    print(f"  Cache Hit Latency:      {cb['cache_hit_latency_ms']} ms")
    print(f"  Speedup Factor:         {cb['speedup_factor']}x faster on repeated searches")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
