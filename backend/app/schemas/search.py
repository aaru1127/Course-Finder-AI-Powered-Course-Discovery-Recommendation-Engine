from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from backend.app.schemas.course import CourseResponse

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language or keyword search query")
    difficulty: Optional[str] = Field(None, description="Beginner, Intermediate, Advanced, or All")
    category: Optional[str] = Field(None, description="Category filter")
    max_duration: Optional[float] = Field(None, ge=1.0, description="Maximum duration in hours")
    min_duration: Optional[float] = Field(None, ge=0.0, description="Minimum duration in hours")
    provider: Optional[str] = Field(None, description="Filter by course provider")
    max_price: Optional[float] = Field(None, ge=0.0, description="Filter by maximum price")
    free_only: Optional[bool] = Field(False, description="Filter for free courses only (price == 0)")
    mode: Literal["hybrid", "semantic", "keyword"] = Field(
        default="hybrid",
        description="Search retrieval mode: hybrid (BM25 + pgvector RRF), semantic (dense vector), or keyword (BM25)"
    )
    top_k: int = Field(default=10, ge=1, le=50, description="Maximum number of results to return")

class SearchResponse(BaseModel):
    query: str
    mode: str
    total_results: int
    results: List[CourseResponse]
    cache_status: Literal["HIT", "MISS", "BYPASS"]
    execution_time_ms: float
    extracted_filters: Optional[dict] = Field(default_factory=dict, description="Auto-extracted filters from natural language query")

class SimilarCoursesRequest(BaseModel):
    course_id: str
    top_k: int = Field(default=6, ge=1, le=20)
    difficulty: Optional[str] = None
    max_duration: Optional[float] = None

class PersonalizationRequest(BaseModel):
    skill_level: str = Field(..., description="Beginner, Intermediate, or Advanced")
    target_technologies: List[str] = Field(default_factory=list, description="Technologies user wants to learn")
    learning_goal: Optional[str] = Field(None, description="Goal e.g. 'Build REST APIs and land backend job'")
    available_weekly_hours: Optional[float] = Field(10.0, description="Weekly hours available")
    preferred_categories: List[str] = Field(default_factory=list)
    top_k: int = Field(default=8, ge=1, le=20)

