from collections import OrderedDict
import inspect
import typing
import yaml

from yaat.requests import Request
from yaat.responses import Response, JSONResponse
from yaat.routing import Route, Router, RouteTypes


class RouteInfo:
    def __init__(
        self,
        path: str,
        methods: typing.List[str],
        handler: typing.Callable,
        tags: typing.List[str] = None,
    ):
        self.path = path
        self.methods = methods
        self.handler = handler
        self.tags = tags if tags else []


class SchemaGenerator:
    def __init__(self, base_schema: dict):
        self.base_schema = base_schema

    def get_routes_info(
        self, routes: typing.List[Route] = None
    ) -> typing.List[RouteInfo]:
        return self._get_info(routes)

    def get_schema(self, routes: typing.List[Route]) -> typing.Dict:
        schema = self.base_schema.copy()  # copy the base schema
        schema.setdefault("paths", {})
        routes_info = self.get_routes_info(routes)

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
                    self._add_to_schema(
                        schema=schema,
                        path=route.path,
                        method=method,
                        handler=handler,
                        tags=route.tags,
                        is_class=True,
                    )
            # if method, just loop through methods and add
            else:
                for method in route.methods:
                    if method in ["HEAD"]:
                        continue
                    self._add_to_schema(
                        schema=schema,
                        path=route.path,
                        method=method,
                        handler=route.handler,
                        tags=route.tags,
                    )

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

                info.append(
                    RouteInfo(path, route.methods, route.handler, route.tags)
                )
            # if router, parse the route to itself
            elif isinstance(route, Router):
                info += self._get_info(route.routes, path)

        return info

    def _add_to_schema(
        self,
        schema: typing.Dict,
        path: str,
        method: str,
        handler: typing.Callable,
        tags: typing.List,
        is_class: bool = False,
    ):
        """
        Add the route documentation to OpenAPI docs
        - automatically add path parameter documentation based on handler parameters
          if not defined by user.
        """

        docs = self.get_docstirng(handler)
        method = method.lower()

        if len(docs) == 0:
            return

        # Auto add parameter documentation for each route
        signature = inspect.signature(handler)
        parameters = signature.parameters.copy()
        param_names = list(signature.parameters.keys())

        # if class, ignore first 2 params (self, request) else 1 (request)
        if is_class:
            del parameters[param_names[0]]
            del parameters[param_names[1]]
            param_names = param_names[2:]
        else:
            del parameters[param_names[0]]
            param_names = param_names[1:]

        # auto add param documentation to route
        if param_names:
            if "parameters" not in docs:
                docs["parameters"] = []

            for param_name in param_names:
                param_data = parameters.get(param_name)
                schema_type = self._get_param_schema_types(
                    param_data.annotation
                )

                updated = False

                # look for exists one and update fields
                for param in docs["parameters"][:]:
                    if param["name"] in parameters.keys():
                        if "in" not in param:
                            param["in"] = "path"

                        # check if schema exists, if not add
                        if "schema" not in param:
                            param["schema"] = {}
                            param["schema"][
                                "type"
                            ] = self._get_param_schema_types(
                                param_data.annotation
                            )

                        # check if required exists, if not auto add
                        if "required" not in param:
                            if param_data.default is inspect.Parameter.empty:
                                param["required"] = "true"

                        # field exists, and updated already
                        # so no need to create new below
                        updated = True
                        break

                if updated:
                    continue

                # if document is not exists at all, create one and add
                param_doc = {}
                param_doc["in"] = "path"
                param_doc["name"] = param_name
                param_doc["schema"] = {"type": schema_type}
                if param_data.default is inspect.Parameter.empty:
                    param_doc["required"] = "true"

                docs["parameters"].append(param_doc)

        if path not in schema["paths"]:
            schema["paths"][path] = {}

        schema["paths"][path][method] = docs
        # do not override tags if user defined inside docstring
        if tags and not schema["paths"][path][method].get("tags"):
            schema["paths"][path][method]["tags"] = tags

    def _get_param_schema_types(self, object_type: typing.Any) -> str:
        if object_type == int:
            return "integer"
        elif object_type == float:
            return "number"
        elif object_type == bool:
            return "boolean"
        else:
            return "string"


class OpenAPIResponse(Response):
    # https://github.com/OAI/OpenAPI-Specification/issues/110#issuecomment-364498200
    media_type = "application/vnd.oai.openapi"

    def render_content(self, content: typing.Any) -> bytes:
        assert isinstance(content, dict), "The schema must be a dictionary."
        return yaml.dump(content, default_flow_style=False).encode("utf-8")


class OpenAPISchema:
    def __init__(
        self, title: str, description: str = None, version: str = None
    ):
        base_schema = {
            "openapi": "3.0.0",
            "info": {"title": title},
        }
        if description:
            base_schema["info"]["description"] = description
        if version:
            base_schema["info"]["version"] = version

        self.schema = SchemaGenerator(base_schema)

    def get_schema(self, routes: typing.List[Route]) -> typing.Dict:
        return self.schema.get_schema(routes)

    def JSONResponse(self, request: Request) -> JSONResponse:
        routes = request.app.router.routes
        schema = self.get_schema(routes)
        return JSONResponse(schema)

    def Response(self, request: Request) -> Response:
        routes = request.app.router.routes
        schema = self.get_schema(routes)
        return OpenAPIResponse(schema)
