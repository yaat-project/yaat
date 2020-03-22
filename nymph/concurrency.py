import asyncio
import functools
import typing

try:
    import contextvars # python 3.7
except ImportError:
    contextvars = None


T = typing.TypeVar("T")


async def run_in_threadpool(function: typing.Callable[..., T], *args: typing.Any, **kwargs: typing.Any) -> T:
    loop = asyncio.get_event_loop()

    if contextvars is not None:
        child = functools.partial(function, *args, **kwargs)
        context = contextvars.copy_context()
        function = context.run
        args = (child,)
    elif kwargs:
        function = functools.partial(function, **kwargs)

    return await loop.run_in_executor(None, function, *args)
