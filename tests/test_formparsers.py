import pytest
import tempfile

from yaat.responses import JSONResponse


class ForceMultipartRequest(dict):
    def __bol__(self):
        return True


FORCE_MULTIPART_REQ = ForceMultipartRequest()


@pytest.mark.asyncio
async def test_read_body(app, client):
    @app.route("/", methods=["POST"])
    async def handler(request):
        await request.body()
        form = await request.form()
        response_data = dict(form)
        return JSONResponse(response_data)

    res = await client.post("/", data={"abc": "123"})
    assert res.json() == {"abc": "123"}


@pytest.mark.asyncio
async def test_data(app, client):
    @app.route("/", methods=["POST"])
    async def handler(request):
        form = await request.form()
        response_data = dict(form)
        return JSONResponse(response_data)

    res = await client.post(
        "/", data={"abc": "123"}, files=FORCE_MULTIPART_REQ
    )
    assert res.json() == {"abc": "123"}


@pytest.mark.asyncio
async def test_upload_files(app, client, tmpdir):
    CONTENT = b"<file_content>"

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix=".txt", delete=False)
    temp.write(CONTENT)
    temp.close()
    filename = temp.name.split("/")[-1]

    @app.route("/", methods=["POST"])
    async def handler(request):
        form = await request.form()
        upload = form.get("test")

        response_data = {
            "filename": upload.name,
            "content": (await upload.read()).decode("utf-8"),
            "content_type": upload.content_type,
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
    temp1 = tempfile.NamedTemporaryFile(
        dir=tmpdir, suffix=".txt", delete=False
    )
    temp1.write(b"<file_content>")
    temp1.close()
    file1 = temp1.name.split("/")[-1]

    temp2 = tempfile.NamedTemporaryFile(
        dir=tmpdir, suffix=".png", delete=False
    )
    temp2.write(b"<image>")
    temp2.close()
    file2 = temp2.name.split("/")[-1]

    @app.route("/", methods=["POST"])
    async def handler(request):
        form = await request.form()
        upload1 = form.get("test1")
        upload2 = form.get("test2")

        response_data = {
            "upload1": {
                "filename": upload1.name,
                "content": (await upload1.read()).decode("utf-8"),
                "content_type": upload1.content_type,
            },
            "upload2": {
                "filename": upload2.name,
                "content": (await upload2.read()).decode("utf-8"),
                "content_type": upload2.content_type,
            },
        }

        return JSONResponse(response_data)

    with open(temp1.name, "rb") as f1, open(temp2.name, "rb") as f2:
        res = await client.post("/", files={"test1": f1, "test2": f2})
        assert res.json() == {
            "upload1": {
                "filename": file1,
                "content": "<file_content>",
                "content_type": "text/plain",
            },
            "upload2": {
                "filename": file2,
                "content": "<image>",
                "content_type": "image/png",
            },
        }


@pytest.mark.asyncio
async def test_multi_items(app, client, tmpdir):
    temp1 = tempfile.NamedTemporaryFile(
        dir=tmpdir, suffix=".txt", delete=False
    )
    temp1.write(b"<file_content>")
    temp1.close()
    file1 = temp1.name.split("/")[-1]

    temp2 = tempfile.NamedTemporaryFile(
        dir=tmpdir, suffix=".png", delete=False
    )
    temp2.write(b"<image>")
    temp2.close()
    file2 = temp2.name.split("/")[-1]

    @app.route("/", methods=["POST"])
    async def handler(request):
        form = await request.form()

        data1 = form.get("abc")
        upload1 = form.get("test1")
        upload2 = form.get("test2")

        response_data = {
            "data": data1,
            "upload1": {
                "filename": upload1.name,
                "content": (await upload1.read()).decode("utf-8"),
                "content_type": upload1.content_type,
            },
            "upload2": {
                "filename": upload2.name,
                "content": (await upload2.read()).decode("utf-8"),
                "content_type": upload2.content_type,
            },
        }

        return JSONResponse(response_data)

    with open(temp1.name, "rb") as f1, open(temp2.name, "rb") as f2:
        res = await client.post(
            "/", data={"abc": "123"}, files={"test1": f1, "test2": f2}
        )
        assert res.json() == {
            "data": "123",
            "upload1": {
                "filename": file1,
                "content": "<file_content>",
                "content_type": "text/plain",
            },
            "upload2": {
                "filename": file2,
                "content": "<image>",
                "content_type": "image/png",
            },
        }


@pytest.mark.asyncio
async def test_multipart_request_mixed_files_and_data(app, client, tmpdir):
    @app.route("/", methods=["POST"])
    async def handler(request):
        form = await request.form()

        data1 = form.get("abc")
        data2 = form.get("xyz")
        upload1 = form.get("file")

        response_data = {
            "abc": data1,
            "xyz": data2,
            "upload": {
                "filename": upload1.name,
                "content": (await upload1.read()).decode("utf-8"),
                "content_type": upload1.content_type,
            },
        }
        return JSONResponse(response_data)

    res = await client.post(
        "/",
        data=(
            # data 1
            b"--XXXXXXXXXX\r\n"
            b'Content-Disposition: form-data; name="abc"\r\n\r\n'
            b"123\r\n"
            # data 2
            b"--XXXXXXXXXX\r\n"
            b'Content-Disposition: form-data; name="xyz"\r\n\r\n'
            b"456\r\n"
            # file upload
            b"--XXXXXXXXXX\r\n"
            b'Content-Disposition: form-data; name="file"; filename="file.txt"\r\n'
            b"Content-Type: text/plain\r\n\r\n"
            b"<file_content>\r\n"
            b"--XXXXXXXXXX--\r\n"
        ),
        headers={"Content-Type": "multipart/form-data; boundary=XXXXXXXXXX"},
    )

    assert res.json() == {
        "abc": "123",
        "xyz": "456",
        "upload": {
            "filename": "file.txt",
            "content": "<file_content>",
            "content_type": "text/plain",
        },
    }


@pytest.mark.asyncio
async def test_multipart_with_chartset_for_filename(app, client):
    @app.route("/", methods=["POST"])
    async def handler(request):
        form = await request.form()
        upload = form.get("file")

        response_data = {
            "filename": upload.name,
            "content": (await upload.read()).decode("utf-8"),
            "content_type": upload.content_type,
        }
        return JSONResponse(response_data)

    res = await client.post(
        "/",
        data=(
            # file
            b"--XXXXXXXXXX\r\n"
            b'Content-Disposition: form-data; name="file"; filename="\xe6\x96\x87\xe6\x9b\xb8.txt"\r\n'
            b"Content-Type: text/plain\r\n\r\n"
            b"<file_content>\r\n"
            b"--XXXXXXXXXX--\r\n"
        ),
        headers={
            "Content-Type": "multipart/form-data; charset=utf-8; boundary=XXXXXXXXXX"
        },
    )

    assert res.json() == {
        "filename": "文書.txt",
        "content": "<file_content>",
        "content_type": "text/plain",
    }


@pytest.mark.asyncio
async def test_multipart_without_charset_for_filename(app, client):
    @app.route("/", methods=["POST"])
    async def handler(request):
        form = await request.form()
        upload = form.get("file")

        response_data = {
            "filename": upload.name,
            "content": (await upload.read()).decode("utf-8"),
            "content_type": upload.content_type,
        }
        return JSONResponse(response_data)

    res = await client.post(
        "/",
        data=(
            # file
            b"--XXXXXXXXXX\r\n"
            b'Content-Disposition: form-data; name="file"; filename="\xe6\x96\x87\xe6\x9b\xb8.txt"\r\n'
            b"Content-Type: text/plain\r\n\r\n"
            b"<file_content>\r\n"
            b"--XXXXXXXXXX--\r\n"
        ),
        headers={"Content-Type": "multipart/form-data; boundary=XXXXXXXXXX"},
    )

    assert res.json() == {
        "filename": "文書.txt",
        "content": "<file_content>",
        "content_type": "text/plain",
    }


@pytest.mark.asyncio
async def test_multipart_with_encoded_value(app, client):
    @app.route("/", methods=["POST"])
    async def handler(request):
        form = await request.form()
        value = form.get("value")
        return JSONResponse({"value": value})

    res = await client.post(
        "/",
        data=(
            b"--XXXXXXXXXX\r\n"
            b"Content-Disposition: form-data; "
            b'name="value"\r\n\r\n'
            b"H\xe9llo World\r\n"
            b"--XXXXXXXXXX--\r\n"
        ),
        headers={
            "Content-Type": "multipart/form-data; charset=utf-8; boundary=XXXXXXXXXX"
        },
    )

    assert res.json() == {"value": "Héllo World"}


@pytest.mark.asyncio
async def test_urlencoding(app, client, tmpdir):
    @app.route("/", methods=["POST"])
    async def handler(request):
        form = await request.form()
        return JSONResponse(dict(form))

    res = await client.post(
        "/", data={"abc": "hello mars!", "hello world": "hi!"}
    )
    assert res.json() == {
        "abc": "hello mars!",
        "hello world": "hi!",
    }


@pytest.mark.asyncio
async def test_no_request_data(app, client, tmpdir):
    @app.route("/", methods=["POST"])
    async def handler(request):
        form = await request.form()
        return JSONResponse(dict(form))

    res = await client.post("/")
    assert res.json() == {}


@pytest.mark.asyncio
async def test_urlencoded_multi_field_reads_body(app, client, tmpdir):
    @app.route("/", methods=["POST"])
    async def handler(request):
        await request.body()
        form = await request.form()
        return JSONResponse(dict(form))

    res = await client.post(
        "/", data={"abc": "hello mars!", "hello world": "hi!"}
    )
    assert res.json() == {
        "abc": "hello mars!",
        "hello world": "hi!",
    }


@pytest.mark.asyncio
async def test_multipart_multi_field_reads_body(app, client, tmpdir):
    @app.route("/", methods=["POST"])
    async def handler(request):
        await request.body()
        form = await request.form()
        return JSONResponse(dict(form))

    res = await client.post(
        "/",
        data={"abc": "hello mars!", "hello world": "hi!"},
        files=FORCE_MULTIPART_REQ,
    )
    assert res.json() == {
        "abc": "hello mars!",
        "hello world": "hi!",
    }
