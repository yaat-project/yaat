import httpx
import pytest

from yaas import Yaas


@pytest.fixture
def app() -> Yaas:
    return Yaas()

@pytest.fixture
def client(app) -> httpx.AsyncClient:
    return app.test_client()
