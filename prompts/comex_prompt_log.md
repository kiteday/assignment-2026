# Prompt Log (Prompt / Answer)

- Prompt:
  musinsa2폴더 안에 있는 폴더로 과제가 올바르게 되어 있는지 확인하고 수정할 부분을 수정해주세요.
- Answer:
  프로젝트 구조 점검 후 문서/코드 보완을 진행. README, REQUIREMENTS, API 문서 작성, 동시성 제어 보완, 테스트 수정 및 실행.

- Prompt:
  테스트 전에 왜 src/schemas 아래에 있는 py 파일을 사용하지 않나요? 필요하지 않은가요?
- Answer:
  스키마가 __init__.py에 집중되어 있어 개별 파일은 자리표시자 상태였음. 필요하면 파일 분리 가능.

- Prompt:
  분리해서 나누는게 유지보수에 더 좋을까요?
- Answer:
  규모 커질수록 분리 구조가 탐색/유지보수에 유리하므로 분리 권장.

- Prompt:
  네 스키마를 분리해주세요
- Answer:
  department/professor/course/student/enrollment 스키마를 파일별로 분리하고 __init__.py에서 재-export.

- Prompt:
  이제 코드를 테스트해보고 싶어요.
- Answer:
  pytest 설치 및 실행 경로 문제 해결. PYTHONPATH 설정 후 전체 테스트 통과.

- Prompt:
  네트워크를 허용합니다. 진행해주세요.
- Answer:
  venv2에 requirements 설치 진행 후 pytest 실행.

- Prompt:
  제가 테스트해서 확인해볼 수 있는 방법이 있을까요? GET /health 확인하고 싶어요.
- Answer:
  uvicorn 실행과 curl /health 테스트 방법 안내.

- Prompt:
  가상환경 활성화를 어떻게 하죠?
- Answer:
  venv/venv2 활성화 명령 안내.

- Prompt:
  Address already in use 오류가 납니다.
- Answer:
  다른 포트 사용 또는 점유 프로세스 종료 안내.

- Prompt:
  ModuleNotFoundError: No module named 'app'
- Answer:
  프로젝트 루트 실행 또는 PYTHONPATH=src로 실행 안내.

- Prompt:
  curl -i http://localhost:8000/health 응답이 없어요.
- Answer:
  별도 터미널에서 curl 실행 및 127.0.0.1 사용 안내.

- Prompt:
  200 OK가 잘 보입니다. 다른 테스트도 있나요?
- Answer:
  강좌/학생 목록, 수강신청, 시간표 조회 등 기본 테스트 순서 안내.

- Prompt:
  실행해보고 결과를 알려주세요.
- Answer:
  격리 환경에서 서버 접근 불가 안내, 사용자 로컬에서 curl 수행 요청.

- Prompt:
  수강신청/취소/중복 신청 로그 확인해 주세요.
- Answer:
  201 Created, CANCELLED, ALREADY_ENROLLED 등 정상 동작 확인.

- Prompt:
  모든 항목(정원/학점/시간충돌) 테스트하고 싶습니다.
- Answer:
  각 실패 케이스별 curl 테스트 시나리오 제공.

- Prompt:
  학점 초과 테스트가 오류가 납니다.
- Answer:
  쉘 heredoc 문제 해결 안내 및 Python one-liner로 대체.

- Prompt:
  시간 충돌 테스트 결과 확인해주세요.
- Answer:
  ALREADY_ENROLLED와 TIME_CONFLICT 발생 확인, 정상 동작 판정.

- Prompt:
  정원 초과가 ALREADY_ENROLLED로 나옵니다.
- Answer:
  동일 학생 중복 신청 때문임. 다른 학생으로 테스트하도록 안내.

- Prompt:
  정원 1 강좌를 만들어서 해봅시다
- Answer:
  capacity=1 강좌 생성 스크립트 실행 및 COURSE_ID 제공.

- Prompt:
  정원 초과 테스트 결과 확인해주세요.
- Answer:
  첫 학생 신청 성공, 두 번째 CAPACITY_EXCEEDED 확인 → 정상.

- Prompt:
  테스트 요약을 문서에 넣어주세요.
- Answer:
  README 수동 테스트 요약 추가 및 REQUIREMENTS 검증 항목 추가.

- Prompt:
  API 문서에 테스트 예시도 넣어주세요.
- Answer:
  docs/API.md에 curl 테스트 예시 섹션 추가.

- Prompt:
  필수 문서 기준으로 수정/생성해주세요.
- Answer:
  README 실행법 보완(PYTHONPATH), API 접속 정보 추가, 문서 상태 확인.

- Prompt:
  prompts 폴더를 더 자세히 기술해주세요.
- Answer:
  01~04 프롬프트 문서 상세화 및 Codex 답변 표기 통일.

- Prompt:
  대화 로그를 파일로 남기고 싶습니다.
- Answer:
  대화 원문 자동 export 불가 안내 후, 요약 로그 작성.

- Prompt:
  지금 제공한 대화 로그로 재정리해 주세요.
- Answer:
  prompts/2026-02-08.md를 재구성 로그 형태로 업데이트.
