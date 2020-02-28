<h1 align="center">Chimera</h1>  
<p align="center">
<img src="https://wallpapercave.com/wp/wp3733068.jpg" height="300" alt="chimera"/>
</p>
<p align="center"><i>lightweight ASGI framework</i> </p>

## Chimera

Chimera is an asynchronous web framework created for learning purpose. Learn more about <a href="https://asgi.readthedocs.io/en/latest/">ASGI</a>.  
This is not developed for production (`at this point`) and I suggested you to try it for learning only.  

## Requirements

Python 3.6+

## Setup

```bash
pip3 install -r requirements.txt
```

You'll also want to install an ASGI server, such as uvicorn.

```bash
pip3 install uvicorn
```

## Example

**example.py**
```python
from chimera import Chimera
from chimera.responses import PlainTextResponse

app = Chimera()

@app.route("/")
async def index(req):
    response = PlainTextResponse(content="Hello, World!")
    return response
```

Then run using uvicorn:

```bash
uvicorn example:app
```

> More examples will be added in the future.
