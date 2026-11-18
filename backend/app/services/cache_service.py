import json
import hashlib
import time
import logging
from typing import Optional, Any, Dict
import numpy as np

logger = logging.getLogger(__name__)

class CacheService:
    """
    Two-Tier Caching Service implementing the Cache-Aside pattern with Redis
    and graceful in-memory fallback.

    Tier 1: Search Result Cache (stores full ranked course response payloads with TTL)
    Tier 2: Query Embedding Cache (stores 384-dimensional query vector floats)
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0", default_ttl: int = 600):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.redis_client = None
        self._in_memory_cache: Dict[str, Dict[str, Any]] = {}
        self._init_redis()

    def _init_redis(self):
        try:
            import redis
            client = redis.from_url(self.redis_url, socket_timeout=1.5, decode_responses=True)
            client.ping()
            self.redis_client = client
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.warning(f"Redis not available ({e}). Using in-memory fallback cache.")
            self.redis_client = None

    @property
    def is_redis_available(self) -> bool:
        if self.redis_client:
            try:
                self.redis_client.ping()
                return True
            except Exception:
                self.redis_client = None
        return False

    @staticmethod
    def generate_cache_key(prefix: str, payload: Dict[str, Any]) -> str:
        """Create deterministic SHA-256 hash key from query and filter parameters."""
        serialized = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return f"{prefix}:{digest}"

    def get_search_results(self, key_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch cached search response."""
        key = self.generate_cache_key("course_search", key_payload)

        # Check Redis
        if self.is_redis_available:
            try:
                val = self.redis_client.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.error(f"Redis get error: {e}")

        # Check In-Memory Fallback
        entry = self._in_memory_cache.get(key)
        if entry:
            if time.time() < entry["expires_at"]:
                return entry["data"]
            else:
                del self._in_memory_cache[key]

        return None

    def set_search_results(self, key_payload: Dict[str, Any], data: Dict[str, Any], ttl: Optional[int] = None):
        """Store search response in cache with TTL."""
        ttl = ttl or self.default_ttl
        key = self.generate_cache_key("course_search", key_payload)

        # Write to Redis
        if self.is_redis_available:
            try:
                self.redis_client.setex(key, ttl, json.dumps(data, default=str))
            except Exception as e:
                logger.error(f"Redis set error: {e}")

        # Write to In-Memory Fallback
        self._in_memory_cache[key] = {
            "data": data,
            "expires_at": time.time() + ttl
        }

    def get_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """Fetch cached query embedding vector."""
        key = self.generate_cache_key("query_emb", {"q": query.strip().lower()})

        # Check Redis
        if self.is_redis_available:
            try:
                val = self.redis_client.get(key)
                if val:
                    data = json.loads(val)
                    return np.array(data, dtype=np.float32)
            except Exception as e:
                logger.error(f"Redis emb get error: {e}")

        # Check In-Memory
        entry = self._in_memory_cache.get(key)
        if entry and time.time() < entry["expires_at"]:
            return np.array(entry["data"], dtype=np.float32)

        return None

    def set_query_embedding(self, query: str, embedding: np.ndarray, ttl: Optional[int] = None):
        """Store query embedding in cache."""
        ttl = ttl or (self.default_ttl * 2)  # Embeddings can live longer
        key = self.generate_cache_key("query_emb", {"q": query.strip().lower()})
        data = embedding.tolist()

        if self.is_redis_available:
            try:
                self.redis_client.setex(key, ttl, json.dumps(data))
            except Exception as e:
                logger.error(f"Redis emb set error: {e}")

        self._in_memory_cache[key] = {
            "data": data,
            "expires_at": time.time() + ttl
        }

    def clear(self) -> int:
        """Clear all cached keys."""
        cleared_count = len(self._in_memory_cache)
        self._in_memory_cache.clear()

        if self.is_redis_available:
            try:
                keys = self.redis_client.keys("course_search:*") + self.redis_client.keys("query_emb:*")
                if keys:
                    cleared_count += self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis clear error: {e}")

        return cleared_count
