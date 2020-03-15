from urllib.parse import parse_qsl
import tempfile
import typing

from .constants import ENCODING_METHOD
from .concurrency import run_in_threadpool
from .types import Scope


class URL(str):
    def __init__(self, scope: Scope):
        self.scheme = scope.get("scheme", "http")
        self.server = scope.get("server", None)  
        self.path = scope.get("root_path", "") + scope["path"]
        self.query_string = scope.get("query_string", b"")
        self.host_header = scope["headers"]
        self.__init_url()

    @property
    def scheme(self) -> str:
        return self.__scheme

    @scheme.setter
    def scheme(self, scheme: str):
        self.__scheme = scheme

    @property
    def server(self) -> typing.Tuple[str, int]:
        return self.__server

    @server.setter
    def server(self, server: typing.Tuple[str, int]):
        self.__server = server # ip and port

    @property
    def host(self) -> str:
        if not hasattr(self, "__host"):
            self.__host = None

            if self.server:
                host, port = self.server
                self.__host = host
        return self.__host

    @property
    def port(self) -> int:
        if not hasattr(self, "__port"):
            self.__port = None

            if self.server:
                host, port = self.server
                self.__port = port
        return self.__port

    @property
    def query_string(self) -> bytes:
        return self.__query_string

    @query_string.setter
    def query_string(self, query_str: bytes):
        self.__query_string = query_str

    @property
    def host_header(self) -> str:
        return self.__host_header

    @host_header.setter
    def host_header(self, headers: list):
        host_header = None
        for key, value in headers:
            if key == b"host":
                host_header = value.decode(ENCODING_METHOD)
                break
        self.__host_header = host_header

    @property
    def url(self) -> str:
        return self.__url

    def __init_url(self):
        if self.host_header is not None:
            url = f"{self.scheme}://{self.host_header}{self.path}"
        elif self.server is None:
            url = self.path
        else:
            host, port = self.server
            default_port = {"http": 80, "https": 443, "ws": 80, "wss": 443}[self.scheme]
            if port == default_port:
                url = f"{self.scheme}://{host}{self.path}"
            else:
                url = f"{self.scheme}://{host}:{port}{self.path}"

        if self.query_string:
            url += "?" + self.query_string.decode(ENCODING_METHOD)

        self.__url = url

    def is_secure(self) -> bool:
        return self.scheme in ("https", "wss")

    def __eq__(self, other: typing.Any) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        return self.__url


class Address:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    @property
    def host(self) -> str:
        return self.__host

    @host.setter
    def host(self, host: str):
        self.__host = str(host)

    @property
    def port(self) -> int:
        return self.__port

    @port.setter
    def port(self, port: int):
        self.__port = int(port) if port else None

    def __str__(self) -> str:
        if self.host and self.port:
            return f"{self.host}:{self.port}"
        return self.host


class Headers:
    def __init__(self, raw_headers: typing.List[typing.Tuple[bytes, bytes]]):
        self.__raw_headers = raw_headers
        self.__init_headers()

    @property
    def raw(self) -> typing.List[typing.Tuple[bytes, bytes]]:
        return self._raw_headers

    def __init_headers(self):
        self.__headers = {key.decode(ENCODING_METHOD): value.decode(ENCODING_METHOD) for key, value in self.__raw_headers}

    def items(self) -> dict:
        return self.__headers.items()

    def get(self, key: str, default: typing.Any = None) -> str:
        try:
            return self.__headers[key]
        except KeyError:
            return default

    def __contains__(self, key: typing.Any) -> bool:
        return key in self.__headers

    def __getitems__(self, key: typing.Any) -> str:
        return self.__headers[key]

    def __iter__(self) -> typing.Iterator[typing.Any]:
        for key, value in self.items():
            yield key, value

    def __len__(self) -> int:
        return len(self.__headers)


class QueryParams:
    def __init__(self, raw_query: str):
        self.__raw_query = raw_query
        self.__init_query()

    @property
    def raw(self) -> bytes:
        return self.__raw_query

    def __init_query(self):
        query_str = self.raw.decode(ENCODING_METHOD)
        self.__query = dict(parse_qsl(query_str))

    def items(self) -> dict:
        return self.__query.items()

    def get(self, key: str, default: typing.Any = None) -> str:
        try:
            return self.__query[key]
        except KeyError:
            return default

    def __contains__(self, key: typing.Any) -> bool:
        return key in self.__query

    def __getitems__(self, key: typing.Any) -> str:
        return self.__query[key]

    def __iter__(self) -> typing.Iterator[typing.Any]:
        for key, value in self.items():
            yield key, value

    def __len__(self) -> int:
        return len(self.__query)


class Form:
    def __init__(self, form_data: typing.List[typing.Tuple[str, str]] = None):
        self.raw = form_data if form_data else []

    @property
    def raw(self):
        return self.__raw

    @raw.setter
    def raw(self, form_data: typing.List[typing.Tuple[str, str]]) -> typing.List:
        self.__raw = form_data
        self.__init_data()

    def __init_data(self):
        self.__data = {}
        for item in self.raw:
            self.__data[item[0]] = item[1]

    def items(self) -> typing.Dict:
        return self.__data.items()

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        return self.items().get(key, default)

    def __contains__(self, key: typing.Any) -> bool:
        return key in self.__data

    def __getitems__(self, key: typing.Any) -> str:
        return self.__data[key]

    def __iter__(self) -> typing.Iterator[typing.Any]:
        for key, value in self.items():
            yield key, value

    def __len__(self) -> int:
        return len(self.__data)


class UploadFile:
    SPOOL_MAX_SIZE = 1024 * 1024

    def __init__(self, name: str, file: typing.IO = None, content_type: str = "") -> None:
        self.name = name
        self.content_type = content_type
        if file is None:
            file = tempfile.SpooledTemporaryFile(max_size=self.SPOOL_MAX_SIZE)
        self.file = file

    async def write(self, data: typing.Union[bytes, str]) -> None:
        await run_in_threadpool(self.file.write, data)

    async def read(self, size: int = None) -> typing.Union[bytes, str]:
        return await run_in_threadpool(self.file.read, size)

    async def seek(self, offset: int) -> None:
        await run_in_threadpool(self.file.seek, offset)

    async def close(self) -> None:
        await run_in_threadpool(self.file.close)

