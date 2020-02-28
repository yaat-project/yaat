import os

from .exceptions import HttpException
from .requests import Request
from .responses import FileResponse


def get_abs_path(static_dir: str) -> str:
    return os.path.abspath(static_dir)

def is_file_exists(filepath: str) -> bool:
    return os.path.exists(filepath)

async def handle_staticfile(request: Request, static_dir: str) -> None:
    requested_path = request.path
    if requested_path.startswith("/"):
        requested_path = requested_path[1:]
    filepath = requested_path.split(static_dir, 1)[1]
    static_path = get_abs_path(static_dir)

    try:
        if not is_file_exists(f"{static_path}{filepath}"):
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
    await response(request.send)
