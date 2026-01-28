from datetime import datetime
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    title: str
    description: str | None = ""


class ProjectRead(BaseModel):
    id: int
    title: str
    description: str | None
    created_at: datetime

    class Config:
        orm_mode = True
