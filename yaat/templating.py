from jinja2 import Environment, FileSystemLoader
import os
import typing

from yaat.responses import HTMLResponse


class BaseTemplate:
    """Skeleon class to be inherited for custom template engine"""

    def get(self, *args, **kwargs) -> bytes:
        raise NotImplementedError

    def TemplateResponse(self, *args, **kwargs) -> HTMLResponse:
        raise NotImplementedError


class Jinja2Template(BaseTemplate):
    def __init__(self, directory: str):
        self.directory = directory

    @property
    def directory(self) -> Environment:
        return self.__directory

    @directory.setter
    def directory(self, directory: str):
        abspath = os.path.abspath(directory)

        # if path not exists, raise error
        if not os.path.exists(abspath):
            raise FileNotFoundError(f"Directory {abspath} does not exists.")

        self.__directory = Environment(loader=FileSystemLoader(abspath))

    def get(self, template_name: str, context: typing.Dict = None) -> bytes:
        if context is None:
            context = {}

        return (
            self.directory.get_template(template_name)
            .render(**context)
            .encode()
        )

    def TemplateResponse(
        self,
        template_name: str,
        context: typing.Dict[str, typing.Any] = None,
        status_code: int = 200,
        headers: typing.Dict[str, str] = None,
    ) -> HTMLResponse:
        template_data = self.get(template_name, context)
        return HTMLResponse(
            status_code=status_code, headers=headers, content=template_data
        )
