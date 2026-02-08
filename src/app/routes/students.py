"""
routes/students.py - 학생 관련 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student
from app.schemas import StudentResponse
from app.utils.exceptions import StudentNotFoundException

router = APIRouter(prefix="/api/v1/students", tags=["students"])


@router.get("", response_model=list[StudentResponse])
def list_students(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    학생 목록 조회
    
    - `skip`: 건너뛸 레코드 수 (페이징)
    - `limit`: 반환할 최대 레코드 수
    """
    students = db.query(Student).offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """학생 상세 조회"""
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise StudentNotFoundException(student_id)
    
    return student