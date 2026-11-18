import re
from typing import Dict, Any, Optional, Tuple

class QueryIntentParser:
    """
    Extracts explicit metadata constraints and semantic intent from natural-language search queries.
    e.g. 'I am a beginner looking for Node.js backend courses under 20 hours'
    -> difficulty='Beginner', max_duration=20, category='Backend Development'
    """

    DIFFICULTIES = ["beginner", "intermediate", "advanced"]
    
    CATEGORY_MAPPINGS = {
        "backend": "Backend Development",
        "server": "Backend Development",
        "frontend": "Frontend Development",
        "react": "Frontend Development",
        "vue": "Frontend Development",
        "devops": "Cloud & DevOps",
        "cloud": "Cloud & DevOps",
        "docker": "Cloud & DevOps",
        "kubernetes": "Cloud & DevOps",
        "aws": "Cloud & DevOps",
        "ai": "AI & Machine Learning",
        "machine learning": "AI & Machine Learning",
        "deep learning": "AI & Machine Learning",
        "llm": "AI & Machine Learning",
        "rag": "AI & Machine Learning",
        "data": "Data Engineering & Analytics",
        "sql": "Data Engineering & Analytics",
        "spark": "Data Engineering & Analytics",
        "system design": "System Design & Architecture",
        "architecture": "System Design & Architecture",
        "mobile": "Mobile Development",
        "ios": "Mobile Development",
        "android": "Mobile Development",
        "security": "Cybersecurity",
        "ethical hacking": "Cybersecurity",
    }

    @classmethod
    def parse(cls, query: str) -> Dict[str, Any]:
        extracted = {}
        q_lower = query.lower()

        # Extract Difficulty
        for diff in cls.DIFFICULTIES:
            if re.search(r'\b' + diff + r'\b', q_lower):
                extracted["difficulty"] = diff.capitalize()
                break

        # Extract Duration (e.g. "under 20 hours", "less than 15 hrs", "< 10 hours", "10h")
        duration_match = re.search(r'(?:under|less than|<|within|max)\s*(\d+(?:\.\d+)?)\s*(?:hours|hrs|hr|h)?', q_lower)
        if duration_match:
            try:
                extracted["max_duration"] = float(duration_match.group(1))
            except Exception:
                pass
        else:
            # Check for direct pattern like "20 hours"
            dur_match2 = re.search(r'(\d+(?:\.\d+)?)\s*(?:hours|hrs)\b', q_lower)
            if dur_match2:
                try:
                    extracted["max_duration"] = float(dur_match2.group(1))
                except Exception:
                    pass

        # Extract Price constraint (free)
        if re.search(r'\b(free|no cost|zero price)\b', q_lower):
            extracted["free_only"] = True

        # Extract Category suggestion
        for kw, cat in cls.CATEGORY_MAPPINGS.items():
            if re.search(r'\b' + re.escape(kw) + r'\b', q_lower):
                extracted["suggested_category"] = cat
                break

        return extracted

