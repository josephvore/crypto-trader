from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from crypto_trader.core.interfaces import Signal
from crypto_trader.risk.model import RiskModel


def test_risk_model_sizes_positive() -> None:
    prices = pd.Series([100 + i * 0.1 for i in range(200)])
    sig = Signal(
        symbol="BTC/USDT", timestamp=datetime.now(tz=UTC), direction=1, strength=0.8, meta={}
    )
    rm = RiskModel(
        params={
            "ann_vol_target": 0.2,
            "vol_window": 50,
            "max_leverage": 2.0,
            "kelly_hit_rate": 0.55,
            "kelly_avg_win": 1.2,
            "kelly_avg_loss": 1.0,
        }
    )
    size = rm.position_size(sig, prices, balance=10_000)
    assert size >= 0.0
