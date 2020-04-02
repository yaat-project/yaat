<h1 align="center">Yaat</h1>  
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
