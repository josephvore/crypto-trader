from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Protocol


@dataclass(frozen=True)
class MarketData:
    symbol: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    bid: float | None = None
    ask: float | None = None


SignalType = Literal["buy", "sell", "flat"]


@dataclass(frozen=True)
class Signal:
    symbol: str
    timestamp: int
    type: SignalType
    strength: float = 1.0
    meta: dict[str, Any] | None = None


OrderSide = Literal["buy", "sell"]
OrderType = Literal["market", "limit", "ioc", "post_only"]


@dataclass(frozen=True)
class Order:
    client_id: str
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: float
    price: float | None = None


@dataclass(frozen=True)
class Fill:
    order_client_id: str
    symbol: str
    side: OrderSide
    price: float
    quantity: float
    fee: float
    timestamp: int


class Strategy(Protocol):
    name: str

    def on_bar(self, data: MarketData) -> None: ...
    def generate_signals(self, data: list[MarketData]) -> list[Signal]: ...


class RiskModel(Protocol):
    def position_size(self, signal: Signal, volatility: float) -> float: ...
    def check_limits(self, portfolio: Any) -> bool: ...


class ExecutionEngine(Protocol):
    async def send(self, order: Order) -> str: ...
    async def cancel(self, order_id: str) -> None: ...
    async def reconcile(self) -> None: ...


class PortfolioEngine(Protocol):
    def update(self, fill: Fill) -> None: ...
    def exposure(self) -> dict[str, float]: ...
