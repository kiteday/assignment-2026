"""
utils/exceptions.py - 비즈니스 예외
"""
from fastapi import HTTPException, status


class BusinessException(HTTPException):
    """비즈니스 로직 예외 기본 클래스"""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        detail: dict = None,
    ):
        self.error_code = error_code
        self.message = message
        self.detail = detail or {}
        
        super().__init__(
            status_code=status_code,
            detail={
                "code": error_code,
                "message": message,
                **self.detail,
            }
        )


# 정원 관련
class CapacityExceededException(BusinessException):
    """정원 초과"""
    def __init__(self, capacity: int, enrolled: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="CAPACITY_EXCEEDED",
            message=f"This course is full (capacity: {capacity}, enrolled: {enrolled})",
        )


# 학점 관련
class CreditExceededException(BusinessException):
    """학점 초과"""
    def __init__(self, current_credits: int, new_credits: int, max_credits: int = 18):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="CREDIT_EXCEEDED",
            message=f"Credit limit exceeded. Current: {current_credits}, Adding: {new_credits}, Max: {max_credits}",
        )


# 시간 충돌
class TimeConflictException(BusinessException):
    """시간 충돌"""
    def __init__(self, conflicting_courses: list = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="TIME_CONFLICT",
            message="Schedule conflicts with your existing enrollment",
            detail={"conflicting_courses": conflicting_courses or []}
        )


# 중복 신청
class AlreadyEnrolledException(BusinessException):
    """이미 신청한 강좌"""
    def __init__(self, course_id: int):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="ALREADY_ENROLLED",
            message=f"You are already enrolled in this course (course_id: {course_id})",
        )


# 찾을 수 없음
class StudentNotFoundException(BusinessException):
    """학생 없음"""
    def __init__(self, student_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="STUDENT_NOT_FOUND",
            message=f"Student not found (id: {student_id})",
        )


class CourseNotFoundException(BusinessException):
    """강좌 없음"""
    def __init__(self, course_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="COURSE_NOT_FOUND",
            message=f"Course not found (id: {course_id})",
        )


class EnrollmentNotFoundException(BusinessException):
    """수강신청 없음"""
    def __init__(self, enrollment_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ENROLLMENT_NOT_FOUND",
            message=f"Enrollment not found (id: {enrollment_id})",
        )


# 데이터 정합성
class DatabaseError(BusinessException):
    """데이터베이스 오류"""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            message=message,
        )


class DeadlockException(BusinessException):
    """데이터베이스 데드락"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="DEADLOCK",
            message="Request failed due to database lock. Please retry.",
        )