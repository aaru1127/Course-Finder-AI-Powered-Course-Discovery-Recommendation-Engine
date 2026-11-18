import pytest
from backend.app.services.bm25_search import BM25Index

SAMPLE_COURSES = [
    {
        "id": "c1",
        "title": "Node.js Backend Development for Beginners",
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
        "title": "Advanced React Patterns and Performance",
        "provider": "Frontend Masters",
        "description": "Master React optimization and compound components.",
        "skills": ["React", "JavaScript", "Frontend"],
        "category": "Frontend Development",
        "difficulty": "Advanced",
        "duration_hours": 18.0,
        "price": 49.99,
        "rating": 4.9,
        "course_url": "https://example.com/c2"
    },
    {
        "id": "c3",
        "title": "Machine Learning with Python",
        "provider": "DeepLearning.AI",
        "description": "Supervised and unsupervised learning with PyTorch.",
        "skills": ["Python", "Machine Learning", "PyTorch"],
        "category": "AI & Machine Learning",
        "difficulty": "Intermediate",
        "duration_hours": 30.0,
        "price": 0.0,
        "rating": 4.9,
        "course_url": "https://example.com/c3"
    }
]

def test_bm25_tokenization():
    tokens = BM25Index.tokenize("Node.js, Express & REST APIs!")
    assert "nodejs" in tokens or "node" in tokens
    assert "express" in tokens

def test_bm25_indexing_and_search():
    index = BM25Index()
    index.index_courses(SAMPLE_COURSES)
    assert index.corpus_size == 3

    results = index.search("Node.js Express", top_k=2)
    assert len(results) >= 1
    assert results[0]["id"] == "c1"
    assert results[0]["score"] > 0

def test_bm25_filtering():
    index = BM25Index()
    index.index_courses(SAMPLE_COURSES)

    # Search with difficulty filter
    res = index.search("JavaScript", difficulty="Advanced")
    assert len(res) == 1
    assert res[0]["id"] == "c2"

    # Search with max duration filter
    res_dur = index.search("JavaScript", max_duration=15.0)
    assert len(res_dur) == 1
    assert res_dur[0]["id"] == "c1"
