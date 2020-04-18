import traceback

from yaat.exceptions import HTTPException, WebSocketException
from yaat.middleware.base import BaseMiddleware
from yaat.requests import Request
from yaat.responses import Response
from yaat.websockets import WebSocket, WebSocketDisconnect


class ExceptionMiddleware(BaseMiddleware):
    async def handle_request(self, request: Request) -> Response:
        try:
            response = await self.app.handle_request(request)
        except Exception:
            # print traceback and send 500 Internal Server Error
            traceback.print_exc()
            response = HTTPException(500).response

        return response

    async def handle_websocket(self, websocket: WebSocket):
        try:
            await self.app.handle_websocket(websocket)

        except WebSocketDisconnect as ws_err:
            raise ws_err

        except WebSocketException as ws_err:
            traceback.print_exc()
            raise ws_err

        except Exception:
            traceback.print_exc()
