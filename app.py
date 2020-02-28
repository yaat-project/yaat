from kelpie import Kelpie
from kelpie.responses import FileResponse, HTMLResponse, PlainTextResponse


# NOTE: Example Web Application To Test Kelpie
app = Kelpie(templates_dir="templates", static_dir="static")


# NOTE: templating
@app.route("/home")
async def home(req):
    return HTMLResponse(
        content=app.template("home.html", context={
            "name": "Kelpie"
        })
    )


# NOTE: Decorate Route
@app.route("/hello/{name}")
async def hello(req, name):
    response = PlainTextResponse(
        content=f"Hello World, {name}"
    )
    return response

@app.route("/about")
async def about(req):
    response = PlainTextResponse(
        content="About"
    )
    return response


# NOTE: Class Route
@app.route("/books")
class BookHandler:
    async def get(self, req):
        response = PlainTextResponse(
            content=f"Books Page"
        )
        return response

    async def post(self, req):
        response = PlainTextResponse(
            content=f"Create Book"
        )
        return response


# NOTE: Add route by method
async def manual_add_route(req):
    response = PlainTextResponse(
        content=f"Manual Add Route"
    )
    return response

app.add_route("/manual_route", manual_add_route)


# NOTE: Custom Exception
# def custom_exception_handler(req, exception_cls) -> PlainTextResponse:
#     response = PlainTextResponse(
#         status_code=500,
#         content=f"Got server error, please contact our tech support!"
#     )
#     return response

# app.exception_handler = custom_exception_handler

# @app.route("/exception")
# def exception_throwing_handler(req):
#     raise AssertionError("This handler should not be user")
