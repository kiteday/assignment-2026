"""
models/course.py - 강좌 및 시간표 모델
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from app.database import Base


class DayOfWeek(PyEnum):
    """요일 열거형"""
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"


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