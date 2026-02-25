from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_code = Column(String, nullable=True)      # User-defined ID e.g. "PRJ-001"
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    general_company = Column(String, nullable=True)   # Main / general contractor
    employer = Column(String, nullable=True)          # Worker's employer on this project
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="projects")
    reports = relationship("WeeklyReport", back_populates="project", cascade="all, delete-orphan")
