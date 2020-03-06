from urllib.parse import parse_qsl
import typing

from .datatypes import Form, Headers


class FormParser:
    def __init__(self, body: bytes):
        self.body = body

    async def parse(self) -> Form:
        body_data = await self.body()
        form_data = [] if body_data.decode() == '' else parse_qsl(body_data)
        form_data = [(item[0].decode(), item[1].decode()) for item in form_data]
        return Form(form_data)


class MultiPartParser:
    def __init__(self, headers: Headers, stream: typing.AsyncGenerator[bytes, None]):
        self.headers = headers
        self.stream = stream
        self.messages = []

    async def parse(self) -> Form:
        return Form()
