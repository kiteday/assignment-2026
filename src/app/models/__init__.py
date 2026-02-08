"""
models/ - 데이터 모델
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Time, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid

from app.database import Base


class DayOfWeek(PyEnum):
    """요일 열거형"""
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"


class Department(Base):
    """학과"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    courses = relationship("Course", back_populates="department")
    students = relationship("Student", back_populates="department")
    professors = relationship("Professor", back_populates="department")
    
    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}')>"


class Professor(Base):
    """교수"""
    __tablename__ = "professors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    department = relationship("Department", back_populates="professors")
    courses = relationship("Course", back_populates="professor")
    
    def __repr__(self):
        return f"<Professor(id={self.id}, name='{self.name}')>"


class Course(Base):
    """강좌"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False)
    credits = Column(Integer, nullable=False)  # 1-4
    capacity = Column(Integer, nullable=False)  # 정원
    enrolled = Column(Integer, default=0)  # 현재 신청 인원
    
    professor_id = Column(Integer, ForeignKey("professors.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    professor = relationship("Professor", back_populates="courses")
    department = relationship("Department", back_populates="courses")
    schedule = relationship("Schedule", back_populates="course", uselist=False, cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}', enrolled={self.enrolled}/{self.capacity})>"


class Schedule(Base):
    """강의 시간표"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, unique=True)
    
    day_of_week = Column(Enum(DayOfWeek), nullable=False)  # MON, TUE, ...
    start_time = Column(Time, nullable=False)  # 09:00
    end_time = Column(Time, nullable=False)  # 10:30
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    course = relationship("Course", back_populates="schedule")
    
    def __repr__(self):
        return f"<Schedule(course_id={self.course_id}, {self.day_of_week} {self.start_time}-{self.end_time})>"


class Student(Base):
    """학생"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    student_id = Column(String(50), unique=True, nullable=False)  # 학번 (예: 2024001)
    email = Column(String(100), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    department = relationship("Department", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}', student_id='{self.student_id}')>"


class Enrollment(Base):
    """수강신청"""
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # 상태
    status = Column(String(20), default="ENROLLED")  # ENROLLED, CANCELLED
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    
    # 복합 고유 제약 (같은 학생이 같은 강좌 중복 신청 불가)
    __table_args__ = (
        # 추후 unique constraint 추가
    )
    
    def __repr__(self):
        return f"<Enrollment(id={self.id}, student_id={self.student_id}, course_id={self.course_id}, status='{self.status}')>"