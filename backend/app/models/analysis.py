"""COE Analysis model."""
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class COEAnalysis(Base):
    __tablename__ = "coe_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    report_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duplicate_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unique_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_complexity: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    results_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
