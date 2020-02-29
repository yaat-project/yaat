from parse import parse
import typing

from .exceptions import HttpException


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
        self._routes = []

    def add_route(self, path: str, handler: callable, methods: list = None):
        self._routes.append(
            Route(path=path, handler=handler, methods=methods)
        )

    @property
    def paths(self) -> list:
        paths = set()
        for route in self._routes:
            paths.add(route.path)
        return list(paths)

    def get_handler(self, request_path: str, method: str) -> (callable, typing.Any):
        for route in self._routes:
            parse_result = parse(route.path, request_path)

            if not route.is_valid_method(method):
                raise HttpException(
                    status_code=405,
                    details="Method Not Allowed"
                )

            if parse_result is not None:
                return route.handler, parse_result.named
    
        return None, None
