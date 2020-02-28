import json
import typing

from .types import Scope, Receive, Send


class Response:
    media_type = None
    charset = 'utf-8'

    def __init__(
        self,
        status_code: int = 200,
        media_type: str = None,
        headers: dict = None,
        content: typing.Any = None,
    ) -> None:
        self.status_code = status_code
        if media_type is not None:
            self.media_type = media_type
        self.headers = self.init_headers(headers)
        self.body = self.render_content(content)

    def render_content(self, content: typing.Any) -> bytes:
        if content is None:
            return b""
        if isinstance(content, bytes):
            return content
        return content.encode(self.charset)

    def init_headers(self, headers: typing.Mapping[str, str] = None) -> list:
        if headers is None:
            raw_headers = []  # type: typing.List[typing.Tuple[bytes, bytes]]
            populate_content_length = True
            populate_content_type = True
        else:
            raw_headers = [
                (k.lower().encode("latin-1"), v.encode("latin-1"))
                for k, v in headers.items()
            ]
            keys = [h[0] for h in raw_headers]
            populate_content_length = b"content-length" not in keys
            populate_content_type = b"content-type" not in keys
        
        body = getattr(self, "body", b"")
        if body and populate_content_length:
            content_length = str(len(body))
            raw_headers.append((b"content-length", content_length.encode("latin-1")))
        
        content_type = self.media_type
        if content_type is not None and populate_content_type:
            if content_type.startswith("text/"):
                content_type += "; charset=" + self.charset
            raw_headers.append((b"content-type", content_type.encode("latin-1")))

        return raw_headers

    def set_cookies(
        self,
        key: str,
        value: str = "",
        max_age: int = None,
        expires: int = None,
        path: str = "/",
        domain: str = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: str = "lax",
    ) -> None:
        # TODO: implement set cookie method
        pass

    async def __call__(self, send: Send) -> None:
        await send({
            "type": "http.response.start",
            "status": self.status_code,
            "headers": self.headers,
        })
        await send({
            "type": "http.response.body",
            "body": self.body
        })


class HTMLResponse(Response):
    media_type = "text/html"


class PlainTextResponse(Response):
    media_type = "text/plain"


class JSONResponse(Response):
    media_type = "application/json"

    def render_content(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


class RedirectResponse(Response):
    # TODO: implement redirection
    pass


class FileResponse(Response):
    # TODO: implement file response
    pass
