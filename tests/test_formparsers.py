import pytest


@pytest.mark.asyncio
async def test_file_upload(app, client):
    pass


@pytest.mark.asyncio
async def test_multi_items(app, client):
    pass


@pytest.mark.asyncio
async def test_read_body(app, client):
    pass


@pytest.mark.asyncio
async def test_multipart_request_data(app, client):
    pass


@pytest.mark.asyncio
async def test_multipart_request_files(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_multipart_request_files_with_content_type(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_multipart_request_multiple_files(app, client, tmpdir):
    pass


@pytest.mark.asyncio
async def test_multiple_items(app, client, tmpdir):
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
