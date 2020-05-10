import pytest

from yaat import Yaat
from yaat.openapi import OpenAPISchema, get_swagger_ui
from yaat.responses import JSONResponse, TextResponse
from yaat.routing import Router


schema = OpenAPISchema("Yaat")


# Test routes
async def list_users(request):
    """
    responses:
        200:
            description: List users.
        examples:
            [{"name": "John"}]
    """
    return JSONResponse([{"name": "John"}])


async def create_user(request):
    """
    responses:
        200:
            description: Create user.
            examples:
                {"userid": "user123"}
    """
    return JSONResponse({"userid": "user123"})


async def get_user(request, userid: str):
    """
    responses:
        200:
            description: Get user details.
    """
    return TextResponse(f"This is {userid}.")


async def websocket_route(websocket):
    pass


class BooksRoute:
    def get(self, request):
        """
        responses:
            200:
                description: List books.
                examples:
                    [{"name": "Harry Potter"}, {"name": "Percy Jackson"}]
        """
        return JSONResponse(
            [{"name": "Harry Potter"}, {"name": "Percy Jackson"}]
        )

    def post(self, request):
        """
        responses:
            200:
                description: Create book.
                examples:
                    {"name": "Harry Potter"}
        """
        return JSONResponse({"name": "Harry Potter"})


async def regular_route_with_docstring_and_invalid_schema(request):
    """
    It has docstring but schema is invalid so should not be included.
    """
    return TextResponse("Hello World!")


async def regular_route_with_docstring(request):
    """
    Hello World!
    """
    return TextResponse("Hello World!")


async def regular_route_without_docstring(request):
    return TextResponse("Hello World!")


async def subrouter_router(request):
    """
    responses:
        200:
            description: Subrouter route.
    """
    return TextResponse("Subrouter route.")


# Schema and Swagger routes
OPEN_API_URL = "/openapi"
SWAGGER_UI_URL = "/swagger"


async def openapi_schema(request):
    return schema.Response(request)


async def swagger_ui(request):
    return get_swagger_ui(openapi_url=OPEN_API_URL, title="Yaat")


# Route Registration
def register_routes(app: Yaat):
    subrouter = Router()

    app.add_route(
        "/users/create",
        create_user,
        methods=["POST"],
        has_schema=True,
        tags=["users"],
    )
    app.add_route("/users/{userid}", get_user, has_schema=True, tags=["users"])
    app.add_route("/users", list_users, has_schema=True, tags=["users"])
    app.add_route("/books", BooksRoute, has_schema=True, tags=["books"])
    app.add_route(
        "/invalid-schema",
        regular_route_with_docstring_and_invalid_schema,
        has_schema=True,
    )
    app.add_route(
        "/normal-docstring", regular_route_with_docstring, has_schema=True
    )
    app.add_route(
        "/without-docstring", regular_route_without_docstring, has_schema=True
    )
    app.add_route(OPEN_API_URL, openapi_schema)
    app.add_route(SWAGGER_UI_URL, swagger_ui)
    app.add_websocket_route("/ws", websocket_route)

    subrouter.add_route("/", subrouter_router, has_schema=True)
    app.mount(prefix="/subroute", router=subrouter)


# Schema
JSON_API_SCHEMA = {
    "openapi": "3.0.0",
    "info": {"title": "Yaat"},
    "paths": {
        "/users/create": {
            "post": {
                "responses": {
                    200: {
                        "description": "Create user.",
                        "examples": {"userid": "user123"},
                    }
                },
                "tags": ["users"],
            }
        },
        "/users/{userid}": {
            "get": {
                "responses": {200: {"description": "Get user details."}},
                "parameters": [
                    {
                        "in": "path",
                        "name": "userid",
                        "schema": {"type": "string"},
                        "required": "true",
                    }
                ],
                "tags": ["users"],
            }
        },
        "/users": {
            "get": {
                "responses": {
                    200: {"description": "List users."},
                    "examples": [{"name": "John"}],
                },
                "tags": ["users"],
            }
        },
        "/books": {
            "get": {
                "responses": {
                    200: {
                        "description": "List books.",
                        "examples": [
                            {"name": "Harry Potter"},
                            {"name": "Percy Jackson"},
                        ],
                    }
                },
                "tags": ["books"],
            },
            "post": {
                "responses": {
                    200: {
                        "description": "Create book.",
                        "examples": {"name": "Harry Potter"},
                    }
                },
                "tags": ["books"],
            },
        },
        "/subroute/": {
            "get": {"responses": {200: {"description": "Subrouter route."}}}
        },
    },
}

YAML_API_SCHEMA = """
info:
  title: Yaat
openapi: 3.0.0
paths:
  /books:
    get:
      responses:
        200:
          description: List books.
          examples:
          - name: Harry Potter
          - name: Percy Jackson
      tags: &id001
      - books
    post:
      responses:
        200:
          description: Create book.
          examples:
            name: Harry Potter
      tags: *id001
  /subroute/:
    get:
      responses:
        200:
          description: Subrouter route.
  /users:
    get:
      responses:
        200:
          description: List users.
        examples:
        - name: John
      tags:
      - users
  /users/create:
    post:
      responses:
        200:
          description: Create user.
          examples:
            userid: user123
      tags:
      - users
  /users/{userid}:
    get:
      parameters:
      - in: path
        name: userid
        required: 'true'
        schema:
          type: string
      responses:
        200:
          description: Get user details.
      tags:
      - users
"""


# Tests
def test_schemas_generator(app):
    register_routes(app)
    api_schema = schema.get_schema(app.router.routes)

    assert api_schema == JSON_API_SCHEMA


@pytest.mark.asyncio
async def test_schemas_route(app, client):
    register_routes(app)
    res = await client.get(OPEN_API_URL)

    assert res.text.strip() == YAML_API_SCHEMA.strip()


@pytest.mark.asyncio
async def test_schemas_swagger_ui(app, client):
    register_routes(app)
    res = await client.get(SWAGGER_UI_URL)

    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert '<div id="swagger-ui"></div>' in res.text
