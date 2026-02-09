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
    """Create all tables and ensure a default admin user for demo/POC."""
    from app.models import user, report, analysis  # noqa: F401
    from app.models.user import User
    from app.core.security import get_password_hash

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Ensure a default admin user exists for demo purposes.
    # Username: admin, Password: Password123
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if not existing:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=get_password_hash("Password123"),
                is_active=True,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()
