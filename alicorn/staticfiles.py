import os

from .exceptions import HttpException
from .requests import Request
from .responses import Response, FileResponse



class StaticFiles:
    def __init__(self, directory: str = ""):
        self.directory = directory

    @property
    def directory(self) -> str:
        return self.__directory

    @directory.setter
    def directory(self, directory: str):
        self.__directory = directory[1:] if directory and directory.startswith("/") else directory


    async def getResponse(self, request: Request) -> Response:
        requested_path = request.path
        if requested_path.startswith("/"):
            requested_path = requested_path[1:]

        filepath = requested_path.split(self.directory, 1)[1]
        static_path = os.path.abspath(self.directory)

        try:
            if not os.path.exists(f"{static_path}{filepath}"):
                raise HttpException(
                    status_code=404,
                    details=f"File does not exists"
                )
            response = FileResponse(
                path=static_path,
                filename=filepath
            )
        except HttpException as e:
            response = e.response
        return response

