# Middleware

Middleware wraps your application. In Yaat, you can write custom middleware easily by overriding
`BaseMiddleware` class.

Methods

- `process_request` - run befores HTTP request goes into your application.
- `process_response` - run befores HTTP response goes back to client.
- `handle_request` - handle HTTP request.
- `handle_websocket` - handle WebSocket.

This is how `BaseMiddleware` handles requests

```python
from yaat.requests import Request
from yaat.responses import Response

class BaseMiddleware:
    ...

    async def process_request(self, request: Request):
        pass

    async def process_response(self, response: Response):
        pass

    async def handle_request(self, request: Request) -> Response:
        await self.process_request(request)
        response = await self.app.handle_request(request)
        await self.process_response(response)
        return response

    async def handle_websocket(self, websocket: WebSocket):
        await self.app.handle_websocket(websocket)

    ...
```

### Registering Middleware

After you implemented custom middleware, you can register with `add_middleware` method.

```python
class CustomMiddleware(BaseMiddleware):
    ...

app.add_middleware(CustomMiddleware)
```

You will need to register middleware in orders. From bird-eye view, registering middleware will look like this.

```python
Middleware2(
    Middleware1(
        Application
    )
)
```

Request will first go into `Middleware2` → `Middleware1` → `Application`.

Response will go out from `Application` → `Middleware1` → `Middleware2`.
