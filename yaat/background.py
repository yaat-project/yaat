import asyncio
import typing

from .concurrency import run_in_threadpool


class BackgroundTask:
    def __init__(self, function: typing.Callable, *args: typing.Any, **kwargs: typing.Any):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    async def __call__(self):
        if asyncio.iscoroutinefunction(self.function):
            await self.function(*self.args, **self.kwargs)
        else:
            await run_in_threadpool(self.function, *self.args, **self.kwargs)


class BackgroundTasks:
    def __init__(self):
        self.tasks = []

    def add(self, function: typing.Callable, *args: typing.Any, **kwargs: typing.Any):
        self.tasks.append(
            BackgroundTask(function, *args, **kwargs)
        )

    async def __call__(self):
        for task in self.tasks:
            await task()
