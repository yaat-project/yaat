# Responses

Endpoints will have to use the following response classes to response back to the client.

### Response

This is the base class for all types of responses Yaat offers.

`Response(content, status_code=200, headers=None, media_type=None)`

- `content` - either a string or bytestring
- `status_code` - HTTP status code
- `headers` - a dictionary of strings
- `media/type` - string that represents a type of the content

You do not need to pass `content-type` and `content-length`. It will be automatically added to the header.

#### Status Code

For `status_code` instead of passing the integer directly you can also pass the value of
constants from python `http.HTTPStatus`.

```python
from http import HTTPStatus

response = Response("Hello World", status=HTTPStatus.OK.value)
```

[read more about http.HTTPStatus](https://docs.python.org/3/library/http.html#http.HTTPStatus)

#### Set Cookie

You can set the cookie on the response with `set_cookie` method.

`set_cookie(key, value, max_age=None, expires=None, path="/", domain=None, secure=False, httponly=False, samesite="lax")`

- `key` - cookie's key.
- `value` - cookie's value.
- `max-age` - cookie's lifetime in seconds. A negative integer or a value of 0 to discard the cookie.
- `expires` - cookie's expiry in seconds.
- `path` - specifies the subset of routes to apply cookie.
- `domain` - specifies the domain to apply cookie.
- `secure` - only send the cookie if connection is made from SSL and HTTPS protocol.
- `httponly` - indicates that cookie cannot be accessed from Javascript.
- `samesite` - indicates that cookie should not be sent with cross-site requests

[read more about HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)

#### Delete Cookie

- You can manually expire the cookie using `delete_cookie`.

`delete_cookie(key, path="/", domain=None)`

- `key` - cookie's key.
- `path` - specifies the subset of routes to apply cookie.
- `domain` - specifies the domain to apply cookie.

### Text Response

Return text/bytes as plain text response.

```python
from yaat.responses import TextResponse

@app.route("/")
async def index(request):
    return TextResponse("Hello World")
```

### HTML Response

Return text/bytes as HTML response.

```python
from yaat.responses import HTMLResponse

@app.route("/")
async def index(request):
    return HTMLResponse("<h1>Hello World</h1>")
```

### JSON Response

Return dictionary as `application/json` encoded response.

```python
from yaat.responses import JSONResponse

@app.route("/")
async def index(request):
    return JSONResponse({"hello": "world"})
```

### Redirect Response

Return HTTP redirect with `307` status code by default.

```python
from yaat.responses import JSONResponse, TextResponse

@app.route("/")
async def index(request):
    return TextResponse("Hello World")

@app.route("/404")
async def notfound(request):
    return RedirectResponse("/")
```

### File Response

Asynchronously streams file as response.

`FileResponse(path, filename=None, status_code=200, headers=None, media_type=None, method=None)`

- `path` - filepath.
- `filename` - name of the file.
- `status_code` - HTTP status code, 200 by default.
- `headers` - response headers.
- `media_type` - string of media type. If not given, it will be determined by the filepath.
- `method` - HTTP method. If `Head` only entity header describing the body content (such as `content-length`) will be sent. Body will be empty.

> `content-length`, `last-modified` and `etag` will be added automatically to headers.

```python
from yaat.responses import FileResponse

@app.route("/")
async def index(request):
    return FileResponse("static/logo.png")
```

### Stream Response

It is used to stream a response from Yaat to the client browser. It is good for cases like generating the response that takes too long to process or uses a lot of memory. For example, generating a large CSV reports.

> If you are serving a generated file/data that takes too long to respond and will be requested over and over, you may also want to consider running it in the background and save it on server.  
> After successfully generated the data, you can serve the file as `StaticFile`.

`StreamResponse(content, status_code=200, headers=None, media_type=None)`

- `content` - method that returns a generator.
- `status_code` - HTTP status code, 200 by default.
- `headers` - response headers.
- `media_type` - string of media type.

```python
from yaat.response import StreamResponse

async def hello():
    yield('Hello World')

@app.route("/")
async def index(request):
    generator = hello()
    return StreamResponse(generator, media_type="text/plain")
```