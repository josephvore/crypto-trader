import time
from collections.abc import Awaitable, Callable

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from crypto_trader.core.config import Settings
from crypto_trader.core.logging import prometheus_middleware_stats, setup_logging

from .routers import backtest, config, market_data, orders, positions, strategies
from .ws_manager import WSManager

app = FastAPI(title="Crypto Trader API")
settings = Settings()
setup_logging(level=settings.log_level)
ws_manager = WSManager()
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_auth(request: Request) -> None:
    expected = Settings().api_password
    if expected is None or expected == "":
        return
    provided = request.headers.get("X-API-Password")
    if provided != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.middleware("http")
async def prometheus_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    path = request.url.path
    method = request.method
    status = response.status_code
    prometheus_middleware_stats(path, method, status, elapsed)
    return response


@app.get("/healthz")
async def healthz() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/metrics")
async def metrics() -> PlainTextResponse:
    data = generate_latest()  # uses default REGISTRY
    return PlainTextResponse(content=data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


app.include_router(strategies.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(orders.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(positions.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(market_data.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(config.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(backtest.router, prefix="/api", dependencies=[Depends(require_auth)])


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    expected = Settings().api_password
    token = websocket.query_params.get("token")
    if (
        expected
        not in (
            None,
            "",
        )
        and token != expected
    ):
        await websocket.close(code=1008)
        return
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
