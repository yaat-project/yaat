import typing

from yaat.requests import Request
from yaat.responses import Response
from yaat.typing import ASGIApp, Scope, Send, Receive
from yaat.websockets import WebSocket


class BaseMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    def add(self, middleware_cls: typing.Type, *args, **kwargs):
        self.app = middleware_cls(self.app, *args, **kwargs)

    async def process_request(self, request: Request):
        pass

    async def process_response(self, response: Response):
        pass

    async def handle_request(self, request: Request) -> Response:
        await self.process_request(request)
        response = await self.app.handle_request(request)
        await self.process_response(response)
        return response

    async def handle_websocket(self, websocket: WebSocket):
        await self.app.handle_websocket(websocket)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Handle Websocket
        if scope["type"] == "websocket":
            websocket = WebSocket(scope=scope, receive=receive, send=send)
            await self.handle_websocket(websocket)
        # Handle Request
        else:
            request = Request(scope, receive)
            response = await self.handle_request(request)
            await response(scope, receive, send)
