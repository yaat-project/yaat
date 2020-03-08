import pytest

from alicorn import Alicorn
from alicorn.responses import (
    JSONResponse,
    PlainTextResponse,
)


@pytest.mark.asyncio
async def test_plain_text_response(app, client):
    RESPONSE = "hello world"

    @app.route("/text")
    async def plain_text_handler(request):
        return PlainTextResponse(content=RESPONSE)

    res = await client.get("/text")

    assert res.text == RESPONSE
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_json_response(app, client):
    RESPONSE = {"hello": "world"}

    @app.route("/json")
    async def json_handler(request):
        return JSONResponse(content=RESPONSE)

    res = await client.get("/json")

    assert res.json() == RESPONSE
    assert res.status_code == 200


