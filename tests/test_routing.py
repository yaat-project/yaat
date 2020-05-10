from urllib.parse import unquote
import pytest

from yaat import Yaat
from yaat.responses import (
    JSONResponse,
    TextResponse,
)
from yaat.routing import Router


@pytest.mark.asyncio
async def test_routing_no_method_specify(app, client):
    RESPONSE = "hello world"

    @app.route("/")
    async def handler(request):
        return TextResponse(RESPONSE)

    res = await client.get("/")
    assert res.text == RESPONSE


@pytest.mark.asyncio
async def test_routing_get_method(app, client):
    RESPONSE = "hello world"

    @app.route("/", methods=["GET"])
    async def handler(request):
        return TextResponse(RESPONSE)

    res = await client.get("/")
    assert res.text == RESPONSE


@pytest.mark.asyncio
async def test_routing_post_method(app, client):
    RESPONSE = "hello world"

    @app.route("/", methods=["POST"])
    async def handler(request):
        return TextResponse(RESPONSE)

    res = await client.post("/")
    assert res.text == RESPONSE


@pytest.mark.asyncio
async def test_routing_put_method(app, client):
    RESPONSE = "hello world"

    @app.route("/", methods=["PUT"])
    async def handler(request):
        return TextResponse(RESPONSE)

    res = await client.put("/")
    assert res.text == RESPONSE


@pytest.mark.asyncio
async def test_routing_patch_method(app, client):
    RESPONSE = "hello world"

    @app.route("/", methods=["PATCH"])
    async def handler(request):
        return TextResponse(RESPONSE)

    res = await client.patch("/")
    assert res.text == RESPONSE


@pytest.mark.asyncio
async def test_routing_delete_method(app, client):
    RESPONSE = "hello world"

    @app.route("/", methods=["DELETE"])
    async def handler(request):
        return TextResponse(RESPONSE)

    res = await client.delete("/")
    assert res.text == RESPONSE


@pytest.mark.asyncio
async def test_routing_multiple_method(app, client):
    RESPONSE = "hello world"

    @app.route("/multiple", methods=["GET", "POST"])
    async def handler(request):
        return TextResponse(RESPONSE)

    res = await client.get("/multiple")
    assert res.text == RESPONSE

    res = await client.post("/multiple")
    assert res.text == RESPONSE


@pytest.mark.asyncio
async def test_routing_invalid_method(app, client):
    RESPONSE = "hello world"

    @app.route("/", methods=["GET"])
    async def handler(request):
        return TextResponse(RESPONSE)

    res = await client.post("/")

    assert res.status_code == 405
    assert res.text != RESPONSE


@pytest.mark.asyncio
async def test_routing_url_param(app, client):
    @app.route("/{name}")
    async def handler(request, name):
        name = unquote(name)
        return TextResponse(f"hello {name}")

    res = await client.get("/John Doe")

    assert res.text == "hello John Doe"


@pytest.mark.asyncio
async def test_routing_class_based_view(app, client):
    @app.route("/")
    class Handler:
        async def get(self, request):
            return TextResponse("This is get method.")

        async def post(self, request):
            return TextResponse("This is post method.")

    res = await client.get("/")
    assert res.text == "This is get method."

    res = await client.post("/")
    assert res.text == "This is post method."

    res = await client.delete("/")
    assert res.status_code == 405


@pytest.mark.asyncio
async def test_routing_method_register_function_view(app, client):
    async def handler(request):
        return TextResponse("hello world")

    app.add_route(path="/", handler=handler, methods=["GET"])

    res = await client.get("/")
    assert res.text == "hello world"


@pytest.mark.asyncio
async def test_routing_method_register_class_view(app, client):
    class Handler:
        async def get(self, request):
            return TextResponse("This is get method.")

        async def post(self, request):
            return TextResponse("This is post method.")

    app.add_route(path="/", handler=Handler)

    res = await client.get("/")
    assert res.text == "This is get method."

    res = await client.post("/")
    assert res.text == "This is post method."

    res = await client.delete("/")
    assert res.status_code == 405


@pytest.mark.asyncio
async def test_routing_mount_sub_application(app, client):
    @app.route("/")
    async def main(request):
        return TextResponse("This is main app.")

    blogRouter = Router()

    @blogRouter.route("/")
    async def blog(request):
        return TextResponse("This is blog app.")

    app.mount(prefix="/blog", router=blogRouter)

    res = await client.get("/")
    res.text == "This is main app."

    res = await client.get("/blog")
    res.text == "This is blog app."


@pytest.mark.asyncio
async def test_routing_list_paths(app, client):
    @app.route("/")
    async def main(request):
        return TextResponse("main route")

    @app.route("/list")
    async def list_routes(request):
        paths = app.router.paths
        return JSONResponse({"routes": paths})

    res = await client.get("/list")
    routes = res.json()["routes"]

    assert "/" in routes
    assert "/list" in routes
