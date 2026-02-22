from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class WorkCode(Base):
    __tablename__ = "work_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    # NULL user_id = system-wide default; set user_id for custom user codes
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="work_codes")
