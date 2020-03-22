import http.cookies
import json
import typing

try:
    from multipart.multipart import parse_options_header
except ImportError:
    parse_options_header = None

from .constants import ENCODING_METHOD
from .datatypes import Address, Form, Headers, QueryParams, URL
from .formparsers import FormParser, MultiPartParser
from .types import Scope, Receive, Send, Message


async def empty_receive() -> Message:
    raise RuntimeError("Receive channel has not been made available")


class HttpConnection:
    def __init__(self, scope: Scope) -> None:
        assert scope["type"] in ("http", "websocket")
        self.scope = scope

    def __getitem__(self, key: str) -> str:
        return self.scope[key]

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self.scope)

    def __len__(self) -> int:
        return len(self.scope)

    @property
    def app(self) -> typing.Any:
        return self.scope["app"]

    @property
    def method(self) -> str:
        return self.scope["method"]

    @property
    def path(self) -> str:
        return self.scope["path"]

    @property
    def url(self) -> URL:
        if not hasattr(self, "_url"):
            self._url = URL(scope=self.scope)
        return self._url

    @property
    def headers(self) -> Headers:
        if not hasattr(self, "_headers"):
            self._headers = Headers(self.scope["headers"])
        return self._headers

    @property
    def query_params(self) -> QueryParams:
        if not hasattr(self, "_query_params"):
            self._query_params = QueryParams(self.scope["query_string"])
        return self._query_params

    @property
    def session(self) -> dict:
        # TODO: implement after Session Middleware
        return None

    @property
    def cookies(self) -> typing.Dict[str, str]:
        if not hasattr(self, "_cookies"):
            cookies = {}
            raw_cookies = self.headers.get("cookie")

            if raw_cookies:
                cookie = http.cookies.SimpleCookie()
                cookie.load(raw_cookies)

                for key, data in cookie.items():
                    cookies[key] = data.value

            self._cookies = cookies

        return self._cookies

    @property
    def client(self) -> Address:
        host, port = self.scope.get("client") or (None, None)
        return Address(host, port) if host else None

    @property
    async def auth(self) -> typing.Any:
        # TODO: implement after Authentication Middleware
        pass

    @property
    async def user(self) -> typing.Any:
        # TODO: implement after Authentication Middleware
        pass


class Request(HttpConnection):
    def __init__(
        self,
        scope: Scope,
        receive: Receive = empty_receive,
    ):
        super().__init__(scope)
        self.receive = receive

    @property
    def receive(self) -> Receive:
        return self.__receive

    @receive.setter
    def receive(self, receive: Receive):
        self.__receive = receive

    async def stream(self) -> typing.AsyncGenerator[bytes, None]:
        if hasattr(self, "_body"):
            yield self._body
            yield b""
            return

        while True:
            message = await self.receive()
            body = message.get('body', b'')
            if body:
                yield body
            if not message.get('more_body', False):
                break

        yield b""

    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            chunks = []
            async for chunk in self.stream():
                chunks.append(chunk)
            self._body = b"".join(chunks)

        return self._body

    async def json(self) -> typing.Any:
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = {}

            if not body == b'':
                self._json = json.loads(body)
        return self._json

    async def form(self) -> dict:
        if not hasattr(self, "_form"):
            assert (
                parse_options_header is not None
            ), "'python-multipart' must be installed to use form."

            content_type, options = parse_options_header(self.headers.get("content-type"))

            if content_type == b"multipart/form-data":
                multipart_parser = MultiPartParser(self.headers, self.stream())
                self._form = await multipart_parser.parse()

            elif content_type == b"application/x-www-form-urlencoded":
                form_parser = FormParser(self.body)
                self._form = await form_parser.parse()

            else:
                self._form = Form()

        return self._form
