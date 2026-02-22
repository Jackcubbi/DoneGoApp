from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class WorkEntry(Base):
    __tablename__ = "work_entries"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("weekly_reports.id"), nullable=False)
    day = Column(String, nullable=False)        # Ma Ti Ke To Pe La Su
    hours = Column(String, nullable=True)       # e.g. "21/22/23"
    area = Column(String, nullable=True)        # m2
    objects = Column(String, nullable=True)      # Kohteet
    description = Column(String, nullable=True) # Työnkuvaus free text
    work_code = Column(Integer, nullable=True)

    report = relationship("WeeklyReport", back_populates="entries")
