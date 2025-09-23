from __future__ import annotations

from dataclasses import dataclass, field

from crypto_trader.core.interfaces import Fill


@dataclass
class PositionState:
    qty: float = 0.0
    avg_price: float = 0.0
    realized_pnl: float = 0.0


@dataclass
class PortfolioEngine:
    cash: float
    positions: dict[str, PositionState] = field(default_factory=dict)
    fees_paid: float = 0.0

    def on_fills(self, fills: list[Fill]) -> None:
        for f in fills:
            pos = self.positions.setdefault(f.symbol, PositionState())
            side_mult = 1.0 if f.side == "buy" else -1.0
            trade_qty = side_mult * f.qty
            notional = f.qty * f.price
            if pos.qty == 0.0 or (pos.qty > 0 and trade_qty > 0) or (pos.qty < 0 and trade_qty < 0):
                new_qty = pos.qty + trade_qty
                pos.avg_price = (pos.avg_price * pos.qty + f.price * trade_qty) / (
                    new_qty if new_qty != 0 else 1
                )
                pos.qty = new_qty
            else:
                close_qty = min(abs(pos.qty), abs(trade_qty)) * (1 if pos.qty > 0 else -1)
                pnl = close_qty * (pos.avg_price - f.price) * (-1 if pos.qty > 0 else 1)
                pos.realized_pnl += pnl
                pos.qty += trade_qty
                if pos.qty == 0:
                    pos.avg_price = 0.0
            self.cash -= notional * side_mult
            self.fees_paid += f.fee
