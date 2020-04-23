# Static Files

Yaat provides `StaticFiles` to serve files from the given directory.

### StaticFiles

`SaticFiles(directory="", html=False)`

- `directory` - directory path.
- `html` - boolean to indicate to run in HTML serving.

```python
from yaat import Yaat
from yaat.staticfiles import StaticFiles

app = Yaat()

statics = StaticFiles(directory="./static")
app.mount(statics, "/static")
```

### Serving HTML Pages

You can serve in HTML by passing `html` as `True`. When you serve the static file in HTML mode,
it will automatically loads `index.html` for a directory if it exists.

```python
statics = StaticFiles(directory="./static", html=True)
app.mount(statics, "/")
```
