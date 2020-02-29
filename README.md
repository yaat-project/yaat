<h1 align="center">Alicorn</h1>  
<p align="center">
<img src="https://wallpapercave.com/wp/wp3733068.jpg" height="300" alt="Alicorn"/>
</p>
<p align="center"><i>lightweight ASGI framework</i> </p>

## Alicorn

Alicorn is an asynchronous web framework created for learning purpose. Learn more about <a href="https://asgi.readthedocs.io/en/latest/">ASGI</a>.  
This is not production yet (at this point). 

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

> More examples will be added in the future.
