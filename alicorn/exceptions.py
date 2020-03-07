from .responses import PlainTextResponse


class HttpException(Exception):
    def __init__(self, status_code: int, details: str = None) -> None:
        if details is None:
            details = b""
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


class NotFoundException(HttpException):
    def __init__(self, details: str = "Not Found"):
        super().__init__(status_code=404, details=details)


class MethodNotAllowException(HttpException):
    def __init__(self, details: str = "Method Not Allowed"):
        super().__init__(status_code=405, details=details)

