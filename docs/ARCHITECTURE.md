# ARCHITECTURE

## 구성
- FastAPI 기반 REST API
- SQLAlchemy ORM + SQLite
- 초기 데이터 생성은 앱 시작 시 실행

## 레이어
- `routes/`: HTTP API
- `services/`: 비즈니스 로직
- `models/`: ORM 엔티티
- `schemas/`: 요청/응답 스키마

## 동시성
- 정원 증감은 원자적 UPDATE로 처리
- 애플리케이션 락으로 동일 강좌/학생/세션 동시 접근을 직렬화
