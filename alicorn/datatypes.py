from urllib.parse import parse_qsl
import typing

from .types import Scope


class URL:
    def __init__(self, scope: Scope):
        pass


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
        return [key.decode() for key, value in self._raw_headers]

    def values(self) -> typing.List[str]:
        return [value.decode() for key, value in self._raw_headers]

    def items(self) -> dict:
        if hasattr(self, "_decoded_header"):
            return self._decoded_header

        self._decoded_header = {key.decode(): value.decode() for key, value in self._raw_headers}
        return self._decoded_header

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
        if hasattr(self, "_query"):
            return self._query

        query_str = self._raw_query.decode()
        self._query = dict(parse_qsl(query_str))
        return self._query

    def get(self, key: str, default: typing.Any = None) -> str:
        try:
            return self.items()[key]
        except KeyError:
            return default


class FormData:
    pass
