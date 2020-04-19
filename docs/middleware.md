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

You can register with `add_middleware` method.

`app.add_middleware(middleware, *args, **kwargs)`

```python
class CustomMiddleware(BaseMiddleware):
    ...

app.add_middleware(CustomMiddleware)
```

You will need to register the middleware in orders. From a bird-eye view, registering middleware will look like this.

```python
Middleware2(
    Middleware1(
        Application
    )
)
```

Request will first go into `Middleware2` → `Middleware1` → `Application`.

Response will go out from `Application` → `Middleware1` → `Middleware2`.

### CORS Middleware

To allow cross-origin requests from browsers, the server need to respond with appropriate 
[CORS headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS).

The default behavior is restrictive and you will need to explicitly specify the origins, methods, or headers so that
the browser will allow cross-origin contents.

```python
from yaat.middleware import CORSMiddleware

app.add_middleware(CORSMiddleware, allow_origins=[
    "http://testserver.com",
    "http://www.testserver.com"
])
```

- `allow_origins` - a list of origins allow for cross-origin requests. You can use `["*"]` to allow any origin.
- `allow_origin_regex` - a regex string to match against origin allow for cross-origin requests. `r"http://.*\.com"` to allow any domains with `.com` top-level domain.
- `allow_methods` - a list of HTTP methods allow for cross-origin requests. Only `GET` is allowed by default. Use `["*"]` to allow all standard HTTP methods.
- `allow_headers` - a list of HTTP request headers allow for cross-origin requests. `[]` by default and [Safelisted Request Headers](https://developer.mozilla.org/en-US/docs/Glossary/CORS-safelisted_request_header) are always allowed for cross-origin requests.
- `allow_credentials` - to indicate cookie to be allowed for cross-origin requests. `False` by default.
- `expose_headers` - to indicate any response headers to be accessible to the browser. `[]` by default.
- `max_age` - set how long (in seconds) to cache CORS responses in the browser. `60` (10 minutes) by default.

CORS middleware handles two type of requests. Preflight requests and simple requests. Read more in details [here](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#Examples_of_access_control_scenarios).

#### Preflight requests

Any request with HTTP `OPTIONS` and `Access-Control-Request-Method` in headers is considered preflight requests.
For those requests, the middleware will intercept and respond with appropriate CORS headers. `HTTP 200` for success requests
and `HTTP 400` for invalid requests.

> `HTTP 200` returns instead of `HTTP 204` because some legacy browsers reject CORS requests if `204` is received.  
> [read more about issue](https://stackoverflow.com/questions/46026409/what-are-proper-status-codes-for-cors-preflight-requests)

#### Simple requests

Any request with an `Origin` in headers. CORS middleware will just pass the request through as normal but will inject
appropriate CORS headers to the response.
