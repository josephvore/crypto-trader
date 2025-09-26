from __future__ import annotations

from fastapi import APIRouter

from crypto_trader.api.schemas import PortfolioSummary, PositionResponse

router = APIRouter(tags=["positions"])

_positions: list[PositionResponse] = []
_cash = 10000.0


@router.get("/positions", response_model=list[PositionResponse])
async def get_positions() -> list[PositionResponse]:
    return _positions


@router.get("/portfolio", response_model=PortfolioSummary)
async def get_portfolio() -> PortfolioSummary:
    positions_value = sum(p.qty * p.avg_price for p in _positions)
    equity = _cash + positions_value
    realized = sum(p.realized_pnl for p in _positions)
    return PortfolioSummary(
        cash=_cash, positions_value=positions_value, equity=equity, realized_pnl=realized
    )
