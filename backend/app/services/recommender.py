import logging
from typing import List, Dict, Any, Optional
import numpy as np
from backend.app.services.vector_search import VectorSearchService

logger = logging.getLogger(__name__)

class RecommendationService:
    """
    Recommendation Service handling:
    1. Content-based Nearest-Neighbor Similar Course Discovery
    2. Multi-Factor Profile Personalization Engine
    """

    def __init__(self, vector_service: VectorSearchService, courses: List[Dict[str, Any]]):
        self.vector_service = vector_service
        self.courses_by_id = {c["id"]: c for c in courses}
        self.courses = courses

    def get_similar_courses(
        self,
        course_id: str,
        top_k: int = 6,
        difficulty: Optional[str] = None,
        max_duration: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Find semantically similar courses based on vector cosine proximity."""
        if course_id not in self.courses_by_id:
            logger.warning(f"Course {course_id} not found for similarity search.")
            return []

        target_emb = self.vector_service.get_course_embedding(course_id)
        if target_emb is None:
            # Re-encode course on the fly
            c = self.courses_by_id[course_id]
            target_emb = self.vector_service.encode_query(VectorSearchService.format_course_text(c))

        results = self.vector_service.search(
            query_embedding=target_emb,
            top_k=top_k,
            difficulty=difficulty,
            max_duration=max_duration,
            exclude_id=course_id
        )

        for r in results:
            r["retrieval_sources"] = ["Semantic Vector Proximity"]

        return results

    def get_personalized_recommendations(
        self,
        skill_level: str,
        target_technologies: List[str],
        learning_goal: Optional[str] = None,
        available_weekly_hours: float = 10.0,
        preferred_categories: Optional[List[str]] = None,
        top_k: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized course recommendations.
        Synthesizes a user profile query vector from target technologies and learning goals,
        then reranks candidates using multi-factor preference scoring.
        """
        preferred_categories = preferred_categories or []

        # 1. Construct rich user profile query text
        tech_text = ", ".join(target_technologies)
        goal_text = learning_goal or f"Learn {tech_text} from {skill_level} level"
        profile_query = f"{goal_text}. Desired skills: {tech_text}. Preferred level: {skill_level}."
        if preferred_categories:
            profile_query += f" Topics: {', '.join(preferred_categories)}."

        # 2. Retrieve initial broad semantic candidates
        profile_emb = self.vector_service.encode_query(profile_query)
        candidates = self.vector_service.search(
            query_embedding=profile_emb,
            top_k=max(top_k * 4, 30)
        )

        # 3. Apply Multi-Factor Preference Scoring:
        # Score = Vector_Sim + Skill_Match_Bonus + Level_Match_Bonus - Duration_Penalty
        target_tech_lower = [t.lower() for t in target_technologies]
        target_level_lower = skill_level.lower()

        scored_candidates = []
        for c in candidates:
            base_score = c["score"]  # 0.0 to 1.0 from vector cosine
            
            # Match count of target technologies in course skills or title
            course_skills_lower = [s.lower() for s in c.get("skills", [])]
            course_title_lower = c.get("title", "").lower()
            matched_tech = [t for t in target_tech_lower if t in course_skills_lower or t in course_title_lower]
            skill_bonus = min(0.20, len(matched_tech) * 0.07)

            # Skill level alignment bonus/penalty
            c_diff = c.get("difficulty", "").lower()
            if c_diff == target_level_lower:
                level_multiplier = 0.10
            elif target_level_lower == "beginner" and c_diff == "advanced":
                level_multiplier = -0.25
            elif target_level_lower == "advanced" and c_diff == "beginner":
                level_multiplier = -0.15
            else:
                level_multiplier = 0.0

            # Available weekly hours heuristic
            # If course is over 2.5x weekly available hours, slight penalty for pace fit
            duration = c.get("duration_hours", 10.0)
            duration_penalty = 0.0
            if available_weekly_hours > 0 and duration > (available_weekly_hours * 2.5):
                duration_penalty = 0.08

            # Category boost
            cat_bonus = 0.05 if c.get("category") in preferred_categories else 0.0

            final_score = base_score + skill_bonus + level_multiplier + cat_bonus - duration_penalty
            final_score = round(max(0.40, min(0.99, final_score)), 3)

            scored_candidates.append({
                **c,
                "score": final_score,
                "matched_skills": matched_tech or c.get("skills", [])[:3],
                "retrieval_sources": ["Personalized Profile Reranker"],
                "recommendation_reason": (
                    f"Aligned with your {skill_level} target"
                    + (f" and {', '.join(matched_tech[:2])}" if matched_tech else "")
                    + (f" within manageable {int(duration)}h duration" if duration <= available_weekly_hours * 2 else "")
                )
            })

        # Sort by final personalized score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates[:top_k]
