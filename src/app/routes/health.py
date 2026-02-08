"""
routes/health.py - 헬스 체크 엔드포인트
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
import logging

router = APIRouter(prefix="", tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health", status_code=200)
def health_check(db: Session = Depends(get_db)):
    """
    헬스 체크 엔드포인트
    
    서버 정상 작동 여부 및 DB 연결 확인
    """
    try:
        # DB 연결 테스트
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "message": "Server is running",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e),
            "database": "disconnected"
        }
