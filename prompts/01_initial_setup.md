# Prompts - 01. 초기 설정

## 질문 1: 프로젝트 구조 설계

### 프롬프트
```
Python으로 대학교 수강신청 시스템을 FastAPI + SQLAlchemy로 구현해야 한다.

요구사항:
1. 핵심: 동시성 제어 (정원 1명 남은 강좌에 100명이 동시 신청 → 1명만 성공)
2. API: 학생/강좌/교수 조회, 수강신청, 수강취소, 시간표 조회
3. 초기 데이터: 학과 10개, 교수 100명, 강좌 500개, 학생 10,000명 (1분 내)
4. 예외 처리: 정원 초과, 학점 초과, 시간 충돌 등

프로젝트 구조를 추천해줘.
```

### Claude의 답변
FastAPI + SQLAlchemy 조합은 좋은 선택입니다.

권장 구조:
- `src/app/models/` - ORM 엔티티
- `src/app/routes/` - API 엔드포인트
- `src/app/services/` - 비즈니스 로직 (동시성 제어)
- `src/app/schemas/` - Pydantic 스키마
- `tests/` - 테스트

동시성 제어는 `services/enrollment_service.py`에서 처리합니다.

---

## 질문 2: 동시성 제어 구현

### 프롬프트
```
SQLAlchemy에서 정원 초과를 방지하려면 어떻게 해야 할까?

시나리오:
- 강좌 정원: 1명
- 동시 신청: 100명
- 기대: 1명 성공, 99명 실패

구현 방식을 제시해줘.
```

### Claude의 답변
비관적 락 (Pessimistic Lock)을 사용하세요.

```python
course = db.query(Course).with_for_update().filter(
    Course.id == course_id
).first()

if course.enrolled >= course.capacity:
    raise CapacityExceededException()

course.enrolled += 1
db.commit()  # 락 해제
```

추가로 SQLite WAL 모드를 활성화하세요:
```python
cursor.execute("PRAGMA journal_mode=WAL")
cursor.execute("PRAGMA busy_timeout=5000")
```

이렇게 하면 정원 초과가 100% 방지됩니다.

---

## 질문 3: 초기 데이터 생성 최적화

### 프롬프트
```
10,000명의 학생을 SQLAlchemy로 생성하려면 1분 이내에 완료해야 한다.

리스트를 반복문으로 돌면서 add()/commit()을 매번 호출하는 방식은 너무 느리다.

최적화 방법을 제시해줘.
```

### Claude의 답변
배치 처리를 사용하세요:

```python
students = []
for i in range(10000):
    students.append(Student(...))

# 배치로 저장 (1000명씩)
batch_size = 1000
for batch_start in range(0, len(students), batch_size):
    batch_end = min(batch_start + batch_size, len(students))
    db.add_all(students[batch_start:batch_end])
    db.commit()
```

추가 팁:
- 동적 검증 비활성화
- 인덱스 생성은 데이터 생성 후에
- `bulk_insert_mappings()` 고려

이렇게 하면 10,000명을 30초 내에 생성할 수 있습니다.

---

## 질문 4: 시간 충돌 검사

### 프롬프트
```
학생이 이미 신청한 강좌들과 시간이 겹치는지 확인하는 로직을 구현해야 한다.

강좌 A: 월요일 09:00-10:30
강좌 B: 월요일 10:00-11:30 (A와 충돌!)
강좌 C: 화요일 09:00-10:30 (충돌 없음)

시간 표현과 충돌 판정 로직을 제시해줘.
```

### Claude의 답변
데이터 모델:

```python
class DayOfWeek(Enum):
    MON, TUE, WED, THU, FRI = "MON", "TUE", "WED", "THU", "FRI"

class Schedule(Base):
    day_of_week = Column(Enum(DayOfWeek))
    start_time = Column(Time)  # 09:00
    end_time = Column(Time)    # 10:30
```

충돌 판정:

```python
def schedules_conflict(schedule1, schedule2):
    if schedule1.day_of_week != schedule2.day_of_week:
        return False
    
    # 시간 겹침: s1.start < s2.end AND s2.start < s1.end
    return (schedule1.start_time < schedule2.end_time and
            schedule2.start_time < schedule1.end_time)
```

---

## 질문 5: 예외 처리 설계

### 프롬프트
```
FastAPI에서 비즈니스 로직 예외들을 처리하려면?

예:
- CapacityExceededException → 400 Bad Request
- TimeConflictException → 409 Conflict
- StudentNotFoundException → 404 Not Found

응답 형식을 통일하고 싶다.
```

### Claude의 답변
커스텀 예외 기본 클래스를 만드세요:

```python
class BusinessException(HTTPException):
    def __init__(self, status_code, error_code, message):
        super().__init__(
            status_code=status_code,
            detail={
                "code": error_code,
                "message": message
            }
        )
```

그리고 `main.py`에서 처리:

```python
@app.exception_handler(BusinessException)
async def business_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )
```

---

## 정리

초기 설정 단계에서 다음을 결정했습니다:

1. **기술 스택**: Python + FastAPI + SQLAlchemy + SQLite
2. **동시성 제어**: 비관적 락 (`with_for_update()`)
3. **데이터 최적화**: 배치 처리 + WAL 모드
4. **시간표**: DayOfWeek enum + Time 타입
5. **예외 처리**: 커스텀 예외 + 통일된 응답 형식

다음 단계: 실제 구현 (models, routes, services)
