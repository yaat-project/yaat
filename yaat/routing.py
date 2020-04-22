from enum import Enum
from parse import parse
import typing

from yaat.constants import HTTP_METHODS


class RouteTypes(Enum):
    HTTP = 1  # http route
    STATIC = 2  # static handler route
    WEBSOCKET = 3  # websocket route


class Route:
    def __init__(
        self,
        route_type: RouteTypes,
        path: str,
        handler: callable,
        methods: list = None,
    ):
        self.route_type = route_type
        self.path = path
        self.handler = handler
        self.methods = methods if methods else HTTP_METHODS

    @property
    def type(self) -> RouteTypes:
        return self.route_type

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
        is_static: bool = False,
    ):
        assert path not in self.paths, f"Route {path}, already exists"
        route_type = RouteTypes.STATIC if is_static else RouteTypes.HTTP
        self.routes.append(
            Route(
                route_type=route_type,
                path=path,
                handler=handler,
                methods=methods,
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
            Route(route_type=RouteTypes.WEBSOCKET, path=path, handler=handler)
        )

    def mount(self, router: callable, prefix: str = None):
        """Mount another router"""
        routes = router.routes

        # register sub routes
        for route in routes:
            if route.type != RouteTypes.STATIC:
                path = (
                    self.__add_prefix(prefix, route.path)
                    if prefix
                    else route.path
                )

                if route.type == RouteTypes.WEBSOCKET:
                    self.add_websocket_route(path=path, handler=route.handler)
                else:
                    self.add_route(
                        path=path, handler=route.handler, methods=route.methods
                    )
            else:
                # StaticFile is not mounted yet to any router
                path = prefix if prefix else "/"
                if route.path is not None:
                    path = self.__add_prefix(path, route.path)

                # update StaticFileHandler path
                router.path = path
                self.add_route(
                    path=path,
                    handler=route.handler,
                    methods=route.methods,
                    is_static=True,
                )

    def get_route(self, request_path: str) -> (Route, typing.Any):
        for route in self.routes:
            # for static routing, use different methods for route comparison
            if route.type == RouteTypes.STATIC and request_path.startswith(
                route.path
            ):
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
