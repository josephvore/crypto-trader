from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class MarketData:
    symbol: str
    timestamp: int
    price: float
    bid: float | None = None
    ask: float | None = None


class Strategy(Protocol):
    name: str

    def on_bar(self, data: MarketData) -> None: ...
    def generate_signals(self, data: Any) -> Any: ...


class RiskModel(Protocol):
    def position_size(self, signal: Any, volatility: float) -> float: ...
    def check_limits(self, portfolio: Any) -> bool: ...


class ExecutionEngine(Protocol):
    async def send(self, order: Any) -> Any: ...
    async def cancel(self, order_id: str) -> None: ...
    async def reconcile(self) -> None: ...


class PortfolioEngine(Protocol):
    def update(self, fill: Any) -> None: ...
    def exposure(self) -> dict[str, float]: ...
