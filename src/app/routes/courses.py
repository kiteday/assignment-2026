"""
routes/courses.py - 강좌 관련 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models import Course, Department, Schedule
from app.schemas import CourseListResponse, CourseResponse
from app.utils.exceptions import CourseNotFoundException

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])


def _format_schedule(schedule: Schedule) -> str:
    """시간표를 문자열로 변환"""
    if not schedule:
        return None
    return f"{schedule.day_of_week.value} {schedule.start_time.strftime('%H:%M')}-{schedule.end_time.strftime('%H:%M')}"


@router.get("", response_model=list[CourseListResponse])
def list_courses(
    db: Session = Depends(get_db),
    department_id: int = Query(None, description="학과 ID (선택)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    강좌 목록 조회
    
    - `department_id`: 특정 학과의 강좌만 조회 (옵션)
    - `skip`: 페이징 오프셋
    - `limit`: 페이징 크기
    """
    query = db.query(Course)
    
    if department_id:
        query = query.filter(Course.department_id == department_id)
    
    courses = query.offset(skip).limit(limit).all()
    
    result = []
    for course in courses:
        course_dict = {
            "id": course.id,
            "name": course.name,
            "code": course.code,
            "credits": course.credits,
            "capacity": course.capacity,
            "enrolled": course.enrolled,
            "professor_id": course.professor_id,
            "department_id": course.department_id,
            "schedule": _format_schedule(course.schedule)
        }
        result.append(course_dict)
    
    return result


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    """강좌 상세 조회"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise CourseNotFoundException(course_id)
    
    return course