from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Task:
    id: int
    title: str
    status: TaskStatus = TaskStatus.PENDING

    def complete(self) -> None:
        self.status = TaskStatus.COMPLETED

    def is_completed(self) -> bool:
        return self.status == TaskStatus.COMPLETED