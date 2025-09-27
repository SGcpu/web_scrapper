"""Database configuration and connection management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# Create SQLite engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Required for SQLite
    },
    poolclass=StaticPool,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Initialize database and create all tables."""
    try:
        # Import all models to ensure they are registered
        from app.models.product import Product
        from app.models.review import Review
        from app.models.analysis import AnalysisResult
        from app.models.scraping_session import ScrapingSession
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization error: {e}")
        # Create basic tables structure if imports fail
        Base.metadata.create_all(bind=engine)
        print("Database created with basic structure")


async def close_db():
    """Close database connections."""
    engine.dispose()
    print("Database connections closed!")