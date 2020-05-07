import pytest

from yaat.background import BackgroundTask, BackgroundTasks, RunAfterResponse
from yaat.responses import Response


@pytest.mark.asyncio
async def test_async_task(app, client):
    TASK_COMPLETE = False

    async def task():
        nonlocal TASK_COMPLETE
        TASK_COMPLETE = True

    background = BackgroundTask(task)

    @app.route("/")
    async def handler(request):
        response = Response()
        return RunAfterResponse(response, background)

    await client.get("/")
    assert TASK_COMPLETE


@pytest.mark.asyncio
async def test_sync_task(app, client):
    TASK_COMPLETE = False

    def task():
        nonlocal TASK_COMPLETE
        TASK_COMPLETE = True

    @app.route("/")
    async def handler(request):
        response = Response()
        background = BackgroundTask(task)
        return RunAfterResponse(response, background)

    await client.get("/")
    assert TASK_COMPLETE


@pytest.mark.asyncio
async def test_task_with_arguments(app, client):
    MESSAGE = None

    def task(name, message):
        nonlocal MESSAGE
        MESSAGE = f"Hello {name}, {message}"

    @app.route("/")
    async def handler(request):
        response = Response()
        background = BackgroundTask(
            task, "Yaat", message="This is background task."
        )
        return RunAfterResponse(response, background)

    await client.get("/")
    assert MESSAGE == "Hello Yaat, This is background task."


@pytest.mark.asyncio
async def test_multiple_tasks(app, client):
    TASK1_COMPLETE = False
    TASK2_COMPLETE = False

    def task1():
        nonlocal TASK1_COMPLETE
        TASK1_COMPLETE = True

    def task2():
        nonlocal TASK2_COMPLETE
        TASK2_COMPLETE = True

    @app.route("/")
    async def handler(request):
        response = Response()
        background = BackgroundTasks()
        background.add(task1)
        background.add(task2)
        return RunAfterResponse(response, background)

    await client.get("/")
    assert TASK1_COMPLETE
    assert TASK2_COMPLETE


@pytest.mark.asyncio
async def test_multiple_both_async_sync_tasks(app, client):
    TASK1_COMPLETE = False
    TASK2_COMPLETE = False

    def task1():
        nonlocal TASK1_COMPLETE
        TASK1_COMPLETE = True

    async def task2():
        nonlocal TASK2_COMPLETE
        TASK2_COMPLETE = True

    @app.route("/")
    async def handler(request):
        response = Response()
        background = BackgroundTasks()
        background.add(task1)
        background.add(task2)
        return RunAfterResponse(response, background)

    await client.get("/")
    assert TASK1_COMPLETE
    assert TASK2_COMPLETE
