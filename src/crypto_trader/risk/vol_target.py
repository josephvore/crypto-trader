from __future__ import annotations

import math

import numpy as np
import pandas as pd  # type: ignore[import-untyped]


def target_size_volatility(
    price_series: pd.Series,
    balance: float,
    ann_vol_target: float = 0.2,
    window: int = 60,
    max_leverage: float = 2.0,
) -> float:
    rets = price_series.pct_change().dropna()
    if len(rets) == 0:
        return 0.0
    vol = rets.tail(window).std()
    if not np.isfinite(vol) or vol <= 0:
        return 0.0
    ann_vol = vol * math.sqrt(365 * 24 * 60)  # minutes to year
    raw = (ann_vol_target / ann_vol) * balance
    cap = max_leverage * balance
    return float(max(min(raw, cap), 0.0))
