from .base import BaseMiddleware


class ExceptionMiddleware(BaseMiddleware):
    async def process_request(self, request: Request):
        print("Processing request", request.url)

    async def process_response(self, response: Request):
        print("Processing response", response.body)
