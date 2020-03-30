import http

from yaat.responses import PlainTextResponse


class HTTPException(Exception):
    def __init__(self, status_code: int, details: str = None):
        if details is None:
            details = http.HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.details = details

    @property
    def response(self) -> PlainTextResponse:
        return PlainTextResponse(
            status_code=self.status_code,
            content=self.details,
        )

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.details!r})"

    def __str__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.details!r})"


class WebSocketException(RuntimeError):
    def __init__(self, message: str):
        self.message = message

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name} (Message: {self.message!r})"

    def __str__(self) -> str:
        return self.message
