from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.settings import settings

# Create SQLite database engine
# connect_args={"check_same_thread": False} is required for SQLite in multithreaded FastAPI apps
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI dependency to yield database sessions and handle teardown."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
