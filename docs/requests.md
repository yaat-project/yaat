# Requests

When an endpoint receives a HTTP request, the router will pass a `Request` object.

```python
from yaat import Yaat
from yaat.responses import TextResponse

app = Yaat()

@app.route("/")
async def index(request):
    return TextResponse("Hello World")
```

The following properties and methods are accessible from `Request` object.

#### HTTP Method

- `request.method` to access the HTTP method.

#### Header

`request.headers` returns `Headers` dictionary. You can access the individual value just like accessing
a dictionary.

```python
headers = request.headers

contentType = headers.get("content-type")
apiToken = headers["api-token"]
```

#### URL

`request.url` returns string-like object with all components parsed out from the URL.

- `request.url.path`
- `request.url.scheme`
- `request.url.server`
- `request.url.netloc`
- `request.url.query`
- `request.url.host_header`
- `request.url.fragment`
- `request.url.is_secure()` to check if secure connection.

#### Query Parameters

`request.query_params` returns `QueryParams` dictionary. You can access the individual value like a dictionary.

```python
queries = request.query_params

abc = queries.get("abc")
xyz = queries["xyz"]
```

#### Client

`request.client` returns client's remote address information. The object provides the followings

- `request.host` to get the client hostname or ip address.
- `reuqest.port` to get the port number client is connecting.

#### Cookie

`request.cookie` returns the cookies in dictionary format.

```python
cookies = request.cookies

cookies.get("Authorization")
cookies["Authorization"]
```

### Body

Calling `request.body()` will returns the body data in *bytes*.

```python
@app.routes("/")
async def index(request):
    body = await request.body()
```

if you want it parsed as form data or multipart (i.e. file uploads), you can call `request.form()` instead.

```python
@app.routes("/")
async def index(request):
    form = await request.form()
```

You can also parse the body as JSON with `request.json()`

```python
@app.routes("/")
async def index(request):
    json_data = await request.json()
```

### Form

You can call `request.form()` to access form data and request files.

When you call the form, you will receive the `Form` dictionary object. You can access the form data just like a dictionary.
If there are duplicate keys inside the form, the values will be grouped into an array.

```javascript
// Request Data
form_data = {
    abc: 123,
    abc: 456,
    xyz: "Hello World",
}
```

```python
json_data = await request.form()
print(dict(json_data))

> {"abc": [123, 456], "xyz": "Hello World"}
```

#### File Upload

While there is a file inside the form, the file will be translated into Yaat's `UploadFile` object. It has the following properties and methods..

- `name` - filename of the uploaded file.
- `await write(data)` - to write `str` or `bytes` data to the file.
- `await read(size)` - to read `int` characters/bytes of the file.
- `await seek(offset)` - to go to the byte position `int` of the file.
    - `await upload.seek(0)` will be the beginning of the file.
- `await close()` - to close the file.

For example if pdf document is uploaded from the client, you can access as below.

```python
form = await request.form()

document = form["document"]
filename = document.filename
content = await document.read()
```
