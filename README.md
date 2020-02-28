<h1 align="center">Chimera</h1>  
<p align="center">
<img src="https://66.media.tumblr.com/tumblr_m8uy1cmim81r0lcy5o1_1280.jpg" height="250" alt="chimera"/>
</p>

## What is this?

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

## Credit
- I used Chimera image from <a href="https://zombiebacons.tumblr.com/post/29558558057/did-a-quick-chimera-logo-for-my-friend-john-over" target="_blank">this tumblr</a>
