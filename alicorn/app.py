import inspect
import typing

from .exceptions import MethodNotAllowException, NotFoundException
from .middleware import Middleware
from .requests import Request
from .responses import Response, FileResponse
from .routing import Router
from .staticfiles import handle_staticfile
from .types import Scope, Receive, Send


class Alicorn:
    def __init__(self,  static_dir=None):
        self.router = Router()
        self.static_dir = static_dir[1:] if static_dir and static_dir.startswith("/") else static_dir
        self.middleware = Middleware(self)
        self.exception_handler = None

    # NOTE: properties
    @property
    def exception_handler(self) -> callable:
        return self.__exception_handler

    @exception_handler.setter
    def exception_handler(self, exception: callable) -> None:
        self.__exception_handler = exception


    # NOTE: Routing
    def add_route(self, path: str, handler: callable, methods: list = None) -> None:
        self.router.add_route(path, handler, methods)

    def route(self, path: str, methods: list = None) -> callable:
        def wrapper(handler):
            self.add_route(path, handler, methods)
            return handler

        return wrapper

    def mount(self, router: Router, prefix: str = None) -> None:
        self.router.mount(router, prefix)


    # NOTE: Handle Request
    async def handle_request(self, request: Request) -> Response:
        # handle static file
        if self.static_dir and request.path.startswith(f"/{self.static_dir}"):
            return await handle_staticfile(request, self.static_dir)

        route, kwargs = self.router.get_route(request_path=request.path, method=request.method)

        try:
            if route and route.handler is not None:
                handler = route.handler
                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise MethodNotAllowException
                if not route.is_valid_method(request.method):
                    raise MethodNotAllowException

                response = await handler(request, **kwargs)
            else:
                # default response when path not found
                raise NotFoundException
        except Exception as e:
            if self.exception_handler is not None:
                response = self.exception_handler(request, e)
            elif isinstance(e, MethodNotAllowException) or isinstance(e, NotFoundException):
                response = e.response
            else:
                raise e
        return response


    # NOTE: Middleware
    def add_middleware(self, middleware_cls: Middleware) -> None:
        self.middleware.add(middleware_cls)


    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.middleware(scope, receive, send)
