from jinja2 import Environment, FileSystemLoader
import os

from .responses import HTMLResponse


class BaseTemplates:
    """Skeleon class to be inherited for custom template engine"""

    def get(self, *args, **kwargs) -> bytes:
        raise NotImplementedError

    def TemplateResponse(self, *args, **kwargs) -> HTMLResponse:
        raise NotImplementedError


class Jinja2Templates(BaseTemplates):
    def __init__(self, directory: str):
        self.directory = directory

    @property
    def directory(self) -> Environment:
        return self.__directory

    @directory.setter
    def directory(self, directory: str) -> None:
        abspath = os.path.abspath(directory)

        # if path not exists, raise error
        if not os.path.exists(abspath):
            raise FileNotFoundError(f"Directory {abspath} does not exists.")

        self.__directory = Environment(
            loader=FileSystemLoader(abspath)
        )

    def get(self, template_name: str, context: dict = None) -> bytes:
        if context is None:
            context = {}

        return self.directory.get_template(template_name).render(**context).encode()

    def TemplateResponse(
        self,
        template_name: str,
        context: dict = None,
        status_code: int = 200,
        headers: dict = None,
    ) -> HTMLResponse:
        template_data = self.get(template_name, context)
        return HTMLResponse(
            status_code=status_code,
            headers=headers,
            content=template_data
        )
