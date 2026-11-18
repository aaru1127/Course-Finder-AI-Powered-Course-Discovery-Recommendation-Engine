import json
from sqlalchemy import Column, String, Text, Float, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class CourseModel(Base):
    __tablename__ = "courses"

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    provider = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    skills = Column(Text, nullable=False)  # JSON-serialized list of skills
    category = Column(String(100), nullable=False, index=True)
    difficulty = Column(String(50), nullable=False, index=True)
    duration_hours = Column(Float, nullable=False, index=True)
    language = Column(String(50), default="English")
    price = Column(Float, default=0.0, index=True)
    rating = Column(Float, default=4.5)
    course_url = Column(String(500), nullable=False)
    embedding_json = Column(Text, nullable=True)  # JSON-serialized 384-float vector

    def to_dict(self):
        try:
            skills_list = json.loads(self.skills) if self.skills else []
        except Exception:
            skills_list = [s.strip() for s in self.skills.split(",")] if self.skills else []

        return {
            "id": self.id,
            "title": self.title,
            "provider": self.provider,
            "description": self.description,
            "skills": skills_list,
            "category": self.category,
            "difficulty": self.difficulty,
            "duration_hours": self.duration_hours,
            "language": self.language,
            "price": self.price,
            "rating": self.rating,
            "course_url": self.course_url,
        }

