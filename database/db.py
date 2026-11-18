
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Get project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database URL
DATABASE_URL = f"sqlite:///{BASE_DIR / 'bankbot.db'}"


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for database models
Base = declarative_base()


# Database session generator
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
