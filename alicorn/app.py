from jinja2 import Environment, FileSystemLoader
from parse import parse
import inspect
import os
import typing

from .exceptions import HttpException
from .middleware import Middleware
from .requests import Request
from .responses import Response, FileResponse
from .staticfiles import handle_staticfile
from .types import Scope, Receive, Send


class Alicorn:
    def __init__(self, templates_dir="templates", static_dir=None):
        self.routes = {}
        self.templates_env = Environment(loader=FileSystemLoader(os.path.abspath(templates_dir)))
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
    def add_route(self, path: str, handler: callable) -> None:
        assert path not in self.routes, f"Route {path}, already exists"
        self.routes[path] = handler

    def route(self, path: str) -> callable:
        def wrapper(handler):
            self.add_route(path, handler)
            return handler

        return wrapper


    # NOTE: Handle Request
    async def handle_request(self, request: Request) -> Response:
        handler, kwargs = self.find_handler(request_path=request.path)

        # handle static file
        if self.static_dir and request.path.startswith(f"/{self.static_dir}"):
            return await handle_staticfile(request, self.static_dir)

        try:
            if handler is not None:
                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise HttpException(
                            status_code=400,
                            details=f"{request.method} method is not allowed for {request.path}"
                        )
                response = await handler(request, **kwargs)
            else:
                # default response when path not found
                raise HttpException(status_code=404, details=f"Not found")
        except Exception as e:
            if self.exception_handler is not None:
                response = self.exception_handler(request, e)
            elif isinstance(e, HttpException):
                response = e.response
            else:
                raise e
        return response

    def find_handler(self, request_path) -> (callable, typing.Any):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named
        return None, None


    # NOTE: Templating
    def template(self, template_name: str, context=None) -> bytes:
        if context is None:
            context = {}

        return self.templates_env.get_template(template_name).render(**context).encode()


    # NOTE: Middleware
    def add_middleware(self, middleware_cls: Middleware) -> None:
        self.middleware.add(middleware_cls)


    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.middleware(scope, receive, send)
