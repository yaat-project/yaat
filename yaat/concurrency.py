import asyncio
import functools
import typing

try:
    # new module from python 3.7+
    # https://docs.python.org/3/whatsnew/3.7.html#contextvars
    import contextvars
except ImportError:
    contextvars = None


T = typing.TypeVar("T")


async def run_in_threadpool(function: typing.Callable[..., T], *args: typing.Any, **kwargs: typing.Any) -> T:
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
    return await loop.run_in_executor(None, function, *args)
