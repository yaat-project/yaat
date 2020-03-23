import pytest

from yaat.exceptions import HttpException
from yaat.responses import PlainTextResponse


@pytest.mark.asyncio
async def test_not_acceptable(app, client):
    @app.route("/")
    async def handler(request):
        raise HttpException(status_code=406)

    res = await client.get("/")
    assert res.status_code == 406


@pytest.mark.asyncio
async def test_not_found(app, client):
    @app.route("/")
    async def handler(request):
        raise HttpException(status_code=404)

    res = await client.get("/")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_method_not_allow(app, client):
    @app.route("/")
    async def handler(request):
        raise HttpException(status_code=405)

    res = await client.get("/")
    assert res.status_code == 405


@pytest.mark.asyncio
async def test_not_modified(app, client):
    @app.route("/")
    async def handler(request):
        raise HttpException(status_code=304)

    res = await client.get("/")
    assert res.status_code == 304


@pytest.mark.asyncio
async def test_internal_server_error(app, client):
    @app.route("/")
    async def handler(request):
        raise RuntimeError("Ooooff")

    res = await client.get("/")
    assert res.status_code == 500
