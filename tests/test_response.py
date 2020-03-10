import pytest
import tempfile

from alicorn import Alicorn
from alicorn.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)


@pytest.mark.asyncio
async def test_plain_text_response(app, client):
    RESPONSE = "hello world"

    @app.route("/text")
    async def handler(request):
        return PlainTextResponse(content=RESPONSE)

    res = await client.get("/text")

    assert res.text == RESPONSE
    assert "text/plain" in res.headers["content-type"]


@pytest.mark.asyncio
async def test_bytes_response(app, client):
    RESPONSE = b"bytes"

    @app.route("/bytes")
    async def handler(request):
        return Response(content=RESPONSE, media_type="image/jpg")

    res = await client.get("/bytes")

    assert res.content == RESPONSE
    assert res.headers["content-type"] == "image/jpg"


@pytest.mark.asyncio
async def test_json_response(app, client):
    RESPONSE = {"hello": "world"}

    @app.route("/json")
    async def handler(request):
        return JSONResponse(content=RESPONSE)

    res = await client.get("/json")

    assert res.json() == RESPONSE
    assert res.headers["content-type"] == "application/json"


@pytest.mark.asyncio
async def test_json_none_response(app, client):
    RESPONSE = None

    @app.route("/json")
    async def handler(request):
        return JSONResponse(content=RESPONSE)

    res = await client.get("/json")

    assert res.json() == RESPONSE
    assert res.headers["content-type"] == "application/json"


@pytest.mark.asyncio
async def test_html_response(app, client):
    RESPONSE = "<h1>Hello World</h1>"

    @app.route("/html")
    async def handler(request):
        return HTMLResponse(content=RESPONSE)

    res = await client.get("/html")

    assert res.text == RESPONSE
    assert "text/html" in res.headers["content-type"]


@pytest.mark.asyncio
async def test_redirect_response(app, client):
    RESPONSE = "This is redirected."
    REDIRECTED_URL = "/text"

    @app.route("/redirect")
    async def redirect_handler(request):
        return RedirectResponse("/text")

    @app.route(REDIRECTED_URL)
    async def handler(request):
        return PlainTextResponse(content=RESPONSE)

    res = await client.get("/redirect")

    assert str(res.url).endswith(REDIRECTED_URL)
    assert res.text == RESPONSE
    assert "text/plain" in res.headers["content-type"]


@pytest.mark.asyncio
async def test_file_response(app, client, tmpdir):
    CONTENT = b"xxxx"

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix='.png', delete=False)
    temp.write(CONTENT)
    temp.close()

    @app.route("/directory")
    async def handler(request):
        # temp.name already has file path, so put path = ''
        return FileResponse(path='', filename=temp.name)

    res = await client.get("/directory")

    assert res.content == CONTENT
    assert "image/png" in res.headers["content-type"]


@pytest.mark.asyncio
async def test_headers_replace(app, client):
    @app.route("/headers")
    async def handler(request):
        headers = {"header-1": "abc", "header-2": "def"}
        response = PlainTextResponse(content="hello world", headers=headers)
        response.headers["header-2"] = "xyz"
        return response

    res = await client.get("/headers")

    assert res.headers["header-1"] == "abc"
    assert res.headers["header-2"] == "xyz"


@pytest.mark.asyncio
async def test_response_status_code(app, client):
    @app.route("/phrase")
    async def handler(request):
        return Response(status_code=204)

    res = await client.get("/phrase")

    assert res.status_code == 204


@pytest.mark.asyncio
async def test_file_response_directory_error(app, client, tmpdir):
    @app.route("/directory")
    async def handler(request):
        return FileResponse(path=tmpdir + "/notfound", filename="example.txt")

    res = await client.get("/directory")

    assert res.status_code == 404


@pytest.mark.asyncio
async def test_file_response_missing_file(app, client, tmpdir):
    @app.route("/file")
    async def handler(request):
        return FileResponse(path=tmpdir, filename="404.txt")

    res = await client.get("/file")

    assert res.status_code == 404


@pytest.mark.asyncio
async def test_set_cookie(app, client):
    pass


@pytest.mark.asyncio
async def test_delete_cookie(app, client):
    pass


@pytest.mark.asyncio
async def test_populate_headers(app, client):
    pass


@pytest.mark.asyncio
async def test_head_method(app, client):
    pass

