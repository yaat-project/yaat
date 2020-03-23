<h1 align="center">Yaat</h1>  
<p align="center"><i>yet another ASGI toolkit</i> </p>

## Yaat

Yaat is an asynchronous web framework (currently under development). Learn more about <a href="https://asgi.readthedocs.io/en/latest/" target="_blank">ASGI</a>.  

**Features**  

- Decorator routing and class based router for sub applications
- Cookie support
- Template responses using <a href="https://jinja.palletsprojects.com/en/2.11.x/">Jinja2</a>
- Static file responses

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

**example.py**
```python
from yaat import Yaat
from yaat.responses import PlainTextResponse

app = Yaat()

@app.route("/")
async def index(req):
    response = PlainTextResponse(content="Hello World")
    return response
```

Then run using uvicorn:

```bash
uvicorn example:app
```

> See <a href="https://github.com/the-robot/yaat/wiki">Wiki</a> for documentation and complete examples

## FYI

1. Is this just another web framework?
    - I started this to learn how a framework like <a href="https://palletsprojects.com/p/flask/" target="_blank">Flask</a> actually works and I am also interested in ASGI, so I decided to build this in ASGI instead of WSGI. However, after I used <a href="https://palletsprojects.com/p/flask/" target="_blank">Flask</a> and <a href="https://www.djangoproject.com" target="_blank">Django</a> for a long time, I found things that I love and hate from each. So when I started working on this, I made it to include good features that both of those have (I.e. `individual small applications` feature from Django).

## TODO

- [ ] Migrate Github Wiki to Read the docs
- [ ] Session Middleware
- [ ] Authentication Middleware
- [ ] Built-in background tasks and scheduler
- [ ] Auto documentation generator (using <a href="https://swagger.io/solutions/api-design/" target="_blank">OpenAPI</a> and <a href="https://swagger.io/tools/swaggerhub/" target="_blank">SwaggerHub</a>)
- [ ] GraphQL using <a href="https://graphene-python.org" target="_blank">Graphene</a>
