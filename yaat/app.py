import httpx
import inspect
import typing

from yaat.exceptions import HTTPException
from yaat.middleware import (
    BaseMiddleware,
    ExceptionMiddleware,
    LifespanMiddleware,
)
from yaat.parsers import UrlParamParser
from yaat.requests import Request
from yaat.responses import Response
from yaat.routing import Router, RouteTypes
from yaat.typing import Scope, Receive, Send
from yaat.websockets import WebSocket


class Yaat:
    def __init__(
        self,
        middlewares: typing.Sequence[BaseMiddleware] = None,
        on_startup: typing.Sequence[typing.Callable] = None,
        on_shutdown: typing.Sequence[typing.Callable] = None,
    ):
        self.router = Router()
        self.middleware = LifespanMiddleware(
            app=self, on_startup=on_startup, on_shutdown=on_shutdown
        )

        # NOTE: setup middleware(s) registration
        self.__setup_middlewares(middlewares)

    # NOTE: Routing
    def route(
        self,
        path: str,
        methods: typing.List[str] = None,
        has_schema: bool = False,
        tags: typing.List[str] = None,
    ) -> typing.Callable:
        def wrapper(handler):
            self.add_route(
                path=path,
                handler=handler,
                methods=methods,
                has_schema=has_schema,
                tags=tags,
            )
            return handler

        return wrapper

    def add_route(
        self,
        path: str,
        handler: typing.Callable,
        methods: typing.List[str] = None,
        has_schema: bool = False,
        tags: typing.List[str] = None,
    ):
        self.router.add_route(
            path=path,
            handler=handler,
            methods=methods,
            has_schema=has_schema,
            tags=tags,
        )

    def websocket_route(
        self, path: str, tags: typing.List[str] = None
    ) -> typing.Callable:
        def wrapper(handler):
            self.add_websocket_route(path, handler, tags)
            return handler

        return wrapper

    def add_websocket_route(
        self,
        path: str,
        handler: typing.Callable,
        tags: typing.List[str] = None,
    ):
        self.router.add_websocket_route(path=path, handler=handler, tags=tags)

    def mount(self, router: Router, prefix: str):
        self.router.mount(router=router, prefix=prefix)

    # NOTE: Handle HTTP Request
    async def handle_request(self, request: Request) -> Response:
        route, kwargs = self.router.get_route(request_path=request.path)

        try:
            # check if route exists and it is not websocket route
            if (
                route
                and route.handler is not None
                and route.type != RouteTypes.WEBSOCKET
            ):
                handler = route.handler

                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise HTTPException(405)
                if not route.is_valid_method(request.method):
                    raise HTTPException(405)

                # convert url param datatypes to annotation types
                param_parser = UrlParamParser(
                    handler, kwargs, inspect.isclass(route.handler)
                )
                kwargs = param_parser.get()
                response = await handler(request, **kwargs)
            else:
                raise HTTPException(404)
        except Exception as e:
            if isinstance(e, HTTPException) or isinstance(e, HTTPException):
                response = e.response
            else:
                raise e
        return response

    # NOTE: Handle Websocket
    async def handle_websocket(self, websocket: WebSocket):
        route, _ = self.router.get_route(request_path=websocket.path)

        if route and route.handler is not None:
            handler = route.handler
            await handler(websocket)

    # NOTE: Middleware
    def add_middleware(self, middleware_cls: BaseMiddleware, *args, **kwargs):
        self.middleware.add(middleware_cls, *args, **kwargs)

    def __setup_middlewares(
        self, middlewares: typing.Sequence[BaseMiddleware] = None
    ):
        # register exception handling middleware
        self.add_middleware(ExceptionMiddleware)

        # register user defined middlewares
        if not middlewares:
            middlewares = []
        for middleware in middlewares:
            self.add_middleware(middleware)

    # NOTE: Test Client
    def test_client(
        self, base_url: str = "http://testserver"
    ) -> httpx.AsyncClient:
        if not hasattr(self, "_test_client"):
            self._test_client = httpx.AsyncClient(app=self, base_url=base_url)

        return self._test_client

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        scope["app"] = self
        await self.middleware(scope, receive, send)
