from datetime import datetime
from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: int
    doc_type: str
    filename: str
    filepath: str
    extracted_at: datetime

    class Config:
        orm_mode = True
