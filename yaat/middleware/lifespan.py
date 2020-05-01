import asyncio
import traceback
import typing

from yaat.middleware.base import BaseMiddleware
from yaat.typing import ASGIApp, Scope, Send, Receive


class LifespanMiddleware(BaseMiddleware):
    """
    Middleware to handle ASGI startup and shutdown lifespan events.
    """

    def __init__(
        self,
        app: ASGIApp,
        on_startup: typing.Sequence[typing.Callable] = None,
        on_shutdown: typing.Sequence[typing.Callable] = None,
    ):
        super().__init__(app)
        self.on_startup = on_startup if on_startup else []
        self.on_shutdown = on_shutdown if on_shutdown else []

    async def startup(self):
        for method in self.on_startup:
            if asyncio.iscoroutinefunction(method):
                await method()
            else:
                method()

    async def shutdown(self):
        for method in self.on_shutdown:
            if asyncio.iscoroutinefunction(method):
                await method()
            else:
                method()

    async def lifespan(self, receive: Receive, send: Send):
        message = await receive()
        assert message["type"] == "lifespan.startup"

        try:
            await self.startup()
        except Exception:
            message = traceback.print_exc()
            await send({"type": "lifespan.startup.failed", "message": message})
            raise

        await send({"type": "lifespan.startup.complete"})

        message = await receive()
        assert message["type"] == "lifespan.shutdown"

        try:
            await self.shutdown()
        except Exception:
            traceback.print_exc()

        await self.shutdown()
        await send({"type": "lifespan.shutdown.complete"})

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        assert scope["type"] in ("http", "websocket", "lifespan")

        if scope["type"] == "lifespan":
            await self.lifespan(receive, send)
        else:
            await super().__call__(scope, receive, send)
