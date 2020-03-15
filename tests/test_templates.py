import pytest
import tempfile

from alicorn import Alicorn
from alicorn.templating import Jinja2Templates


@pytest.mark.asyncio
async def test_templates(app, client, tmpdir):
    temp = tempfile.NamedTemporaryFile(dir=tmpdir, suffix='.html', delete=False)
    temp.write(b"<html>Hello World</html>")
    temp.close()

    templates = Jinja2Templates(directory=tmpdir)
    template_name = temp.name.split("/")[-1]

    @app.route("/")
    async def handler(request):
        return templates.TemplateResponse(template_name)

    res = await client.get("/")
    assert res.content == b"<html>Hello World</html>"

