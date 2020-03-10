import pytest
import tempfile

from alicorn import Alicorn
from alicorn.responses import (
    PlainTextResponse,
)


@pytest.mark.asyncio
async def test_no_method_specify(app, client):
    RESPONSE = "hello world"

    @app.route("/text")
    async def handler(request):
        return PlainTextResponse(content=RESPONSE)

    res = await client.get("/text")

    assert res.text == RESPONSE


@pytest.mark.asyncio
async def test_get_method(app, client):
    pass


@pytest.mark.asyncio
async def test_post_method(app, client):
    pass



@pytest.mark.asyncio
async def test_put_method(app, client):
    pass


@pytest.mark.asyncio
async def test_patch_method(app, client):
    pass


@pytest.mark.asyncio
async def test_delete_method(app, client):
    pass


@pytest.mark.asyncio
async def test_url_param(app, client):
    pass


@pytest.mark.asyncio
async def test_class_based_view(app, client):
    pass


@pytest.mark.asyncio
async def test_method_register(app, client):
    pass


@pytest.mark.asyncio
async def test_mount_sub_application(app, client):
    pass

