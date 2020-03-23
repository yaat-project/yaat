import httpx
import pytest

from yaat import Yaat


@pytest.fixture
def app() -> Yaat:
    return Yaat()

@pytest.fixture
def client(app) -> httpx.AsyncClient:
    return app.test_client()
