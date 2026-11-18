from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

class CourseBase(BaseModel):
    id: str = Field(..., description="Unique course identifier e.g. course_001")
    title: str = Field(..., min_length=3, description="Course title")
    provider: str = Field(..., description="Content publisher or platform")
    description: str = Field(..., min_length=10, description="Full course description")
    skills: List[str] = Field(default_factory=list, description="Extracted technology and skill tags")
    category: str = Field(..., description="Domain category e.g. Backend Development")
    difficulty: str = Field(..., description="Difficulty level: Beginner, Intermediate, or Advanced")
    duration_hours: float = Field(..., ge=0.5, description="Estimated total course duration in hours")
    language: str = Field(default="English", description="Course instruction language")
    price: float = Field(default=0.0, ge=0.0, description="Enrollment fee in USD (0.0 = free)")
    rating: float = Field(default=4.5, ge=1.0, le=5.0, description="Average learner star rating")
    course_url: str = Field(..., description="Web URL to the course")

class CourseCreate(CourseBase):
    pass

class CourseInDB(CourseBase):
    has_embedding: bool = False

class CourseResponse(CourseBase):
    score: Optional[float] = Field(None, description="Search relevance score (0.0 to 1.0 or normalized %)")
    matched_skills: Optional[List[str]] = Field(default_factory=list, description="Skills matching search query")
    retrieval_sources: Optional[List[str]] = Field(default_factory=list, description="BM25, Semantic, or Both")

