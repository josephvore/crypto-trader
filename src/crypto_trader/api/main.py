import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from crypto_trader.core.config import Settings
from crypto_trader.core.logging import prometheus_middleware_stats, setup_logging

app = FastAPI(title="Crypto Trader API")
settings = Settings()
setup_logging(level=settings.log_level)


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
