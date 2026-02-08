"""
tests/test_health.py - 헬스 체크 테스트
"""
def test_health_check(client):
    """헬스 체크 엔드포인트 테스트"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "database" in data