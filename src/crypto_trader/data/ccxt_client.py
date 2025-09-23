from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import Any, cast

import ccxt.async_support as ccxt
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class CCXTClient:
    def __init__(self, exchange_id: str, config: dict[str, Any] | None = None) -> None:
        if not hasattr(ccxt, exchange_id):
            raise ValueError(f"Unknown exchange: {exchange_id}")
        cfg = config or {}
        cls = getattr(ccxt, exchange_id)
        self._exchange: ccxt.Exchange = cls(
            {
                "apiKey": cfg.get("api_key") or cfg.get("apiKey"),
                "secret": cfg.get("api_secret") or cfg.get("secret"),
                "password": cfg.get("password"),
                "enableRateLimit": cfg.get("enableRateLimit", cfg.get("rate_limit", True)),
                "timeout": cfg.get("timeout") or cfg.get("timeout_ms", 10000),
                **cfg.get("options", {}),
            }
        )
        sandbox = bool(cfg.get("sandbox", True))
        if sandbox and hasattr(self._exchange, "set_sandbox_mode"):
            with suppress(Exception):
                self._exchange.set_sandbox_mode(True)

        self._closed = False
        self._lock = asyncio.Lock()

    async def close(self) -> None:
        if not self._closed:
            await self._exchange.close()
            self._closed = True

    async def __aenter__(self) -> CCXTClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        await self.close()

    async def _retry_call(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        async for attempt in AsyncRetrying(
            wait=wait_exponential(multiplier=0.2, min=0.2, max=5),
            stop=stop_after_attempt(5),
            retry=retry_if_exception_type((ccxt.NetworkError, ccxt.ExchangeError)),
            reraise=True,
        ):
            with attempt:
                return await func(*args, **kwargs)
        raise RuntimeError("unreachable")

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since_ms: int | None = None,
        limit: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> list[list[float | int]]:
        async with self._lock:
            try:
                result = await self._retry_call(
                    self._exchange.fetch_ohlcv, symbol, timeframe, since_ms, limit, params or {}
                )
                return cast(list[list[float | int]], list(result))
            except RetryError as e:
                err = e.last_attempt.exception()
                raise cast(BaseException, err) from None

    async def fetch_trades(
        self,
        symbol: str,
        since_ms: int | None = None,
        limit: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        async with self._lock:
            try:
                result = await self._retry_call(
                    self._exchange.fetch_trades, symbol, since_ms, limit, params or {}
                )
                return cast(list[dict[str, Any]], list(result))
            except RetryError as e:
                err = e.last_attempt.exception()
                raise cast(BaseException, err) from None
