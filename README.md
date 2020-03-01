<h1 align="center">Alicorn 🦄</h1>  
<p align="center">
<img src="https://i.ya-webdesign.com/images/flying-unicorn-png-5.png" height="300" alt="Alicorn"/>
</p>
<p align="center"><i>lightweight ASGI framework</i> </p>

## Alicorn

Alicorn is an asynchronous web framework created for learning purpose. Learn more about <a href="https://asgi.readthedocs.io/en/latest/" target="_blank">ASGI</a>.  
This is not for production (at this point). 

## Requirements

Python 3.6+

## Setup

```bash
pip3 install alicorn
```

> or just clone this and use directly to get currently development latest version.

You'll also want to install an ASGI server, such as uvicorn.

```bash
pip3 install uvicorn
```

## Example

**example.py**
```python
from alicorn import Alicorn
from alicorn.responses import PlainTextResponse

app = Alicorn()

@app.route("/")
async def index(req):
    response = PlainTextResponse(content="Hello, World!")
    return response
```

Then run using uvicorn:

```bash
uvicorn example:app
```

> See Wiki for documentation

## FYI

1. Can I use this for my projects?
    - No. Not at this point because it is still under development and there are so many things left to be done/improved. Besides, there is no test coverage yet.
    - You can see the list of things I planned to work in the near future at the bottom.

2. Is this just another web framework?
    - I started this to learn how a framework like <a href="https://palletsprojects.com/p/flask/" target="_blank">Flask</a> actually works and I am also interested in ASGI, so I decided to build this in ASGI instead of WSGI. However, after I used <a href="https://palletsprojects.com/p/flask/" target="_blank">Flask</a> and <a href="https://www.djangoproject.com" target="_blank">Django</a> for a long time, I found things that I love and hate from each. So when I started working on this, I made it to include good features that both of those have (I.e. `individual small applications` feature from Django).

## TODO

- [ ] Test Client for Unit Testing
- [ ] Session Middleware
- [ ] Authentication Middleware
- [ ] Built-in background tasks and scheduler
- [ ] Auto documentation generator (using <a href="https://swagger.io/solutions/api-design/" target="_blank">OpenAPI</a> and <a href="https://swagger.io/tools/swaggerhub/" target="_blank">SwaggerHub</a>)
- [ ] GraphQL using <a href="https://graphene-python.org" target="_blank">Graphene</a>
