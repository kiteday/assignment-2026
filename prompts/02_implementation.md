# Prompts - 02. 구현 단계

## 질문 1: SQLAlchemy 모델 설계

### 프롬프트
```
SQLAlchemy로 다음 엔티티들을 모델링해줘:

1. Department (학과)
   - id, name, 생성일시

2. Professor (교수)
   - id, name, email, department_id

3. Course (강좌)
   - id, name, code, credits, capacity, enrolled, professor_id, department_id

4. Schedule (강의 시간표)
   - course_id, day_of_week, start_time, end_time

5. Student (학생)
   - id, name, student_id (학번), email, department_id

6. Enrollment (수강신청)
   - id, student_id, course_id, status, enrolled_at, cancelled_at

관계(relationships)도 포함해줘.
```

### Codex의 답변
제공된 `models/__init__.py` 코드를 사용하면 됩니다.

핵심:
- `relationship()` 설정으로 양방향 네비게이션 가능
- `cascade="all, delete-orphan"`으로 고아 데이터 방지
- `Enum` 타입으로 요일 표현

---

## 질문 2: Pydantic 스키마

### 프롬프트
```
FastAPI 요청/응답을 위한 Pydantic 스키마를 설계해줘.

API:
1. POST /api/v1/students/{id}/enrollments
   요청: {"course_id": 123}
   응답: {id, student_id, course_id, status, enrolled_at, ...}

2. GET /api/v1/courses?department_id=1&limit=100
   응답: [{id, name, credits, capacity, enrolled, schedule}, ...]

3. GET /api/v1/students/{id}/schedule
   응답: {student_id, student_name, total_credits, courses: [...]} 

스키마를 정의해줘.
```

### Codex의 답변
제공된 `schemas/__init__.py`를 참고하세요.

중요 포인트:
- `from_attributes = True`: ORM 객체 → Pydantic
- `response_model`로 스키마 지정
- 중첩 모델 사용 (CourseResponse in EnrollmentResponse)

---

## 질문 3: 수강신청 서비스 구현

### 프롬프트
```
수강신청 로직을 구현해줘.

체크리스트:
1. 학생 존재 확인
2. 강좌 존재 확인
3. 정원 체크 (with_for_update)
4. 중복 신청 확인
5. 학점 체크 (현재 학점 + 신청 학점 > 18)
6. 시간 충돌 확인
7. Enrollment 생성
8. course.enrolled 증가

모든 체크를 순서대로 해줘.
```

### Codex의 답변
제공된 `services/enrollment_service.py`를 참고하세요.

핵심:
```python
@staticmethod
def enroll_course(db, student_id, course_id):
    # 1. 학생 조회 (락)
    student = db.query(Student).with_for_update().first()
    
    # 2. 강좌 조회 (락) ← 가장 중요!
    course = db.query(Course).with_for_update().first()
    
    # 3-6. 각종 체크
    if course.enrolled >= course.capacity:
        raise CapacityExceededException()
    
    # 7-8. 생성 & 증가
    enrollment = Enrollment(...)
    course.enrolled += 1
    db.add(enrollment)
    db.commit()  # ← 락 해제
```

---

## 질문 4: 초기 데이터 생성

### 프롬프트
```
서버 시작 시 다음 데이터를 생성해줘 (1분 이내):

- 학과: 10개 (한국식 이름)
- 교수: 100명 (한국식 이름, 무작위 학과 배치)
- 강좌: 500개 (무작위 시간표, 1-4학점)
- 학생: 10,000명 (한국식 이름, 무작위 학과 배치)

FastAPI lifespan을 사용해서 startup 이벤트에서 생성해줘.
```

### Codex의 답변
제공된 `services/data_service.py`를 참고하세요.

핵심:
- 한국식 이름 리스트 (KOREAN_FIRST_NAMES, etc.)
- 배치 처리 (1000명씩)
- WAL 모드로 빠른 삽입

`main.py`의 `lifespan` 함수에서:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    db = SessionLocal()
    DataService.create_sample_data(db)
    yield
    # shutdown
```

---

## 질문 5: API 라우터

### 프롬프트
```
FastAPI 라우터를 만들어줘.

엔드포인트:
1. GET /api/v1/students
2. GET /api/v1/students/{id}
3. GET /api/v1/courses
4. GET /api/v1/courses/{id}
5. GET /api/v1/professors
6. POST /api/v1/students/{id}/enrollments (핵심!)
7. DELETE /api/v1/students/{id}/enrollments/{enrollment_id}
8. GET /api/v1/students/{id}/schedule

라우터 파일 구조를 보여줘.
```

### Codex의 답변
제공된 `routes/` 디렉토리를 참고하세요.

파일 구조:
- `routes/health.py` - GET /health
- `routes/students.py` - 학생 관련
- `routes/courses.py` - 강좌 관련
- `routes/professors.py` - 교수 관련
- `routes/enrollments.py` - 수강신청 (핵심)

각 라우터를 `main.py`에서:
```python
app.include_router(students.router)
app.include_router(courses.router)
...
```

---

## 질문 6: FastAPI 메인 앱

### 프롬프트
```
main.py를 만들어줘.

포함할 것:
1. lifespan 이벤트 (초기 데이터 생성)
2. CORS 미들웨어
3. 예외 처리
4. 요청/응답 로깅
5. 라우터 등록
```

### Codex의 답변
제공된 `main.py`를 참고하세요.

순서:
1. lifespan 정의 (dataservice 실행)
2. FastAPI 앱 생성
3. 미들웨어 추가
4. 예외 핸들러
5. 라우터 포함
6. 루트 경로 정의

---

## 정리

구현 단계에서:
1. ORM 모델 설계 (6개 엔티티)
2. Pydantic 스키마 (요청/응답)
3. 비즈니스 로직 (동시성 제어 포함)
4. 초기 데이터 생성 (10,000명)
5. API 라우터 (8개 엔드포인트)
6. FastAPI 앱 통합

다음: 테스트 & 문서화
