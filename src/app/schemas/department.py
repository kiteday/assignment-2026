"""
Department schemas.
"""
from pydantic import BaseModel
from datetime import datetime


class DepartmentResponse(BaseModel):
    """학과 응답"""
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
