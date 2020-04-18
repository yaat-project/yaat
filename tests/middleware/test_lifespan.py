import pytest

from yaat import Yaat


@pytest.mark.asyncio
async def test_sync_lifespan():
    ran_startup = False
    ran_shutdown = False

    def startup():
        nonlocal ran_startup
        ran_startup = True

    def shutdown():
        nonlocal ran_shutdown
        ran_shutdown = True

    app = Yaat(on_startup=[startup], on_shutdown=[shutdown])
    client = app.test_client()

    # mock async scope, receive, send
    asgi_scope = {"type": "lifespan"}

    async def asgi_receive():
        if not ran_startup:
            return {"type": "lifespan.startup"}
        else:
            return {"type": "lifespan.shutdown"}

    async def asgi_send(*args , **kwargs):
        pass

    await app(asgi_scope, asgi_receive, asgi_send)

    assert ran_startup
    assert ran_shutdown

@pytest.mark.asyncio
async def test_async_lifespan():
    ran_startup = False
    ran_shutdown = False

    async def startup():
        nonlocal ran_startup
        ran_startup = True

    async def shutdown():
        nonlocal ran_shutdown
        ran_shutdown = True

    app = Yaat(on_startup=[startup], on_shutdown=[shutdown])
    client = app.test_client()

    # mock async scope, receive, send
    asgi_scope = {"type": "lifespan"}

    async def asgi_receive(*args, **kwargs):
        return {"type": "lifespan.shutdown"} if ran_startup else {"type": "lifespan.startup"}

    async def asgi_send(*args , **kwargs):
        pass

    await app(asgi_scope, asgi_receive, asgi_send)
    assert ran_startup
    assert ran_shutdown


@pytest.mark.asyncio
async def test_raise_on_startup():
    ran_startup = False
    startup_failed = False

    async def startup():
        nonlocal ran_startup
        ran_startup = True
        raise Exception

    app = Yaat(on_startup=[startup])
    client = app.test_client()

    # mock async scope, receive, send
    asgi_scope = {"type": "lifespan"}

    async def asgi_receive(*args, **kwargs):
        return {"type": "lifespan.startup"}

    async def asgi_send(*args , **kwargs):
        nonlocal startup_failed
        startup_failed = True

    try:
        await app(asgi_scope, asgi_receive, asgi_send)
    except Exception:
        pass

    assert ran_startup
    assert startup_failed


@pytest.mark.asyncio
async def test_raise_on_shutdown():
    ran_startup = False
    ran_shutdown = False
    shutdown_failed = False

    async def startup():
        nonlocal ran_startup
        ran_startup = True

    async def shutdown():
        nonlocal ran_shutdown
        ran_shutdown = True
        raise

    app = Yaat(on_startup=[startup], on_shutdown=[shutdown])
    client = app.test_client()

    # mock async scope, receive, send
    asgi_scope = {"type": "lifespan"}

    async def asgi_receive(*args, **kwargs):
        return {"type": "lifespan.shutdown"} if ran_startup else {"type": "lifespan.startup"}

    async def asgi_send(*args , **kwargs):
        pass

    try:
        await app(asgi_scope, asgi_receive, asgi_send)
    except Exception:
        shutdown_failed = True

    assert ran_shutdown
    assert shutdown_failed
