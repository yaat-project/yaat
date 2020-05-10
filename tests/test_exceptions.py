import pytest

from yaat.exceptions import HTTPException
from yaat.responses import TextResponse


@pytest.mark.asyncio
async def test_exceptions_not_acceptable(app, client):
    @app.route("/")
    async def handler(request):
        raise HTTPException(status_code=406)

    res = await client.get("/")
    assert res.status_code == 406


@pytest.mark.asyncio
async def test_exceptions_not_found(app, client):
    @app.route("/")
    async def handler(request):
        raise HTTPException(status_code=404)

    res = await client.get("/")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_exceptions_method_not_allow(app, client):
    @app.route("/")
    async def handler(request):
        raise HTTPException(status_code=405)

    res = await client.get("/")
    assert res.status_code == 405


@pytest.mark.asyncio
async def test_exceptions_not_modified(app, client):
    @app.route("/")
    async def handler(request):
        raise HTTPException(status_code=304)

    res = await client.get("/")
    assert res.status_code == 304


@pytest.mark.asyncio
async def test_exceptions_internal_server_error(app, client):
    @app.route("/")
    async def handler(request):
        raise RuntimeError("Ooooff")

    res = await client.get("/")
    assert res.status_code == 500
