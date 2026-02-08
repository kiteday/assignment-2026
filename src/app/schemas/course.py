"""
Course schemas.
"""
from pydantic import BaseModel
from datetime import datetime, time
from typing import Optional


class ScheduleResponse(BaseModel):
    """강의 시간표 응답"""
    id: int
    day_of_week: str  # "MON", "TUE", ...
    start_time: time  # "09:00"
    end_time: time    # "10:30"

    class Config:
        from_attributes = True

    def __str__(self):
        return f"{self.day_of_week} {self.start_time}-{self.end_time}"


class CourseResponse(BaseModel):
    """강좌 응답 (상세)"""
    id: int
    name: str
    code: str
    credits: int
    capacity: int
    enrolled: int
    professor_id: int
    department_id: int
    schedule: Optional[ScheduleResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    """강좌 목록 응답 (간단)"""
    id: int
    name: str
    code: str
    credits: int
    capacity: int
    enrolled: int
    professor_id: int
    department_id: int
    schedule: Optional[str] = None  # "월 09:00-10:30" 형식

    class Config:
        from_attributes = True
