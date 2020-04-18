import pytest
import tempfile

from yaat.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    TextResponse,
    RedirectResponse,
    Response,
    StreamResponse,
)


@pytest.mark.asyncio
async def test_plain_text_response(app, client):
    RESPONSE = "hello world"

    @app.route("/")
    async def handler(request):
        return TextResponse(content=RESPONSE)

    res = await client.get("/")

    assert res.text == RESPONSE
    assert "text/plain" in res.headers["content-type"]


@pytest.mark.asyncio
async def test_bytes_response(app, client):
    RESPONSE = b"bytes"

    @app.route("/")
    async def handler(request):
        return Response(content=RESPONSE, media_type="image/jpg")

    res = await client.get("/")

    assert res.content == RESPONSE
    assert res.headers["content-type"] == "image/jpg"


@pytest.mark.asyncio
async def test_json_response(app, client):
    RESPONSE = {"hello": "world"}

    @app.route("/")
    async def handler(request):
        return JSONResponse(content=RESPONSE)

    res = await client.get("/")

    assert res.json() == RESPONSE
    assert res.headers["content-type"] == "application/json"


@pytest.mark.asyncio
async def test_json_none_response(app, client):
    RESPONSE = None

    @app.route("/")
    async def handler(request):
        return JSONResponse(content=RESPONSE)

    res = await client.get("/")

    assert res.json() == RESPONSE
    assert res.headers["content-type"] == "application/json"


@pytest.mark.asyncio
async def test_html_response(app, client):
    RESPONSE = "<h1>Hello World</h1>"

    @app.route("/")
    async def handler(request):
        return HTMLResponse(content=RESPONSE)

    res = await client.get("/")

    assert res.text == RESPONSE
    assert "text/html" in res.headers["content-type"]


@pytest.mark.asyncio
async def test_redirect_response(app, client):
    RESPONSE = "This is redirected."
    REDIRECTED_URL = "/text"

    @app.route("/")
    async def redirect_handler(request):
        return RedirectResponse("/text")

    @app.route(REDIRECTED_URL)
    async def handler(request):
        return TextResponse(content=RESPONSE)

    res = await client.get("/")

    assert str(res.url).endswith(REDIRECTED_URL)
    assert res.text == RESPONSE
    assert "text/plain" in res.headers["content-type"]


@pytest.mark.asyncio
async def test_file_response(app, client, tmpdir):
    CONTENT = b"xxxx"

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix=".png", delete=False)
    temp.write(CONTENT)
    temp.close()

    @app.route("/")
    async def handler(request):
        # temp.name already has file path, so put path = ''
        return FileResponse(path=temp.name)

    res = await client.get("/")

    assert res.content == CONTENT
    assert "image/png" in res.headers["content-type"]


@pytest.mark.asyncio
async def test_headers_replace(app, client):
    @app.route("/")
    async def handler(request):
        headers = {"header-1": "abc", "header-2": "def"}
        response = TextResponse(content="hello world", headers=headers)
        response.headers["header-2"] = "xyz"
        return response

    res = await client.get("/")

    assert res.headers["header-1"] == "abc"
    assert res.headers["header-2"] == "xyz"


@pytest.mark.asyncio
async def test_response_status_code(app, client):
    @app.route("/")
    async def handler(request):
        return Response(status_code=204)

    res = await client.get("/")

    assert res.status_code == 204


@pytest.mark.asyncio
async def test_file_response_directory_error(app, client, tmpdir):
    @app.route("/")
    async def handler(request):
        return FileResponse(path=tmpdir + "/notfound/example.txt")

    res = await client.get("/")

    assert res.status_code == 404


@pytest.mark.asyncio
async def test_file_response_missing_file(app, client, tmpdir):
    @app.route("/")
    async def handler(request):
        return FileResponse(path="404.txt")

    res = await client.get("/")

    assert res.status_code == 404


@pytest.mark.asyncio
async def test_set_cookie(app, client):
    @app.route("/")
    async def handler(request):
        response = Response(content="hello world")
        response.set_cookie(
            key="mycookie",
            value="myvalue",
            max_age=1800,
            expires=1800,
            path="/",
            domain="localhost",
            secure=False,
            httponly=False,
            samesite="none",
        )
        return response

    res = await client.get("/")

    assert "mycookie=myvalue" in res.headers["set-cookie"]


@pytest.mark.asyncio
async def test_delete_cookie(app, client):
    @app.route("/")
    async def handler(request):
        response = Response(content="hello world")
        response.delete_cookie(key="mycookie")
        return response

    res = await client.get("/")

    assert "mycookie" in res.headers["set-cookie"]
    assert not res.cookies.get("mycookie")


@pytest.mark.asyncio
async def test_populate_headers(app, client):
    CONTENT = "hello world"

    @app.route("/")
    async def handler(request):
        return Response(content=CONTENT, headers={}, media_type="text/html")

    res = await client.get("/")

    assert res.text == CONTENT
    assert res.headers["content-length"] == str(len(CONTENT))
    assert "text/html" in res.headers["content-type"]


@pytest.mark.asyncio
async def test_head_method(app, client):
    @app.route("/")
    async def handler(request):
        return TextResponse(content="hello world")

    res = await client.head("/")

    assert res.text == ""


@pytest.mark.asyncio
async def test_stream_response(app, client):
    filled_by_bg_task = ""

    @app.route("/")
    async def handler(request):
        async def get_numbers(min, max):
            for i in range(min, max + 1):
                yield str(i)
                if i != max:
                    yield " + "

        generator = get_numbers(1, 3)
        response = StreamResponse(generator, media_type="text/plain")
        return response

    res = await client.get("/")

    assert res.text == "1 + 2 + 3"
