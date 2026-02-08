"""
models/department.py - 학과 및 교수 모델
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


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