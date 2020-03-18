import pytest
import tempfile

from alicorn.staticfiles import StaticFiles


@pytest.mark.asyncio
async def test_staticfiles(app, client, tmpdir):
    CONTENT = b"xxxx"

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix='.png', delete=False)
    temp.write(CONTENT)
    temp.close()

    directory = f"/{str(tmpdir)}"
    imagename = temp.name.split("/")[-1]

    statics = StaticFiles(path="/static", directory=directory)
    app.mount(statics)

    res = await client.get(f"/static/{imagename}")
    assert res.content == CONTENT


@pytest.mark.asyncio
async def test_post_method(app, client, tmpdir):
    CONTENT = b"xxxx"

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix='.png', delete=False)
    temp.write(CONTENT)
    temp.close()

    directory = f"/{str(tmpdir)}"
    imagename = temp.name.split("/")[-1]

    statics = StaticFiles(path="/static", directory=directory)
    app.mount(statics)

    res = await client.post(f"/static/{imagename}")
    assert res.status_code == 405


@pytest.mark.asyncio
async def test_missing_file(app, client, tmpdir):
    directory = f"/{str(tmpdir)}"

    statics = StaticFiles(path="/static", directory=directory)
    app.mount(statics)

    res = await client.get(f"/static/404.png")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_missing_directory(app, client, tmpdir):
    directory = f"/{str(tmpdir)}"

    statics = StaticFiles(path="/static", directory=directory)
    app.mount(statics)

    res = await client.get(f"/static/sub/404.png")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_configured_with_file(app, client, tmpdir):
    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix='.png', delete=False)
    temp.write(b"xxxx")
    temp.close()

    with pytest.raises(RuntimeError) as exc_info:
        statics = StaticFiles(path="/static", directory=temp.name)

    assert "is not a directory" in str(exc_info.value)


@pytest.mark.asyncio
async def test_head_method(app, client, tmpdir):
    CONTENT = b"xxxx"

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix='.png', delete=False)
    temp.write(CONTENT)
    temp.close()

    directory = f"/{str(tmpdir)}"
    imagename = temp.name.split("/")[-1]

    statics = StaticFiles(path="/static", directory=directory)
    app.mount(statics)

    res = await client.head(f"/static/{imagename}")

    assert res.status_code == 200
    assert res.content == b""
    assert res.headers["content-length"] == str(len(CONTENT))


@pytest.mark.asyncio
async def test_304_with_etag_match(app, client, tmpdir):
    CONTENT = b"xxxx"

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix='.png', delete=False)
    temp.write(CONTENT)
    temp.close()

    directory = f"/{str(tmpdir)}"
    imagename = temp.name.split("/")[-1]

    statics = StaticFiles(path="/static", directory=directory)
    app.mount(statics)

    first_res = await client.get(f"/static/{imagename}")
    first_etag = first_res.headers["etag"]

    assert first_res.status_code == 200

    second_res = await client.get(f"/static/{imagename}", headers={"if-none-match": first_etag})

    assert second_res.status_code == 304
    assert second_res.content == b""


@pytest.mark.asyncio
async def test_304_last_modified_compare_last_request(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_static_html(app, client, tmpdir):
    pass

