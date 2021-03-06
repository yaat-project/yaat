# Events

You can register multiple handlers to events you want to run some code during the server startup or shutdown events.

### Registering Handlers

Handlers can either be synchronous functions or async coroutines. For example, connecting to the database should be done on the `on_startup` event.

```python
from yaat import Yaat

async def startup_task():
    ...

async def shutdown_task():
    ...

app = Yaat(
    on_startup=[connect_database],
    on_shutdown=[email_stuffs]
)
```

> In Uvicorn, pass the argument `lifespan` to set the lifespan protocol.

```sh
uvicorn app:app --lifespan on
```

[Read more here](https://www.uvicorn.org/settings/#implementation)
