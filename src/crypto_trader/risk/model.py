from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from crypto_trader.core.interfaces import RiskModel as RiskModelProto
from crypto_trader.core.interfaces import Signal
from crypto_trader.risk.kelly_cap import kelly_fraction
from crypto_trader.risk.vol_target import target_size_volatility


@dataclass
class RiskModel(RiskModelProto):
    params: dict[str, Any]

    def position_size(self, signal: Signal, price_history: pd.Series, balance: float) -> float:
        ann_vol_target = float(self.params.get("ann_vol_target", 0.2))
        window = int(self.params.get("vol_window", 60))
        max_lev = float(self.params.get("max_leverage", 2.0))
        base_size = target_size_volatility(price_history, balance, ann_vol_target, window, max_lev)
        hr = float(self.params.get("kelly_hit_rate", 0.5))
        aw = float(self.params.get("kelly_avg_win", 1.0))
        al = float(self.params.get("kelly_avg_loss", 1.0))
        cap = float(self.params.get("kelly_cap_fraction", 0.25))
        mult = kelly_fraction(hr, aw, al, cap_fraction=cap)
        size = base_size * abs(signal.strength) * mult
        return float(size)

    def check_limits(self, equity: float, peak_equity: float, position_value: float) -> bool:
        max_dd = float(self.params.get("max_drawdown_pct", 0.3))
        max_pos = float(self.params.get("max_position_pct", 0.5))
        dd_breach = peak_equity > 0 and (peak_equity - equity) / peak_equity > max_dd
        pos_breach = equity > 0 and (position_value / equity) > max_pos
        return not (dd_breach or pos_breach)
