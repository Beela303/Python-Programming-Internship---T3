from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=100,
        description="The title of the task.",
    )
    description: str = Field(
        default="",
        max_length=500,
        description="A description of the task.",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="The priority of the task.",
    )


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    priority: TaskPriority | None = None
    completed: bool | None = None

    model_config = ConfigDict(extra="forbid")


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: TaskPriority
    completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict[str, object]] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
