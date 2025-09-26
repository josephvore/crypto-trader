from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class StrategyResponse(BaseModel):
    name: str
    class_path: str
    params: dict[str, Any] = Field(default_factory=dict)


class StrategyConfigUpdate(BaseModel):
    class_path: str
    params: dict[str, Any] = Field(default_factory=dict)


OrderSide = Literal["buy", "sell"]
OrderType = Literal["market", "limit", "ioc", "post_only"]


class OrderRequest(BaseModel):
    client_order_id: str | None = None
    exchange: str = "paper"
    symbol: str
    side: OrderSide
    type: OrderType = "market"
    qty: float
    price: float | None = None


class OrderResponse(BaseModel):
    id: int
    client_order_id: str
    exchange: str
    symbol: str
    side: OrderSide
    type: OrderType
    qty: float
    price: float | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class FillResponse(BaseModel):
    order_id: int
    trade_id: str | None = None
    symbol: str
    side: OrderSide
    qty: float
    price: float
    fee: float
    timestamp: datetime


class PositionResponse(BaseModel):
    exchange: str
    symbol: str
    qty: float
    avg_price: float
    realized_pnl: float
    updated_at: datetime


class PortfolioSummary(BaseModel):
    cash: float
    positions_value: float
    equity: float
    realized_pnl: float


class OhlcvBar(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketDataResponse(BaseModel):
    exchange: str = "ccxt"
    symbol: str
    timeframe: str
    ohlcv: list[OhlcvBar]


class BacktestRequest(BaseModel):
    symbol: str
    timeframe: str = "1m"
    start: str
    end: str | None = None
    fee_bps: float = 10.0
    slippage_bps: float = 5.0
    latency_ms: int = 200
    leverage: float = 1.0


class EquityPoint(BaseModel):
    ts: int
    equity: float


class BacktestResponse(BaseModel):
    trades: int
    pnl: float
    equity_curve: list[EquityPoint]
