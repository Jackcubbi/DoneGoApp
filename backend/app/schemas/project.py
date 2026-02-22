from datetime import datetime
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    project_code: str | None = None
    name: str
    address: str | None = None
    general_company: str | None = None
    employer: str | None = None


class ProjectUpdate(BaseModel):
    project_code: str | None = None
    name: str | None = None
    address: str | None = None
    general_company: str | None = None
    employer: str | None = None


class ProjectOut(BaseModel):
    id: int
    user_id: int
    project_code: str | None
    name: str
    address: str | None
    general_company: str | None
    employer: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
