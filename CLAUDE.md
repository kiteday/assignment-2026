# CLAUDE.md - AI 에이전트 지침

이 파일은 Claude와 같은 AI 에이전트가 이 프로젝트에 참여할 때 따라야 할 지침입니다.

## 🎯 목표

대학교 수강신청 시스템을 구현합니다. **가장 중요한 요구사항은 동시성 제어**입니다.

- 정원 1명 남은 강좌에 100명이 동시에 신청 → 정확히 1명만 성공
- 나머지 99명은 "정원 초과" 에러를 받음
- 절대로 정원을 초과해서는 안 됨

## 🏗️ 프로젝트 구조

```
src/app/
├── main.py                # FastAPI 앱 진입점
├── config.py              # 설정
├── database.py            # DB 설정 (핵심: SQLite WAL)
├── models/                # ORM 모델
├── schemas/               # Pydantic 스키마
├── routes/                # API 엔드포인트
├── services/
│   ├── enrollment_service.py  # ⭐ 수강신청 (동시성 제어)
│   └── data_service.py        # 초기 데이터 생성
└── utils/
    └── exceptions.py      # 비즈니스 예외
```

## 🔒 동시성 제어 전략

**원자적 업데이트 + 애플리케이션 락**을 사용합니다.

```python
# enrollment_service.py 에서
update_stmt = (
    update(Course)
    .where(Course.id == course_id, Course.enrolled < Course.capacity)
    .values(enrolled=Course.enrolled + 1)
)
result = db.execute(update_stmt)
```

**중요:**
- 정원 증가는 `UPDATE ... WHERE enrolled < capacity`로 원자적으로 처리
- 동일 강좌/학생/세션 동시 접근은 애플리케이션 락으로 직렬화
- SQLite WAL 모드 필수 (`database.py` 참조)
- `busy_timeout=5000` 설정으로 5초 대기

## 📋 할 일

### Phase 1: 기본 구조 ✅
- [x] 프로젝트 레이아웃
- [x] 데이터베이스 설정
- [x] ORM 모델
- [x] 헬스 체크 API

### Phase 2: 조회 API ✅
- [x] 학생 목록/상세 조회
- [x] 강좌 목록/상세 조회
- [x] 교수 목록 조회

### Phase 3: 핵심 기능 ✅
- [x] 수강신청 (동시성 제어)
- [x] 수강취소
- [x] 시간표 조회
- [x] 초기 데이터 생성 (10,000명 학생)

### Phase 4: 테스트 & 문서 ✅
- [x] 동시성 테스트
- [x] 기본 기능 테스트
- [x] README.md
- [x] REQUIREMENTS.md
- [x] API 문서

## 🚨 주의사항

### 동시성 제어 테스트
```bash
python -m pytest tests/test_concurrency.py -v
```

**이 테스트가 실패하면 안 됩니다!**
- 50명이 정원 1명인 강좌에 신청
- 정확히 1명만 성공
- 나머지 49명은 CapacityExceededException

### 초기 데이터 생성 시간
- 목표: 1분 이내
- 데이터 규모:
  - 학과: 10개
  - 교수: 100명
  - 강좌: 500개
  - 학생: 10,000명

### 에러 처리
모든 비즈니스 로직 에러는 `exceptions.py`의 커스텀 예외를 사용합니다.

```python
from app.utils.exceptions import (
    CapacityExceededException,
    CreditExceededException,
    TimeConflictException,
    ...
)
```

## 🔧 코딩 스타일

### Python
- Python 3.9+
- PEP 8 준수
- 타입 힌팅 사용

```python
def enroll_course(
    db: Session,
    student_id: int,
    course_id: int
) -> Enrollment:
    """설명"""
    ...
```

### 로깅
```python
import logging
logger = logging.getLogger(__name__)

logger.info("✅ 성공")
logger.warning("⚠️ 경고")
logger.error("❌ 오류")
```

### 주석
- 복잡한 로직에만 주석 추가
- 이모지 사용 가능 (가독성 향상)
- 중국어/일본어 문자 사용 금지 (인코딩 문제)

## 📝 커밋 메시지

```bash
git commit -m "feat: 수강신청 API 구현 (동시성 제어)"
git commit -m "test: 동시성 테스트 추가"
git commit -m "docs: API 문서 작성"
```

## 🐛 문제 해결

### "Address already in use"
```bash
# 다른 포트로 실행
python -m uvicorn src.app.main:app --port 8001
```

### 데이터베이스 락 (Deadlock)
```bash
# DB 초기화
rm course_enrollment.db*

# 다시 실행
python -m uvicorn src.app.main:app
```

### 가상 환경 오류
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🎓 학습 자료

- **SQLAlchemy 동시성 제어**
  - https://docs.sqlalchemy.org/en/20/orm/query.html#sqlalchemy.orm.Query.with_for_update

- **SQLite WAL**
  - https://www.sqlite.org/wal.html

- **FastAPI**
  - https://fastapi.tiangolo.com/

## 📞 연락처

질문이 있으면:
1. 코드 주석 읽기
2. REQUIREMENTS.md 확인
3. 테스트 코드 참고

## 체크리스트

완성 전에 다음을 확인하세요:

- [ ] `python -m uvicorn src.app.main:app` 실행 가능
- [ ] `curl http://localhost:8000/health` 응답 200
- [ ] `pytest tests/test_concurrency.py` 통과
- [ ] README.md에 빌드/실행 방법 명시
- [ ] git 커밋 의미 있게 분리
- [ ] prompts/ 디렉토리에 AI 프롬프트 저장
- [ ] docs/REQUIREMENTS.md 완성

---

**Happy Coding! 🚀**

> "Move fast and break things, but not the concurrency control."
