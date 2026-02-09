"""Report model."""
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sql_query: Mapped[str | None] = mapped_column(Text, nullable=True)
    complexity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    complexity_category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_system: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    migrated: Mapped[bool] = mapped_column(Boolean, default=False)
