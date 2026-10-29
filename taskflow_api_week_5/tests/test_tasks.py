from fastapi.testclient import TestClient

from app.dependencies import get_task_service
from app.main import app
from app.services import TaskService


def create_test_client() -> TestClient:
    app.dependency_overrides[get_task_service] = lambda: TaskService()
    return TestClient(app)


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_create_task() -> None:
    client = create_test_client()
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Learn FastAPI",
            "description": "Build a REST API",
            "priority": "high",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Learn FastAPI"
    assert data["priority"] == "high"
    assert data["completed"] is False
    assert "created_at" in data


def test_list_tasks() -> None:
    client = create_test_client()
    client.post("/api/v1/tasks", json={"title": "First task"})

    response = client.get("/api/v1/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_invalid_task_title() -> None:
    client = create_test_client()
    response = client.post("/api/v1/tasks", json={"title": "Hi"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_task_not_found() -> None:
    client = create_test_client()
    response = client.get("/api/v1/tasks/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_NOT_FOUND"


def test_update_task() -> None:
    client = create_test_client()
    created = client.post(
        "/api/v1/tasks",
        json={"title": "Learn testing"},
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"completed": True},
    )

    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_delete_task() -> None:
    client = create_test_client()
    created = client.post(
        "/api/v1/tasks",
        json={"title": "Delete this task"},
    )
    task_id = created.json()["id"]

    response = client.delete(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/v1/tasks/{task_id}").status_code == 404


def test_empty_update_is_rejected() -> None:
    client = create_test_client()
    created = client.post(
        "/api/v1/tasks",
        json={"title": "Update task"},
    )
    task_id = created.json()["id"]

    response = client.patch(f"/api/v1/tasks/{task_id}", json={})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


def test_null_update_is_rejected() -> None:
    client = create_test_client()
    created = client.post(
        "/api/v1/tasks",
        json={"title": "Update task"},
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"completed": None},
    )

    assert response.status_code == 422


def test_extra_update_field_is_rejected() -> None:
    client = create_test_client()
    created = client.post(
        "/api/v1/tasks",
        json={"title": "Update task"},
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"unexpected": "value"},
    )

    assert response.status_code == 422


def test_health_check() -> None:
    client = create_test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
