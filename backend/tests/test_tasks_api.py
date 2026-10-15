"""任务 CRUD API 测试（不依赖真实 CDP / 浏览器）。"""

from fastapi.testclient import TestClient

from app.main import create_app


def test_create_and_get_task():
    app = create_app()
    client = TestClient(app)

    r = client.post(
        "/tasks",
        json={
            "name": "test-task",
            "description": "unit test",
            "flow": {"source": "temu", "target": "mabang"},
        },
    )
    assert r.status_code == 201
    task = r.json()
    assert task["name"] == "test-task"
    assert task["id"]

    r2 = client.get(f"/tasks/{task['id']}")
    assert r2.status_code == 200
    assert r2.json()["flow"]["source"] == "temu"


def test_list_tasks():
    app = create_app()
    client = TestClient(app)
    r = client.get("/tasks")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
