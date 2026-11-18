import os
import json
import time
import logging
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.database import init_db, seed_database_if_empty, get_db
from backend.app.models.course import CourseModel
from backend.app.schemas.course import CourseResponse, CourseBase
from backend.app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SimilarCoursesRequest,
    PersonalizationRequest
)
from backend.app.schemas.evaluation import BenchmarkSummary
from backend.app.services.bm25_search import BM25Index
from backend.app.services.vector_search import VectorSearchService
from backend.app.services.hybrid_search import HybridSearchService
from backend.app.services.cache_service import CacheService
from backend.app.services.recommender import RecommendationService
from backend.app.services.query_parser import QueryIntentParser
from backend.app.evaluation.evaluator import SearchEvaluator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Global singletons
all_courses: List[Dict[str, Any]] = []
bm25_index: Optional[BM25Index] = None
vector_service: Optional[VectorSearchService] = None
hybrid_service: Optional[HybridSearchService] = None
cache_service: Optional[CacheService] = None
recommendation_service: Optional[RecommendationService] = None
evaluator: Optional[SearchEvaluator] = None
cached_benchmark_results: Optional[Dict[str, Any]] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global all_courses, bm25_index, vector_service, hybrid_service, cache_service, recommendation_service, evaluator
    logger.info("Initializing CourseFinder backend services...")

    # 1. Initialize Database & Seed
    init_db()
    seed_database_if_empty()

    # 2. Load dataset
    with open(settings.DATASET_PATH, "r", encoding="utf-8") as f:
        all_courses = json.load(f)
    logger.info(f"Loaded {len(all_courses)} courses from {settings.DATASET_PATH}")

    # 3. Initialize BM25 Index
    bm25_index = BM25Index(k1=settings.BM25_K1, b=settings.BM25_B)
    bm25_index.index_courses(all_courses)
    logger.info("BM25 Index initialized.")

    # 4. Initialize Dense Vector Service
    vector_service = VectorSearchService(
        model_name=settings.EMBEDDING_MODEL_NAME,
        cache_path=settings.EMBEDDINGS_CACHE_PATH
    )
    vector_service.index_courses(all_courses)
    logger.info("Vector Search Service initialized.")

    # 5. Initialize Hybrid Search Service
    hybrid_service = HybridSearchService(
        bm25_index=bm25_index,
        vector_service=vector_service,
        rrf_k=settings.RRF_K
    )

    # 6. Initialize Redis Cache Service
    cache_service = CacheService(
        redis_url=settings.REDIS_URL,
        default_ttl=settings.CACHE_DEFAULT_TTL
    )

    # 7. Initialize Recommendation Service
    recommendation_service = RecommendationService(
        vector_service=vector_service,
        courses=all_courses
    )

    # 8. Initialize Evaluator
    evaluator = SearchEvaluator(
        bm25_index=bm25_index,
        vector_service=vector_service,
        hybrid_service=hybrid_service,
        cache_service=cache_service,
        all_courses=all_courses
    )

    logger.info("CourseFinder Backend ready to accept requests.")
    yield
    logger.info("Shutting down CourseFinder backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Course Discovery & Recommendation Engine API with Hybrid Search (BM25 + pgvector RRF) and Redis Caching",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    """System health check and component status."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "courses_loaded": len(all_courses),
        "bm25_corpus_size": bm25_index.corpus_size if bm25_index else 0,
        "vector_embeddings_loaded": vector_service.embeddings is not None if vector_service else False,
        "redis_connected": cache_service.is_redis_available if cache_service else False,
        "cache_backend": "Redis" if (cache_service and cache_service.is_redis_available) else "In-Memory LRU"
    }

@app.post("/api/search", response_model=SearchResponse)
def search_courses(req: SearchRequest):
    """
    Search courses using Hybrid Search (BM25 + pgvector RRF), Semantic Vector Search,
    or Lexical BM25, backed by two-tier Redis caching.
    """
    t_start = time.perf_counter()

    # 1. Natural Language Intent Parsing & Extracted Filters
    extracted_filters = QueryIntentParser.parse(req.query)

    # Merge explicit request filters with auto-extracted filters (explicit takes precedence)
    difficulty = req.difficulty or extracted_filters.get("difficulty")
    category = req.category or extracted_filters.get("suggested_category")
    max_duration = req.max_duration or extracted_filters.get("max_duration")
    min_duration = req.min_duration
    free_only = req.free_only or extracted_filters.get("free_only", False)

    # 2. Redis Cache Lookup (Cache-Aside pattern)
    cache_payload = {
        "q": req.query.strip().lower(),
        "diff": difficulty,
        "cat": category,
        "max_d": max_duration,
        "min_d": min_duration,
        "free": free_only,
        "prov": req.provider,
        "mode": req.mode,
        "k": req.top_k
    }

    cached_data = cache_service.get_search_results(cache_payload) if cache_service else None
    if cached_data is not None:
        exec_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return SearchResponse(
            query=req.query,
            mode=req.mode,
            total_results=len(cached_data),
            results=cached_data,
            cache_status="HIT",
            execution_time_ms=exec_ms,
            extracted_filters=extracted_filters
        )

    # 3. Cache Miss: Execute Retrieval
    # Check if query vector is cached
    query_emb = None
    if req.mode in ["hybrid", "semantic"]:
        if cache_service:
            query_emb = cache_service.get_query_embedding(req.query)
        if query_emb is None:
            query_emb = vector_service.encode_query(req.query)
            if cache_service:
                cache_service.set_query_embedding(req.query, query_emb)

    # Run hybrid retrieval
    ranked_courses = hybrid_service.search(
        query=req.query,
        query_embedding=query_emb,
        top_k=req.top_k,
        difficulty=difficulty,
        category=category,
        max_duration=max_duration,
        min_duration=min_duration,
        provider=req.provider,
        free_only=free_only,
        mode=req.mode
    )

    # 4. Store in Cache with TTL
    if cache_service:
        cache_service.set_search_results(cache_payload, ranked_courses, ttl=settings.CACHE_DEFAULT_TTL)

    exec_ms = round((time.perf_counter() - t_start) * 1000, 2)

    return SearchResponse(
        query=req.query,
        mode=req.mode,
        total_results=len(ranked_courses),
        results=ranked_courses,
        cache_status="MISS",
        execution_time_ms=exec_ms,
        extracted_filters=extracted_filters
    )

@app.get("/api/courses", response_model=List[CourseBase])
def list_courses(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List courses with optional filtering and pagination."""
    filtered = all_courses
    if category and category.lower() != "all":
        filtered = [c for c in filtered if c.get("category", "").lower() == category.lower()]
    if difficulty and difficulty.lower() != "all":
        filtered = [c for c in filtered if c.get("difficulty", "").lower() == difficulty.lower()]

    return filtered[offset : offset + limit]

@app.get("/api/courses/{course_id}", response_model=CourseResponse)
def get_course_details(course_id: str):
    """Retrieve detailed course information by ID."""
    for c in all_courses:
        if c["id"] == course_id:
            return CourseResponse(**c)
    raise HTTPException(status_code=404, detail="Course not found")

@app.get("/api/courses/{course_id}/similar", response_model=List[CourseResponse])
def get_similar_courses(
    course_id: str,
    top_k: int = Query(6, ge=1, le=20),
    difficulty: Optional[str] = None,
    max_duration: Optional[float] = None
):
    """Find courses semantically similar to a given course."""
    if not recommendation_service:
        raise HTTPException(status_code=503, detail="Recommendation service unavailable")
    results = recommendation_service.get_similar_courses(
        course_id=course_id,
        top_k=top_k,
        difficulty=difficulty,
        max_duration=max_duration
    )
    return results

@app.post("/api/recommend", response_model=List[Dict[str, Any]])
def get_personalized_recommendations(req: PersonalizationRequest):
    """Generate personalized recommendations aligned with learner profile and goals."""
    if not recommendation_service:
        raise HTTPException(status_code=503, detail="Recommendation service unavailable")
    results = recommendation_service.get_personalized_recommendations(
        skill_level=req.skill_level,
        target_technologies=req.target_technologies,
        learning_goal=req.learning_goal,
        available_weekly_hours=req.available_weekly_hours or 10.0,
        preferred_categories=req.preferred_categories,
        top_k=req.top_k
    )
    return results

@app.get("/api/filters")
def get_filter_options():
    """Retrieve dynamic filter facets (categories, difficulties, providers, duration stats)."""
    categories = sorted(list({c.get("category", "") for c in all_courses if c.get("category")}))
    difficulties = ["Beginner", "Intermediate", "Advanced"]
    providers = sorted(list({c.get("provider", "") for c in all_courses if c.get("provider")}))
    
    # Extract top skills
    skill_counts: Dict[str, int] = {}
    for c in all_courses:
        for s in c.get("skills", []):
            skill_counts[s] = skill_counts.get(s, 0) + 1
    top_skills = [s for s, _ in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:30]]

    return {
        "categories": categories,
        "difficulties": difficulties,
        "providers": providers,
        "top_skills": top_skills,
        "duration_min": min((c.get("duration_hours", 0) for c in all_courses), default=0),
        "duration_max": max((c.get("duration_hours", 0) for c in all_courses), default=60)
    }

@app.get("/api/evaluation/benchmark")
def get_benchmark_report(force_refresh: bool = False):
    """Run quantitative information retrieval evaluation comparing BM25, Vector, and Hybrid RRF."""
    global cached_benchmark_results
    if cached_benchmark_results and not force_refresh:
        return cached_benchmark_results

    if not evaluator:
        raise HTTPException(status_code=503, detail="Evaluator service unavailable")

    logger.info("Running live search evaluation benchmark...")
    report = evaluator.run_benchmark(k=10)
    cached_benchmark_results = report
    return report

@app.post("/api/cache/clear")
def clear_cache():
    """Invalidate Redis and in-memory caches."""
    if cache_service:
        count = cache_service.clear()
        return {"status": "success", "cleared_entries": count}
    return {"status": "noop"}
