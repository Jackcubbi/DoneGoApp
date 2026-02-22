from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    week_number = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(String, default="draft")  # draft | saved | sent
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="reports")
    project = relationship("Project", back_populates="reports")
    entries = relationship(
        "WorkEntry", back_populates="report", cascade="all, delete-orphan"
    )
