import httpx
import inspect
import typing

from yaat.exceptions import HTTPException
from yaat.middleware import BaseMiddleware, ExceptionMiddleware
from yaat.requests import Request
from yaat.responses import Response, FileResponse
from yaat.routing import Router
from yaat.staticfiles import StaticFiles
from yaat.types import Scope, Receive, Send
from yaat.websockets import WebSocket


class Yaat:
    def __init__(self, middlewares: typing.Sequence[BaseMiddleware] = None):
        self.router = Router()
        self.middleware = BaseMiddleware(self)
        self.exception_handler = None

        # NOTE: middleware registration
        self.__register_middlewares(middlewares)


    # NOTE: properties
    @property
    def exception_handler(self) -> callable:
        return self.__exception_handler

    @exception_handler.setter
    def exception_handler(self, exception: callable):
        self.__exception_handler = exception


    # NOTE: Routing
    def route(self, path: str, methods: list = None) -> callable:
        def wrapper(handler):
            self.add_route(path, handler, methods)
            return handler
        return wrapper

    def add_route(self, path: str, handler: callable, methods: list = None):
        self.router.add_route(path=path, handler=handler, methods=methods)

    def websocket_route(self, path: str) -> callable:
        def wrapper(handler):
            self.add_websocket_route(path, handler)
            return handler
        return wrapper 

    def add_websocket_route(self, path: str, handler: callable):
        self.router.add_websocket_route(path=path, handler=handler)

    def mount(self, router: Router, prefix: str = None, websocket: bool = False):
        # check if its static route
        static = isinstance(router, StaticFiles)

        if prefix and static:
            # NOTE: because 'prefix' is already defined in static route
            raise ValueError("'prefix' must be None when mounting static routes.")
        if websocket and static:
            raise ValueError("'websocket' must be None when mounting static routes.")

        self.router.mount(
            router=router,
            prefix=prefix,
            static=static,
            websocket=websocket,
        )


    # NOTE: Handle HTTP Request
    async def handle_request(self, request: Request) -> Response:
        route, kwargs = self.router.get_route(request_path=request.path)

        try:
            # check if route exists and it is not websocket route
            if route and route.handler is not None and not route.is_websocket:
                handler = route.handler

                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise HTTPException(405)
                if not route.is_valid_method(request.method):
                    raise HTTPException(405)

                response = await handler(request, **kwargs)
            else:
                raise HTTPException(404)
        except Exception as e:
            if self.exception_handler is not None:
                response = self.exception_handler(request, e)
            elif isinstance(e, HTTPException) or isinstance(e, HTTPException):
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
    def add_middleware(self, middleware_cls: BaseMiddleware):
        self.middleware.add(middleware_cls)

    def __register_middlewares(self, middlewares: typing.Sequence[BaseMiddleware] = None):
        # register exception handling middleware
        self.add_middleware(ExceptionMiddleware)

        # register user defined middlewares
        if not middlewares:
            middlewares = []
        for middleware in middlewares:
            self.add_middleware(middleware)


    # NOTE: Test Client
    def test_client(self, base_url: str = "http://testserver") -> httpx.AsyncClient:
        if not hasattr(self, "_test_client"):
            self._test_client = httpx.AsyncClient(app=self, base_url=base_url)

        return self._test_client


    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        await self.middleware(scope, receive, send)
