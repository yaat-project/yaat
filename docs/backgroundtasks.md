# Background Tasks

Yaat has built-in background task runner using `BackgroundTask`.

If you want to run a task in background after responding to the client, you will have wrap your `Response`
and `BackgroundTask` in `BackgroundResponse` and return.

### Background Task

Use to run a single background task after responding to a client. 

`BackgroundTask(function, *args, **kwargs)`

- `function` - function to be called from the background task. It can be either `sync` or `async`.

```python
from yaat.background import BackgroundTask
from yaat.responses import TextResponse

async def task():
    ...

background_task = BackgroundTask(task)

@app.route("/")
async def handler(request):
    response = TextResponse("Hello World")
    return BackgroundResponse(response, background_task)
```

### Background Tasks

Use to run multiple background tasks after responding to a client.

```python
from yaat.background import BackgroundTasks
from yaat.responses import TextResponse

async def task1():
    ...

async def task2(something):
    ...

background_tasks = BackgroundTasks()
background_tasks.add(task1)
background_tasks.add(task2, "hello")

@app.route("/")
async def handler(request):
    response = TextResponse("Hello World")
    return BackgroundResponse(response, background_tasks)
```
