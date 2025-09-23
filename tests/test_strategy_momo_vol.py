from __future__ import annotations

import numpy as np
import pandas as pd

from crypto_trader.core.interfaces import MarketData
from crypto_trader.strategies.momo_vol import MomentumVolStrategy


def _mk_df(trend: float = 0.1) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=400, freq="1min", tz="UTC")
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


def test_momo_vol_generates_signal() -> None:
    df = _mk_df(trend=0.2)
    md = MarketData(symbol="BTC/USDT", df=df)
    strat = MomentumVolStrategy(params={"ema_fast": 10, "ema_slow": 30, "adx_min": 0})
    sigs = strat.generate_signals(md)
    assert len(sigs) == 1
    assert sigs[0].direction in (-1, 0, 1)
