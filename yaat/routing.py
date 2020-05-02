from collections import OrderedDict
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
        handler: typing.Callable,
        methods: typing.List[str] = None,
    ):
        self.route_type = route_type
        self.path = path
        self.handler = handler
        self.methods = methods if methods else HTTP_METHODS

    @property
    def type(self) -> RouteTypes:
        return self.route_type

    @property
    def methods(self) -> typing.List[str]:
        return self.__methods

    @methods.setter
    def methods(self, methods: typing.List[str]):
        # make sure all HTTP methods are upper
        self.__methods = [method.upper() for method in methods]

    def is_valid_method(self, method: str) -> bool:
        return method.upper() in self.methods


class Router:
    def __init__(self):
        self.routes = OrderedDict()

    @property
    def paths(self) -> typing.List[str]:
        paths = set()
        for _, route in self.routes.items():
            paths.add(route.path)
        return list(paths)

    def route(
        self, path: str, methods: typing.List[str] = None
    ) -> typing.Callable:
        def wrapper(handler):
            self.add_route(path=path, handler=handler, methods=methods)
            return handler

        return wrapper

    def add_route(
        self,
        path: str,
        handler: typing.Callable,
        methods: typing.List[str] = None,
        is_static: bool = False,
    ):
        assert path not in self.paths, f"Route {path}, already exists"
        route_type = RouteTypes.STATIC if is_static else RouteTypes.HTTP
        self.routes[path] = Route(
            route_type=route_type, path=path, handler=handler, methods=methods,
        )

    def websocket_route(self, path: str) -> typing.Callable:
        def wrapper(handler):
            self.add_websocket_route(path=path)
            return handler

        return wrapper

    def add_websocket_route(self, path: str, handler: typing.Callable):
        assert path not in self.paths, f"Route {path}, already exists"
        self.routes[path] = Route(
            route_type=RouteTypes.WEBSOCKET, path=path, handler=handler
        )

    def mount(self, router: typing.Callable, prefix: str):
        """Mount another router"""
        self.routes[prefix] = router

    def get_route(
        self,
        *,
        request_path: str,
        prev_path: str = None,
        routes: OrderedDict = None,
    ) -> (Route, typing.Dict[str, typing.Any]):
        # if not given, use self
        if not routes:
            routes = self.routes

        for path, router in routes.items():
            # if route instance, just loop and search
            if isinstance(router, Route):
                route = router

                # for static routing, use different methods for route comparison
                if route.type == RouteTypes.STATIC:
                    return route, {"router_path": prev_path}

                parse_result = parse(route.path, request_path)
                if parse_result is not None:
                    return route, parse_result.named

            # else, router itself
            # Type of router
            #   - Sub Application
            #   - Static Files Handler
            else:
                directories = self._path_to_directories(request_path)
                first_directory = directories[0]

                # if != 1,means has multiple sub directory other than /
                # and if first directory not equal to router's path means
                # the requested url is not for the current router
                if len(directories) != 1 and first_directory != path:
                    continue

                # reconstruct previous path for next router
                if prev_path and first_directory != "/":
                    prev_path = f"{prev_path}{first_directory}"
                elif not prev_path and len(directories) == 1:
                    # first sub directory, so previous should be root /
                    prev_path = "/"
                else:
                    prev_path = first_directory

                # request path for next router would be all sub directories
                # below the current one
                request_path = self._directories_to_path(directories[1:])
                return self.get_route(
                    request_path=request_path,
                    prev_path=prev_path,
                    routes=router.routes,
                )

        return None, None

    def _path_to_directories(self, path: str) -> typing.List[str]:
        if path == "/":
            return ["/"]
        return [f"/{p}" for p in path.split("/") if p != ""]

    def _directories_to_path(self, directories: typing.List[str]) -> str:
        url = "/".join(directories)
        if not url.startswith("/"):
            return f"/{url}"
        return url
