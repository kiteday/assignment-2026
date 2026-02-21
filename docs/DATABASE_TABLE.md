# 📊 데이터베이스 테이블 구조

## 📋 목차
1. [테이블 개요](#테이블-개요)
2. [각 테이블 상세](#각-테이블-상세)
3. [관계도](#관계도)
4. [인덱스 및 제약](#인덱스-및-제약)
5. [초기 데이터 규모](#초기-데이터-규모)

---

## 🏗️ 테이블 개요

| # | 테이블명 | 설명 | 행 수 | 목적 |
|---|---------|------|-------|------|
| 1 | **departments** | 학과 | 10개 | 조직 단위 |
| 2 | **professors** | 교수 | 100명 | 강의 담당자 |
| 3 | **courses** | 강좌 | 500개 | 수강신청 대상 |
| 4 | **schedules** | 시간표 | 500개 | 강의 시간 정보 |
| 5 | **students** | 학생 | 10,000명 | 수강신청 주체 |
| 6 | **enrollments** | 수강신청 | 0~5M건 | 신청/취소 기록 |

---

## 📌 각 테이블 상세

### 1️⃣ departments (학과)

**테이블명**: `departments`  
**목적**: 대학의 학과 관리  
**행 수**: 10개  
**PK**: `id`

| 컬럼명 | 타입 | 제약 | 설명 | 예시 |
|-------|------|------|------|------|
| **id** | INTEGER | PK, AUTO | 학과 ID | 1 |
| **name** | STRING(100) | UNIQUE, NOT NULL, INDEX | 학과명 | "컴퓨터공학과" |
| **created_at** | DATETIME | NOT NULL | 생성 시간 | 2026-02-08 10:00:00 |

**샘플 데이터**:
```
1, "컴퓨터공학과", 2026-02-08 10:00:00
2, "전자공학과", 2026-02-08 10:00:00
3, "기계공학과", 2026-02-08 10:00:00
4, "화학공학과", 2026-02-08 10:00:00
5, "물리학과", 2026-02-08 10:00:00
...
```

**관계**:
- 1:N with professors (한 학과 → 여러 교수)
- 1:N with courses (한 학과 → 여러 강좌)
- 1:N with students (한 학과 → 여러 학생)

---

### 2️⃣ professors (교수)

**테이블명**: `professors`  
**목적**: 강의 담당 교수 정보  
**행 수**: 100명  
**PK**: `id`  
**FK**: `department_id` → departments.id

| 컬럼명 | 타입 | 제약 | 설명 | 예시 |
|-------|------|------|------|------|
| **id** | INTEGER | PK, AUTO | 교수 ID | 1 |
| **name** | STRING(100) | NOT NULL, INDEX | 교수명 | "김교수" |
| **email** | STRING(100) | UNIQUE, NOT NULL | 이메일 | "kim@university.edu" |
| **department_id** | INTEGER | FK, NOT NULL | 소속 학과 ID | 1 |
| **created_at** | DATETIME | NOT NULL | 생성 시간 | 2026-02-08 10:00:00 |

**샘플 데이터**:
```
1, "김교수", "kim@university.edu", 1, 2026-02-08 10:00:00
2, "이교수", "lee@university.edu", 1, 2026-02-08 10:00:00
3, "박교수", "park@university.edu", 2, 2026-02-08 10:00:00
...
```

**관계**:
- N:1 with departments (여러 교수 → 한 학과)
- 1:N with courses (한 교수 → 여러 강좌)

---

### 3️⃣ courses (강좌)

**테이블명**: `courses`  
**목적**: 수강신청 대상 강좌  
**행 수**: 500개  
**PK**: `id`  
**FK**: `professor_id`, `department_id`  
**UNIQUE**: `code` (강좌 코드)

| 컬럼명 | 타입 | 제약 | 설명 | 예시 |
|-------|------|------|------|------|
| **id** | INTEGER | PK, AUTO, INDEX | 강좌 ID | 1 |
| **name** | STRING(100) | NOT NULL, INDEX | 강좌명 | "자료구조" |
| **code** | STRING(50) | UNIQUE, NOT NULL | 강좌 코드 | "CS201" |
| **credits** | INTEGER | NOT NULL | 학점 | 3 |
| **capacity** | INTEGER | NOT NULL | 정원 | 30 |
| **enrolled** | INTEGER | NOT NULL | 현재 신청 인원 | 25 |
| **professor_id** | INTEGER | FK, NOT NULL | 담당 교수 ID | 1 |
| **department_id** | INTEGER | FK, NOT NULL | 개설 학과 ID | 1 |
| **created_at** | DATETIME | NOT NULL | 생성 시간 | 2026-02-08 10:00:00 |

**샘플 데이터**:
```
1, "자료구조", "CS201", 3, 30, 0, 1, 1, 2026-02-08 10:00:00
2, "알고리즘", "CS202", 3, 30, 0, 1, 1, 2026-02-08 10:00:00
3, "데이터베이스", "CS301", 3, 25, 0, 2, 1, 2026-02-08 10:00:00
...
```

**제약사항**:
- 1 ≤ credits ≤ 4
- 20 ≤ capacity ≤ 50
- 0 ≤ enrolled ≤ capacity (**동시성 제어**로 보장)

**관계**:
- N:1 with professors
- N:1 with departments
- 1:1 with schedules
- 1:N with enrollments

**동시성 제어**:
```
UPDATE courses 
SET enrolled = enrolled + 1 
WHERE id = ? AND enrolled < capacity

rowcount == 1 → 성공
rowcount == 0 → 정원 초과
```

---

### 4️⃣ schedules (시간표)

**테이블명**: `schedules`  
**목적**: 강의 시간표  
**행 수**: 500개 (courses와 1:1)  
**PK**: `id`  
**FK**: `course_id` → courses.id (UNIQUE, NOT NULL)

| 컬럼명 | 타입 | 제약 | 설명 | 예시 |
|-------|------|------|------|------|
| **id** | INTEGER | PK, AUTO | 시간표 ID | 1 |
| **course_id** | INTEGER | FK, UNIQUE, NOT NULL | 강좌 ID | 1 |
| **day_of_week** | ENUM | NOT NULL | 요일 | "MON" |
| **start_time** | TIME | NOT NULL | 시작 시간 | 09:00 |
| **end_time** | TIME | NOT NULL | 종료 시간 | 10:30 |
| **created_at** | DATETIME | NOT NULL | 생성 시간 | 2026-02-08 10:00:00 |

**DayOfWeek Enum**:
```
MON = "MON"  (월요일)
TUE = "TUE"  (화요일)
WED = "WED"  (수요일)
THU = "THU"  (목요일)
FRI = "FRI"  (금요일)
```

**샘플 데이터**:
```
1, 1, "MON", "09:00", "10:30", 2026-02-08 10:00:00
2, 2, "WED", "10:30", "12:00", 2026-02-08 10:00:00
3, 3, "TUE", "13:00", "14:30", 2026-02-08 10:00:00
...
```

**제약사항**:
- 08:00 ≤ start_time ≤ 17:00
- 수업 길이: 90분 (start_time + 90분 = end_time)
- 각 강좌는 정확히 1개의 시간표만 보유

**관계**:
- 1:1 with courses (역관계)

**시간 충돌 판정**:
```python
def schedules_conflict(s1, s2):
    if s1.day_of_week != s2.day_of_week:
        return False  # 다른 요일 → 충돌 없음
    
    # 같은 요일이면 시간 겹침 확인
    return (
        s1.start_time < s2.end_time and
        s2.start_time < s1.end_time
    )

예시:
s1: MON 09:00-10:30
s2: MON 10:00-11:30
→ 09:00 < 11:30 ✅ AND 10:00 < 10:30 ✅ → 충돌!
```

---

### 5️⃣ students (학생)

**테이블명**: `students`  
**목적**: 수강신청 주체  
**행 수**: 10,000명  
**PK**: `id`  
**FK**: `department_id` → departments.id  
**UNIQUE**: `student_id` (학번), `email`

| 컬럼명 | 타입 | 제약 | 설명 | 예시 |
|-------|------|------|------|------|
| **id** | INTEGER | PK, AUTO | 학생 ID | 1 |
| **name** | STRING(100) | NOT NULL, INDEX | 이름 | "김민준" |
| **student_id** | STRING(50) | UNIQUE, NOT NULL | 학번 | "2024000001" |
| **email** | STRING(100) | UNIQUE, NOT NULL | 이메일 | "student1@university.edu" |
| **department_id** | INTEGER | FK, NOT NULL | 소속 학과 ID | 1 |
| **created_at** | DATETIME | NOT NULL | 생성 시간 | 2026-02-08 10:00:00 |

**샘플 데이터**:
```
1, "김민준", "2024000001", "student1@university.edu", 1, 2026-02-08 10:00:00
2, "이서준", "2024000002", "student2@university.edu", 2, 2026-02-08 10:00:00
3, "박예준", "2024000003", "student3@university.edu", 1, 2026-02-08 10:00:00
...
10000, "임준호", "2024009999", "student10000@university.edu", 5, 2026-02-08 10:00:00
```

**관계**:
- N:1 with departments
- 1:N with enrollments

---

### 6️⃣ enrollments (수강신청)

**테이블명**: `enrollments`  
**목적**: 학생 수강신청 기록  
**행 수**: 0~5M건 (동적)  
**PK**: `id`  
**FK**: `student_id`, `course_id`

| 컬럼명 | 타입 | 제약 | 설명 | 예시 |
|-------|------|------|------|------|
| **id** | INTEGER | PK, AUTO | 수강신청 ID | 1 |
| **student_id** | INTEGER | FK, NOT NULL | 학생 ID | 1 |
| **course_id** | INTEGER | FK, NOT NULL | 강좌 ID | 1 |
| **status** | STRING(20) | NOT NULL | 상태 | "ENROLLED" |
| **enrolled_at** | DATETIME | NOT NULL | 신청 시간 | 2026-02-08 10:30:00 |
| **cancelled_at** | DATETIME | NULL | 취소 시간 | NULL |
| **created_at** | DATETIME | NOT NULL | 생성 시간 | 2026-02-08 10:30:00 |

**Status 값**:
```
"ENROLLED"   → 신청 상태 (활성)
"CANCELLED"  → 취소 상태 (비활성)
```

**샘플 데이터**:
```
1, 1, 1, "ENROLLED", 2026-02-08 10:30:00, NULL, 2026-02-08 10:30:00
2, 1, 2, "ENROLLED", 2026-02-08 10:32:00, NULL, 2026-02-08 10:32:00
3, 2, 1, "ENROLLED", 2026-02-08 10:35:00, NULL, 2026-02-08 10:35:00
4, 1, 2, "CANCELLED", 2026-02-08 10:32:00, 2026-02-08 11:00:00, 2026-02-08 10:32:00
```

**제약사항**:
- ENROLLED 상태인 (student_id, course_id)는 유일 (중복 신청 방지)
- status ∈ {"ENROLLED", "CANCELLED"}
- enrolled_at ≤ cancelled_at (if cancelled_at is not NULL)

**관계**:
- N:1 with students
- N:1 with courses

**비즈니스 규칙**:
```
1. 중복 신청 방지
   SELECT * FROM enrollments
   WHERE student_id = ? AND course_id = ? AND status = "ENROLLED"
   
   결과가 있으면 ALREADY_ENROLLED 에러

2. 학점 제한 (최대 18학점)
   SELECT SUM(courses.credits)
   FROM enrollments
   JOIN courses ON courses.id = enrollments.course_id
   WHERE student_id = ? AND status = "ENROLLED"
   
   합계 + 신청 학점 > 18 → CREDIT_EXCEEDED 에러

3. 시간 충돌 방지
   학생의 모든 ENROLLED 강좌의 Schedule과
   신청할 강좌의 Schedule 비교
   
   겹치면 TIME_CONFLICT 에러

4. 정원 초과 방지
   UPDATE courses
   SET enrolled = enrolled + 1
   WHERE id = ? AND enrolled < capacity
   
   rowcount != 1 → CAPACITY_EXCEEDED 에러
```

---

## 📈 관계도

### ERD (Entity Relationship Diagram)

```
┌─────────────────────────────────────────────────────────────┐
│                     DEPARTMENTS                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ id (PK)                                                │ │
│  │ name (UNIQUE)                                          │ │
│  │ created_at                                             │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────┬──────────────────────────────┬─────────────┘
                 │ 1:N                    1:N   │
         ┌───────▼─────────┐          ┌────────▼──────────┐
         │   PROFESSORS    │          │     STUDENTS      │
         ├─────────────────┤          ├───────────────────┤
         │ id (PK)         │          │ id (PK)           │
         │ name            │          │ name              │
         │ email (UNIQUE)  │          │ student_id (UNIQ) │
         │ dept_id (FK) ───┼──────────┼─► department_id   │
         │ created_at      │          │ email (UNIQUE)    │
         └────────┬────────┘          │ created_at        │
                  │ 1:N               └─────────┬─────────┘
         ┌────────▼──────────┐                  │ 1:N
         │     COURSES       │         ┌────────▼───────────┐
         ├──────────────────┤         │   ENROLLMENTS      │
         │ id (PK)          │         ├────────────────────┤
         │ name             │         │ id (PK)            │
         │ code (UNIQUE)    │         │ student_id (FK) ───┼─→
         │ credits          │ 1:1     │ course_id (FK) ────┼─→
         │ capacity         │◄────────┤ status             │
         │ enrolled         │ │       │ enrolled_at        │
         │ prof_id (FK) ────┼─┼──────►│ cancelled_at       │
         │ dept_id (FK) ────┼─┼──┐    │ created_at         │
         │ created_at       │ │  │    └────────────────────┘
         └────────┬─────────┘ │  │
                  │ 1:1       │  │
         ┌────────▼─────────┐ │  │
         │    SCHEDULES     │ │  │
         ├──────────────────┤ │  │
         │ id (PK)          │ │  │
         │ course_id (FK)───┼─┘  │
         │ day_of_week      │    │
         │ start_time       │    │
         │ end_time         │    │
         │ created_at       │    │
         └──────────────────┘    │
                                 │
         ┌───────────────────────┘
         └──────────────────────────────────────►
```

### 관계 요약

| 관계 | 타입 | 설명 |
|------|------|------|
| departments ↔ professors | 1:N | 한 학과 → 여러 교수 |
| departments ↔ courses | 1:N | 한 학과 → 여러 강좌 |
| departments ↔ students | 1:N | 한 학과 → 여러 학생 |
| professors ↔ courses | 1:N | 한 교수 → 여러 강좌 |
| courses ↔ schedules | 1:1 | 한 강좌 ↔ 한 시간표 |
| courses ↔ enrollments | 1:N | 한 강좌 ← 여러 신청 |
| students ↔ enrollments | 1:N | 한 학생 → 여러 신청 |

---

## 🔑 인덱스 및 제약

### 인덱스 (Index)

```sql
-- departments
CREATE INDEX idx_departments_name ON departments(name);

-- professors
CREATE INDEX idx_professors_name ON professors(name);

-- courses
CREATE INDEX idx_courses_name ON courses(name);

-- students
CREATE INDEX idx_students_name ON students(name);

-- foreign keys (자동 인덱싱)
CREATE INDEX idx_professors_department_id ON professors(department_id);
CREATE INDEX idx_courses_professor_id ON courses(professor_id);
CREATE INDEX idx_courses_department_id ON courses(department_id);
CREATE INDEX idx_schedules_course_id ON schedules(course_id);
CREATE INDEX idx_students_department_id ON students(department_id);
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
```

### UNIQUE 제약

```sql
ALTER TABLE departments ADD UNIQUE (name);
ALTER TABLE professors ADD UNIQUE (email);
ALTER TABLE courses ADD UNIQUE (code);
ALTER TABLE students ADD UNIQUE (student_id);
ALTER TABLE students ADD UNIQUE (email);
ALTER TABLE schedules ADD UNIQUE (course_id);
```

### CHECK 제약 (비즈니스 규칙)

```sql
-- courses 테이블
ALTER TABLE courses ADD CHECK (credits >= 1 AND credits <= 4);
ALTER TABLE courses ADD CHECK (capacity >= 20 AND capacity <= 50);
ALTER TABLE courses ADD CHECK (enrolled >= 0 AND enrolled <= capacity);

-- enrollments 테이블
ALTER TABLE enrollments ADD CHECK (
    status IN ('ENROLLED', 'CANCELLED')
);
ALTER TABLE enrollments ADD CHECK (
    cancelled_at IS NULL OR cancelled_at >= enrolled_at
);
```

### 복합 제약

```sql
-- 중복 신청 방지
CREATE UNIQUE INDEX idx_enrollment_active 
ON enrollments(student_id, course_id) 
WHERE status = 'ENROLLED';

-- 설명:
-- 같은 학생이 같은 강좌를 ENROLLED 상태로 
-- 여러 번 신청할 수 없음
```

---

## 📊 초기 데이터 규모

### 생성 계획

```
┌─────────────────────────────────────────┐
│ 초기 데이터 생성 (1분 내)               │
├─────────────────────────────────────────┤
│ 1. Departments: 10개                    │
│    └─ 생성 시간: 0.1초                 │
│                                         │
│ 2. Professors: 100명                    │
│    └─ 각 학과별 무작위 배정             │
│    └─ 생성 시간: 1초                   │
│                                         │
│ 3. Courses: 500개                       │
│    ├─ 학점: 1-4 (무작위)                │
│    ├─ 정원: 20-50 (무작위)              │
│    ├─ enrolled: 0 (초기값)              │
│    └─ 생성 시간: 5초                   │
│                                         │
│ 4. Schedules: 500개                     │
│    ├─ 요일: MON-FRI (무작위)            │
│    ├─ 시간: 08:00-17:00 (무작위)        │
│    └─ 생성 시간: 2초                   │
│                                         │
│ 5. Students: 10,000명                   │
│    ├─ 이름: 한국식 무작위               │
│    ├─ 학번: 2024000001~2024009999       │
│    ├─ 배치 처리: 1,000명씩 커밋        │
│    └─ 생성 시간: 30초                  │
│                                         │
│ 6. Enrollments: 0건 (초기값)            │
│    └─ 런타임에 동적 생성                │
│                                         │
│ TOTAL: ~45초                            │
└─────────────────────────────────────────┘
```

### 데이터 분포

```
Departments (10개):
- 컴퓨터공학과
- 전자공학과
- 기계공학과
- 화학공학과
- 물리학과
- 수학과
- 통계학과
- 경영학과
- 경제학과
- 법학과

Professors (100명):
- 각 학과별 10명씩 무작위 배치

Courses (500개):
- 학점 분포: 
  | 1학점 | 2학점 | 3학점 | 4학점 |
  |-------|-------|-------|-------|
  | 25%   | 25%   | 25%   | 25%   |
  
- 정원 분포: 20-50명 (균등 분포)

Students (10,000명):
- 학번: 2024000001 ~ 2024009999
- 이름: 한국식 (김, 이, 박, ... + 민준, 서준, ...)
- 학과: 각 학과별 1,000명씩

Enrollments (0건 초기):
- 실행 시간에 동적 생성
- 최대 예상: 5M건 (학생 10K × 평균 신청 500강좌)
```

---

## 💾 데이터베이스 파일 구조

### SQLite WAL 모드

```
course_enrollment.db          (메인 DB 파일)
├─ 전체 테이블 정의
├─ 기본 데이터 (초기값)
└─ 커밋된 트랜잭션

course_enrollment.db-wal      (Write-Ahead Log)
├─ 미커밋 트랜잭션
├─ 쓰기 중인 변경사항
└─ 동시 읽기 지원

course_enrollment.db-shm      (Shared Memory)
└─ WAL 인덱스 메타데이터
```

### 파일 크기 추정

```
초기 상태:
- course_enrollment.db: ~2MB
- WAL 관련: 정상 운영 중 자동 정리

10,000명 수강신청 후:
- course_enrollment.db: ~50MB
- Enrollments 테이블: ~10MB
- 인덱스: ~5MB
```

---

## 🔄 테이블 간 데이터 흐름

### 수강신청 프로세스

```
┌────────────────────────────────────────────────────────┐
│ 학생이 수강신청 요청                                   │
│ POST /students/{id}/enrollments                        │
└──────────────────┬───────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │ 1. 학생 조회        │
        │ SELECT * FROM       │
        │ students            │
        │ WHERE id = ?        │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ 2. 강좌 조회        │
        │ SELECT * FROM       │
        │ courses             │
        │ WHERE id = ?        │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ 3. 중복 신청 확인   │
        │ SELECT * FROM       │
        │ enrollments         │
        │ WHERE student_id=?  │
        │ AND course_id=?     │
        │ AND status=ENROLLED │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ 4. 학점 확인        │
        │ SELECT SUM(credits) │
        │ FROM courses        │
        │ JOIN enrollments... │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ 5. 시간 충돌 확인   │
        │ SELECT * FROM       │
        │ schedules           │
        │ WHERE course_id IN  │
        │ (학생 신청 강좌들)  │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ 6. 정원 확인        │
        │ UPDATE courses      │
        │ SET enrolled+=1     │
        │ WHERE id=?          │
        │ AND enrolled<cap    │ ◄─── ⭐ 동시성 제어!
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ 7. 신청 기록 생성   │
        │ INSERT INTO         │
        │ enrollments(...)    │
        │ VALUES(...)         │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ 8. 트랜잭션 커밋    │
        │ COMMIT              │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ 응답 반환 (201)     │
        │ {신청 정보}         │
        └─────────────────────┘
```

---

## 📋 쿼리 예제

### 학생의 현재 신청 강좌 조회

```sql
SELECT 
    e.id,
    c.name,
    c.credits,
    s.day_of_week,
    s.start_time,
    s.end_time
FROM enrollments e
JOIN courses c ON e.course_id = c.id
JOIN schedules s ON c.id = s.course_id
WHERE e.student_id = 1
  AND e.status = 'ENROLLED'
ORDER BY s.day_of_week, s.start_time;
```

### 강좌별 신청 현황

```sql
SELECT 
    c.id,
    c.name,
    c.capacity,
    c.enrolled,
    COUNT(e.id) as actual_count,
    (c.capacity - c.enrolled) as available
FROM courses c
LEFT JOIN enrollments e ON c.id = e.course_id AND e.status = 'ENROLLED'
GROUP BY c.id, c.name, c.capacity, c.enrolled
ORDER BY c.id;
```

### 학생의 현재 신청 학점

```sql
SELECT 
    s.id,
    s.name,
    SUM(c.credits) as total_credits
FROM students s
LEFT JOIN enrollments e ON s.id = e.student_id AND e.status = 'ENROLLED'
LEFT JOIN courses c ON e.course_id = c.id
WHERE s.id = 1
GROUP BY s.id, s.name;
```

### 시간 충돌하는 강좌 찾기

```sql
SELECT 
    c1.id as course1_id,
    c1.name as course1_name,
    s1.day_of_week,
    s1.start_time,
    s1.end_time,
    c2.id as course2_id,
    c2.name as course2_name,
    s2.day_of_week,
    s2.start_time,
    s2.end_time
FROM courses c1
JOIN schedules s1 ON c1.id = s1.course_id
JOIN courses c2 ON c1.department_id = c2.department_id
JOIN schedules s2 ON c2.id = s2.course_id
WHERE c1.id < c2.id  -- 중복 제거
  AND s1.day_of_week = s2.day_of_week
  AND s1.start_time < s2.end_time
  AND s2.start_time < s1.end_time
ORDER BY c1.id, c2.id;
```

---

## 🎯 정리

**테이블 총 6개**:
| 테이블 | 행 수 | 주요 역할 |
|-------|------|---------|
| departments | 10 | 조직 단위 |
| professors | 100 | 강의 담당 |
| courses | 500 | **수강신청 대상** |
| schedules | 500 | 시간 정보 |
| students | 10,000 | 신청 주체 |
| enrollments | 동적 | **신청 기록** |

**핵심 관계**:
- students (1:N) enrollments (N:1) courses
- courses (1:1) schedules
- 모든 엔티티는 department 또는 professor와 연결

**동시성 제어 지점**:
- courses.enrolled (원자적 UPDATE로 보호)
- enrollments 중복 여부 (UNIQUE 제약)

**제약사항**:
- 학생당 최대 18학점
- 강좌당 정원 제한
- 시간 충돌 방지

---
**최초 작성일**: 2026-02-08
**작성일**: 2026-02-08
