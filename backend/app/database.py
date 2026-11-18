import json
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from backend.app.config import settings
from backend.app.models.course import Base, CourseModel

logger = logging.getLogger(__name__)

engine = None
SessionLocal = None
is_postgres = False

def init_db():
    global engine, SessionLocal, is_postgres
    
    # Try PostgreSQL first
    try:
        pg_engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 2})
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
            # Attempt to create pgvector extension if postgres
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
                logger.info("PostgreSQL pgvector extension verified.")
            except Exception as e:
                logger.info(f"pgvector extension check notice: {e}")
        engine = pg_engine
        is_postgres = True
        logger.info(f"Connected to PostgreSQL at {settings.DATABASE_URL}")
    except Exception as e:
        logger.info(f"PostgreSQL connection skipped ({e}). Falling back to SQLite.")
        sqlite_url = f"sqlite:///{settings.SQLITE_FALLBACK_PATH}"
        Path(settings.SQLITE_FALLBACK_PATH).parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        is_postgres = False

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")

def get_db():
    if SessionLocal is None:
        init_db()
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_database_if_empty():
    """Populate courses into the database if the table is empty."""
    if SessionLocal is None:
        init_db()

    db: Session = SessionLocal()
    try:
        count = db.query(CourseModel).count()
        if count == 0:
            logger.info("Database empty. Seeding from dataset...")
            with open(settings.DATASET_PATH, "r", encoding="utf-8") as f:
                courses = json.load(f)

            for c in courses:
                model = CourseModel(
                    id=c["id"],
                    title=c["title"],
                    provider=c["provider"],
                    description=c["description"],
                    skills=json.dumps(c.get("skills", [])),
                    category=c["category"],
                    difficulty=c["difficulty"],
                    duration_hours=float(c["duration_hours"]),
                    language=c.get("language", "English"),
                    price=float(c.get("price", 0.0)),
                    rating=float(c.get("rating", 4.5)),
                    course_url=c["course_url"],
                    embedding_json=None
                )
                db.add(model)
            db.commit()
            logger.info(f"Seeded {len(courses)} courses into database.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

