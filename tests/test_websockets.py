import json
import pytest
import websocket


@pytest.mark.asyncio
async def test_websockets_url(ws_uri):
    ws = websocket.WebSocket()
    ws.connect(f"{ws_uri}/hello")
    res = ws.recv()
    assert res == "Hello"


@pytest.mark.asyncio
async def test_websockets_text(ws_uri):
    ws = websocket.WebSocket()
    ws.connect(f"{ws_uri}/text")
    ws.send("Hello")
    res = ws.recv()
    assert res == f"You sent me 'Hello'"


@pytest.mark.asyncio
async def test_websockets_json(ws_uri):
    DATA = {"hello": "world"}

    ws = websocket.WebSocket()
    ws.connect(f"{ws_uri}/json")
    ws.send(json.dumps(DATA))
    res = json.loads(ws.recv())
    assert res == DATA


@pytest.mark.asyncio
async def test_websockets_bytes(ws_uri):
    DATA = b"bytes"

    ws = websocket.WebSocket()
    ws.connect(f"{ws_uri}/bytes", subprotocols=["binary"])
    ws.send(DATA, websocket.ABNF.OPCODE_BINARY)
    res = ws.recv()
    assert res == DATA


@pytest.mark.asyncio
async def test_websockets_query_params(ws_uri):
    ws = websocket.WebSocket()
    ws.connect(f"{ws_uri}/query-param?a=123&b=xyz")
    res = json.loads(ws.recv())
    assert res == {"a": "123", "b": "xyz"}


@pytest.mark.asyncio
async def test_websockets_headers(ws_uri):
    ws = websocket.WebSocket()
    ws.connect(f"{ws_uri}/headers", header={"hello": "world"})
    res = json.loads(ws.recv())
    assert res == {"hello": "world"}
