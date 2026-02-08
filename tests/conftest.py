"""
tests/conftest.py - pytest 공통 설정
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import Department, Professor, Course, Student, Schedule, DayOfWeek
from app.config import settings
from datetime import time

# 테스트용 파일 DB (동시성 테스트 안정성)
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///"


@pytest.fixture(scope="function")
def test_db(tmp_path):
    """테스트용 데이터베이스"""
    db_file = tmp_path / "test.db"
    engine = create_engine(
        f"{TEST_SQLALCHEMY_DATABASE_URL}{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_session_factory(test_db: Session):
    """테스트용 세션 팩토리 (동시성 테스트용)"""
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db.get_bind(),
    )


@pytest.fixture(scope="function")
def client(test_db: Session):
    """테스트 클라이언트"""
    
    def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_data(test_db: Session):
    """샘플 데이터"""
    # 학과
    dept = Department(name="컴퓨터공학과")
    test_db.add(dept)
    test_db.commit()
    
    # 교수
    prof = Professor(
        name="김교수",
        email="prof@example.com",
        department_id=dept.id
    )
    test_db.add(prof)
    test_db.commit()
    
    # 강좌
    course1 = Course(
        name="자료구조",
        code="CS101",
        credits=3,
        capacity=2,  # 정원 2명 (테스트용)
        professor_id=prof.id,
        department_id=dept.id
    )
    
    course2 = Course(
        name="알고리즘",
        code="CS102",
        credits=3,
        capacity=30,
        professor_id=prof.id,
        department_id=dept.id
    )
    
    test_db.add_all([course1, course2])
    test_db.commit()
    
    # 시간표
    schedule1 = Schedule(
        course_id=course1.id,
        day_of_week=DayOfWeek.MON,
        start_time=time(9, 0),
        end_time=time(10, 30)
    )
    
    schedule2 = Schedule(
        course_id=course2.id,
        day_of_week=DayOfWeek.TUE,
        start_time=time(9, 0),
        end_time=time(10, 30)
    )
    
    test_db.add_all([schedule1, schedule2])
    test_db.commit()
    
    # 학생
    student1 = Student(
        name="김학생",
        student_id="2024001",
        email="student1@example.com",
        department_id=dept.id
    )
    
    student2 = Student(
        name="이학생",
        student_id="2024002",
        email="student2@example.com",
        department_id=dept.id
    )
    
    student3 = Student(
        name="박학생",
        student_id="2024003",
        email="student3@example.com",
        department_id=dept.id
    )
    
    test_db.add_all([student1, student2, student3])
    test_db.commit()
    
    return {
        "department": dept,
        "professor": prof,
        "courses": [course1, course2],
        "students": [student1, student2, student3],
        "schedules": [schedule1, schedule2]
    }
