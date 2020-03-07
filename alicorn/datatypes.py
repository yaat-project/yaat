from urllib.parse import parse_qsl
import tempfile
import typing

from .constants import ENCODING_METHOD
from .concurrency import run_in_threadpool
from .types import Scope


class URL:
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
        self._raw_headers = raw_headers

    @property
    def raw(self) -> typing.List[typing.Tuple[bytes, bytes]]:
        return self._raw_headers

    def keys(self) -> typing.List[str]:
        return [key.decode(ENCODING_METHOD) for key, value in self._raw_headers]

    def values(self) -> typing.List[str]:
        return [value.decode(ENCODING_METHOD) for key, value in self._raw_headers]

    def items(self) -> dict:
        if hasattr(self, "__decoded_header"):
            return self.__decoded_header

        self.__decoded_header = {key.decode(ENCODING_METHOD): value.decode(ENCODING_METHOD) for key, value in self._raw_headers}
        return self.__decoded_header

    def get(self, key: str, default: typing.Any = None) -> str:
        try:
            return self.items()[key]
        except KeyError:
            return default


class QueryParams:
    def __init__(self, raw_query: str):
        self._raw_query = raw_query

    @property
    def raw(self) -> bytes:
        return self._raw_query

    def keys(self) -> typing.List[str]:
        return [key for key, value in self.items().items()]

    def values(self) -> typing.List[str]:
        return [value for key, value in self.items().items()]

    def items(self) -> dict:
        if hasattr(self, "__query"):
            return self.__query

        query_str = self._raw_query.decode(ENCODING_METHOD)
        self.__query = dict(parse_qsl(query_str))
        return self.__query

    def get(self, key: str, default: typing.Any = None) -> str:
        try:
            return self.items()[key]
        except KeyError:
            return default


class Form:
    def __init__(self, form_data: typing.List[typing.Tuple[str, str]] = None):
        self.raw = form_data if form_data else []

    @property
    def raw(self):
        return self.__raw

    @raw.setter
    def raw(self, form_data: typing.List[typing.Tuple[str, str]]) -> typing.List:
        self.__raw = form_data

    def keys(self) -> typing.List:
        return self.items().keys()

    def values(self) -> typing.List:
        return self.items().values()

    def items(self) -> typing.Dict:
        if not hasattr(self, "__data"):
            self.__data = {}
            for item in self.raw:
                self.__data[item[0]] = item[1]
        return self.__data

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        return self.items().get(key, default)


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

