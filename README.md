<h1 align="center">Yaat</h1>  

<p align="center">
    <img src="https://avatars0.githubusercontent.com/u/62506028?s=200&v=4">
</p>

<p align="center"><i>yet another ASGI toolkit</i></p>

<p align="center">
    <a href="https://pypi.org/project/yaat/">
        <img src="https://badge.fury.io/py/yaat.svg" alt="pypi package version">
    </a>
</p>

## Yaat

Yaat is an asynchronous web framework/toolkit.

- [Documentation](https://yaat.readthedocs.io/)

**Features**  

- Provide decorator routes & class based views.
- Template support with [Jinja2](https://jinja.palletsprojects.com/).
- Cookie support.
- WebSocket support.
- Background tasks runner.
- Test client using [httpx](https://www.python-httpx.org/).
- Static file serving.

## Requirements

Python 3.6+

## Setup

```bash
pip3 install yaat
```

> or just clone this and use directly to get the latest development version.

You'll also want to install an ASGI server, such as uvicorn.

```bash
pip3 install uvicorn
```

## Example

Writing with Yaat is as simple as...

**app.py**

```python
from yaat import Yaat
from yaat.responses import TextResponse

app = Yaat()

@app.route("/")
async def index(request):
    return TextResponse("Hello World")
```

Then run using uvicorn:

```bash
uvicorn app:app
```

## Inspiration

I know there are a lot of awesome frameworks out there. So some might ask why did I write my own. Actually I created this to learn how the web framework actually works.

I started this after following [Jahongir Rahmonov's blog post](https://rahmonov.me/posts/write-python-framework-part-one/) about writing a web framework. Feel free to check out his WSGI framework [Alcazar](https://github.com/rahmonov/alcazar).

More features will be added in the future. You can checkout the [project board](https://github.com/yaat-project/yaat/projects/1).
