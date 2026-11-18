from typing import List, Dict, Any, Set

EVALUATION_QUERIES = [
    {
        "query": "Beginner Node.js backend development",
        "intent_skills": ["Node.js", "Express", "Backend"],
        "category": "Backend Development",
        "difficulty": "Beginner"
    },
    {
        "query": "Advanced React performance optimization",
        "intent_skills": ["React", "Performance", "Frontend Architecture"],
        "category": "Frontend Development",
        "difficulty": "Advanced"
    },
    {
        "query": "Python machine learning courses under 10 hours",
        "intent_skills": ["Machine Learning", "Python", "NumPy"],
        "category": "AI & Machine Learning",
        "max_duration": 15
    },
    {
        "query": "Database design and PostgreSQL optimization for backend developers",
        "intent_skills": ["PostgreSQL", "SQL", "Database Internals"],
        "category": "Backend Development",
    },
    {
        "query": "Docker and Kubernetes for beginners",
        "intent_skills": ["Docker", "Kubernetes", "Containers"],
        "category": "Cloud & DevOps",
        "difficulty": "Beginner"
    },
    {
        "query": "FastAPI asynchronous REST API with Python",
        "intent_skills": ["FastAPI", "Python", "Pydantic", "SQLAlchemy"],
        "category": "Backend Development"
    },
    {
        "query": "Full Stack web development with Next.js App Router",
        "intent_skills": ["Next.js", "React", "TypeScript"],
        "category": "Frontend Development"
    },
    {
        "query": "Infrastructure as Code using Terraform and AWS",
        "intent_skills": ["Terraform", "AWS", "Infrastructure as Code"],
        "category": "Cloud & DevOps"
    },
    {
        "query": "Deep learning and neural networks with PyTorch",
        "intent_skills": ["PyTorch", "Deep Learning", "Neural Networks"],
        "category": "AI & Machine Learning"
    },
    {
        "query": "Building RAG applications and vector search with LangChain",
        "intent_skills": ["Generative AI", "LangChain", "RAG", "Vector Search"],
        "category": "AI & Machine Learning"
    },
    {
        "query": "Apache Spark and PySpark big data engineering",
        "intent_skills": ["Apache Spark", "PySpark", "Big Data", "Data Engineering"],
        "category": "Data Engineering & Analytics"
    },
    {
        "query": "Modern SQL bootcamp with window functions and aggregation",
        "intent_skills": ["SQL", "PostgreSQL", "Data Analysis"],
        "category": "Data Engineering & Analytics"
    },
    {
        "query": "Microservices architecture and event-driven systems",
        "intent_skills": ["Microservices", "System Design", "Architecture"],
        "category": "System Design & Architecture"
    },
    {
        "query": "Cross-platform mobile apps with Flutter and Dart",
        "intent_skills": ["Flutter", "Dart", "Mobile"],
        "category": "Mobile Development"
    },
    {
        "query": "Ethical hacking and web penetration testing OWASP",
        "intent_skills": ["Cybersecurity", "Ethical Hacking", "OWASP"],
        "category": "Cybersecurity"
    },
    {
        "query": "High performance caching and Redis data structures",
        "intent_skills": ["Redis", "Caching", "Performance"],
        "category": "System Design & Architecture"
    },
    {
        "query": "Go Golang backend microservices with gRPC",
        "intent_skills": ["Go", "Golang", "gRPC", "Microservices"],
        "category": "Backend Development"
    },
    {
        "query": "Vue 3 Composition API and Pinia state management",
        "intent_skills": ["Vue.js", "Pinia", "Vite"],
        "category": "Frontend Development"
    },
    {
        "query": "CI/CD pipelines with GitHub Actions and Docker",
        "intent_skills": ["CI/CD", "GitHub Actions", "Docker"],
        "category": "Cloud & DevOps"
    },
    {
        "query": "Real-time streaming data architectures with Apache Kafka",
        "intent_skills": ["Apache Kafka", "Streaming", "Data Engineering"],
        "category": "Data Engineering & Analytics"
    },
    {
        "query": "TypeScript static typing for modern JavaScript applications",
        "intent_skills": ["TypeScript", "JavaScript", "Types"],
        "category": "Frontend Development"
    },
    {
        "query": "Site reliability engineering and Prometheus Grafana monitoring",
        "intent_skills": ["SRE", "Prometheus", "Grafana"],
        "category": "Cloud & DevOps"
    },
    {
        "query": "Natural language processing with Hugging Face Transformers",
        "intent_skills": ["NLP", "Transformers", "Hugging Face"],
        "category": "AI & Machine Learning"
    },
    {
        "query": "Cross-platform iOS and Android apps with React Native Expo",
        "intent_skills": ["React Native", "Mobile", "Expo"],
        "category": "Mobile Development"
    },
    {
        "query": "Enterprise Java Spring Boot 3 microservices",
        "intent_skills": ["Java", "Spring Boot", "Microservices"],
        "category": "Backend Development"
    }
]

def find_relevant_course_ids(query_spec: Dict[str, Any], all_courses: List[Dict[str, Any]]) -> Set[str]:
    """
    Determine ground-truth relevant courses based on explicit semantic labels and content match.
    """
    relevant = set()
    intent_skills = [s.lower() for s in query_spec.get("intent_skills", [])]
    target_category = query_spec.get("category", "")
    target_difficulty = query_spec.get("difficulty", "")
    max_duration = query_spec.get("max_duration")

    for c in all_courses:
        # Category check
        if target_category and c.get("category") != target_category:
            continue

        # Difficulty check if specified
        if target_difficulty and c.get("difficulty") != target_difficulty:
            continue

        # Duration check if specified
        if max_duration and c.get("duration_hours", 0) > max_duration:
            continue

        # Skill match check
        course_skills = [s.lower() for s in c.get("skills", [])]
        course_title = c.get("title", "").lower()
        course_desc = c.get("description", "").lower()

        # Check if any intent skill is present in course skills, title, or description
        skill_hits = sum(1 for s in intent_skills if s in course_skills or s in course_title or s in course_desc)
        if skill_hits >= 1:
            relevant.add(c["id"])

    return relevant

