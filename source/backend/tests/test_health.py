from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_ok():
    res = client.get('/health')
    assert res.status_code == 200
    data = res.json()
    assert data['status'] == 'ok'


def test_health_db_ok(monkeypatch):
    monkeypatch.setattr('app.main.check_db_connection', lambda: True)
    res = client.get('/health/db')
    assert res.status_code == 200
    assert res.json() == {'status': 'ok', 'database': True}


def test_health_db_fail(monkeypatch):
    monkeypatch.setattr('app.main.check_db_connection', lambda: False)
    res = client.get('/health/db')
    assert res.status_code == 200
    assert res.json() == {'status': 'error', 'database': False}
