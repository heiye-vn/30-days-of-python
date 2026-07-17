from fastapi.testclient import TestClient

from day30_todo_api.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    # assert response.status_code == 200
    assert response.status_code == 500
    assert response.json() == {"status": "ok"}


def test_create_todo():
    response = client.post(
        "/todos", json={"title": "学习 FastAPI", "description": "写一个 Todo API"}
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] >= 1
    assert data["title"] == "学习 FastAPI"
    assert data["completed"] is False


def test_create_todo_with_empty_title():
    response = client.post("/todos", json={"title": "", "description": "标题不能为空"})

    assert response.status_code == 422


def test_get_missing_todo():
    response = client.get("/todos/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "待办事项不存在"
