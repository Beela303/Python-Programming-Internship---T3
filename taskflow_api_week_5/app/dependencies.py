from typing import Annotated

from fastapi import Depends

from app.services import TaskService


task_service = TaskService()


def get_task_service() -> TaskService:
    """Provide the shared service instance to API routes."""
    return task_service


TaskServiceDependency = Annotated[
    TaskService,
    Depends(get_task_service),
]
