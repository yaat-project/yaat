import pytest

from yaat.responses import HTMLResponse
from yaat.websockets import WebSocket, WebSocketDisconnect

import websocket


@pytest.mark.asyncio
async def test_websocket_url(ws_uri):
    ws = websocket.WebSocket()
    ws.connect(ws_uri)