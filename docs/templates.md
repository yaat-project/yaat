# Templates

Yaat has built-in support for serving Templates. It comes with [Jinja2](https://jinja.palletsprojects.com/) templating engine out of the box.

```python
from yaat import Yaat
from yaat.templating import Jinja2Template

app = Yaat()
templates = Jinja2Template(directory="templates")

@app.route("/")
async def about(request):
   return templates.TemplateResponse("index.html", {"name": "Stranger"})
```

Then create a directory `templates` and write `index.html` inside.

**templates/index.html**
```html
<html>
  <head>
    <title>Yaat Template</title>
  </head>

  <body>
    <h1>Hello {{name}}</h1>
  </body>
</html>
```

### Custom Template Engine

You can also implement/configure your own templating engine.

First you will need to import `BaseTemplate` to override.

```python
from yaat.responses import HTMLResponse
from yaat.templating import BaseTemplate

class CustomTemplate(BaseTemplate):
    def get(self, *args, **kwargs) -> bytes:
        # To read HTML file and return as bytes
        ...

    def TemplateResponse(self, *args, **kwargs) -> HTMLResponse:
       # call self.get() to get bytes and return as HTMLResponse
```
