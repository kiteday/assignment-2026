# API 명세

Base URL: `http://localhost:8000`

## 공통 에러 응답
```json
{
  "code": "ERROR_CODE",
  "message": "에러 메시지",
  "conflicting_courses": []
}
```
- `conflicting_courses`는 TIME_CONFLICT일 때만 포함됩니다.

## Health
### GET /health
- 200 OK
```json
{
  "status": "healthy",
  "message": "Server is running",
  "database": "connected"
}
```

## 학생
### GET /api/v1/students
Query
- `skip` (int, default 0)
- `limit` (int, default 100)

Response 200
```json
[
  {
    "id": 1,
    "name": "김민준",
    "student_id": "2024000001",
    "email": "student000001@university.edu",
    "department_id": 1,
    "created_at": "2026-02-08T05:12:00.000Z"
  }
]
```

### GET /api/v1/students/{student_id}
Response 200
```json
{
  "id": 1,
  "name": "김민준",
  "student_id": "2024000001",
  "email": "student000001@university.edu",
  "department_id": 1,
  "created_at": "2026-02-08T05:12:00.000Z"
}
```
Errors
- 404 `STUDENT_NOT_FOUND`

## 테스트 예시 (curl)
### Health
```bash
curl -i http://127.0.0.1:8000/health
```

### 강좌/학생 목록
```bash
curl -s http://127.0.0.1:8000/api/v1/courses | head -c 800
curl -s http://127.0.0.1:8000/api/v1/students | head -c 800
```

### 수강신청/취소
```bash
STUDENT_ID=1
COURSE_ID=1

curl -s -X POST http://127.0.0.1:8000/api/v1/students/$STUDENT_ID/enrollments \
  -H "Content-Type: application/json" \
  -d "{\"course_id\": $COURSE_ID}"

curl -s -X DELETE http://127.0.0.1:8000/api/v1/students/$STUDENT_ID/enrollments/1
```

### 시간표 조회
```bash
curl -s http://127.0.0.1:8000/api/v1/students/1/schedule
```

### 에러 케이스
```bash
# 중복 신청
curl -s -X POST http://127.0.0.1:8000/api/v1/students/1/enrollments \
  -H "Content-Type: application/json" \
  -d "{\"course_id\": 1}"

# 없는 학생
curl -s http://127.0.0.1:8000/api/v1/students/999999

# 없는 강좌
curl -s http://127.0.0.1:8000/api/v1/courses/999999
```

## 교수
### GET /api/v1/professors
Query
- `skip` (int, default 0)
- `limit` (int, default 100)

Response 200
```json
[
  {
    "id": 1,
    "name": "김교수",
    "email": "prof000@university.edu",
    "department_id": 1,
    "created_at": "2026-02-08T05:12:00.000Z"
  }
]
```

## 강좌
### GET /api/v1/courses
Query
- `department_id` (int, optional)
- `skip` (int, default 0)
- `limit` (int, default 100)

Response 200
```json
[
  {
    "id": 1,
    "name": "자료구조 1",
    "code": "컴퓨터공0001",
    "credits": 3,
    "capacity": 30,
    "enrolled": 25,
    "professor_id": 1,
    "department_id": 1,
    "schedule": "MON 09:00-10:30"
  }
]
```

### GET /api/v1/courses/{course_id}
Response 200
```json
{
  "id": 1,
  "name": "자료구조 1",
  "code": "컴퓨터공0001",
  "credits": 3,
  "capacity": 30,
  "enrolled": 25,
  "professor_id": 1,
  "department_id": 1,
  "created_at": "2026-02-08T05:12:00.000Z",
  "schedule": {
    "id": 1,
    "day_of_week": "MON",
    "start_time": "09:00:00",
    "end_time": "10:30:00"
  }
}
```
Errors
- 404 `COURSE_NOT_FOUND`

## 수강신청
### POST /api/v1/students/{student_id}/enrollments
Request
```json
{
  "course_id": 123
}
```

Response 201
```json
{
  "id": 10,
  "student_id": 1,
  "course_id": 123,
  "status": "ENROLLED",
  "enrolled_at": "2026-02-08T05:12:00.000Z",
  "cancelled_at": null,
  "created_at": "2026-02-08T05:12:00.000Z"
}
```
Errors
- 400 `CAPACITY_EXCEEDED`
- 400 `CREDIT_EXCEEDED`
- 409 `TIME_CONFLICT`
- 409 `ALREADY_ENROLLED`
- 404 `STUDENT_NOT_FOUND`
- 404 `COURSE_NOT_FOUND`

### DELETE /api/v1/students/{student_id}/enrollments/{enrollment_id}
Response 200
```json
{
  "id": 10,
  "student_id": 1,
  "course_id": 123,
  "status": "CANCELLED",
  "enrolled_at": "2026-02-08T05:12:00.000Z",
  "cancelled_at": "2026-02-08T05:15:00.000Z",
  "created_at": "2026-02-08T05:12:00.000Z"
}
```
Errors
- 404 `ENROLLMENT_NOT_FOUND`

### GET /api/v1/students/{student_id}/enrollments
Query
- `status` (ENROLLED | CANCELLED, optional)

Response 200
```json
[
  {
    "id": 10,
    "student_id": 1,
    "course_id": 123,
    "status": "ENROLLED",
    "enrolled_at": "2026-02-08T05:12:00.000Z",
    "cancelled_at": null,
    "created_at": "2026-02-08T05:12:00.000Z"
  }
]
```

## 시간표
### GET /api/v1/students/{student_id}/schedule
Response 200
```json
{
  "student_id": 1,
  "student_name": "김민준",
  "total_credits": 6,
  "courses": [
    {
      "id": 1,
      "name": "자료구조 1",
      "code": "컴퓨터공0001",
      "credits": 3,
      "capacity": 30,
      "enrolled": 25,
      "professor_id": 1,
      "department_id": 1,
      "schedule": "MON 09:00-10:30"
    }
  ]
}
```
Errors
- 404 `STUDENT_NOT_FOUND`
