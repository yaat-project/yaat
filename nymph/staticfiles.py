from email.utils import parsedate
import os
import typing

try:
    from aiofiles.os import stat as aio_stat
except ImportError:
    aio_stat = None

from .exceptions import HttpException
from .requests import Request
from .responses import FileResponse, NotModifiedResponse, Response
from .routing import Router, Route


class StaticFilesHandler:
    def __init__(self, path: str = "/", directory: str = "", html: bool = False):
        self.path = path
        self.directory = directory
        self.html = html

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
        # if starts with / remove
        filepath = filepath[1:] if filepath.startswith("/") else filepath

        try:
            full_path = os.path.join(self.directory, filepath)
            is_directory = os.path.isdir(full_path)
            is_file_exists = os.path.exists(full_path)

            # if html response
            if self.html:
                index_path = os.path.join(self.directory, "index.html")
                is_index_exists = os.path.exists(index_path)

                # if directory, check if there is index file
                if is_index_exists and is_directory:
                    full_path = index_path
                # raise 404 if not directory and file also not exists
                elif not is_file_exists and not is_directory:
                    raise HttpException(404)

                stat_result = await aio_stat(full_path)
                response = FileResponse(path=full_path, stat_result=stat_result)

            # if file response
            else:
                if is_directory or not is_file_exists:
                    raise HttpException(
                        status_code=404,
                        details="File does not exists"
                    )

                stat_result = await aio_stat(full_path)
                response = FileResponse(path=full_path, stat_result=stat_result)

                # check if file is modified
                if self.is_not_modified(dict(request.headers), response.headers):
                    response = NotModifiedResponse(response.headers)

        except HttpException as e:
            response = e.response

        return response


class StaticFiles:
    def __init__(self, path: str, directory: str, html: bool = False):
        self.path = path
        self.router = Router()
        self.router.add_route(
            path=self.path,
            handler=StaticFilesHandler(self.path, directory, html),
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
