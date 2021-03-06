import pytest

from yaat.middleware import BaseMiddleware
from yaat.requests import Request
from yaat.responses import TextResponse, Response


class CustomMiddleware(BaseMiddleware):
    async def process_request(self, request: Request):
        request.scope["server"] = "modifiedserver"

    async def process_response(self, response: Response):
        response.body = b"modified body"


@pytest.mark.asyncio
async def test_base_middleware_plain_text_response(app, client):
    app.add_middleware(CustomMiddleware)

    @app.route("/")
    async def handler(request):
        assert request.scope["server"] == "modifiedserver"
        return TextResponse("hello world")

    res = await client.get("/")

    assert res.text == "modified body"
