from alicorn import Alicorn
from alicorn.responses import JsonResponse


app = Alicorn()

@app.route("/")
async def index(req):
    response = JsonResponse(content={"hello": "world"})
    return response
