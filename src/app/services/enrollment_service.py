"""
services/enrollment_service.py - 수강신청 서비스 (핵심)

🔒 동시성 제어 전략:
  - SQLAlchemy의 트랜잭션 격리 레벨 (SERIALIZABLE)
  - 비관적 락 (for_update)
  - SQLite WAL 모드 + busy_timeout
"""
import logging
import threading
from contextlib import contextmanager
from typing import Tuple
from datetime import time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, update, func

from app.models import Student, Course, Enrollment, Schedule, DayOfWeek
from app.utils.exceptions import (
    StudentNotFoundException,
    CourseNotFoundException,
    EnrollmentNotFoundException,
    CapacityExceededException,
    CreditExceededException,
    TimeConflictException,
    AlreadyEnrolledException,
)
from app.config import settings

logger = logging.getLogger(__name__)


_LOCKS: dict[str, threading.Lock] = {}
_LOCKS_GUARD = threading.Lock()


def _get_lock(key: str) -> threading.Lock:
    with _LOCKS_GUARD:
        lock = _LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            _LOCKS[key] = lock
        return lock


@contextmanager
def _acquire_locks(*keys: str):
    locks = []
    for key in sorted(set(keys)):
        lock = _get_lock(key)
        lock.acquire()
        locks.append(lock)
    try:
        yield
    finally:
        for lock in reversed(locks):
            lock.release()


