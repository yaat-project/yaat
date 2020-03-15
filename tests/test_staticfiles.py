import pytest

from alicorn.staticfiles import StaticFiles


@pytest.mark.asyncio
async def test_staticfiles(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_post_method(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_missing_file(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_missing_directory(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_configured_with_file(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_breaking_out_of_directory(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_head_method(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_304_with_etag_match(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_304_last_modified_compare_last_request(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_static_html(app, client, tmpdir):
    pass

