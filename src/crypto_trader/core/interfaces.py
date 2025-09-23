from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Protocol

import pandas as pd  # type: ignore[import-untyped]


@dataclass(frozen=True)
class MarketData:
    symbol: str
    df: pd.DataFrame


@dataclass(frozen=True)
class Signal:
    symbol: str
    timestamp: datetime
    direction: int
    strength: float = 1.0
    meta: dict[str, Any] | None = None


OrderSide = Literal["buy", "sell"]
OrderType = Literal["market", "limit", "ioc", "post_only"]


@dataclass(frozen=True)
class Order:
    client_order_id: str
    exchange: str
    symbol: str
    side: OrderSide
    type: OrderType
    qty: float
    price: float | None = None
    status: str = "new"
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class Fill:
    order_id: int
    trade_id: str
    symbol: str
    side: OrderSide
    qty: float
    price: float
    fee: float
    timestamp: datetime


class Strategy(Protocol):
    name: str

    def generate_signals(self, data: MarketData) -> list[Signal]: ...


class RiskModel(Protocol):
    def position_size(self, signal: Signal, price_history: pd.Series, balance: float) -> float: ...
    def check_limits(self, equity: float, peak_equity: float, position_value: float) -> bool: ...


class ExecutionEngine(Protocol):
    async def submit(self, order: Order) -> Order: ...
    async def cancel(self, client_order_id: str) -> None: ...
    async def reconcile(self, price: float) -> list[Fill]: ...


class PortfolioEngine(Protocol):
    def on_fills(self, fills: list[Fill]) -> None: ...
