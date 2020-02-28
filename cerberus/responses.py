import json
from mimetypes import guess_type
from urllib.parse import quote, quote_plus
import typing

from .types import Scope, Receive, Send

try:
    import aiofiles
    from aiofiles.os import stat as aio_stat
except ImportError:
    aiofiles = None
    aio_stat = None


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
        self.headers = headers
        self.init_headers(headers)  # will set self.raw_headers
        self.body = self.render_content(content)

    def render_content(self, content: typing.Any) -> bytes:
        if content is None:
            return b""
        if isinstance(content, bytes):
            return content
        return content.encode(self.charset)

    def init_headers(self, headers: typing.Mapping[str, str] = None) -> None:
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

        self.raw_headers = raw_headers

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
            "headers": self.raw_headers,
        })
        await send({
            "type": "http.response.body",
            "body": self.body
        })


class HTMLResponse(Response):
    media_type = "text/html"


class PlainTextResponse(Response):
    media_type = "text/plain"


class JsonResponse(Response):
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
    chunk_size = 4096

    def __init__(
        self,
        path: str,
        filename: str,
        status_code: int = 200,
        media_type: str = None,
        headers: dict = None,
        method: str = None,
    ) -> None:
        assert aiofiles is not None, "'aiofiles' must be installed to use FileResponse"

        self.path = path
        self.status_code = status_code
        self.filename = filename
        self.send_header_only = method is not None and method.upper() == "HEAD"
        if media_type is None:
            media_type = guess_type(filename or path)[0] or "text/plain"
        self.media_type = media_type
        self.headers = headers
        self.init_headers(headers)
        if self.filename is not None:
            content_disposition_filename = quote(self.filename)
            if content_disposition_filename != self.filename:
                content_disposition = "attachment; filename*=utf-8''{}".format(
                    content_disposition_filename
                )
            else:
                content_disposition = 'attachment; filename="{}"'.format(self.filename)
            # self.headers.setdefault("content-disposition", content_disposition)

    async def __call__(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        if self.send_header_only:
            await send({"type": "http.response.body"})
        else:
            path = f"{self.path}{self.filename}"
            async with aiofiles.open(path, mode="rb") as file:
                more_body = True
                while more_body:
                    chunk = await file.read(self.chunk_size)
                    more_body = len(chunk) == self.chunk_size
                    await send(
                        {
                            "type": "http.response.body",
                            "body": chunk,
                            "more_body": more_body,
                        }
                    )
