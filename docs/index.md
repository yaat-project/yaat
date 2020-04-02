# Introduction

Yaat is an asynchronous web toolkit. It is as simple as..

```python
from yaat import Yaat
from yaat.responses import TextResponse

app = Yaat()

@app.route("/")
async def index(request):
    return TextResponse("Hello World")
```

## Features

- Provides functional routes & class based routes.
- Template support with [Jinja2](https://jinja.palletsprojects.com/).
- Cookie support.
- WebSocket support.
- Background tasks runner.
- Test client using [httpx](https://www.python-httpx.org/).
- Static file serving.

## Requirements

Python 3.6+

## Installation

```sh
pip3 install yaat
```

In order to run the application, you will need an ASGI server. Such as [uvicorn](https://www.uvicorn.org/), [hypercorn](https://pgjones.gitlab.io/hypercorn) or [daphne](https://github.com/django/daphne/).

For example, if you put the example code from the top in `app.py`. You can run the application by

```sh
uvicorn app:app
```

> [view example codes](/examples)

## Dependencies

- [aiofiles](https://github.com/Tinche/aiofiles) - to read files for `FileResponse` or `StaticFiles`.
- [httpx](https://www.python-httpx.org/) - for test client
- [Jinja2](https://jinja.palletsprojects.com/) - to use `Jinja2Templates` for template responses.
- [parse](https://github.com/r1chardj0n3s/parse) - for parsing url parameters.
- [python-multpart](http://andrew-d.github.io/python-multipart/) - for form parser, `request.form()`

## License

Yaat is licensed under [GNU Lesser General Public License](https://github.com/yaat-project/yaat/blob/master/LICENSE).

## Inspiration

I know there are a lot of awesome frameworks out there. So some might ask why did I write my own. Actually I created this to learn how the web framework actually works.

I started this after following [Jahongir Rahmonov's blog post](https://rahmonov.me/posts/write-python-framework-part-one/) about writing a web framework. Feel free to check out his WSGI framework [Alcazar](https://github.com/rahmonov/alcazar).

More features will be added in the future. You can checkout the [project board](https://github.com/yaat-project/yaat/projects/1).
