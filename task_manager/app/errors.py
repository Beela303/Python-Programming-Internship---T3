class TaskError(Exception):
    """Base exception for task-related errors."""


class TaskNotFoundError(TaskError):
    """Raised when a task cannot be found."""


class InvalidTaskTitleError(TaskError):
    """Raised when a task title is invalid."""