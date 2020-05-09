from collections import OrderedDict
from enum import Enum
from parse import parse
import inspect
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
        has_schema: bool = False,
        tags: typing.List[str] = None,
    ):
        if inspect.isclass(handler):
            # if handler is class, if will check in function level
            # so allow all HTTP methods
            methods = methods if methods else HTTP_METHODS
        else:
            # if handler is function, if methods are not provided
            # only allow GET
            methods = methods if methods else ["GET"]

        self.route_type = route_type
        self.path = path
        self.handler = handler
        self.methods = methods
        self.has_schema = has_schema
        self.tags = tags if tags else []

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
        self.__paths = []

    @property
    def paths(self):
        self.__paths = []  # reset before loading paths
        return self._get_paths()

    def _get_paths(
        self, routes: OrderedDict = None, prev_path: str = None
    ) -> typing.List[str]:
        """
        Method to traverse through routes and sub router inside its to get all handler paths.
        """
        if not routes:
            routes = self.routes

        for path, router in routes.items():
            if isinstance(router, Route):
                fullpath = (
                    f"{prev_path}{router.path}" if prev_path else router.path
                )
                self.__paths.append(fullpath)
            else:
                self._get_paths(router.routes, path)

        return self.__paths

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
        is_static: bool = False,
        tags: typing.List[str] = None,
    ):
        assert path not in self.paths, f"Route {path}, already exists"
        route_type = RouteTypes.STATIC if is_static else RouteTypes.HTTP
        path = self._clean_path(path)
        self.routes[path] = Route(
            route_type=route_type,
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
            self.add_websocket_route(path=path)
            return handler

        return wrapper

    def add_websocket_route(
        self,
        path: str,
        handler: typing.Callable,
        tags: typing.List[str] = None,
    ):
        assert path not in self.paths, f"Route {path}, already exists"
        path = self._clean_path(path)
        self.routes[path] = Route(
            route_type=RouteTypes.WEBSOCKET,
            path=path,
            handler=handler,
            tags=tags,
        )

    def mount(self, router: typing.Callable, prefix: str):
        """Mount another router"""
        assert (
            prefix not in self.routes.keys()
        ), f"Route with {prefix}, already exists"
        prefix = self._clean_path(prefix)
        self.routes[prefix] = router

    def get_route(
        self,
        *,
        request_path: str,
        prev_path: str = None,
        routes: OrderedDict = None,
    ) -> (Route, typing.Dict[str, typing.Any]):
        # NOTE: to prevent circular import
        from yaat.staticfiles import StaticFiles

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

                # if router is Static Files, and router path is root, means
                # first directory should be "/" as anything after is filename (with dirs)
                # for static files handler
                if path == "/" and isinstance(router, StaticFiles):
                    first_directory = "/"

                # if first directory not equal to router's path means
                # the requested url is not for the current router
                if first_directory != path:
                    continue

                # reconstruct previous path for next router
                if prev_path and first_directory != "/":
                    # if current path is not root, then next previous path
                    # is current router prex path + current path
                    next_prev_path = f"{prev_path}{first_directory}"
                elif prev_path and first_directory == "/":
                    # because we are not going to add slash to the end,
                    # so just same previous path for next router
                    next_prev_path = prev_path
                else:
                    # no previous path, means use current path for next
                    # router
                    next_prev_path = first_directory

                # request path for next router would be all sub directories
                # after the current one
                next_request_path = self._directories_to_path(directories[1:])

                # search in sub router, if route is found return
                # else continue
                route, kwargs = self.get_route(
                    request_path=next_request_path,
                    prev_path=next_prev_path,
                    routes=router.routes,
                )
                if route:
                    return route, kwargs

        return None, None

    def _clean_path(self, path: str) -> str:
        if path == "/":
            return path
        if not path.startswith("/"):
            path = f"/{path}"
        if path.endswith("/"):
            path = path[:-1]
        return path

    def _path_to_directories(self, path: str) -> typing.List[str]:
        if path == "/":
            return ["/"]
        return [f"/{p}" for p in path.split("/") if p != ""]

    def _directories_to_path(self, directories: typing.List[str]) -> str:
        url = "".join(directories)
        if not url.startswith("/"):
            return f"/{url}"
        return url
