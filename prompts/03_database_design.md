# Prompts - 03. 데이터베이스 설계

## 질문 1: 엔티티 모델링

### 프롬프트
```
수강신청 시스템의 핵심 엔티티를 설계해줘.

필수 엔티티:
- 학과, 교수, 강좌, 학생, 시간표, 수강신청

요구사항:
- 강좌는 정원/현재신청인원/학점/시간표 정보 필요
- 학생은 학과와 연결
- 수강신청은 학생-강좌 관계 및 상태(ENROLLED/CANCELLED) 관리

SQLAlchemy ORM 모델 구조로 제안해줘.
```

### Codex의 답변
다음과 같은 엔티티 구조가 적합합니다.

- Department: 학과
- Professor: 교수 (department_id FK)
- Course: 강좌 (professor_id, department_id FK)
- Schedule: 강좌 시간표 (course_id FK, 1:1)
- Student: 학생 (department_id FK)
- Enrollment: 수강신청 (student_id, course_id FK)

관계:
- Department 1:N Course/Professor/Student
- Course 1:1 Schedule
- Course 1:N Enrollment
- Student 1:N Enrollment

---

## 질문 2: 초기 데이터 생성

### 프롬프트
```
서버 시작 시 다음 수량을 동적으로 생성해야 한다.
- 학과 10개
- 교수 100명
- 강좌 500개
- 학생 10,000명

1분 이내에 생성 가능하도록 구현 전략을 제시해줘.
```

### Codex의 답변
데이터 생성은 서비스 레이어에서 수행하고, 학생은 배치 커밋으로 처리하세요.

전략:
- 학과: 하드코딩된 이름 리스트 사용
- 교수/학생: 랜덤 조합 이름 + 유니크 이메일
- 강좌: 학과당 일정 수량 생성 + 스케줄 랜덤 배정
- 학생: 1,000명 단위 배치 커밋

---

## 질문 3: 데이터 현실성

### 프롬프트
```
데이터가 현실적이어야 한다.
"User1" 같은 이름 대신 한국식 이름, 실제 학과/강좌명 패턴을 쓰고 싶다.
간단한 샘플 이름/학과/강좌 리스트를 추천해줘.
```

### Codex의 답변
다음과 같이 최소 토큰 리스트를 사용하고 조합하세요.

- 학과: 컴퓨터공학과, 전자공학과, 기계공학과, 경영학과...
- 강좌명: 자료구조, 알고리즘, 운영체제, 데이터베이스...
- 이름: 성/이름 토큰 리스트 조합 (김/이/박 + 민준/서연 등)

---

## 정리

데이터베이스 설계 단계에서 다음을 결정했습니다:

1. **엔티티**: Department, Professor, Course, Schedule, Student, Enrollment
2. **관계**: Department 중심 1:N, Course-Enrollment 1:N, Course-Schedule 1:1
3. **데이터 생성**: 서비스 레이어에서 동적 생성, 학생은 배치 커밋
4. **현실성 확보**: 한국식 이름/학과/강좌명 토큰 리스트 조합
