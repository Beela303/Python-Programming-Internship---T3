from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.dependencies import TaskServiceDependency
from app.schemas import (
    ErrorResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.services import TaskNotFoundError


app = FastAPI(
    title="TaskFlow API",
    description=(
        "A typed task management REST API demonstrating validation, "
        "dependency injection, and error handling."
    ),
    version="1.0.0",
)


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(
    request: Request,
    exc: TaskNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "code": "TASK_NOT_FOUND",
                "message": str(exc),
                "details": None,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request data is invalid.",
                "details": exc.errors(
                    include_input=False,
                    include_context=False,
                    include_url=False,
                ),
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
    }
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "error": {
                "code": error_codes.get(exc.status_code, "HTTP_ERROR"),
                "message": str(exc.detail),
                "details": None,
            }
        },
    )


@app.post(
    "/api/v1/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
    responses={422: {"model": ErrorResponse}},
)
def create_task(
    data: TaskCreate,
    service: TaskServiceDependency,
) -> TaskResponse:
    return service.create_task(data)


@app.get(
    "/api/v1/tasks",
    response_model=list[TaskResponse],
    tags=["Tasks"],
)
def list_tasks(
    service: TaskServiceDependency,
) -> list[TaskResponse]:
    return service.list_tasks()


@app.get(
    "/api/v1/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["Tasks"],
    responses={404: {"model": ErrorResponse}},
)
def get_task(
    task_id: int,
    service: TaskServiceDependency,
) -> TaskResponse:
    return service.get_task(task_id)


@app.patch(
    "/api/v1/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["Tasks"],
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def update_task(
    task_id: int,
    data: TaskUpdate,
    service: TaskServiceDependency,
) -> TaskResponse:
    updates = data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one field to update.",
        )

    if any(value is None for value in updates.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Updated fields cannot be null.",
        )

    return service.update_task(task_id, data)


@app.delete(
    "/api/v1/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"],
    responses={404: {"model": ErrorResponse}},
)
def delete_task(
    task_id: int,
    service: TaskServiceDependency,
) -> Response:
    service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Simple process health check."""
    return {"status": "ok"}
