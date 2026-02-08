# Prompts - 04. 동시성 제어

## 질문 1: 정원 초과 방지 전략

### 프롬프트
```
정원 1명 남은 강좌에 100명이 동시에 신청하는 상황에서
정확히 1명만 성공하도록 보장해야 한다.

SQLite + SQLAlchemy 환경에서 가능한 동시성 제어 전략을 제안해줘.
```

### Codex의 답변
원자적 UPDATE와 애플리케이션 락을 조합하세요.

```python
update_stmt = (
    update(Course)
    .where(Course.id == course_id, Course.enrolled < Course.capacity)
    .values(enrolled=Course.enrolled + 1)
)
result = db.execute(update_stmt)
```

- rowcount가 1이면 성공, 0이면 정원 초과
- SQLite는 `SELECT ... FOR UPDATE`를 지원하지 않으므로 원자적 UPDATE가 안전
- 앱 레벨 락으로 동일 강좌/학생에 대한 동시 요청을 직렬화

---

## 질문 2: 테스트 시나리오 설계

### 프롬프트
```
동시성 테스트를 어떻게 구성하면 신뢰성이 높을까?
100명 동시 요청 시나리오를 포함해야 한다.
```

### Codex의 답변
ThreadPoolExecutor로 다중 스레드 요청을 만들고,
성공 1명/실패 99명을 검증하세요.

추가로,
- 다른 강좌 동시 신청은 모두 성공해야 함
- 테스트 DB는 동일 DB 파일/세션 팩토리를 사용해야 함

---

## 정리

동시성 제어 단계에서 다음을 결정했습니다:

1. **정원 갱신**: `UPDATE ... WHERE enrolled < capacity` 원자적 처리
2. **락 전략**: `course:{id}`, `student:{id}`, `session:{id}` 키로 앱 락 직렬화
3. **SQLite 설정**: WAL + busy_timeout
4. **테스트**: 50/100명 동시 신청 테스트 + 다른 강좌 동시 신청 테스트
