import asyncio
import functools
import typing

try:
    # new module from python 3.7+
    # https://docs.python.org/3/whatsnew/3.7.html#contextvars
    import contextvars
except ImportError:
    contextvars = None


_T = typing.TypeVar("_T")


async def run_in_threadpool(
    function: typing.Callable[..., _T], *args: typing.Any, **kwargs: typing.Any
) -> _T:
    """
    run function in another thread inside event loops
    it will not block the whole treads in case when
    function can be some blocking code
    """
    loop = asyncio.get_event_loop()

    if contextvars is not None:
        child = functools.partial(function, *args, **kwargs)
        context = contextvars.copy_context()
        function = context.run
        args = (child,)
    elif kwargs:
        function = functools.partial(function, **kwargs)

    # https://cheat.readthedocs.io/en/latest/python/asyncio.html
    # None uses default ThreadPoolExecutor
    # (might want to give option to support executator `ProcessPoolExecutor`
    #  for CPU intensive tasks)
    return await loop.run_in_executor(None, function, *args)


class _StopGenerator(Exception):
    pass


def _next(iterator: typing.Iterator) -> typing.Any:
    # You can raise anything other than StopIteration inside futures
    # https://www.osgeo.cn/tornado/_modules/asyncio/futures.html
    try:
        return next(iterator)
    except StopIteration:
        raise _StopGenerator


async def generate_in_threadpool(
    iterator: typing.Iterator,
) -> typing.AsyncGenerator:
    while True:
        try:
            yield await run_in_threadpool(_next, iterator)
        except _StopGenerator:
            break


async def run_until_first_complete(
    tasks: typing.Tuple[typing.Callable],
) -> None:
    # create tasks
    # https://docs.python.org/3/library/asyncio-task.html#asyncio-example-wait-coroutine
    try:
        tasks = tuple(asyncio.create_task(task) for task in tasks)
    except AttributeError:
        # create_task is added in python3.7 and in python3.6 it is only available
        # as a method on event loop
        loop = asyncio.get_event_loop()
        tasks = tuple(loop.create_task(task) for task in tasks)

    # run until at least one of the task is complete
    # https://docs.python.org/3/library/asyncio-task.html#waiting-primitives
    done, pending = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_COMPLETED
    )

    # cancel pending tasks
    for task in pending:
        task.cancel()
