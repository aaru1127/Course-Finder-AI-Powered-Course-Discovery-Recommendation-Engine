import time
import pytest
from backend.app.services.cache_service import CacheService

def test_cache_aside_pattern():
    cache = CacheService(default_ttl=2)

    payload = {"q": "react beginner", "k": 10}
    test_data = [{"id": "c1", "title": "React 18"}]

    # Initially cache miss
    assert cache.get_search_results(payload) is None

    # Cache write
    cache.set_search_results(payload, test_data, ttl=2)

    # Cache hit
    cached = cache.get_search_results(payload)
    assert cached is not None
    assert cached[0]["id"] == "c1"

    # Wait for TTL expiration
    time.sleep(2.1)
    assert cache.get_search_results(payload) is None

def test_cache_invalidation():
    cache = CacheService(default_ttl=10)
    payload = {"q": "python fast", "k": 5}
    cache.set_search_results(payload, [{"id": "c3"}])
    assert cache.get_search_results(payload) is not None

    cache.clear()
    assert cache.get_search_results(payload) is None
