from parse import parse
import typing

from .exceptions import MethodNotAllowException


class Route:
    HTTP_METHODS = [
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "CONNECT",
        "OPTIONS",
        "TRACE",
    ]

    def __init__(self, path: str, handler: callable, methods: list = None):
        self.path = path
        self.handler = handler
        self.methods = methods if methods else self.HTTP_METHODS

    @property
    def path(self) -> str:
        return self.__path

    @path.setter
    def path(self, path: str) -> None:
        self.__path = path

    @property
    def handler(self) -> callable:
        return self.__handler

    @handler.setter
    def handler(self, handler: callable) -> None:
        self.__handler = handler

    @property
    def methods(self) -> list:
        return self.__methods

    @methods.setter
    def methods(self, methods: list) -> None:
        # make sure all HTTP methods are upper
        self.__methods = [method.upper() for method in methods]

    def is_valid_method(self, method: str) -> bool:
        return method.upper() in self.methods


class Router:
    def __init__(self):
        self.routes = []

    @property
    def routes(self) -> typing.List[Route]:
        return self.__routes

    @routes.setter
    def routes(self, routes: typing.List[Route]):
        self.__routes = routes

    @property
    def paths(self) -> typing.List[str]:
        paths = set()
        for route in self.routes:
            paths.add(route.path)
        return list(paths)

    def add_route(self, path: str, handler: callable, methods: list = None) -> None:
        assert path not in self.paths, f"Route {path}, already exists"
        self.routes.append(
            Route(path=path, handler=handler, methods=methods)
        )

    def route(self, path: str, methods: list = None) -> callable:
        def wrapper(handler):
            self.add_route(path, handler, methods)
            return handler

        return wrapper

    def mount(self, router: callable, prefix: str = None) -> None:
        """Mount another router"""
        routes = router.routes

        # register sub routes
        for route in routes:
            path = self.__add_prefix(prefix, route.path) if prefix else route.path
            self.add_route(path=path, handler=route.handler, methods=route.methods)

    def get_handler(self, request_path: str, method: str) -> (callable, typing.Any):
        for route in self.routes:
            parse_result = parse(route.path, request_path)

            if not route.is_valid_method(method):
                raise MethodNotAllowException

            if parse_result is not None:
                return route.handler, parse_result.named
    
        return None, None

    def __add_prefix(self, prefix: str, path: str) -> str:
        if not prefix.startswith("/"):
            prefix = "/" + prefix

        return f"{prefix}{path}" if path.startswith("/") else f"{prefix}/{path}"
