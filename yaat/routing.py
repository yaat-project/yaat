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
        request_path: str,
        prev_path: str = None,
        routes: OrderedDict = None,
    ) -> (Route, typing.Any):
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

            # else, sub application and the router itself
            else:
                url_struct = self.__url_to_path_struct(request_path)

                # if only first item, instead / to first index
                first_url_struct = url_struct[0]

                # remove "/" from start
                if first_url_struct.startswith("/"):
                    first_url_struct = first_url_struct[1:]
                if path.startswith("/"):
                    path = path[1:]

                # reconstruct prev path
                if prev_path:
                    prev_path = f"{prev_path}{url_struct[0]}"
                elif len(url_struct) == 1:
                    prev_path = "/"
                else:
                    prev_path = url_struct[0]
                # add / if not at the start
                if not prev_path.startswith("/"):
                    prev_path = f"/{prev_path}"

                # in case, router is mounted on "/" (for len to 1)
                if first_url_struct == path or len(url_struct) == 1:
                    url = self.__path_struct_to_url(url_struct[1:])
                    return self.get_route(
                        request_path=url,
                        prev_path=prev_path,
                        routes=router.routes,
                    )

        return None, None

    def __add_prefix(self, prefix: str, path: str) -> str:
        if not prefix.startswith("/"):
            prefix = "/" + prefix

        return (
            f"{prefix}{path}" if path.startswith("/") else f"{prefix}/{path}"
        )

    def __url_to_path_struct(self, path: str) -> typing.List[str]:
        if path == "/":
            return ["/"]
        return [p for p in path.split("/") if p != ""]

    def __path_struct_to_url(self, struct: typing.List[str]) -> str:
        url = "/".join(struct)
        if not url.startswith("/"):
            return f"/{url}"
        return url
