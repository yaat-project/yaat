import os
import pytest
import tempfile
import time

from yaat.staticfiles import StaticFiles


@pytest.mark.asyncio
async def test_staticfiles(app, client, tmpdir):
    CONTENT = b"xxxx"

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix=".png", delete=False)
    temp.write(CONTENT)
    temp.close()

    directory = f"/{str(tmpdir)}"
    imagename = temp.name.split("/")[-1]

    statics = StaticFiles(directory=directory)
    app.mount(statics, "/static")

    res = await client.get(f"/static/{imagename}")
    assert res.content == CONTENT


@pytest.mark.asyncio
async def test_post_method(app, client, tmpdir):
    CONTENT = b"xxxx"

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix=".png", delete=False)
    temp.write(CONTENT)
    temp.close()

    directory = f"/{str(tmpdir)}"
    imagename = temp.name.split("/")[-1]

    statics = StaticFiles(directory=directory)
    app.mount(statics, "/static")

    res = await client.post(f"/static/{imagename}")
    assert res.status_code == 405


@pytest.mark.asyncio
async def test_missing_file(app, client, tmpdir):
    directory = f"/{str(tmpdir)}"

    statics = StaticFiles(directory=directory)
    app.mount(statics, "/static")

    res = await client.get(f"/static/404.png")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_missing_directory(app, client, tmpdir):
    directory = f"/{str(tmpdir)}"

    statics = StaticFiles(directory=directory)
    app.mount(statics, "/static")

    res = await client.get(f"/static/sub/404.png")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_configured_with_file(app, client, tmpdir):
    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix=".png", delete=False)
    temp.write(b"xxxx")
    temp.close()

    with pytest.raises(RuntimeError) as exc_info:
        StaticFiles(directory=temp.name)

    assert "is not a directory" in str(exc_info.value)


@pytest.mark.asyncio
async def test_head_method(app, client, tmpdir):
    CONTENT = b"xxxx"

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix=".png", delete=False)
    temp.write(CONTENT)
    temp.close()

    directory = f"/{str(tmpdir)}"
    imagename = temp.name.split("/")[-1]

    statics = StaticFiles(directory=directory)
    app.mount(statics, "/static")

    res = await client.head(f"/static/{imagename}")

    assert res.status_code == 200
    assert res.content == b""
    assert res.headers["content-length"] == str(len(CONTENT))


@pytest.mark.asyncio
async def test_304_with_etag_match(app, client, tmpdir):
    CONTENT = b"xxxx"

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix=".png", delete=False)
    temp.write(CONTENT)
    temp.close()

    directory = f"/{str(tmpdir)}"
    imagename = temp.name.split("/")[-1]

    statics = StaticFiles(directory=directory)
    app.mount(statics, "/static")

    first_res = await client.get(f"/static/{imagename}")
    first_etag = first_res.headers["etag"]

    assert first_res.status_code == 200

    second_res = await client.get(
        f"/static/{imagename}", headers={"if-none-match": first_etag}
    )

    assert second_res.status_code == 304
    assert second_res.content == b""


@pytest.mark.asyncio
async def test_304_last_modified_compare_last_request(app, client, tmpdir):
    CONTENT = b"xxxx"
    FILE_LAST_MODIFIED_TIME = time.mktime(
        time.strptime("2020-02-02 01:00:00", "%Y-%m-%d %H:%M:%S")
    )

    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix=".png", delete=False)
    temp.write(CONTENT)
    temp.close()

    directory = f"/{str(tmpdir)}"
    imagename = temp.name.split("/")[-1]

    # change the time of created temporary file
    os.utime(temp.name, (FILE_LAST_MODIFIED_TIME, FILE_LAST_MODIFIED_TIME))

    statics = StaticFiles(directory=directory)
    app.mount(statics, "/static")

    # file last modified date < last request
    # means no modification, should get HTTP 304 with empty body
    first_res = await client.get(
        f"/static/{imagename}",
        headers={"if-modified-since": "Mon, 03 Feb 2020 12:00:00 GMT"},
    )
    assert first_res.status_code == 304
    assert first_res.content == b""

    # file last modified date > last request
    # means there are changes, and file need to be sent back
    # should get HTTP 200 with content in body
    second_res = await client.get(
        f"/static/{imagename}",
        headers={"if-modified-since": "Sat, 01 Feb 2020 04:00:00 GMT"},
    )
    assert second_res.status_code == 200
    assert second_res.content == CONTENT


@pytest.mark.asyncio
async def test_static_html(app, client, tmpdir):
    # create html file with name
    named_html = tempfile.NamedTemporaryFile(
        dir=tmpdir, suffix=".html", delete=False
    )
    named_html.write(b"<h1>Hello World</h1>")
    named_html.close()

    # create index html file
    index_html = open(os.path.join(tmpdir, "index.html"), "w+b")
    index_html.write(b"<h1>Index</h1>")
    index_html.close()

    directory = f"/{str(tmpdir)}"
    named_html_file = named_html.name.split("/")[-1]

    statics = StaticFiles(directory=directory, html=True)
    app.mount(statics, "/")

    first_res = await client.get(f"/{named_html_file}")
    assert first_res.status_code == 200
    assert first_res.text == "<h1>Hello World</h1>"

    second_res = await client.get(f"/")
    assert second_res.status_code == 200
    assert second_res.text == "<h1>Index</h1>"

    third_res = await client.get(f"/notfound.html")
    assert third_res.status_code == 404
