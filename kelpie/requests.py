import typing

from .types import Scope, Receive, Send, Message


async def empty_receive() -> Message:
    raise RuntimeError("Receive channel has not been made available")

async def empty_send(message: Message) -> None:
    raise RuntimeError("Send channel has not been made available")


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
    def path(self) -> str:
        return self.scope["path"]

    @property
    def cookie(self) -> typing.Dict[str, str]:
        # TODO: implement getting cookie
        return None

    @property
    def client(self) -> typing.Any:
        host, port = self.scope.get("client") or (None, None)
        # TODO: implemnt datatype and return
        return None

    @property
    def session(self) -> dict:
        # TODO: implemnt session
        return None


class Request(HttpConnection):
    def __init__(
        self,
        scope: Scope,
        receive: Receive = empty_receive,
        send: Send = empty_send,
    ):
        super().__init__(scope)
        self.receive = receive
        self.send = send

    @property
    def method(self) -> str:
        return self.scope["method"]

    @property
    def receive(self) -> Receive:
        return self.__receive

    @receive.setter
    def receive(self, receive: Receive):
        self.__receive = receive

    @property
    def send(self) -> Send:
        return self.__send

    @send.setter
    def send(self, send: Send):
        self.__send = send

    async def body(self) -> bytes:
        return self.send.get("body", b"")
