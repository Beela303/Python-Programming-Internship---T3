"""Reusable function decorators."""
import logging
from functools import wraps
from time import perf_counter
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


def measure_time(function: Callable[..., T]) -> Callable[..., T]:
    """Log how long a normal function call takes."""
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start = perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            logger.info(
                "%s completed in %.6f seconds",
                function.__name__,
                perf_counter() - start,
            )
    return wrapper


def log_call(function: Callable[..., T]) -> Callable[..., T]:
    """Log entry and exit, including when the function raises."""
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        logger.info("Starting %s", function.__name__)
        try:
            return function(*args, **kwargs)
        finally:
            logger.info("Finished %s", function.__name__)
    return wrapper


def count_calls(function: Callable[..., T]) -> Callable[..., T]:
    """Decorator with a call_count attribute for learning purposes."""
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        wrapper.call_count += 1  # type: ignore[attr-defined]
        return function(*args, **kwargs)
    wrapper.call_count = 0  # type: ignore[attr-defined]
    return wrapper
