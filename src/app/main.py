"""
main.py - FastAPI 메인 애플리케이션

실행: python -m uvicorn src.app.main:app --reload --port 8000
"""
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db, engine, Base, get_db
from app.services.data_service import DataService
from app.database import SessionLocal
from app.routes import health, students, courses, professors, enrollments
from app.utils.exceptions import BusinessException

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== 라이프사이클 이벤트 ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 라이프사이클 관리
    - startup: 서버 시작 시 초기 데이터 생성
    - shutdown: 서버 종료 시 정리
    """
    # ✅ STARTUP
    start_time = time.time()
    logger.info("🚀 서버 시작...")
    
    try:
        # 데이터베이스 테이블 생성
        init_db()
        
        # 초기 데이터 생성
        db = SessionLocal()
        try:
            # 기존 데이터 정리
            DataService.clear_all(db)
            
            # 샘플 데이터 생성
            stats = DataService.create_sample_data(db)
            
            elapsed = time.time() - start_time
            logger.info(f"✅ 초기화 완료 ({elapsed:.2f}초)")
            logger.info(f"   📊 데이터 통계: {stats}")
            
            if elapsed > 60:
                logger.warning(f"⚠️ 초기화 시간이 60초를 초과했습니다: {elapsed:.2f}초")
        finally:
            db.close()
        
        yield
        
    except Exception as e:
        logger.error(f"❌ 초기화 중 오류 발생: {e}")
        raise
    
    # ✅ SHUTDOWN
    logger.info("🛑 서버 종료 중...")


# ==================== FastAPI 앱 생성 ====================
app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)


# ==================== CORS 설정 ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (프로덕션에서는 제한)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 예외 처리 ====================
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """비즈니스 예외 처리"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 처리"""
    logger.error(f"❌ 예상치 못한 오류: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "서버 내부 오류가 발생했습니다.",
            "error": str(exc)
        }
    )


# ==================== 요청/응답 로깅 미들웨어 ====================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """HTTP 요청/응답 로깅"""
    start_time = time.time()
    
    # 요청 로깅
    logger.debug(f"→ {request.method} {request.url.path}")
    
    # 응답 처리
    response = await call_next(request)
    
    # 응답 로깅
    elapsed = time.time() - start_time
    logger.debug(f"← {request.method} {request.url.path} [{response.status_code}] ({elapsed:.3f}s)")
    
    return response


# ==================== 라우트 등록 ====================
app.include_router(health.router)
app.include_router(students.router)
app.include_router(courses.router)
app.include_router(professors.router)
app.include_router(enrollments.router)


# ==================== 루트 경로 ====================
@app.get("/")
async def root():
    """API 루트"""
    return {
        "message": "Course Enrollment System API",
        "version": settings.app_version,
        "docs_url": "/docs",
        "health_check": "/health"
    }


# ==================== 개발용 테스트 엔드포인트 ====================
@app.get("/api/v1/test/data-stats")
async def get_data_stats(db: Session = Depends(get_db)):
    """데이터 통계"""
    from sqlalchemy import func
    from app.models import Student, Course, Professor, Department, Enrollment
    
    try:
        stats = {
            "students": db.query(func.count(Student.id)).scalar(),
            "courses": db.query(func.count(Course.id)).scalar(),
            "professors": db.query(func.count(Professor.id)).scalar(),
            "departments": db.query(func.count(Department.id)).scalar(),
            "enrollments": db.query(func.count(Enrollment.id)).filter(Enrollment.status == "ENROLLED").scalar(),
        }
        return stats
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
