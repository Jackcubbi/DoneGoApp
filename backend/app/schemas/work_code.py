from pydantic import BaseModel


class WorkCodeCreate(BaseModel):
    code: int
    description: str


class WorkCodeUpdate(BaseModel):
    code: int | None = None
    description: str | None = None


class WorkCodeOut(BaseModel):
    id: int
    code: int
    description: str
    user_id: int | None

    model_config = {"from_attributes": True}
