from copy import deepcopy
import pytest

from yaat.middleware import CorsMiddleware
from yaat.requests import Request
from yaat.responses import TextResponse


@pytest.mark.asyncio
async def test_allow_all(app, client):
    app.add_middleware(
        CorsMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-My-Custom-Header"],
        allow_credentials=True,
    )

    @app.route("/")
    async def handler(request):
        return TextResponse("hello world")

    # preflight request
    res = await client.options("/", headers={
        "Origin": "http://testserver.com",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-Example-Header",
    })
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == "*"
    assert res.headers["access-control-allow-headers"] == "X-Example-Header"


@pytest.mark.asyncio
async def test_allow_specific_origin(app, client):
    app.add_middleware(
        CorsMiddleware,
        allow_origins=["http://testserver.com"],
        allow_headers=["X-My-Custom-Header"],
    )

    @app.route("/")
    async def handler(request):
        return TextResponse("hello world")

    # preflight request
    res = await client.options("/", headers={
        "Origin": "http://testserver.com",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-My-Custom-Header",
    })
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == "http://testserver.com"
    assert "X-My-Custom-Header" in res.headers["access-control-allow-headers"].split(", ")

    # simple request
    res = await client.get("/", headers= {"Origin": "http://testserver.com"})
    assert res.status_code == 200
    assert res.text == "hello world"
    assert res.headers["access-control-allow-origin"] == "http://testserver.com"

    # non-cors request
    res = await client.get("/")
    assert res.status_code == 200
    assert res.text == "hello world"
    assert "access-control-allow-origin" not in res.headers


@pytest.mark.asyncio
async def test_disallowed_preflight(app, client):
    app.add_middleware(
        CorsMiddleware,
        allow_origins=["http://testserver.com"],
        allow_headers=["X-My-Custom-Header"],
    )

    @app.route("/")
    async def handler(request):
        return TextResponse("hello world")

    # preflight request
    res = await client.options("/", headers={
        "Origin": "http://invalid-server.org",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-Header",
    })
    assert res.status_code == 400
    assert res.text == "Disallowed cors Origin, Method, Headers"


@pytest.mark.asyncio
async def test_credentialed_return_specific_origin(app, client):
    app.add_middleware(CorsMiddleware, allow_origins=["*"])

    @app.route("/")
    async def handler(request):
        return TextResponse("hello world")

    res = await client.get("/", headers={
        "Origin": "http://testserver.com",
        "Cookie": "cookie=monster"
    })
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == "http://testserver.com"


@pytest.mark.asyncio
async def test_vary_headers_origin_default(app, client):
    app.add_middleware(CorsMiddleware, allow_origins=["http://testserver.com"])

    @app.route("/")
    async def handler(request):
        return TextResponse("hello world")

    res = await client.get("/", headers={"Origin": "http://testserver.com"})
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == "http://testserver.com"
    assert res.headers["vary"] == "Origin"


@pytest.mark.asyncio
async def test_vary_headers_set(app, client):
    app.add_middleware(CorsMiddleware, allow_origins=["http://testserver.com"])

    @app.route("/")
    async def handler(request):
        return TextResponse("hello world", headers={"Vary": "User-Agent"})

    res = await client.get("/", headers={"Origin": "http://testserver.com"})
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == "http://testserver.com"
    assert res.headers["vary"] == "User-Agent, Origin"


@pytest.mark.asyncio
async def test_allow_origin_regex(app, client):
    app.add_middleware(
        CorsMiddleware,
        allow_origin_regex="http://.*.com",
        allow_headers=["X-My-Custom-Header"],
    )

    @app.route("/")
    async def handler(request):
        return TextResponse("hello world")

    # preflight request
    res = await client.options("/", headers={
        "Origin": "http://testserver.com",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-My-Custom-Header",
    })
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == "http://testserver.com"
    assert "X-My-Custom-Header" in res.headers["access-control-allow-headers"].split(", ")

    # disallowed preflight request
    res = await client.options("/", headers={
        "Origin": "http://testserver.org",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-My-Custom-Header",
    })
    assert res.status_code == 400
    assert res.text == "Disallowed cors Origin"
    assert "access-control-allow-origin" not in res.headers

    # simple request
    res = await client.get("/", headers={"Origin": "http://testserver.com"})
    assert res.status_code == 200
    assert res.text == "hello world"
    assert res.headers["access-control-allow-origin"] == "http://testserver.com"

    # disallowed simple request
    res = await client.get("/", headers={"Origin": "http://testserver.org"})
    assert res.status_code == 200
    assert res.text == "hello world"
    assert "access-control-allow-origin" not in res.headers
