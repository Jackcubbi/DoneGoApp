from datetime import datetime

from pydantic import BaseModel


class WorkEntryIn(BaseModel):
    day: str
    hours: str | None = None
    area: str | None = None
    objects: str | None = None
    description: str | None = None
    work_code: int | None = None


class WorkEntryOut(BaseModel):
    id: int
    day: str
    hours: str | None
    area: str | None
    objects: str | None
    description: str | None
    work_code: int | None

    model_config = {"from_attributes": True}


class ReportCreate(BaseModel):
    week_number: int
    year: int
    status: str = "draft"
    project_id: int | None = None
    entries: list[WorkEntryIn] = []


class ReportUpdate(BaseModel):
    week_number: int | None = None
    year: int | None = None
    project_id: int | None = None
    entries: list[WorkEntryIn] | None = None


class ReportOut(BaseModel):
    id: int
    user_id: int
    project_id: int | None
    week_number: int
    year: int
    status: str
    created_at: datetime
    entries: list[WorkEntryOut] = []

    model_config = {"from_attributes": True}
