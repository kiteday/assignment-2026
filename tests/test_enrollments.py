"""
tests/test_enrollments.py - 수강신청 테스트
"""
import pytest
from fastapi import status


def test_enroll_course_success(client, sample_data):
    """수강신청 성공"""
    student = sample_data["students"][0]
    course = sample_data["courses"][0]
    
    response = client.post(
        f"/api/v1/students/{student.id}/enrollments",
        json={"course_id": course.id}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert data["student_id"] == student.id
    assert data["course_id"] == course.id
    assert data["status"] == "ENROLLED"


def test_enroll_course_capacity_exceeded(client, sample_data, test_db):
    """정원 초과"""
    course = sample_data["courses"][0]  # 정원 2명
    students = sample_data["students"]
    
    # 학생 1, 2 신청 (정원 도달)
    response1 = client.post(
        f"/api/v1/students/{students[0].id}/enrollments",
        json={"course_id": course.id}
    )
    assert response1.status_code == status.HTTP_201_CREATED
    
    response2 = client.post(
        f"/api/v1/students/{students[1].id}/enrollments",
        json={"course_id": course.id}
    )
    assert response2.status_code == status.HTTP_201_CREATED
    
    # 학생 3 신청 (정원 초과)
    response3 = client.post(
        f"/api/v1/students/{students[2].id}/enrollments",
        json={"course_id": course.id}
    )
    
    assert response3.status_code == status.HTTP_400_BAD_REQUEST
    data = response3.json()
    assert data["code"] == "CAPACITY_EXCEEDED"


def test_enroll_course_time_conflict(client, sample_data, test_db):
    """시간 충돌"""
    from app.models import Course, Schedule, DayOfWeek
    from datetime import time
    
    student = sample_data["students"][0]
    base_course = sample_data["courses"][0]
    
    # 동일 시간표의 새 강좌 생성
    conflict_course = Course(
        name="시간충돌강좌",
        code="CS999",
        credits=3,
        capacity=10,
        professor_id=base_course.professor_id,
        department_id=base_course.department_id
    )
    test_db.add(conflict_course)
    test_db.commit()
    
    conflict_schedule = Schedule(
        course_id=conflict_course.id,
        day_of_week=DayOfWeek.MON,
        start_time=time(9, 0),
        end_time=time(10, 30)
    )
    test_db.add(conflict_schedule)
    test_db.commit()
    
    # 기존 강좌 신청
    response1 = client.post(
        f"/api/v1/students/{student.id}/enrollments",
        json={"course_id": base_course.id}
    )
    assert response1.status_code == status.HTTP_201_CREATED
    
    # 시간 충돌 강좌 신청
    response2 = client.post(
        f"/api/v1/students/{student.id}/enrollments",
        json={"course_id": conflict_course.id}
    )
    assert response2.status_code == status.HTTP_409_CONFLICT
    data = response2.json()
    assert data["code"] == "TIME_CONFLICT"


def test_enroll_course_duplicate(client, sample_data):
    """중복 신청"""
    student = sample_data["students"][0]
    course = sample_data["courses"][0]
    
    # 첫 번째 신청
    response1 = client.post(
        f"/api/v1/students/{student.id}/enrollments",
        json={"course_id": course.id}
    )
    assert response1.status_code == status.HTTP_201_CREATED
    
    # 두 번째 신청 (중복)
    response2 = client.post(
        f"/api/v1/students/{student.id}/enrollments",
        json={"course_id": course.id}
    )
    assert response2.status_code == status.HTTP_409_CONFLICT
    data = response2.json()
    assert data["code"] == "ALREADY_ENROLLED"


def test_cancel_enrollment(client, sample_data):
    """수강취소"""
    student = sample_data["students"][0]
    course = sample_data["courses"][0]
    
    # 신청
    enroll_response = client.post(
        f"/api/v1/students/{student.id}/enrollments",
        json={"course_id": course.id}
    )
    enrollment_id = enroll_response.json()["id"]
    
    # 취소
    cancel_response = client.delete(
        f"/api/v1/students/{student.id}/enrollments/{enrollment_id}"
    )
    
    assert cancel_response.status_code == status.HTTP_200_OK
    data = cancel_response.json()
    assert data["status"] == "CANCELLED"


def test_get_student_schedule(client, sample_data):
    """학생 시간표 조회"""
    student = sample_data["students"][0]
    courses = sample_data["courses"]
    
    # 두 강좌 신청
    client.post(
        f"/api/v1/students/{student.id}/enrollments",
        json={"course_id": courses[0].id}
    )
    client.post(
        f"/api/v1/students/{student.id}/enrollments",
        json={"course_id": courses[1].id}
    )
    
    # 시간표 조회
    response = client.get(f"/api/v1/students/{student.id}/schedule")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["student_id"] == student.id
    assert len(data["courses"]) == 2
    assert data["total_credits"] == 6  # 3 + 3


def test_get_courses_list(client, sample_data):
    """강좌 목록 조회"""
    response = client.get("/api/v1/courses")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert len(data) > 0
    assert "name" in data[0]
    assert "capacity" in data[0]
    assert "enrolled" in data[0]


def test_get_students_list(client, sample_data):
    """학생 목록 조회"""
    response = client.get("/api/v1/students")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert len(data) >= 3
