from __future__ import annotations

import asyncio
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from crypto_trader.core.interfaces import Fill, MarketData
from crypto_trader.execution.paper import PaperExecution
from crypto_trader.portfolio.engine import PortfolioEngine


@dataclass
class LiveConfig:
    exchange_id: str
    symbol: str
    timeframe: str
    window: int = 500
    poll_secs: float = 60.0
    sandbox: bool = True


class LiveRunner:
    def __init__(
        self,
        strategy: Any,
        risk: Any,
        portfolio: PortfolioEngine,
        cfg: LiveConfig,
        ccxt_client: Any | None = None,
    ) -> None:
        self.strategy = strategy
        self.risk = risk
        self.exec = PaperExecution()
        self.portfolio = portfolio
        self.cfg = cfg
        self._stop = asyncio.Event()
        self._client = ccxt_client

    async def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        from crypto_trader.data.ccxt_client import (
            CCXTClient,  # local to avoid heavy import at module load
        )

        self._client = CCXTClient(
            exchange_id=self.cfg.exchange_id,
            config={"sandbox": self.cfg.sandbox},
        )
        return self._client

    @staticmethod
    def _ohlcv_to_df(ohlcv: Iterable[list[float | int]]) -> pd.DataFrame:
        cols = ["timestamp", "open", "high", "low", "close", "volume"]
        df = pd.DataFrame(list(ohlcv), columns=cols)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.set_index("timestamp").sort_index()
        return df

    def _last_price(self, df: pd.DataFrame) -> float:
        return float(df["close"].iloc[-1])

    def _maybe_trade(self, df: pd.DataFrame) -> None:
        md = MarketData(symbol=self.cfg.symbol, df=df)
        sigs = self.strategy.generate_signals(md)
        if not sigs:
            return
        sig = sigs[0]
        price = self._last_price(df)
        equity = self.portfolio.cash + sum(p.qty * price for p in self.portfolio.positions.values())
        size = self.risk.position_size(sig, df["close"], equity)
        if size <= 0 or sig.direction == 0 or price <= 0:
            return
        qty = size / price * (1 if sig.direction > 0 else -1)
        side = "buy" if qty > 0 else "sell"
        fee = abs(qty) * price * (self.exec.fee_bps / 10000.0)
        fill = Fill(
            order_id=0,
            trade_id=f"live-{datetime.now(tz=UTC).timestamp()}",
            symbol=self.cfg.symbol,
            side=side,  # type: ignore[arg-type]
            qty=abs(qty),
            price=price,
            fee=fee,
            timestamp=datetime.now(tz=UTC),
        )
        self.portfolio.on_fills([fill])

    async def start_once(self) -> None:
        client = await self._ensure_client()
        if hasattr(client, "__aenter__"):
            async with client:
                ohlcv = await client.fetch_ohlcv(
                    self.cfg.symbol, self.cfg.timeframe, limit=self.cfg.window
                )
        else:
            ohlcv = await client.fetch_ohlcv(
                self.cfg.symbol, self.cfg.timeframe, limit=self.cfg.window
            )
        df = self._ohlcv_to_df(ohlcv)
        self._maybe_trade(df)

    async def start(self) -> None:
        client = await self._ensure_client()
        context_mgr = client if hasattr(client, "__aenter__") else _DummyAsyncContext(client)
        async with context_mgr as ex:
            while not self._stop.is_set():
                started = asyncio.get_running_loop().time()
                ohlcv = await ex.fetch_ohlcv(
                    self.cfg.symbol, self.cfg.timeframe, limit=self.cfg.window
                )
                df = self._ohlcv_to_df(ohlcv)
                self._maybe_trade(df)
                elapsed = asyncio.get_running_loop().time() - started
                sleep_for = max(0.0, self.cfg.poll_secs - elapsed)
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=sleep_for)
                except TimeoutError:
                    continue

    async def stop(self) -> None:
        self._stop.set()


class _DummyAsyncContext:
    def __init__(self, obj: Any) -> None:
        self._obj = obj

    async def __aenter__(self) -> Any:
        return self._obj

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None
