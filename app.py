from kelpie import Kelpie
from kelpie.responses import PlainTextResponse


# NOTE: Example Web Application To Test Kelpie
app = Kelpie()


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
