from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import pandas as pd  # type: ignore[import-untyped]

from crypto_trader.core.interfaces import MarketData
from crypto_trader.execution.paper import PaperExecution
from crypto_trader.portfolio.engine import PortfolioEngine


@dataclass
class BacktestResult:
    trades: int
    pnl: float
    equity_curve: pd.Series


class BacktestEngine:
    def __init__(self, strategy: Any, risk_model: Any) -> None:
        self.strategy = strategy
        self.risk = risk_model

    def run(self, df: pd.DataFrame, symbol: str, starting_cash: float = 10_000.0) -> BacktestResult:
        md = MarketData(symbol=symbol, df=df)
        exec_eng = PaperExecution()
        port = PortfolioEngine(cash=starting_cash)
        equity = []
        peak = starting_cash
        for i in range(max(200, 1), len(df)):
            window = df.iloc[: i + 1]
            md = MarketData(symbol=symbol, df=window)
            sigs = self.strategy.generate_signals(md)
            if not sigs:
                continue
            sig = sigs[0]
            size = self.risk.position_size(
                sig,
                window["close"],
                port.cash
                + sum((abs(p.qty) * window["close"].iloc[-1]) for p in port.positions.values()),
            )
            qty = 0.0
            price = window["close"].iloc[-1]
            if size > 0 and sig.direction != 0 and price > 0:
                qty = size / price * (1 if sig.direction > 0 else -1)
            if qty != 0:
                side: Literal["buy", "sell"] = "buy" if qty > 0 else "sell"
                from crypto_trader.core.interfaces import Fill  # local import to avoid circular

                fee = abs(qty) * price * (exec_eng.fee_bps / 10000.0)
                fills = [
                    Fill(
                        order_id=0,
                        trade_id=f"fill-{i}",
                        symbol=symbol,
                        side=side,
                        qty=abs(qty),
                        price=price,
                        fee=fee,
                        timestamp=window.index[-1].to_pydatetime(),
                    )
                ]
                port.on_fills(fills)
            equity_val = port.cash + sum(p.qty * price for p in port.positions.values())
            peak = max(peak, equity_val)
            if not self.risk.check_limits(
                equity_val, peak, abs(sum(p.qty * price for p in port.positions.values()))
            ):
                break
            equity.append(equity_val)
        eq_series = (
            pd.Series(equity, index=df.index[-len(equity) :])
            if equity
            else pd.Series([starting_cash])
        )
        pnl = (eq_series.iloc[-1] - starting_cash) if len(eq_series) else 0.0
        return BacktestResult(trades=0, pnl=float(pnl), equity_curve=eq_series)
