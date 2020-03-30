from multiprocessing import Process
import httpx
import pytest
import typing
import uvicorn

from yaat import Yaat
from yaat.websockets import WebSocket, WebSocketDisconnect


# CONSTANTS
WS_TEST_SERVER_HOST = 'localhost'
WS_TEST_SERVER_PORT = 41864


@pytest.fixture
def app() -> Yaat:
    return Yaat()

@pytest.fixture
def client(app) -> httpx.AsyncClient:
    return app.test_client()

@pytest.fixture
def ws_uri() -> str:
    return f"ws://{WS_TEST_SERVER_HOST}:{WS_TEST_SERVER_PORT}"

@pytest.fixture(scope="session", autouse=True)
def ws_background_server() -> typing.AsyncGenerator:
    """
        WebSocket server to run in background for
        websocket unit tests
    """
    app = Yaat()

    # Endpoints
    @app.websocket_route("/hello")
    async def handler(websocket: WebSocket):
        await websocket.accept()
        await websocket.send_text("Hello")
        await websocket.close()

    @app.websocket_route("/text")
    async def handler(websocket: WebSocket):
        await websocket.accept()
        data = await websocket.receive_text()
        await websocket.send_text(f"You sent me '{data}'")
        await websocket.close()

    @app.websocket_route("/json")
    async def handler(websocket: WebSocket):
        await websocket.accept()
        data = await websocket.receive_json()
        await websocket.send_json(data)
        await websocket.close()

    @app.websocket_route("/bytes")
    async def handler(websocket: WebSocket):
        await websocket.accept("binary")
        data = await websocket.receive_bytes()
        await websocket.send_bytes(data)
        await websocket.close()

    @app.websocket_route("/query-param")
    async def handler(websocket: WebSocket):
        await websocket.accept()
        query = dict(websocket.query_params)
        await websocket.send_json(query)
        await websocket.close()

    @app.websocket_route("/headers")
    async def handler(websocket: WebSocket):
        await websocket.accept()
        headers = websocket.headers
        await websocket.send_json({"hello": headers["hello"]})
        await websocket.close()


    # run server with uvicorn as daemon
    process = Process(
        target=lambda: uvicorn.run(
            app,
            host=WS_TEST_SERVER_HOST,
            port=WS_TEST_SERVER_PORT,
        ),
        daemon=True
    )
    process.start()
    yield
    process.kill()
