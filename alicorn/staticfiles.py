from email.utils import parsedate
import os
import typing

from .exceptions import NotFoundException
from .requests import Request
from .responses import FileResponse, NotModifiedResponse, Response
from .routing import Router, Route

try:
    from aiofiles.os import stat as aio_stat
except ImportError:
    aio_stat = None


class StaticFilesHandler:
    def __init__(self, path: str = "/", directory: str = ""):
        self.path = path
        self.directory = directory

    @property
    def directory(self) -> str:
        return self.__directory

    @directory.setter
    def directory(self, directory: str):
        if os.path.isfile(directory):
            raise RuntimeError(f"StaticFiles directory {directory} is not a directory.")
        self.__directory = directory

    def is_not_modified(self, request_headers: dict, response_headers: dict) -> bool:
        """
        Check if file is modified, if not return "Not Modified" response instead.
        """

        try:
            if_none_match = request_headers["if-none-match"]
            etag = response_headers["etag"]
            if if_none_match == etag:
                return True
        except KeyError:
            pass

        try:
            if_modified_since = parsedate(request_headers["if-modified-since"])
            last_modified = parsedate(response_headers["last-modified"])
            if (
                if_modified_since is not None
                and last_modified is not None
                and if_modified_since >= last_modified
            ):
                return True
        except KeyError:
            pass

        return False


    async def __call__(self, request: Request, *args, **kwargs) -> Response:
        assert aio_stat is not None, "'aiofiles' must be installed to use StaticFilesHandler"

        request_path = request.path
        # NOTE: remove route prefix and get file path
        if request_path.startswith(self.path) and self.path != "/":
            filepath = request_path[len(self.path):]
        else:
            filepath = request_path

        try:
            full_path = f"{self.directory}{filepath}" if filepath.startswith("/") else f"{self.directory}/{filepath}"

            if not os.path.exists(full_path):
                raise NotFoundException("File does not exists")

            stat_result = await aio_stat(full_path)
            response = FileResponse(path=full_path, stat_result=stat_result)

            # check if file is modified
            if self.is_not_modified(dict(request.headers), response.headers):
                response = NotModifiedResponse(response.headers)

        except NotFoundException as e:
            response = e.response

        return response


class StaticFiles:
    def __init__(self, path: str, directory: str):
        self.path = path
        self.router = Router()
        self.router.add_route(
            path=self.path,
            handler=StaticFilesHandler(self.path, directory),
            methods=["GET", "HEAD"]
        )

    @property
    def path(self) -> str:
        return self.__path

    @path.setter
    def path(self, path: str) -> None:
        # clean static directory path
        if path.endswith("/"):
            path = path[:-1]
        if not path.startswith("/"):
            path = f"/{path}"

        self.__path = path

    @property
    def routes(self) -> typing.List[Route]:
        return self.router.routes

