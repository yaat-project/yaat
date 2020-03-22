import httpx
import pytest

from alicorn import Alicorn


@pytest.fixture
def app() -> Alicorn:
    return Alicorn()

@pytest.fixture
def client(app) -> httpx.AsyncClient:
    return app.test_client()
