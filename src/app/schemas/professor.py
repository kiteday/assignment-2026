"""
Professor schemas.
"""
from pydantic import BaseModel
from datetime import datetime


class ProfessorResponse(BaseModel):
    """교수 응답"""
    id: int
    name: str
    email: str
    department_id: int
    created_at: datetime

    class Config:
        from_attributes = True
