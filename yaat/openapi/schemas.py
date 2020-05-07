from collections import OrderedDict
import inspect
import typing
import yaml

from yaat.requests import Request
from yaat.responses import Response, JSONResponse
from yaat.routing import Route, Router, RouteTypes


class RouteInfo:
    def __init__(
        self, path: str, methods: typing.List[str], handler: typing.Callable
    ):
        self.path = path
        self.methods = methods
        self.handler = handler


class SchemaGenerator:
    def __init__(self, base_schema: dict):
        self.base_schema = base_schema

    def get_routes_info(
        self, routes: typing.List[Route] = None
    ) -> typing.List[RouteInfo]:
        return self._get_info(routes)

    def get_schema(self, routes: typing.List[Route] = None) -> typing.Dict:
        if not routes:
            routes = self.router.routes

        schema = self.base_schema.copy()  # copy the base schema
        schema.setdefault("paths", {})
        routes_info = self.get_routes_info(routes)

        def add_schema(
            schema: typing.Dict,
            path: str,
            methods: str,
            handler: typing.Callable,
        ):
            docs = self.get_docstirng(handler)

            if len(docs) == 0:
                return

            if path not in schema["paths"]:
                schema["paths"][path] = {}

            schema["paths"][path][method] = docs

        for route in routes_info:
            # if it is a class, check by its class methods
            if inspect.isclass(route.handler):
                http_methods = [
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                    "options",
                ]
                for method in http_methods:
                    if not hasattr(route.handler, method):
                        continue
                    handler = getattr(route.handler, method)
                    add_schema(schema, route.path, method, handler)
            # if method, just loop through methods and add
            else:
                for method in route.methods:
                    if method in ["HEAD"]:
                        continue
                    add_schema(schema, route.path, method, route.handler)

        return schema

    def get_docstirng(self, method: typing.Callable) -> typing.Dict:
        """
        Parse the YAML docstring and return as dictionary
        """
        docstring = method.__doc__
        if not docstring:
            return {}

        data = yaml.safe_load(docstring)
        if not isinstance(data, dict):
            return {}

        return data

    def _get_info(self, routes: OrderedDict, prev_path: str = None):
        info = []

        for path, route in routes.items():
            # if route, check if its HTTP route, then parse docstring
            if (
                isinstance(route, Route)
                and route.type == RouteTypes.HTTP
                and route.has_schema
            ):
                # if the route is inside subroute, it will have previous path
                if prev_path:
                    path = f"{prev_path}{path}"

                info.append(RouteInfo(path, route.methods, route.handler))
            # if router, parse the route to itself
            elif isinstance(route, Router):
                info += self._get_info(route.routes, path)

        return info


class OpenAPIResponse(Response):
    # https://github.com/OAI/OpenAPI-Specification/issues/110#issuecomment-364498200
    media_type = "application/vnd.oai.openapi"

    def render_content(self, content: typing.Any) -> bytes:
        assert isinstance(content, dict), "The schema must be a dictionary."
        return yaml.dump(content, default_flow_style=False).encode("utf-8")


class OpenAPISchema:
    def __init__(self, title: str, version: str):
        base_schema = {
            "openapi": "3.0.0",
            "info": {"title": title, "version": version},
        }
        self.schema = SchemaGenerator(base_schema)

    def JSONResponse(self, request: Request) -> JSONResponse:
        routes = request.app.router.routes
        schema = self.schema.get_schema(routes)
        return JSONResponse(schema)

    def Response(self, request: Request) -> Response:
        routes = request.app.router.routes
        schema = self.schema.get_schema(routes)
        return OpenAPIResponse(schema)