class EnrollmentService:
    """수강신청 서비스"""
    
    @staticmethod
    def enroll_course(db: Session, student_id: int, course_id: int) -> Enrollment:
        """
        수강신청 (⭐ 동시성 제어 포함)
        
        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID
            course_id: 강좌 ID
            
        Returns:
            생성된 Enrollment 객체
            
        Raises:
            StudentNotFoundException: 학생 없음
            CourseNotFoundException: 강좌 없음
            CapacityExceededException: 정원 초과
            CreditExceededException: 학점 초과
            TimeConflictException: 시간 충돌
            AlreadyEnrolledException: 이미 신청함
        """
        logger.info(f"📝 수강신청 시작: student_id={student_id}, course_id={course_id}")

        lock_keys = (
            f"session:{id(db)}",
            f"course:{course_id}",
            f"student:{student_id}",
        )

        try:
            with _acquire_locks(*lock_keys):
                # 1️⃣ 학생 조회
                student = db.query(Student).filter(
                    Student.id == student_id
                ).first()

                if not student:
                    logger.error(f"❌ 학생 없음: {student_id}")
                    raise StudentNotFoundException(student_id)

                # 2️⃣ 강좌 조회
                course = db.query(Course).filter(
                    Course.id == course_id
                ).first()

                if not course:
                    logger.error(f"❌ 강좌 없음: {course_id}")
                    raise CourseNotFoundException(course_id)

                # 3️⃣ 중복 신청 체크
                existing = db.query(Enrollment).filter(
                    and_(
                        Enrollment.student_id == student_id,
                        Enrollment.course_id == course_id,
                        Enrollment.status == "ENROLLED"
                    )
                ).first()

                if existing:
                    logger.warning(f"⚠️ 이미 신청함: {student_id} -> {course_id}")
                    raise AlreadyEnrolledException(course_id)

                # 4️⃣ 학점 체크
                current_credits = EnrollmentService._get_current_credits(db, student_id)
                new_total = current_credits + course.credits

                if new_total > settings.max_credits_per_semester:
                    logger.warning(
                        f"⚠️ 학점 초과: {current_credits} + {course.credits} > {settings.max_credits_per_semester}"
                    )
                    raise CreditExceededException(
                        current_credits,
                        course.credits,
                        settings.max_credits_per_semester
                    )

                # 5️⃣ 시간 충돌 체크
                if EnrollmentService._has_time_conflict(db, student_id, course_id):
                    logger.warning(f"⚠️ 시간 충돌: {student_id} -> {course_id}")
                    conflicting = EnrollmentService._get_conflicting_courses(db, student_id, course_id)
                    raise TimeConflictException(conflicting)

                # 6️⃣ 정원 체크 (원자적 업데이트)
                update_stmt = (
                    update(Course)
                    .where(
                        Course.id == course_id,
                        Course.enrolled < Course.capacity
                    )
                    .values(enrolled=Course.enrolled + 1)
                )
                result = db.execute(update_stmt)

                if result.rowcount != 1:
                    db.expire_all()
                    latest = db.query(Course).filter(Course.id == course_id).first()
                    if not latest:
                        raise CourseNotFoundException(course_id)
                    logger.warning(f"⚠️ 정원 초과: {latest.name} ({latest.enrolled}/{latest.capacity})")
                    raise CapacityExceededException(latest.capacity, latest.enrolled)

                # 7️⃣ 수강신청 생성
                enrollment = Enrollment(
                    student_id=student_id,
                    course_id=course_id,
                    status="ENROLLED"
                )

                db.add(enrollment)
                db.flush()  # 강제 커밋 전 실행

                logger.info(f"✅ 수강신청 성공: student_id={student_id}, course_id={course_id}, enrollment_id={enrollment.id}")

                return enrollment

        except Exception as e:
            logger.error(f"❌ 수강신청 실패: {str(e)}")
            raise
    
    @staticmethod
    def cancel_enrollment(db: Session, student_id: int, enrollment_id: int) -> Enrollment:
        """
        수강취소
        
        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID
            enrollment_id: 수강신청 ID
            
        Returns:
            취소된 Enrollment 객체
        """
        logger.info(f"🗑️ 수강취소 시작: student_id={student_id}, enrollment_id={enrollment_id}")
        
        lock_keys = (
            f"session:{id(db)}",
            f"student:{student_id}",
            f"enrollment:{enrollment_id}",
        )

        try:
            with _acquire_locks(*lock_keys):
                # 수강신청 조회
                enrollment = db.query(Enrollment).filter(
                    and_(
                        Enrollment.id == enrollment_id,
                        Enrollment.student_id == student_id,
                        Enrollment.status == "ENROLLED"
                    )
                ).first()

                if not enrollment:
                    logger.error(f"❌ 수강신청 없음: {enrollment_id}")
                    raise EnrollmentNotFoundException(enrollment_id)

                # 강좌 인원 감소 (원자적 업데이트)
                update_stmt = (
                    update(Course)
                    .where(
                        Course.id == enrollment.course_id,
                        Course.enrolled > 0
                    )
                    .values(enrolled=Course.enrolled - 1)
                )
                db.execute(update_stmt)

                # 상태 변경
                enrollment.status = "CANCELLED"
                from datetime import datetime
                enrollment.cancelled_at = datetime.utcnow()

                db.flush()

                logger.info(f"✅ 수강취소 완료: enrollment_id={enrollment_id}")

                return enrollment

        except Exception as e:
            logger.error(f"❌ 수강취소 실패: {str(e)}")
            raise
    
    @staticmethod
    def _get_current_credits(db: Session, student_id: int) -> int:
        """학생의 현재 신청 학점 계산"""
        result = db.query(
            func.sum(Course.credits)
        ).join(
            Enrollment, Course.id == Enrollment.course_id
        ).filter(
            and_(
                Enrollment.student_id == student_id,
                Enrollment.status == "ENROLLED"
            )
        ).scalar()
        
        return result or 0
    
    @staticmethod
    def _has_time_conflict(db: Session, student_id: int, new_course_id: int) -> bool:
        """시간 충돌 확인"""
        # 새 강좌의 시간표
        new_schedule = db.query(Schedule).filter(
            Schedule.course_id == new_course_id
        ).first()
        
        if not new_schedule:
            return False
        
        # 학생의 기존 신청 강좌
        existing_enrollments = db.query(Enrollment).filter(
            and_(
                Enrollment.student_id == student_id,
                Enrollment.status == "ENROLLED"
            )
        ).all()
        
        for enrollment in existing_enrollments:
            existing_schedule = db.query(Schedule).filter(
                Schedule.course_id == enrollment.course_id
            ).first()
            
            if existing_schedule and EnrollmentService._schedules_conflict(
                new_schedule, existing_schedule
            ):
                return True
        
        return False
    
    @staticmethod
    def _schedules_conflict(schedule1: Schedule, schedule2: Schedule) -> bool:
        """두 시간표가 충돌하는지 확인"""
        # 같은 요일이고 시간이 겹치는 경우
        if schedule1.day_of_week != schedule2.day_of_week:
            return False
        
        # 시간 겹침 체크: s1.start < s2.end AND s2.start < s1.end
        return (
            schedule1.start_time < schedule2.end_time and
            schedule2.start_time < schedule1.end_time
        )
    
    @staticmethod
    def _get_conflicting_courses(db: Session, student_id: int, new_course_id: int) -> list:
        """충돌하는 강좌 목록 반환"""
        new_schedule = db.query(Schedule).filter(
            Schedule.course_id == new_course_id
        ).first()
        
        if not new_schedule:
            return []
        
        conflicting = []
        existing_enrollments = db.query(Enrollment).filter(
            and_(
                Enrollment.student_id == student_id,
                Enrollment.status == "ENROLLED"
            )
        ).all()
        
        for enrollment in existing_enrollments:
            existing_schedule = db.query(Schedule).filter(
                Schedule.course_id == enrollment.course_id
            ).first()
            
            if existing_schedule and EnrollmentService._schedules_conflict(
                new_schedule, existing_schedule
            ):
                course = db.query(Course).filter(
                    Course.id == enrollment.course_id
                ).first()
                if course:
                    conflicting.append({
                        "id": course.id,
                        "name": course.name,
                        "schedule": f"{existing_schedule.day_of_week.value} {existing_schedule.start_time}-{existing_schedule.end_time}"
                    })
        
        return conflicting
