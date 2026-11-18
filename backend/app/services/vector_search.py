import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class VectorSearchService:
    """
    Dense semantic retrieval service.
    Converts course metadata and search queries into 384-dimensional dense vectors
    using Sentence Transformers (all-MiniLM-L6-v2).
    Calculates cosine similarity and supports both in-memory and pgvector execution.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_path: Optional[str] = None):
        self.model_name = model_name
        self.cache_path = cache_path
        self._model = None
        self.embeddings: Optional[np.ndarray] = None
        self.course_ids: List[str] = []
        self.courses_by_id: Dict[str, Dict[str, Any]] = {}
        self.dim = 384

    @property
    def model(self):
        """Lazy load SentenceTransformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.error(f"Failed to load SentenceTransformer: {e}")
                raise
        return self._model

    @staticmethod
    def format_course_text(course: Dict[str, Any]) -> str:
        """Combine course title, skills, category, and description for rich semantic representation."""
        title = course.get("title", "")
        category = course.get("category", "")
        skills = ", ".join(course.get("skills", []))
        desc = course.get("description", "")
        diff = course.get("difficulty", "")
        return f"{title}. Category: {category}. Level: {diff}. Key skills: {skills}. Overview: {desc}"

    def index_courses(self, courses: List[Dict[str, Any]], force_recompute: bool = False):
        """
        Generate or load embeddings for courses and index them.
        Embeddings are L2 normalized so cosine similarity is simple dot product.
        """
        self.courses_by_id = {c["id"]: c for c in courses}
        self.course_ids = [c["id"] for c in courses]

        # Check if cached embeddings exist on disk
        if not force_recompute and self.cache_path and os.path.exists(self.cache_path):
            try:
                loaded = np.load(self.cache_path)
                if loaded.shape[0] == len(courses) and loaded.shape[1] == self.dim:
                    logger.info(f"Loaded {len(courses)} cached embeddings from {self.cache_path}")
                    self.embeddings = loaded
                    return
            except Exception as e:
                logger.warning(f"Failed to load cached embeddings: {e}. Recomputing.")

        # Compute embeddings
        texts = [self.format_course_text(c) for c in courses]
        logger.info(f"Computing embeddings for {len(texts)} courses using {self.model_name}...")
        raw_embeddings = self.model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
        self.embeddings = np.array(raw_embeddings, dtype=np.float32)

        # Save to disk cache if path is provided
        if self.cache_path:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            np.save(self.cache_path, self.embeddings)
            logger.info(f"Saved computed embeddings to {self.cache_path}")

    def encode_query(self, query: str) -> np.ndarray:
        """Encode query text into normalized 1D vector."""
        emb = self.model.encode([query], normalize_embeddings=True)[0]
        return np.array(emb, dtype=np.float32)

    def search(
        self,
        query: Optional[str] = None,
        query_embedding: Optional[np.ndarray] = None,
        top_k: int = 10,
        difficulty: Optional[str] = None,
        category: Optional[str] = None,
        max_duration: Optional[float] = None,
        min_duration: Optional[float] = None,
        provider: Optional[str] = None,
        free_only: bool = False,
        exclude_id: Optional[str] = None,
        min_similarity: float = 0.25
    ) -> List[Dict[str, Any]]:
        """
        Semantic vector search via cosine similarity (dot product of L2 normalized vectors).
        Applies metadata filters, enforces minimum similarity threshold, and returns ranked results.
        """
        if query_embedding is None:
            if not query:
                return []
            query_embedding = self.encode_query(query)

        if self.embeddings is None or len(self.course_ids) == 0:
            return []

        # Cosine similarity for normalized vectors: S = E . q
        # Shape: (N, 384) . (384,) -> (N,)
        similarities = np.dot(self.embeddings, query_embedding)

        # Sort indices by similarity descending
        sorted_indices = np.argsort(-similarities)

        results = []
        for idx in sorted_indices:
            sim_score = float(similarities[idx])
            # If similarity drops below the noise threshold, break immediately (indices are descending)
            if sim_score < min_similarity:
                break

            course_id = self.course_ids[idx]
            if exclude_id and course_id == exclude_id:
                continue

            course = self.courses_by_id[course_id]

            # Metadata filtering
            if difficulty and difficulty.lower() != "all" and course.get("difficulty", "").lower() != difficulty.lower():
                continue
            if category and category.lower() != "all" and course.get("category", "").lower() != category.lower():
                continue
            if max_duration is not None and course.get("duration_hours", 0) > max_duration:
                continue
            if min_duration is not None and course.get("duration_hours", 0) < min_duration:
                continue
            if provider and provider.lower() != "all" and course.get("provider", "").lower() != provider.lower():
                continue
            if free_only and course.get("price", 0.0) > 0.0:
                continue

            # Bound between 0.0 and 1.0
            sim_score = max(0.0, min(1.0, sim_score))

            results.append({
                **course,
                "score": round(sim_score, 4),
                "matched_skills": course.get("skills", [])[:4],
                "retrieval_sources": ["Semantic"],
                "rank": len(results) + 1
            })

            if len(results) >= top_k:
                break

        return results

    def get_course_embedding(self, course_id: str) -> Optional[np.ndarray]:
        """Fetch embedding vector for a given course ID."""
        if course_id not in self.course_ids or self.embeddings is None:
            return None
        idx = self.course_ids.index(course_id)
        return self.embeddings[idx]

