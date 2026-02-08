"""
config.py - 애플리케이션 설정
"""
from pydantic_settings import BaseSettings
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # FastAPI
    app_title: str = "Course Enrollment System"
    app_version: str = "1.0.0"
    app_description: str = "대학교 수강신청 시스템"
    
    # 데이터베이스
    database_url: str = f"sqlite:///{BASE_DIR}/course_enrollment.db"
    database_echo: bool = False  # SQL 로깅 (디버깅 시 True로 변경)
    
    # 초기 데이터
    init_departments: int = 10
    init_courses: int = 500
    init_students: int = 10000
    init_professors: int = 100
    
    # 비즈니스 규칙
    max_credits_per_semester: int = 18
    
    # 로깅
    log_level: str = "INFO"
    log_file: str = f"{BASE_DIR}/logs/app.log"
    
    class Config:
        env_file = f"{BASE_DIR}/.env"
        case_sensitive = False


settings = Settings()