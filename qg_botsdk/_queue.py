from asyncio import Semaphore
from typing import Any, Awaitable, Callable


class Queue:
    def __init__(self, max_concurrency: int):
        self._semaphore = Semaphore(max_concurrency) if max_concurrency > 0 else None

    async def create_task(
        self, task: Callable[[Any, Any], Awaitable[Any]], *args, **kwargs
    ):
        if self._semaphore:
            async with self._semaphore:
                return await task(*args, **kwargs)
        else:
            return await task(*args, **kwargs)
