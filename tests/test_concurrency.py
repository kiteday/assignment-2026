"""
tests/test_concurrency.py - 동시성 제어 테스트 (가장 중요!)

정원 1명 남은 강좌에 여러 명이 동시에 신청할 때,
정확히 1명만 성공하고 나머지는 실패해야 한다.
"""
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from fastapi import status

from app.models import Department, Professor, Course, Student, Schedule, DayOfWeek
from app.services.enrollment_service import EnrollmentService
from app.utils.exceptions import CapacityExceededException
from datetime import time


@pytest.fixture
def concurrent_setup(test_db: Session):
    """동시성 테스트 셋업"""
    # 학과
    dept = Department(name="컴퓨터공학과")
    test_db.add(dept)
    test_db.commit()
    
    # 교수
    prof = Professor(
        name="김교수",
        email="prof@concurrent.test",
        department_id=dept.id
    )
    test_db.add(prof)
    test_db.commit()
    
    # 강좌 (정원 1명!)
    course = Course(
        name="동시성 테스트 강좌",
        code="CONC001",
        credits=3,
        capacity=1,  # ⭐ 중요: 정원 1명
        professor_id=prof.id,
        department_id=dept.id
    )
    test_db.add(course)
    test_db.commit()
    
    # 시간표
    schedule = Schedule(
        course_id=course.id,
        day_of_week=DayOfWeek.MON,
        start_time=time(9, 0),
        end_time=time(10, 30)
    )
    test_db.add(schedule)
    test_db.commit()
    
    # 학생 50명
    students = []
    for i in range(50):
        student = Student(
            name=f"학생{i:02d}",
            student_id=f"CONC{i:04d}",
            email=f"student{i:04d}@concurrent.test",
            department_id=dept.id
        )
        students.append(student)
    
    test_db.add_all(students)
    test_db.commit()
    
    return {
        "course": course,
        "students": students,
        "db": test_db
    }


def test_concurrent_enrollment_50_students(concurrent_setup, test_session_factory):
    """
    ⭐ 핵심 테스트: 50명이 동시에 신청 → 정확히 1명만 성공
    
    이것이 동시성 제어가 제대로 작동하는지 검증하는 가장 중요한 테스트입니다.
    """
    test_db = concurrent_setup["db"]
    course = concurrent_setup["course"]
    students = concurrent_setup["students"]
    
    success_count = 0
    failure_count = 0
    failures = []
    
    def enroll_student(student_id: int):
        """학생 신청"""
        db = test_session_factory()
        try:
            EnrollmentService.enroll_course(db, student_id, course.id)
            db.commit()
            return True
        except CapacityExceededException as e:
            db.rollback()
            return False
        except Exception as e:
            db.rollback()
            return False
        finally:
            db.close()
    
    # 50개 스레드에서 동시 실행
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [
            executor.submit(enroll_student, student.id)
            for student in students
        ]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                success_count += 1
            else:
                failure_count += 1
    
    # 검증
    print(f"\n🎯 동시성 제어 테스트 결과:")
    print(f"   성공: {success_count}명")
    print(f"   실패: {failure_count}명")
    print(f"   총: {success_count + failure_count}명")
    
    # ⭐ 가장 중요한 검증: 정확히 1명만 성공!
    assert success_count == 1, f"정확히 1명만 성공해야 하는데, {success_count}명이 성공했습니다."
    assert failure_count == 49, f"{failure_count}명이 실패했습니다."
    
    # DB 검증
    test_db.expire_all()  # 캐시 무효화
    updated_course = test_db.query(Course).filter(Course.id == course.id).first()
    
    assert updated_course.enrolled == 1, f"enrolled 값이 올바르지 않습니다: {updated_course.enrolled}"
    assert updated_course.enrolled <= updated_course.capacity, "정원을 초과했습니다!"


