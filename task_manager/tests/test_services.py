import pytest

from app.errors import InvalidTaskTitleError, TaskNotFoundError
from app.services import TaskService
from app.storage import TaskStorage


def create_service() -> TaskService:
    return TaskService(TaskStorage())


def test_create_task() -> None:
    service = create_service()

    task = service.create_task("Learn Python")

    assert task.id == 1
    assert task.title == "Learn Python"
    assert not task.is_completed()


def test_complete_task() -> None:
    service = create_service()

    task = service.create_task("Learn OOP")
    service.complete_task(task.id)

    assert task.is_completed()


def test_empty_title_raises_error() -> None:
    service = create_service()

    with pytest.raises(InvalidTaskTitleError):
        service.create_task("")


def test_missing_task_raises_error() -> None:
    service = create_service()

    with pytest.raises(TaskNotFoundError):
        service.complete_task(999)