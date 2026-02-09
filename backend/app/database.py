"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.config import settings

# SQLite needs check_same_thread=False for FastAPI
connect_args = {}
if "sqlite" in settings.database_url:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    poolclass=StaticPool if "sqlite" in settings.database_url else None,
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


def get_db():
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Call on startup."""
    from app.models import user, report, analysis  # noqa: F401
    Base.metadata.create_all(bind=engine)
