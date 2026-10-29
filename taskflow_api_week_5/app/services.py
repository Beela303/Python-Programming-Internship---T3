from datetime import datetime, timezone

from app.schemas import TaskCreate, TaskResponse, TaskUpdate


class TaskNotFoundError(Exception):
    """Raised when a requested task does not exist."""


class TaskService:
    """In-memory task service; data is lost when the process stops."""

    def __init__(self) -> None:
        self._tasks: dict[int, TaskResponse] = {}
        self._next_id = 1

    def create_task(self, data: TaskCreate) -> TaskResponse:
        task = TaskResponse(
            id=self._next_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            completed=False,
            created_at=datetime.now(timezone.utc),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def list_tasks(self) -> list[TaskResponse]:
        return list(self._tasks.values())

    def get_task(self, task_id: int) -> TaskResponse:
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(
                f"Task with ID {task_id} was not found."
            )
        return task

    def update_task(
        self,
        task_id: int,
        data: TaskUpdate,
    ) -> TaskResponse:
        existing_task = self.get_task(task_id)
        updates = data.model_dump(exclude_unset=True)
        updated_data = existing_task.model_dump()
        updated_data.update(updates)
        updated_task = TaskResponse(**updated_data)
        self._tasks[task_id] = updated_task
        return updated_task

    def delete_task(self, task_id: int) -> None:
        self.get_task(task_id)
        del self._tasks[task_id]
