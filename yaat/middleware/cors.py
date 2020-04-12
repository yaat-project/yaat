import typing

from yaat.constants import HTTP_METHODS
from yaat.datatypes import Headers
from yaat.requests import Request
from yaat.responses import Response, TextResponse
from yaat.types import ASGIApp


class CorsMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        allow_origins: typing.Sequence[str] = (),
        allow_methods: typing.Sequence[str] = ("GET",),
        allow_headers: typing.Sequence[str] = (),
        allow_credentials: bool = False,
        expose_headers: typing.Sequence[str] = (),
        max_age: int = 600,  # 10 mins
    ):
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

        if "*" in allow_methods:
            allow_methods = HTTP_METHODS

        self.app = app
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = [header.lower() for header in allow_headers]
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers
        self.max_age = max_age
        self.allow_all_origins = "*" in allow_origins
        self.allow_all_headers = "*" in allow_headers

    def is_allowed_origin(self, origin: str) -> bool:
        if self.allow_all_origins:
            return True

        return origin in self.allow_origins    

    def preflight_response(self, request_headers: Headers) -> Response:
        # https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request

        request_origin = request_headers["origin"]
        request_method = request_headers["access-control-request-method"]
        request_headers = request_headers.get("access-control-request-headers")

        # initialize preflight headers
        headers = {
            "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
            "Access-Control-Max-Age": str(self.max_age)
        }
        failures = set()

        # check origin
        if self.is_allowed_origin(request_origin) and not self.allow_all_origins:
            headers["Access-Control-Allow-Origin"] = requested_origin
            headers["Vary"] = "Origin"
        elif self.allow_all_origins:
            headers["Access-Control-Allow-Origin"] = "*"
        else:
            failures.add("Origin")

        # check HTTP method
        if request_method not in self.allow_methods:
            failures.add("Method")

        # check allow headers
        if request_headers is not None:
            for header in requested_headers.split(","):
                if header.lower().strip() not in self.allow_all_headers:
                    failures.add("Headers")
                    break

        if failures:
            message = f"Disallowed cors {', '.join(failures)}"
            return TextResponse(message, status_code=400, headers=headers)

        # Do not return 204, as some legacy browser does not work with 204
        return Response(status_code=200, headers=headers)

    def simple_response(self, request_headers: Headers, response: Response) -> Response:
        origin = request_headers["origin"]
        has_cookie = "cookie" in request_headers

        # check allow credentials
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"

        # check expose header
        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)

        # check origin
        # if cookie presents, server must specify the origin
        # instead of wildcard
        if self.allow_all_origins and has_cookie:
            response.headers["Access-Control-Allow-Origin"] = origin

        elif self.is_allowed_origin(origin) and not self.allow_all_origins:
            response.headers["Access-Control-Allow-Origin"] = origin

            vary = response.headers.get("Vary")
            if vary:
                vary = vary.split(",")
                vary.append("Origin")
            else:
                vary = ["Origin"]
            vary = ", ".join(vary)
            response.headers["Vary"] = vary

        elif self.allow_all_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"

        return response

    async def handle_request(self, request: Request) -> Response:
        origin = request.headers.get("origin")

        # not cors
        if not origin:
            return await self.app.handle_request(request)

        # preflight request
        if request.method == "OPTIONS" and "access-control-request-method" in request.headers:
            return self.preflight_response(request.headers)

        response = await self.app.handle_request(request)
        return self.simple_response(request.headers, response)
