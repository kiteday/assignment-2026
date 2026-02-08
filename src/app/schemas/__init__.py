"""
schemas/ - Pydantic 스키마 (API 요청/응답)
"""
from app.schemas.department import DepartmentResponse
from app.schemas.professor import ProfessorResponse
from app.schemas.course import ScheduleResponse, CourseResponse, CourseListResponse
from app.schemas.student import StudentResponse, StudentWithEnrollmentsResponse, StudentScheduleResponse
from app.schemas.enrollment import EnrollmentRequest, EnrollmentResponse, EnrollmentCancelRequest

__all__ = [
    "DepartmentResponse",
    "ProfessorResponse",
    "ScheduleResponse",
    "CourseResponse",
    "CourseListResponse",
    "StudentResponse",
    "StudentWithEnrollmentsResponse",
    "StudentScheduleResponse",
    "EnrollmentRequest",
    "EnrollmentResponse",
    "EnrollmentCancelRequest",
]

# Forward refs
StudentWithEnrollmentsResponse.model_rebuild()
