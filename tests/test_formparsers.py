import pytest
import tempfile

from alicorn.responses import JSONResponse


class ForceMultipart(dict):
    def __bol__(self):
        return True

FORCE_MULTIPART = ForceMultipart()


@pytest.mark.asyncio
async def test_read_body(app, client):
    @app.route("/")
    async def handler(request):
        await request.body()
        form = await request.form()
        response_data = dict(form)
        return JSONResponse(response_data)

    res = await client.post("/", data={"abc": "123"})
    assert res.json() == {"abc": "123"}


@pytest.mark.asyncio
async def test_data(app, client):
    @app.route("/")
    async def handler(request):
        form = await request.form()
        response_data = dict(form)
        return JSONResponse(response_data)

    res = await client.post("/", data={"abc": "123"}, files=FORCE_MULTIPART)
    assert res.json() == {"abc": "123"}


@pytest.mark.asyncio
async def test_upload_files(app, client, tmpdir):
    CONTENT = b"<file_content>"

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix='.txt', delete=False)
    temp.write(CONTENT)
    temp.close()
    filename = temp.name.split("/")[-1]

    @app.route("/")
    async def handler(request):
        form = await request.form()
        upload = form.get("test")

        response_data = {
            "filename": upload.name,
            "content": (await upload.read()).decode("utf-8"),
            "content_type": upload.content_type
        }        

        return JSONResponse(response_data)

    with open(temp.name, "rb") as f:
        res = await client.post("/", files={"test": f})
        assert res.json() == {
            "filename": filename,
            "content_type": "text/plain",
            "content": "<file_content>",
        }


@pytest.mark.asyncio
async def test_multiple_upload_files(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_multi_items(app, client):
    pass


@pytest.mark.asyncio
async def test_multipart_request_mixed_files_and_data(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_multipart_with_chartset_for_filename(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_multipart_without_charset_for_filename(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_multipart_with_encoded_value(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_urlencoded_data(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_no_request_data(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_urlencoded_multi_field_reads_body(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_multipart_multi_field_reads_body(app, client, tmpdir):
    pass
