import pytest

from yaat import Yaat
from yaat.responses import JSONResponse, PlainTextResponse


@pytest.mark.asyncio
async def test_request_url(app, client):
    @app.route("/")
    async def handler(request):
        data = {"method": request.method, "url": str(request.url)}
        return JSONResponse(data)

    res = await client.get("/#anchor")
    res_data = res.json()

    assert res_data["method"] == "GET"
    assert res_data["url"] == 'http://testserver/'


@pytest.mark.asyncio
async def test_request_query_params(app, client):
    @app.route("/")
    async def handler(request):
        query_params = dict(request.query_params)
        return JSONResponse(query_params)

    res = await client.get("/?param=你好，世界")
    res_data = res.json()

    assert res_data["param"] == "你好，世界"


@pytest.mark.asyncio
async def test_request_header(app, client):
    @app.route("/")
    async def handler(request):
        headers = dict(request.headers)
        return JSONResponse(headers=headers)

    res = await client.get("/", headers={'host': 'example.com'})

    assert res.headers["host"] == "example.com"


@pytest.mark.asyncio
async def test_request_client(app, client):
    @app.route("/")
    async def handler(request):
        client = request.client
        return JSONResponse({
            "host": client.host,
            "port": client.port
        })

    res = await client.get("/")
    res_data = res.json()

    assert res_data["host"] == '127.0.0.1'
    assert res_data["port"] == 123


@pytest.mark.asyncio
async def test_request_body(app, client):
    @app.route("/")
    async def handler(request):
        body = await request.body()
        return JSONResponse({"body": body.decode()})

    res = await client.post("/", data={"hello": "world"})

    assert res.content == b'{"body":"hello=world"}'


@pytest.mark.asyncio
async def test_request_json(app, client):
    DATA = {"hello": "world", "hello_chinese": "世界"}
    
    @app.route("/")
    async def handler(request):
        json = await request.json()
        return JSONResponse(json)

    res = await client.post("/", json=DATA)

    assert res.json() == DATA


@pytest.mark.asyncio
async def test_request_form_urlencode(app, client):
    DATA = {"hello": "world", "hello_chinese": "世界"}
    
    @app.route("/")
    async def handler(request):
        form = await request.form()
        form = dict(form)
        return JSONResponse(form)

    res = await client.post("/", data=DATA)

    assert res.json() == DATA


@pytest.mark.asyncio
async def test_request_cookies(app, client):
    COOKIE_VALUE = "Hello cookie!"

    @app.route("/")
    async def handler(request):
        mycookie = request.cookies.get("mycookie")

        if mycookie:
            res = PlainTextResponse(mycookie)
        else:
            res = PlainTextResponse("Hello world!")
            res.set_cookie("mycookie", COOKIE_VALUE)

        return res

    res = await client.get("/")
    assert res.text == "Hello world!"

    res = await client.get("/")
    assert res.text == COOKIE_VALUE
