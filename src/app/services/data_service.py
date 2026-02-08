"""
services/data_service.py - 초기 데이터 생성

⏱️ 목표: 1분 이내에 데이터 생성
   - 10개 학과
   - 100명 교수
   - 500개 강좌
   - 10,000명 학생
"""
import logging
from datetime import time
import random
from sqlalchemy.orm import Session
from sqlalchemy import delete

from app.models import (
    Department, Professor, Course, Student, Schedule, DayOfWeek
)
from app.config import settings

logger = logging.getLogger(__name__)

# 한국식 샘플 데이터
DEPARTMENT_NAMES = [
    "컴퓨터공학과",
    "전자공학과",
    "기계공학과",
    "화학공학과",
    "물리학과",
    "수학과",
    "통계학과",
    "경영학과",
    "경제학과",
    "법학과",
]

KOREAN_FIRST_NAMES = [
    "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임",
    "한", "오", "서", "신", "권", "황", "안", "송", "홍", "유"
]

KOREAN_LAST_NAMES = [
    "민준", "서준", "예준", "시우", "준호", "준영", "상호", "준열", "대열", "주영",
    "민지", "하은", "서연", "지은", "혜원", "예은", "수빈", "지은", "가은", "승연"
]

COURSE_NAME_PREFIXES = [
    "자료구조", "알고리즘", "데이터베이스", "운영체제", "컴퓨터 네트워크",
    "웹 프로그래밍", "모바일 앱", "머신러닝", "딥러닝", "빅데이터",
    "소프트웨어 공학", "자연어 처리", "컴퓨터 비전", "그래픽스", "보안",
    "분산시스템", "클라우드 컴퓨팅", "임베디드 시스템", "고성능 컴퓨팅", "양자 컴퓨팅"
]


class DataService:
    """초기 데이터 생성 서비스"""
    
    @staticmethod
    def clear_all(db: Session):
        """모든 데이터 삭제"""
        logger.info("🗑️ 기존 데이터 삭제 중...")
        
        db.execute(delete(Schedule))
        db.execute(delete(Course))
        db.execute(delete(Student))
        db.execute(delete(Professor))
        db.execute(delete(Department))
        
        db.commit()
        logger.info("✅ 데이터 삭제 완료")
    
    @staticmethod
    def create_sample_data(db: Session):
        """초기 데이터 생성"""
        logger.info("📊 초기 데이터 생성 시작...")
        
        # 1️⃣ 학과 생성
        departments = DataService._create_departments(db)
        logger.info(f"✅ 학과 {len(departments)}개 생성 완료")
        
        # 2️⃣ 교수 생성
        professors = DataService._create_professors(db, departments)
        logger.info(f"✅ 교수 {len(professors)}명 생성 완료")
        
        # 3️⃣ 강좌 생성
        courses = DataService._create_courses(db, departments, professors)
        logger.info(f"✅ 강좌 {len(courses)}개 생성 완료")
        
        # 4️⃣ 학생 생성
        students = DataService._create_students(db, departments)
        logger.info(f"✅ 학생 {len(students)}명 생성 완료")
        
        logger.info("✅ 모든 초기 데이터 생성 완료!")
        
        return {
            "departments": len(departments),
            "professors": len(professors),
            "courses": len(courses),
            "students": len(students),
        }
    
    @staticmethod
    def _create_departments(db: Session) -> list:
        """학과 생성"""
        departments = []
        
        for name in DEPARTMENT_NAMES[:settings.init_departments]:
            dept = Department(name=name)
            departments.append(dept)
        
        db.add_all(departments)
        db.commit()
        
        return departments
    
    @staticmethod
    def _create_professors(db: Session, departments: list) -> list:
        """교수 생성"""
        professors = []
        
        for i in range(settings.init_professors):
            dept = random.choice(departments)
            
            first_name = random.choice(KOREAN_FIRST_NAMES)
            last_name = random.choice(KOREAN_LAST_NAMES)
            name = first_name + last_name
            
            prof = Professor(
                name=name,
                email=f"prof{i:03d}@university.edu",
                department_id=dept.id
            )
            professors.append(prof)
        
        db.add_all(professors)
        db.commit()
        
        return professors
    
    @staticmethod
    def _create_courses(db: Session, departments: list, professors: list) -> list:
        """강좌 생성"""
        courses = []
        course_idx = 0
        
        for dept in departments:
            # 학과당 50개 강좌
            for i in range(settings.init_courses // len(departments)):
                course_idx += 1
                
                prof = random.choice([p for p in professors if p.department_id == dept.id] or professors)
                
                course_name = random.choice(COURSE_NAME_PREFIXES)
                
                course = Course(
                    name=f"{course_name} {i % 3 + 1}",  # 강좌명 (예: 알고리즘 1, 2, 3)
                    code=f"{dept.name[:3]}{course_idx:04d}",  # 강좌 코드
                    credits=random.choice([1, 2, 3, 4]),  # 1-4학점
                    capacity=random.randint(20, 50),  # 정원 20-50명
                    professor_id=prof.id,
                    department_id=dept.id
                )
                courses.append(course)
        
        db.add_all(courses)
        db.commit()
        
        # 시간표 생성 (강좌마다)
        DataService._create_schedules(db, courses)
        
        return courses
    
    @staticmethod
    def _create_schedules(db: Session, courses: list):
        """시간표 생성"""
        schedules = []
        
        days = list(DayOfWeek)
        hours = list(range(8, 17))  # 08:00 - 17:00
        
        for course in courses:
            day = random.choice(days)
            hour = random.choice(hours)
            
            schedule = Schedule(
                course_id=course.id,
                day_of_week=day,
                start_time=time(hour=hour, minute=0),
                end_time=time(hour=hour + 1, minute=30)
            )
            schedules.append(schedule)
        
        db.add_all(schedules)
        db.commit()
    
    @staticmethod
    def _create_students(db: Session, departments: list) -> list:
        """학생 생성"""
        students = []
        
        for i in range(settings.init_students):
            dept = random.choice(departments)
            
            first_name = random.choice(KOREAN_FIRST_NAMES)
            last_name = random.choice(KOREAN_LAST_NAMES)
            name = first_name + last_name
            
            # 학번: 2024 + 4자리
            student_id = f"2024{i:06d}"
            
            student = Student(
                name=name,
                student_id=student_id,
                email=f"student{i:06d}@university.edu",
                department_id=dept.id
            )
            students.append(student)
        
        # 배치 저장 (10,000명을 한 번에 저장하면 느리므로 나누기)
        batch_size = 1000
        for batch_start in range(0, len(students), batch_size):
            batch_end = min(batch_start + batch_size, len(students))
            db.add_all(students[batch_start:batch_end])
            db.commit()
            logger.debug(f"  학생 {batch_end}/{len(students)} 생성 중...")
        
        return students