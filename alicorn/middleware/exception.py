import traceback

from .base import BaseMiddleware
from ..exceptions import HttpException
from ..requests import Request
from ..responses import Response


class ExceptionMiddleware(BaseMiddleware):
    async def handle_request(self, request: Request) -> Response:
        await self.process_request(request)

        try:
            response = await self.app.handle_request(request)
        except Exception as err:
            # print traceback and send 500 Internal Server Error
            traceback.print_exc()
            response = HttpException(500).response        

        await self.process_response(response)
        return response
