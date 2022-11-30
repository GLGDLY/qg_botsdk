from asyncio import sleep
from typing import Any, Awaitable, Callable


class Queue:
    def __init__(self, max_concurrency: int):
        self._running_queue = []
        self._MAX_RUNNING_SLOTS = max_concurrency

    async def create_task(
        self, task: Callable[[Any, Any], Awaitable[Any]], *args, **kwargs
    ):
        if self._MAX_RUNNING_SLOTS > 0:
            while not len(self._running_queue) < self._MAX_RUNNING_SLOTS:
                await sleep(1)
        self._running_queue.append(0)
        result = await task(*args, **kwargs)
        self._running_queue.pop()
        return result
