import pytest

from yaat.constants import WebSocketCloseEvent
from yaat.responses import HTMLResponse
from yaat.websockets import WebSocket, WebSocketDisconnect

import websocket


@pytest.mark.asyncio
async def test_websocket_url(ws_uri):
    ws = websocket.WebSocket()
    ws.connect(ws_uri)


@pytest.mark.asyncio
async def test_websocket_text(ws_uri):
    pass


@pytest.mark.asyncio
async def test_websocket_json(ws_uri):
    pass


@pytest.mark.asyncio
async def test_websocket_bytes(ws_uri):
    pass


@pytest.mark.asyncio
async def test_websocket_query_params(ws_uri):
    pass


@pytest.mark.asyncio
async def test_websocket_headers(ws_uri):
    pass


@pytest.mark.asyncio
async def test_client_close(ws_uri):
    pass


@pytest.mark.asyncio
async def test_server_close(ws_uri):
    pass


@pytest.mark.asyncio
async def test_reject_connection(ws_uri):
    pass


@pytest.mark.asyncio
async def test_subprotocol(ws_uri):
    pass


@pytest.mark.asyncio
async def test_websocket_exception(ws_uri):
    pass


@pytest.mark.asyncio
async def test_duplicate_close(ws_uri):
    pass


@pytest.mark.asyncio
async def test_duplicate_disconnect(ws_uri):
    pass
