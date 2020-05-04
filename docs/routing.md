# Routing

Yaat provides simple yet powerful routing.

### Decorator Route

This is the most common and simplest routing.

```python
@app.route("/")
async def index(request):
    ...
```

### Path Parameters

You can specify the path parameters using URI templating style.

```python
@app.route("/{post_id}")
async def detail(request, post_id: int):
    ...
```

Yaat will automatically convert the value it captured in the path when type hinting is defined in parameters. Three convertors are available
- `str` - return a string, and it is also the default when type hinting is not defined.
- `int` - returns an integer.
- `float` - returns a float.

> If it failed to convert the type, it will automatically fall back to `str`.


### Register Routes By Method

You can also register a routing using `add_route` instead of using a decorator.

```python
async def index(request):
    ...

app.add_route(
    path="/",
    handler=index,
    methods=["GET"],
)
```

### Handling HTTP methods

You can specify the HTTP methods during registration to restrict the route to specific HTTP method.
If you do not specify, the route will be open to all HTTP methods.

```python
@app.route("/", methods=["GET"])
async def index(request):
    ...

async def blog(request):
    ...

app.add_route(
    path="/blog",
    handler=blog,
    methods=["GET"],
)
```

### Class Based View

Decorator routes are simple however, it is not suitable when you want the same route to provide different functionalities based
on HTTP method. Such as writing REST endpoint.

Therefore, you can use class based view instead.

```python
@app.route("/books")
class Books:
    async def get(self, request):
        response = TextResponse("List Books")
        return response

    async def post(self, request):
        response = TextResponse("Create Book")
        return response

    async def put(self, request):
        response = TextResponse("Replace Book")
        return response

    async def patch(self, request):
        response = TextResponse("Update Existing Book")
        return response

    async def delete(self, request):
        response = TextResponse("Delete Book")
        return response

class Blog:
    ...

app.add_route(path="/blog", handler=blog)
```

### Sub Applications

When your application grows, it is better to break down into smaller applications. Each application will have their own routes
and mount those routes back to the main application.

`mount(router, prefix)`

- `router` - Yaat `Router` object.
- `prefix` - url prefix to be added to all routes under the router.

**app.py**
```python
from yaat import Yaat
from yaat.responses import TextResponse

from .blog import router as BlogRouter

app = Yaat()

@app.route("/")
async def index(request):
    return TextResponse(content="Hello World")

app.mount(router=BlogRouter, prefix="/blog")
```

**blog.py**
```python
from yaat.responses import TextResponse
from yaat.routing import Router

router = Router()

@router.route("/list")
async def list(request):
    return TextResponse(content="All Blog Posts")

@router.route("/post/{post_id}")  # learn more about Path Parameters below
async def view_post(request, post_id):
    return TextResponse(content=f"Reading post {post_id}")
```

### Routing Priority

Incoming path is matched against each `Route` in order.

In cases where incoming path can be matched with more than one routes, you need to ensure that more specific routes are listed first.

**Don't do this**
```python
@app.route("/account/{username}")
async def my_account(request, name):
    return TextResponse(f"Account page of {username}")

@app.route("/account/me")
async def account(request):
    return TextResponse("This is my account page")
```

**Do like this**
```python
@app.route("/account/me")
async def account(request):
    return TextResponse("This is my account page")

@app.route("/account/{username}")
async def my_account(request, name):
    return TextResponse(f"Account page of {username}")
```
