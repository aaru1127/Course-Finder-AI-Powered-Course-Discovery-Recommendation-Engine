"""
Precompute and save 384-dimensional embeddings for all courses in courses_dataset.json.
This ensures sub-millisecond cold starts and offline readiness.
"""
import json
import logging
from pathlib import Path
import numpy as np
from backend.app.services.vector_search import VectorSearchService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    base_dir = Path(__file__).resolve().parent
    dataset_path = base_dir / "courses_dataset.json"
    cache_path = base_dir / "courses_embeddings.npy"

    with open(dataset_path, "r", encoding="utf-8") as f:
        courses = json.load(f)

    logger.info(f"Loaded {len(courses)} courses from {dataset_path}")
    service = VectorSearchService(cache_path=str(cache_path))
    service.index_courses(courses, force_recompute=True)
    logger.info(f"Successfully precomputed and saved embeddings to {cache_path}")
    logger.info(f"Embeddings shape: {service.embeddings.shape}")

if __name__ == "__main__":
    main()

