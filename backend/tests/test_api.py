import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["courses_loaded"] > 0
    assert data["bm25_corpus_size"] > 0
    assert data["vector_embeddings_loaded"] is True

def test_search_endpoint_miss_then_hit(client):
    query_payload = {
        "query": "Node.js Express backend practical beginner",
        "mode": "hybrid",
        "top_k": 5
    }

    # First request: Cache MISS
    res1 = client.post("/api/search", json=query_payload)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["cache_status"] in ["MISS", "HIT"]
    assert len(data1["results"]) > 0
    assert "score" in data1["results"][0]

    # Second identical request: Cache HIT
    res2 = client.post("/api/search", json=query_payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["cache_status"] == "HIT"
    assert data2["execution_time_ms"] < 20.0  # sub-20ms cache response

def test_get_filters(client):
    res = client.get("/api/filters")
    assert res.status_code == 200
    data = res.json()
    assert len(data["categories"]) > 0
    assert len(data["difficulties"]) == 3
    assert len(data["top_skills"]) > 0

def test_similar_courses(client):
    # Fetch first course
    res = client.get("/api/courses?limit=1")
    assert res.status_code == 200
    course_id = res.json()[0]["id"]

    sim_res = client.get(f"/api/courses/{course_id}/similar?top_k=3")
    assert sim_res.status_code == 200
    similar_list = sim_res.json()
    assert len(similar_list) > 0
    assert all(c["id"] != course_id for c in similar_list)

def test_recommendation_endpoint(client):
    rec_payload = {
        "skill_level": "Beginner",
        "target_technologies": ["Node.js", "Express"],
        "learning_goal": "Build REST APIs",
        "available_weekly_hours": 10.0,
        "top_k": 4
    }
    res = client.post("/api/recommend", json=rec_payload)
    assert res.status_code == 200
    recs = res.json()
    assert len(recs) > 0
    assert "recommendation_reason" in recs[0]

