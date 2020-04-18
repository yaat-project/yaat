import enum
import json
import typing

from yaat.constants import (
    WebSocketCloseEvent as WsCloseEvent,
    WebSocketMessages as WsMessages,
)
from yaat.exceptions import WebSocketException
from yaat.requests import HTTPConnection
from yaat.typing import Message, Scope, Receive, Send


# CONSTANTS
class WebSocketStates(enum.Enum):
    # To identify whether client/server is connected/disconnected
    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2


class WebSocketDisconnect(Exception):
    def __init__(self, code: int = WsCloseEvent.NORMAL_CLOSURE):
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

        self.__receive = receive
        self.__send = send
        self.client_state = WebSocketStates.CONNECTING
        self.server_state = WebSocketStates.CONNECTING

    async def receive(self) -> Message:
        """
        Receive ASGI websocket message
        """
        if self.client_state == WebSocketStates.CONNECTING:
            message = await self.__receive()
            assert message["type"] == WsMessages.CONNECT
            self.client_state = WebSocketStates.CONNECTED
            return message

        elif self.client_state == WebSocketStates.CONNECTED:
            message = await self.__receive()
            message_type = message["type"]
            assert message_type in {WsMessages.RECEIVE, WsMessages.DISCONNECT}

            if message_type == WsMessages.DISCONNECT:
                self.cleint_state = WebSocketStates.DISCONNECTED
            return message

        else:
            raise WebSocketException("Cannot 'receive' when disconnected")

    async def send(self, message: Message):
        """
        Send ASGI websocket message
        """
        if self.server_state == WebSocketStates.CONNECTING:
            message_type = message["type"]
            assert message_type in {WsMessages.ACCEPT, WsMessages.CLOSE}

            if message_type == WsMessages.CLOSE:
                self.server_state = WebSocketStates.DISCONNECTED
            else:
                self.server_state = WebSocketStates.CONNECTED
            await self.__send(message)

        elif self.server_state == WebSocketStates.CONNECTED:
            message_type = message["type"]
            assert message_type in {WsMessages.SEND, WsMessages.CLOSE}

            if message_type == WsMessages.CLOSE:
                self.server_state = WebSocketStates.DISCONNECTED
            await self.__send(message)

        else:
            raise WebSocketException("Cannot 'send' when disconnected")

    # Accept/Close connections
    async def accept(self, subprotocol: str = None):
        if self.client_state == WebSocketStates.CONNECTING:
            await self.receive()
        await self.send(
            {"type": WsMessages.ACCEPT, "subprotocol": subprotocol}
        )

    async def close(self, code: int = WsCloseEvent.NORMAL_CLOSURE):
        # Websocket status codes
        # https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent#Status_codes
        await self.send({"type": WsMessages.CLOSE, "code": code})

    # Sending methods
    async def send_text(self, data: str):
        await self.send({"type": WsMessages.SEND, "text": data})

    async def send_bytes(self, data: bytes):
        await self.send({"type": WsMessages.SEND, "bytes": data})

    async def send_json(self, data: typing.Any, mode: str = "text"):
        assert mode in ["text", "bytes"]
        raw = json.dumps(data)

        if mode == "text":
            message = {"type": WsMessages.SEND, "text": raw}
        else:
            message = {"type": WsMessages.SEND, "bytes": raw.encode("utf-8")}

        await self.send(message)

    # Receiving methods
    async def receive_text(self) -> str:
        assert self.server_state == WebSocketStates.CONNECTED
        message = await self.receive()
        self.__raise_if_disconnected(message)
        return message["text"]

    async def receive_bytes(self) -> bytes:
        assert self.server_state == WebSocketStates.CONNECTED
        message = await self.receive()
        self.__raise_if_disconnected(message)
        return message["bytes"]

    async def receive_json(self, mode: str = "text") -> typing.Any:
        assert mode in ["text", "bytes"]
        assert self.server_state == WebSocketStates.CONNECTED

        message = await self.receive()
        self.__raise_if_disconnected(message)
        text = (
            message["text"]
            if mode == "text"
            else message["bytes"].decode("utf-8")
        )
        return json.loads(text)

    # Exception handlers
    def __raise_if_disconnected(self, message: Message):
        if message["type"] == WsMessages.DISCONNECT:
            raise WebSocketDisconnect(message["code"])
