# https://asgi.readthedocs.io/en/latest/specs/www.html#wsgi-encoding-differences
ENCODING_METHOD = "latin-1"

HTTP_METHODS = [
    "GET",
    "HEAD",
    "PATCH",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "OPTIONS",
    "TRACE",
]


class WebSocketMessages:
    # https://asgi.readthedocs.io/en/latest/specs/www.html#websocket
    ACCEPT = "websocket.accept"
    CONNECT = "websocket.connect"
    DISCONNECT = "websocket.disconnect"
    SEND = "websocket.send"
    RECEIVE = "websocket.receive"
    CLOSE = "websocket.close"


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
