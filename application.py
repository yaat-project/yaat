from yaat import Yaat
from yaat.responses import HTMLResponse
from yaat.staticfiles import StaticFiles

static = StaticFiles(path="static", directory="./static")

app = Yaat()
app.mount(static)


@app.route("/")
async def index(request):
    return HTMLResponse(
        """<html>
            <head><title>Hello World</title></head>

            <body>
                <h1> Hello World Is A Simple Program </h1>
            </body>
            </html>
        """
    )
