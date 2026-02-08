# Course Enrollment System

대학교 수강신청 시스템 백엔드 (FastAPI + SQLAlchemy)

## 요구 사항 요약
- REST API 제공
- 정원 초과 방지 동시성 제어
- 학생당 최대 18학점
- 시간표 충돌 금지
- 초기 데이터 자동 생성 (학과 10+, 교수 100+, 강좌 500+, 학생 10,000+)

## 환경
- Python 3.9+

## 설치
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 실행
```bash
PYTHONPATH=src python -m uvicorn app.main:app --reload --port 8000
```

## 헬스 체크
```bash
curl http://localhost:8000/health
```

## API 접속 정보
- Base URL: `http://127.0.0.1:8000`
- 기본 포트: `8000`

## 테스트
```bash
pytest -v
```

## 수동 테스트 요약
- `/health` → 200 OK 확인
- 강좌 목록/학생 목록 조회 정상
- 수강신청 성공(201 Created)
- 시간표 조회 정상
- 수강취소 정상(상태 CANCELLED)
- 중복 신청 → `ALREADY_ENROLLED` (409)
- 시간 충돌 → `TIME_CONFLICT` (409)
- 학점 초과 → `CREDIT_EXCEEDED` (400)
- 정원 초과 → `CAPACITY_EXCEEDED` (400)

## 참고
- API 문서: `docs/API.md`
- 요구사항 및 설계 결정: `docs/REQUIREMENTS.md`
