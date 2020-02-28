from parse import parse
import inspect
import typing

from .exceptions import HttpException
from .requests import Request
from .responses import PlainTextResponse
from .types import Scope, Receive, Send


class Kelpie:
    def __init__(self):
        self.routes = {}

    def add_route(self, path: str, handler: callable):
        assert path not in self.routes, "Route already exists"
        self.routes[path] = handler

    def route(self, path: str) -> callable:
        def wrapper(handler):
            self.add_route(path, handler)
            return handler

        return wrapper

    async def handle_request(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive, send)
        handler, kwargs = self.find_handler(request_path=request.path)

        if handler is not None:
            try:
                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise HttpException(
                            status_code=400,
                            details=f"{request.method} method is not allowed for {request.path}"
                        )
                response = await handler(request, **kwargs)
            except HttpException as e:
                response = e.response
        else:
            # default response when path not found
            response = self.default_response()

        await response(request.send)

    def find_handler(self, request_path) -> (callable, typing.Any):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named
        return None, None

    def default_response(self) -> PlainTextResponse:
        return PlainTextResponse(
            content='Not found',
            status_code=404
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        assert scope['type'] == 'http'
        await self.handle_request(scope, receive, send)
