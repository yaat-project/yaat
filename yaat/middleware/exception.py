import traceback

from .base import BaseMiddleware
from ..exceptions import HTTPException, WebSocketException
from ..requests import Request
from ..responses import Response
from ..websockets import WebSocket, WebSocketDisconnect


class ExceptionMiddleware(BaseMiddleware):
    async def handle_request(self, request: Request) -> Response:
        await self.process_request(request)

        try:
            response = await self.app.handle_request(request)
        except Exception as err:
            # print traceback and send 500 Internal Server Error
            traceback.print_exc()
            response = HTTPException(500).response        

        await self.process_response(response)
        return response

    async def handle_websocket(self, websocket: WebSocket):
        try:
            await self.app.handle_websocket(websocket)

        except WebSocketDisconnect as ws_err:
            raise ws_err

        except WebSocketException as ws_err:
            traceback.print_exc()
            raise ws_err

        except Exception as err:
            traceback.print_exc()