def test_concurrent_enrollment_100_students(concurrent_setup, test_session_factory):
    """
    100명이 동시에 신청 → 정확히 1명만 성공
    
    더 많은 동시 요청으로 테스트
    """
    test_db = concurrent_setup["db"]
    course = concurrent_setup["course"]
    
    # 추가 학생 생성
    extra_students = []
    for i in range(50, 100):
        student = Student(
            name=f"학생{i:02d}",
            student_id=f"CONC{i:04d}",
            email=f"student{i:04d}@concurrent.test",
            department_id=course.department_id
        )
        extra_students.append(student)
    
    test_db.add_all(extra_students)
    test_db.commit()
    
    all_students = concurrent_setup["students"] + extra_students
    
    success_count = 0
    failure_count = 0
    
    def enroll_student(student_id: int):
        """학생 신청"""
        db = test_session_factory()
        try:
            EnrollmentService.enroll_course(db, student_id, course.id)
            db.commit()
            return True
        except:
            db.rollback()
            return False
        finally:
            db.close()
    
    # 100개 스레드에서 동시 실행
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [
            executor.submit(enroll_student, student.id)
            for student in all_students
        ]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                success_count += 1
            else:
                failure_count += 1
    
    print(f"\n🎯 100명 동시성 테스트 결과:")
    print(f"   성공: {success_count}명")
    print(f"   실패: {failure_count}명")
    
    # ⭐ 정확히 1명만 성공
    assert success_count == 1, f"정확히 1명만 성공해야 하는데, {success_count}명이 성공했습니다."


def test_concurrent_different_courses(test_db: Session, test_session_factory):
    """
    다른 강좌는 동시성 영향 없음
    
    강좌 A: 1명 신청 (정원 1)
    강좌 B: 1명 신청 (정원 1)
    → 둘 다 성공해야 함
    """
    # 학과, 교수
    dept = Department(name="테스트학과")
    test_db.add(dept)
    test_db.commit()
    
    prof = Professor(
        name="교수",
        email="prof@test.com",
        department_id=dept.id
    )
    test_db.add(prof)
    test_db.commit()
    
    # 두 강좌
    courseA = Course(
        name="강좌A",
        code="A001",
        credits=3,
        capacity=1,
        professor_id=prof.id,
        department_id=dept.id
    )
    
    courseB = Course(
        name="강좌B",
        code="B001",
        credits=3,
        capacity=1,
        professor_id=prof.id,
        department_id=dept.id
    )
    
    test_db.add_all([courseA, courseB])
    test_db.commit()
    
    # 시간표
    scheduleA = Schedule(
        course_id=courseA.id,
        day_of_week=DayOfWeek.MON,
        start_time=time(9, 0),
        end_time=time(10, 30)
    )
    
    scheduleB = Schedule(
        course_id=courseB.id,
        day_of_week=DayOfWeek.TUE,
        start_time=time(9, 0),
        end_time=time(10, 30)
    )
    
    test_db.add_all([scheduleA, scheduleB])
    test_db.commit()
    
    # 학생
    student1 = Student(
        name="학생1",
        student_id="DIFF001",
        email="s1@test.com",
        department_id=dept.id
    )
    
    student2 = Student(
        name="학생2",
        student_id="DIFF002",
        email="s2@test.com",
        department_id=dept.id
    )
    
    test_db.add_all([student1, student2])
    test_db.commit()
    
    # 동시 신청 (다른 강좌)
    success_a = False
    success_b = False
    student1_id = student1.id
    student2_id = student2.id
    courseA_id = courseA.id
    courseB_id = courseB.id
    
    def enroll_a():
        db = test_session_factory()
        try:
            EnrollmentService.enroll_course(db, student1_id, courseA_id)
            db.commit()
            return True
        except:
            db.rollback()
            return False
        finally:
            db.close()
    
    def enroll_b():
        db = test_session_factory()
        try:
            EnrollmentService.enroll_course(db, student2_id, courseB_id)
            db.commit()
            return True
        except:
            db.rollback()
            return False
        finally:
            db.close()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(enroll_a)
        future_b = executor.submit(enroll_b)
        
        success_a = future_a.result()
        success_b = future_b.result()
    
    # 둘 다 성공해야 함 (다른 강좌이므로)
    assert success_a and success_b, "다른 강좌 신청은 모두 성공해야 합니다."
    
    print("\n✅ 다른 강좌 동시 신청: 모두 성공")
