import numpy as np
import pytest
from backend.app.services.vector_search import VectorSearchService

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

def test_vector_search_service():
    service = VectorSearchService()
    service.index_courses(SAMPLE_COURSES)
    assert service.embeddings is not None
    assert service.embeddings.shape[0] == 2
    assert service.embeddings.shape[1] == 384

    # Semantic similarity: query with no keyword overlap should still rank backend higher
    results = service.search("building server-side applications and web services", top_k=2)
    assert len(results) > 0
    assert results[0]["id"] == "c1"
    assert 0.0 <= results[0]["score"] <= 1.0
