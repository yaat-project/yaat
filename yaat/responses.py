from email.utils import formatdate
from mimetypes import guess_type
from urllib.parse import quote, quote_plus
import hashlib
import http.cookies
import json
import os
import typing

# Workaround for adding samesite support to pre 3.8 python
http.cookies.Morsel._reserved["samesite"] = "SameSite"  # type: ignore

try:
    import aiofiles
except ImportError:
    aiofiles = None

from .constants import ENCODING_METHOD
from .types import Scope, Receive, Send


class Response:
    media_type = None
    charset = 'utf-8'

    def __init__(
        self,
        content: typing.Any = None,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
    ) -> None:
        self.status_code = status_code
        if media_type is not None:
            self.media_type = media_type
        self.headers = headers if headers is not None else {}
        self.body = self.render_content(content)


    def render_content(self, content: typing.Any) -> bytes:
        if content is None:
            return b""
        if isinstance(content, bytes):
            return content
        return content.encode(self.charset)

    def get_raw_headers(self, headers: typing.Mapping[str, str] = None) -> list:
        if headers == None:
            headers = self.headers

        if headers is None:
            raw_headers = []  # type: typing.List[typing.Tuple[bytes, bytes]]
            populate_content_length = True
            populate_content_type = True
        else:
            raw_headers = [
                (k.lower().encode(ENCODING_METHOD), v.encode(ENCODING_METHOD))
                for k, v in headers.items()
            ]
            keys = [h[0] for h in raw_headers]
            populate_content_length = b"content-length" not in keys
            populate_content_type = b"content-type" not in keys
 
        body = getattr(self, "body", b"")
        if body and populate_content_length:
            content_length = str(len(body))
            raw_headers.append((b"content-length", content_length.encode(ENCODING_METHOD)))
 
        content_type = self.media_type
        if content_type is not None and populate_content_type:
            if content_type.startswith("text/"):
                content_type += "; charset=" + self.charset
            raw_headers.append((b"content-type", content_type.encode(ENCODING_METHOD)))

        return raw_headers

    def set_cookie(
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
        cookie: http.cookies.BaseCookie = http.cookies.SimpleCookie()
        cookie[key] = value
        if max_age is not None:
            cookie[key]["max-age"] = max_age
        if expires is not None:
            cookie[key]["expires"] = expires
        if path is not None:
            cookie[key]["path"] = path
        if domain is not None:
            cookie[key]["domain"] = domain
        if secure:
            cookie[key]["secure"] = True
        if httponly:
            cookie[key]["httponly"] = True
        if samesite is not None:
            # 'none' for cross-site access
            assert samesite.lower() in [
                "strict",
                "lax",
                "none",
            ], "samesite must be either 'strict', 'lax' or 'none'"

            cookie[key]["samesite"] = samesite

        self.headers["set-cookie"] = cookie.output(header="").strip()

    def delete_cookie(self, key: str, path: str = "/",domain: str = None) -> None:
        self.set_cookie(key=key, path=path, domain=domain, expires=0, max_age=0)

    async def __call__(self, send: Send) -> None:
        await send({
            "type": "http.response.start",
            "status": self.status_code,
            "headers": self.get_raw_headers(),
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
    def __init__(self, url: str, status_code: int = 307, headers: dict={}) -> None:
        headers["location"] = quote_plus(str(url), safe=":/%#?&=@[]!$&'()*+,;")
        super().__init__(content=b"", status_code=status_code, headers=headers)


class FileResponse(Response):
    chunk_size = 4096

    def __init__(
        self,
        path: str,
        filename: str = None,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        stat_result: os.stat_result = None,
        method: str = None,
    ) -> None:
        assert aiofiles is not None, "'aiofiles' must be installed to use FileResponse"

        self.path = path
        self.filename = filename
        self.status_code = status_code
        self.send_header_only = method is not None and method.upper() == "HEAD"
        if media_type is None:
            media_type = guess_type(filename or path)[0] or "text/plain"
        self.headers = headers if headers is not None else {}
        self.media_type = media_type
        self.stat_result = stat_result

        if self.filename is not None:
            content_disposition_filename = quote(self.filename)

            if content_disposition_filename != self.filename:
                content_disposition = "attachment; filename*=utf-8''{}".format(
                    content_disposition_filename
                )
            else:
                content_disposition = 'attachment; filename="{}"'.format(self.filename)
            self.headers["content-disposition"] = content_disposition

        if stat_result is not None:
            self.set_stat_headers(stat_result)


    def set_stat_headers(self, stat_result: os.stat_result) -> None:
        content_length = str(stat_result.st_size)
        last_modified = formatdate(stat_result.st_mtime, usegmt=True)
        etag_base = str(stat_result.st_mtime) + "-" + str(stat_result.st_size)
        etag = hashlib.md5(etag_base.encode()).hexdigest()

        self.headers["content-length"] = content_length
        self.headers["last-modified"] = last_modified
        self.headers["etag"] = etag


    async def __call__(self, send: Send) -> None:
        # Send 404 if file does not exists
        if not os.path.exists(self.path):
            # clear custom headers
            await send(
                {
                    "type": "http.response.start",
                    "status": 404,
                    "headers": self.get_raw_headers(headers={
                        "content-type": "text/plain"
                    }),
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"file not found",
                }
            )
            return

        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.get_raw_headers(),
            }
        )
        if self.send_header_only:
            await send({"type": "http.response.body"})
        else:    
            async with aiofiles.open(self.path, mode="rb") as file:
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


class NotModifiedResponse(Response):
    """ Use when the file requested from user is not modifed
         so instead of sending FileResponse, send NotModifiedResponse with
         empty body """

    NOT_MODIFIED_HEADERS = (
        "cache-control",
        "content-location",
        "date",
        "etag",
        "expires",
        "vary",
    )

    def __init__(self, headers: dict):
        headers = {
            name: value
            for name, value in headers.items()
            if name in self.NOT_MODIFIED_HEADERS
        }
        super().__init__(status_code=304, headers=headers)
