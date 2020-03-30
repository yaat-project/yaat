import enum
import json
import typing

from .requests import HTTPConnection
from .types import Message, Scope, Receive, Send


# CONSTANTS
class WebSocketStates(enum.Enum):
    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2

class WebSocketMessages:
    ACCEPT = "websocket.accept"
    CONNECT = "websocket.connect"
    DISCONNECT = "websocket.disconnect"
    SEND = "websocket.send"
    RECEIVE = "websocket.receive"
    CLOSE = "websocket.close"


class WebSocketDisconnect(Exception):
    def __init__(self, code: int = 1000):
        self.code = code

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name} (Status Code: {self.code!r})"

    def __str__(self) -> str:
        return f"WebSocket Disconnected with ({self.code!r})"


class WebSocket(HTTPConnection):
    def __init__(self, scope: Scope, receive: Receive, send: Send):
        super().__init__(scope)
        assert scope["type"] == "websocket"

        self._receive = receive
        self._send = send
        self.client_state = WebSocketStates.CONNECTING
        self.application_state = WebSocketStates.CONNECTING

    async def receive(self) -> Message:
        """
        Receive ASGI websocket message
        """
        if self.client_state == WebSocketStates.CONNECTING:
            message = await self._receive()
            assert message["type"] == WebSocketMessages.CONNECT
            self.client_state = WebSocketStates.CONNECTED
            return message

        elif self.client_state == WebSocketStates.CONNECTED:
            message = await self._receive()
            message_type = message["type"]
            assert message_type in {WebSocketMessages.RECEIVE, WebSocketMessages.DISCONNECT}
            if message_type == WebSocketMessages.DISCONNECT:
                self.cleint_state = WebSocketStates.DISCONNECTED
            return message

        else:
            raise RuntimeError("Cannot 'receive' when disconnected")

    async def send(self, message: Message):
        """
        Send ASGI websocket message
        """
        if self.application_state == WebSocketStates.CONNECTING:
            message_type = message["type"]
            assert message_type in {WebSocketMessages.ACCEPT, WebSocketMessages.CLOSE}

            if message_type == WebSocketMessages.CLOSE:
                self.application_state = WebSocketStates.DISCONNECTED
            else:
                self.application_state = WebSocketStates.CONNECTED
            await self._send(message)

        elif self.application_state == WebSocketStates.CONNECTED:
            message_type = message["type"]
            assert message_type in {WebSocketMessages.SEND, WebSocketMessages.CLOSE}
            if message_type == WebSocketMessages.CLOSE:
                self.application_state = WebSocketStates.DISCONNECTED
            await self._send(message)

        else:
            raise RuntimeError("Cannot 'send' when disconnected")


    # Accept/Close connections
    async def accept(self, subprotocol: str = None):
        if self.client_state == WebSocketStates.CONNECTING:
            await self.receive()
        await self.send({"type": WebSocketMessages.ACCEPT, "subprotocol": subprotocol})

    async def close(self, code: int = 1000):
        # Websocket status codes
        # https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent#Status_codes
        await self.send({"type": WebSocketMessages.CLOSE, "code": code})


    # Sending methods
    async def send_text(self, data: str):
        await self.send({"type": WebSocketMessages.SEND, "text": data})

    async def send_bytes(self, data: bytes):
        await self.send({"type": WebSocketMessages.SEND, "bytes": data})

    async def send_json(self, data: typing.Any, mode: str = "text"):
        assert mode in ["text", "binary"]
        raw = json.dumps(data)

        if mode == "text":
            await self.send({"type": "websocket.send", "text": raw})
        else:
            await self.send({"type": "websocket.send", "bytes": raw.encode("utf-8")})


    # Receiving methods
    async def receive_text(self) -> str:
        assert self.application_state == WebSocketStates.CONNECTED
        message = await self.receive()
        self.__raise_if_disconnected(message)
        return message["text"]

    async def receive_bytes(self) -> bytes:
        assert self.application_state == WebSocketState.CONNECTED
        message = await self.receive()
        self.__raise_if_disconnected(message)
        return message["bytes"]

    async def receive_json(self, mode: str = "text") -> typing.Any:
        assert mode in ["text", "binary"]
        assert self.application_state == WebSocketState.CONNECTED
        message = await self.receive()
        self.__raise_if_disconnected(message)

        text = message["text"] if mode == "text" else message["bytes"].decode("utf-8")
        return json.loads(text)


    # Exception handlers
    def __raise_if_disconnected(self, message: Message):
        if message["type"] == WebSocketMessages.DISCONNECT:
            raise WebSocketDisconnect(message["code"])
