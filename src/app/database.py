"""
database.py - SQLAlchemy 데이터베이스 설정
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# 엔진 생성
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    poolclass=StaticPool if "sqlite" in settings.database_url else None,
)

# 세션 팩토리
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base 임포트 (모든 모델이 이를 상속)
from sqlalchemy.orm import declarative_base
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """DB 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """데이터베이스 초기화 (테이블 생성)"""
    logger.info("🗂️ 데이터베이스 테이블 생성 중...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 테이블 생성 완료")


# SQLite 트랜잭션 격리 레벨 설정 (동시성 제어 필수)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """SQLite 동시성 설정"""
    if "sqlite" in settings.database_url:
        cursor = dbapi_conn.cursor()
        # SERIALIZABLE 격리 레벨
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        cursor.execute("PRAGMA busy_timeout=5000")  # 5초 대기
        cursor.close()