# WebSockets

Yaat also supports sending and receiving data on a WebSocket.

### WebSocket

`WebSocket(scope, receive, send)`

It provides an interface to talk with the ASGI server. It has similar properties as `Request`.

- `url` - string-like object with all components parsed out from the URL.
- `headers` - returns `Headers` dictionary. You can access the individual value just like accessing a dictionary.
- `query_params` - returns `QueryParams` dictionary. You can access the individual value like a dictionary.

### Accept Connection

You can accept the WebSocket connection by calling `accept()`.

`await websocket.accept(subprotocol=None)`

### Sending Data

- `await websocket.send_text(data)`
    - `data` - a string data.
- `await websocket.send_bytes(data)`
    - `data` - bytes data.
- `await websocket.send_json(data, mode="text")`
    - `data` - a dictionary object.
    - `mode` - to send data in text and bytes. 2 modes available (`text`, `bytes`). Send in `text` by default.

### Receiving Data

- `await websocket.receive_text()`
- `await websocket.receive_bytes()`
- `await websocket.receive_json(mode="text")`
    - `data` - a dictionary object.
    - `mode` - to receive data in text and bytes. 2 modes available (`text`, `bytes`). Receive in `text` by default.

### Sending Raw Messages

If you want to send raw ASGI messages you can call `send()`.

- `await websocket.send(message)`

### Receiving Raw Messages

If you want to receive raw ASGI messages you can call `receive()`.

- `await websocket.receive()`

### Close Connection

You can close the connection by calling `close()`.

- `await websocket.close(code=1000)`
    - `code` - websocket close event

If you want to use different close event, you can enter the code number or import the constant.

```python
from yaat.constants import WebSocketCloseEvent as WsClose

...
    await websocket.close(WsClose.ABNORMAL_CLOSURE)
...
```

```python
class WebSocketCloseEvent:
    # https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent

    NORMAL_CLOSURE = 1000
    GOING_AWAY = 1001
    PROTOCOL_ERROR = 1002
    UNSUPPORTED_DATA = 1003
    NO_STATUS_RECEIVED = 1005
    ABNORMAL_CLOSURE = 1006
    INVALID_FRAME_PAYLOAD_DATA = 1007
    POLICY_VIOLATION = 1008
    MESSAGE_TOO_BIG = 1009
    MISSING_EXTENSION = 1010
    INTERNAL_ERROR = 1011
    SERVICE_RESTART = 1012
    TRY_AGAIN_LATER = 1013
    BAD_GATEWAY = 1014
    TLS_HANDSHAKE = 1015
```

### WebSocket Route

Yaat also comes with a separate decorator to indicates WebSocket endpoints.
When the request comes in, the router will pass the `WebSocket` class to the endpoint.

```python
@app.websocket_route("/ws")
async def ws_handler(websocket):
    await websocket.accept()
    await websocket.send_text("Hello")
    await websocket.close()
```

You can also register WebSocket endpoints via `add_websocket_route`.

`add_websocket_route(path, handler)`

- `path` - url of the endpoint.
- `handler` - WebSocket endpoint method.

```python
async def ws_handler(websocket):
    await websocket.accept()
    await websocket.send_text("Hello")
    await websocket.close()

app.add_websocket_route(ws_handler)
```

### Mounting WebSocket Routes

If you have to mount the WebSocket application, you can just indicate `websocket=True` to `mount()`.

```python
app.mount(prefix="ws", router=WebSocketRouter, websocket=True)
```
