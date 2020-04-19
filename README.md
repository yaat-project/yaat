<h1 align="center">Yaat</h1>  

<p align="center">
    <img src="https://avatars0.githubusercontent.com/u/62506028?s=200&v=4">
</p>

<p align="center"><i>yet another ASGI toolkit</i></p>

<p align="center">
    <a href="https://travis-ci.org/github/yaat-project/yaat">
        <img src="https://travis-ci.org/yaat-project/yaat.svg?branch=master" alt="travis status"/>
    </a>
    <a href='https://yaat.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/yaat/badge/?version=latest' alt='docs status' />
    </a>
    <a href="https://codecov.io/gh/yaat-project/yaat/">
        <img src="https://codecov.io/gh/yaat-project/yaat/branch/master/graph/badge.svg" alt="codecov report"/>
    </a>
    <a href="https://pypi.org/project/yaat/">
        <img src="https://badge.fury.io/py/yaat.svg" alt="pypi package version"/>
    </a>
    <a href="https://github.com/psf/black">
        <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
    </a>
</p>

## Yaat

Yaat is an asynchronous web framework/toolkit.

- [Documentation](https://yaat.readthedocs.io/)

**Features**  

- Provide decorator routes & class-based views.
- Template support with [Jinja2](https://jinja.palletsprojects.com/).
- Static file serving.
- HTTP streaming response.
- Cookie support.
- WebSocket support.
- Background tasks runner.
- Server startup and shutdown events.
- CORS support.
- Test client using [httpx](https://www.python-httpx.org/).

## Requirements

Python 3.6+

## Setup

```bash
pip3 install yaat
```

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

I know there are a lot of awesome frameworks out there. So some might ask why did I write my own. Actually, I created this to learn how the web framework works.

I started this after following [Jahongir Rahmonov's blog post](https://rahmonov.me/posts/write-python-framework-part-one/) about writing a web framework. Feel free to check out his WSGI framework [Alcazar](https://github.com/rahmonov/alcazar).

More features will be added in the future. You can check out the [project board](https://github.com/yaat-project/yaat/projects/1).


## Icon Credit

Icons made by <a href="https://www.flaticon.com/authors/dave-gandy" title="Dave Gandy">Dave Gandy</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>
