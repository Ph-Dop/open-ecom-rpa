from fastapi.testclient import TestClient

from app.main import create_app


def test_health():
    app = create_app()
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["app"] == "OpenEcom-RPA"
    assert body["db"] == "ok"
