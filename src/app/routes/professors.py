"""
routes/professors.py - 교수 관련 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Professor
from app.schemas import ProfessorResponse

router = APIRouter(prefix="/api/v1/professors", tags=["professors"])


@router.get("", response_model=list[ProfessorResponse])
def list_professors(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """교수 목록 조회"""
    professors = db.query(Professor).offset(skip).limit(limit).all()
    return professors