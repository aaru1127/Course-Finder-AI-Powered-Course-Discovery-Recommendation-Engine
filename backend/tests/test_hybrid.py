import pytest
from backend.app.services.bm25_search import BM25Index
from backend.app.services.vector_search import VectorSearchService
from backend.app.services.hybrid_search import HybridSearchService

SAMPLE_COURSES = [
    {
        "id": "c1",
        "title": "Node.js Backend Development",
        "provider": "Coursera",
        "description": "Learn server-side JavaScript with Node.js and Express.",
        "skills": ["Node.js", "Express", "Backend"],
        "category": "Backend Development",
        "difficulty": "Beginner",
        "duration_hours": 12.0,
        "price": 0.0,
        "rating": 4.8,
        "course_url": "https://example.com/c1"
    },
    {
        "id": "c2",
        "title": "React Frontend Development",
        "provider": "Frontend Masters",
        "description": "Build single page client applications in JavaScript.",
        "skills": ["React", "JavaScript", "Frontend"],
        "category": "Frontend Development",
        "difficulty": "Beginner",
        "duration_hours": 15.0,
        "price": 29.99,
        "rating": 4.9,
        "course_url": "https://example.com/c2"
    }
]

def test_hybrid_rrf_fusion():
    bm25 = BM25Index()
    bm25.index_courses(SAMPLE_COURSES)

    vector = VectorSearchService()
    vector.index_courses(SAMPLE_COURSES)

    hybrid = HybridSearchService(bm25_index=bm25, vector_service=vector, rrf_k=60)
    results = hybrid.search(query="Node.js server", top_k=2, mode="hybrid")

    assert len(results) >= 1
    assert results[0]["id"] == "c1"
    assert "score" in results[0]
    assert 0.0 <= results[0]["score"] <= 1.0
    assert len(results[0]["retrieval_sources"]) >= 1
