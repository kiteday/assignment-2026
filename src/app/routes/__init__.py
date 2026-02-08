"""
routes/ - API 엔드포인트 라우터

각 라우터는 별도 파일에 정의되어 있습니다:
- health.py: GET /health (헬스 체크)
- students.py: 학생 조회 API
- courses.py: 강좌 조회 API
- professors.py: 교수 조회 API
- enrollments.py: 수강신청 API (핵심)
"""

from app.routes import health, students, courses, professors, enrollments

__all__ = ["health", "students", "courses", "professors", "enrollments"]