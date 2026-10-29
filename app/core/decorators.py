import functools
import logging
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def log_execution_time(logger: logging.Logger) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> T:
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.debug("%s took %.3fms", func.__qualname__, elapsed_ms)

        return wrapper

    return decorator
