# Static Files

Yaat provides `StaticFiles` to serve files from given directory.

### StaticFiles

`SaticFiles(path="/", directory="", html=False)`

- `path` - url path.
- `directory` - directory path.
- `html` - boolean to indicate to run in HTML serving.

```python
from yaat import Yaat
from yaat.staticfiles import StaticFiles

app = Yaat()

statics = StaticFiles(path="/static", directory="./static")
app.mount(statics)
```

### Serving HTML Pages

You can serve in HTML by passing `html` as `True`. When you serve the static file in HTML mode,
it will automatically loads `index.html` for directory if exists.

```python
statics = StaticFiles(path="/", directory="./static", html=True)
app.mount(statics)
```
