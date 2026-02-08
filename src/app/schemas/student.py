"""
Student schemas.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List

from app.schemas.course import CourseListResponse
from app.schemas.enrollment import EnrollmentResponse


class StudentResponse(BaseModel):
    """학생 응답"""
    id: int
    name: str
    student_id: str
    email: str
    department_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StudentWithEnrollmentsResponse(StudentResponse):
    """학생 + 수강신청 목록"""
    enrollments: List[EnrollmentResponse] = []


class StudentScheduleResponse(BaseModel):
    """학생 시간표 응답"""
    student_id: int
    student_name: str
    total_credits: int
    courses: List[CourseListResponse] = []

    class Config:
        from_attributes = True
