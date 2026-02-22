from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    phone: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
