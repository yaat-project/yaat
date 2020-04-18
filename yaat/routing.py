from parse import parse
import typing

from yaat.constants import HTTP_METHODS


class Route:
    def __init__(
        self,
        path: str,
        handler: callable,
        methods: list = None,
        is_static: bool = False,
        is_websocket: bool = False,
    ):
        self.path = path
        self.handler = handler
        self.methods = methods if methods else HTTP_METHODS
        self.is_static = is_static  # check if  static route
        self.is_websocket = is_websocket  # check if websocket route

    @property
    def path(self) -> str:
        return self.__path

    @path.setter
    def path(self, path: str):
        self.__path = path

    @property
    def handler(self) -> callable:
        return self.__handler

    @handler.setter
    def handler(self, handler: callable):
        self.__handler = handler

    @property
    def methods(self) -> list:
        return self.__methods

    @methods.setter
    def methods(self, methods: list):
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

    def route(self, path: str, methods: list = None) -> callable:
        def wrapper(handler):
            self.add_route(path=path, handler=handler, methods=methods)
            return handler

        return wrapper

    def add_route(
        self,
        path: str,
        handler: callable,
        methods: list = None,
        static: bool = False,
    ):
        assert path not in self.paths, f"Route {path}, already exists"
        self.routes.append(
            Route(
                path=path, handler=handler, methods=methods, is_static=static
            )
        )

    def websocket_route(self, path: str) -> callable:
        def wrapper(handler):
            self.add_websocket_route(path=path)
            return handler

        return wrapper

    def add_websocket_route(self, path: str, handler: callable):
        assert path not in self.paths, f"Route {path}, already exists"
        self.routes.append(
            Route(path=path, handler=handler, is_websocket=True)
        )

    def mount(
        self,
        router: callable,
        prefix: str = None,
        static: bool = False,
        websocket: bool = False,
    ):
        """Mount another router"""
        routes = router.routes

        # register sub routes
        for route in routes:
            path = (
                self.__add_prefix(prefix, route.path) if prefix else route.path
            )

            if websocket:
                self.add_websocket_route(path=path, handler=route.handler)
            else:
                self.add_route(
                    path=path,
                    handler=route.handler,
                    methods=route.methods,
                    static=static,
                )

    def get_route(self, request_path: str) -> (Route, typing.Any):
        for route in self.routes:
            # for static routing, use different methods for route comparison
            if route.is_static and request_path.startswith(route.path):
                return route, {}

            parse_result = parse(route.path, request_path)
            if parse_result is not None:
                return route, parse_result.named

        return None, None

    def __add_prefix(self, prefix: str, path: str) -> str:
        if not prefix.startswith("/"):
            prefix = "/" + prefix

        return (
            f"{prefix}{path}" if path.startswith("/") else f"{prefix}/{path}"
        )
