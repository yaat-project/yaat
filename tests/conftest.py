import httpx
import pytest

from nymph import Nymph


@pytest.fixture
def app() -> Nymph:
    return Nymph()

@pytest.fixture
def client(app) -> httpx.AsyncClient:
    return app.test_client()
