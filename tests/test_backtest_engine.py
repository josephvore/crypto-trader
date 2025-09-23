from __future__ import annotations

import numpy as np
import pandas as pd

from crypto_trader.backtest.engine import BacktestEngine
from crypto_trader.risk.model import RiskModel
from crypto_trader.strategies.momo_vol import MomentumVolStrategy


def _mk_df(trend: float = 0.1) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=500, freq="1min", tz="UTC")
    prices = pd.Series(100 + trend * np.arange(len(idx)), index=idx)
    df = pd.DataFrame(
        {
            "open": prices.shift(1).fillna(prices.iloc[0]),
            "high": prices + 0.5,
            "low": prices - 0.5,
            "close": prices,
            "volume": 1.0,
        },
        index=idx,
    )
    return df


def test_backtest_runs() -> None:
    df = _mk_df(trend=0.05)
    strat = MomentumVolStrategy(params={"ema_fast": 10, "ema_slow": 40, "adx_min": 0})
    risk = RiskModel(
        params={
            "ann_vol_target": 0.2,
            "vol_window": 50,
            "max_leverage": 2.0,
            "kelly_hit_rate": 0.55,
            "kelly_avg_win": 1.2,
            "kelly_avg_loss": 1.0,
        }
    )
    bt = BacktestEngine(strat, risk)
    res = bt.run(df, "BTC/USDT", starting_cash=10_000)
    assert res.equity_curve.iloc[-1] > 0
