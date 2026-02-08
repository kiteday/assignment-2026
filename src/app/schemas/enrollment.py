"""
Enrollment schemas.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.schemas.course import CourseResponse


class EnrollmentRequest(BaseModel):
    """수강신청 요청"""
    course_id: int = Field(..., gt=0, description="강좌 ID")


class EnrollmentResponse(BaseModel):
    """수강신청 응답"""
    id: int
    student_id: int
    course_id: int
    status: str
    enrolled_at: datetime
    cancelled_at: Optional[datetime] = None
    created_at: datetime

    # 추가 정보 (nested)
    course: Optional[CourseResponse] = None

    class Config:
        from_attributes = True


class EnrollmentCancelRequest(BaseModel):
    """수강취소 요청"""
    enrollment_id: int = Field(..., gt=0, description="수강신청 ID")
