"""
routes/enrollments.py - 수강신청 관련 API (핵심)
"""
from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models import Enrollment, Student, Course, Schedule
from app.schemas import EnrollmentRequest, EnrollmentResponse, StudentScheduleResponse, CourseListResponse
from app.services.enrollment_service import EnrollmentService
from app.utils.exceptions import StudentNotFoundException, EnrollmentNotFoundException

router = APIRouter(prefix="/api/v1/students", tags=["enrollments"])


@router.post("/{student_id}/enrollments", response_model=EnrollmentResponse, status_code=201)
def enroll_course(
    student_id: int,
    request: EnrollmentRequest,
    db: Session = Depends(get_db)
):
    """
    수강신청 (⭐ 동시성 제어 적용)
    
    - `student_id`: 학생 ID
    - `course_id`: 강좌 ID
    
    성공 시 201 Created, 실패 시 400/409 에러 반환
    """
    enrollment = EnrollmentService.enroll_course(
        db=db,
        student_id=student_id,
        course_id=request.course_id
    )
    
    # 트랜잭션 커밋
    db.commit()
    db.refresh(enrollment)
    
    return enrollment


@router.delete("/{student_id}/enrollments/{enrollment_id}", response_model=EnrollmentResponse)
def cancel_enrollment(
    student_id: int,
    enrollment_id: int,
    db: Session = Depends(get_db)
):
    """
    수강취소
    
    - `student_id`: 학생 ID
    - `enrollment_id`: 수강신청 ID
    """
    enrollment = EnrollmentService.cancel_enrollment(
        db=db,
        student_id=student_id,
        enrollment_id=enrollment_id
    )
    
    db.commit()
    db.refresh(enrollment)
    
    return enrollment


@router.get("/{student_id}/schedule", response_model=StudentScheduleResponse)
def get_schedule(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    학생의 이번 학기 시간표 조회
    
    - 신청한 모든 강좌와 총 학점 표시
    """
    # 학생 존재 확인
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise StudentNotFoundException(student_id)
    
    # 신청 강좌 조회
    enrollments = db.query(Enrollment).filter(
        and_(
            Enrollment.student_id == student_id,
            Enrollment.status == "ENROLLED"
        )
    ).all()
    
    # 강좌 목록 + 시간표
    courses = []
    total_credits = 0
    
    for enrollment in enrollments:
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        if course:
            schedule = db.query(Schedule).filter(Schedule.course_id == course.id).first()
            
            course_dict = CourseListResponse(
                id=course.id,
                name=course.name,
                code=course.code,
                credits=course.credits,
                capacity=course.capacity,
                enrolled=course.enrolled,
                professor_id=course.professor_id,
                department_id=course.department_id,
                schedule=f"{schedule.day_of_week.value} {schedule.start_time.strftime('%H:%M')}-{schedule.end_time.strftime('%H:%M')}" if schedule else None
            )
            courses.append(course_dict)
            total_credits += course.credits
    
    return StudentScheduleResponse(
        student_id=student_id,
        student_name=student.name,
        total_credits=total_credits,
        courses=courses
    )


@router.get("/{student_id}/enrollments", response_model=list[EnrollmentResponse])
def list_enrollments(
    student_id: int,
    db: Session = Depends(get_db),
    status: str = Query(None, description="상태 필터 (ENROLLED, CANCELLED)")
):
    """
    학생의 수강신청 목록 조회
    
    - `status`: ENROLLED (신청) 또는 CANCELLED (취소) 필터링
    """
    # 학생 존재 확인
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise StudentNotFoundException(student_id)
    
    query = db.query(Enrollment).filter(Enrollment.student_id == student_id)
    
    if status:
        query = query.filter(Enrollment.status == status)
    
    enrollments = query.all()
    
    return enrollments