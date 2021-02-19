from functools import wraps
from typing import Callable

from fastapi import APIRouter
from fastapi.types import DecoratedCallable


# Custom wrapper
def dec(router: APIRouter, **kwargs) -> Callable[[DecoratedCallable], DecoratedCallable]:
    def decorator(func) -> Callable:
        @router.post(path=f"/{func.__name__}", name=f"{router.prefix}_{func.__name__}", **kwargs)
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator
