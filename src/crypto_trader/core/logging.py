from __future__ import annotations

import logging
import sys
from collections.abc import Callable, Iterable, Mapping, MutableMapping
from typing import Any, cast

import structlog
from prometheus_client import Counter, Histogram

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds", "HTTP request latency", ["path", "method"]
)
REQUEST_COUNT = Counter("http_requests_total", "HTTP requests", ["path", "method", "status_code"])
ORDERS_PLACED = Counter("orders_placed_total", "Orders placed")
EXECUTION_LATENCY = Histogram("execution_latency_seconds", "Order execution latency")


def setup_logging(level: str = "INFO") -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    shared_processors: Iterable[
        Callable[
            [Any, str, MutableMapping[str, Any]],
            Mapping[str, Any] | str | bytes | bytearray | tuple[Any, ...],
        ]
    ] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )

    structlog.configure(
        processors=shared_processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    logger = structlog.get_logger(name) if name else structlog.get_logger()
    return cast(structlog.stdlib.BoundLogger, logger)


def prometheus_middleware_stats(
    path: str, method: str, status_code: int, latency_seconds: float
) -> None:
    REQUEST_LATENCY.labels(path=path, method=method).observe(latency_seconds)
    REQUEST_COUNT.labels(path=path, method=method, status_code=str(status_code)).inc()
