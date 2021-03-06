import io
import pytest

from yaat.components import (
    URL,
    Address,
    Headers,
    QueryParams,
    Form,
)


@pytest.mark.asyncio
async def test_datatypes_url():
    url = URL(
        url="https://example.com:8080/path/to/somewhere?xyz=123#fragment1"
    )

    assert url.scheme == "https"
    assert url.host == "example.com"
    assert url.port == 8080
    assert url.netloc == "example.com:8080"
    assert url.path == "/path/to/somewhere"
    assert url.query == "xyz=123"
    assert url.fragment == "fragment1"


@pytest.mark.asyncio
async def test_datatypes_url_from_scope():
    url = URL(
        scope={
            "server": ("example.com", "8080"),
            "path": "/path/to/somewhere",
            "query_string": b"xyz=123",
            "headers": [],
        }
    )

    assert url == "http://example.com:8080/path/to/somewhere?xyz=123"
    assert url.scheme == "http"
    assert url.host == "example.com"
    assert url.port == 8080
    assert url.netloc == "example.com:8080"
    assert url.path == "/path/to/somewhere"
    assert url.query == "xyz=123"


@pytest.mark.asyncio
async def test_datatypes_address():
    address = Address("example.com", "8080")
    assert address.host == "example.com"
    assert address.port == 8080
    assert str(address) == "example.com:8080"


@pytest.mark.asyncio
async def test_datatypes_headers(app, client):
    header = Headers(
        [
            (b"content-type", b"application/json"),
            (b"api-token", b"secret"),
            (b"location", b"localhost"),
        ]
    )

    assert "content-type" in header
    assert "api-token" in header
    assert "location" in header
    assert "xyz" not in header
    assert header.get("content-type") == "application/json"
    assert header.get("api-token") == "secret"
    assert header["location"] == "localhost"
    assert list(header.keys()) == ["content-type", "api-token", "location"]
    assert dict(header) == {
        "content-type": "application/json",
        "api-token": "secret",
        "location": "localhost",
    }


@pytest.mark.asyncio
async def test_datatypes_queryparams(app, client):
    query = QueryParams("a=123&a=456&b=789&c")

    assert "a" in query
    assert "y" not in query
    assert "z" not in query
    assert query.get("a") == ["123", "456"]
    assert query["b"] == "789"
    assert dict(query) == {"a": ["123", "456"], "b": "789", "c": ""}
    assert list(query.keys()) == ["a", "b", "c"]
    assert str(query) == "a=123&a=456&b=789&c"


@pytest.mark.asyncio
async def test_datatypes_url_blank_params():
    query = QueryParams("a=123&b=456&abc&xyz")

    assert "a" in query
    assert "b" in query
    assert "abc" in query
    assert "xyz" in query
    assert "def" not in query
    assert len(query.get("abc")) == 0
    assert len(query.get("a")) == 3
    assert list(query.keys()) == ["a", "b", "abc", "xyz"]


@pytest.mark.asyncio
async def test_datatypes_form(app, client):
    upload = io.BytesIO(b"test")
    form = Form(
        [("abc", "123"), ("abc", "456"), ("def", "789"), ("xyz", upload)]
    )

    assert "abc" in form
    assert "xyz" in form
    assert "def" in form
    assert "hij" not in form
    assert form.get("abc") == ["123", "456"]
    assert form.get("def") == "789"
    assert form["xyz"] == upload
    assert dict(form) == {"abc": ["123", "456"], "def": "789", "xyz": upload}
