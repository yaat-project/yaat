import pytest

from yaat.responses import TextResponse


@pytest.mark.asyncio
async def test_sync_lifespan(app, client):
    pass


@pytest.mark.asyncio
async def test_async_lifespan(app, client):
    pass


@pytest.mark.asyncio
async def test_raise_on_startup(app, client):
    pass


@pytest.mark.asyncio
async def test_raise_on_shutdown(app, client):
    pass
