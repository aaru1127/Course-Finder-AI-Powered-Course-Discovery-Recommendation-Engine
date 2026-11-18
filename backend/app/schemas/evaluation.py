from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class MetricScores(BaseModel):
    precision_at_k: float
    recall_at_k: float
    ndcg_at_k: float
    mrr: float

class BenchmarkStrategyResult(BaseModel):
    strategy: str  # "bm25", "vector", "hybrid"
    metrics: MetricScores
    avg_latency_ms: float

class BenchmarkSummary(BaseModel):
    total_queries: int
    k: int
    strategies: Dict[str, BenchmarkStrategyResult]
    redis_cache_benchmark: Dict[str, Any]
    timestamp: str

