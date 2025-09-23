from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

from crypto_trader.core.interfaces import MarketData, Signal, Strategy


def _ema(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False).mean()


def _rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0).ewm(alpha=1 / window, adjust=False).mean()
    down = (-delta.clip(upper=0)).ewm(alpha=1 / window, adjust=False).mean()
    rs = up / (down.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def _adx(df: pd.DataFrame, window: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    plus_dm = (high.diff()).clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / window, adjust=False).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1 / window, adjust=False).mean() / atr.replace(0, np.nan))
    minus_di = 100 * (minus_dm.ewm(alpha=1 / window, adjust=False).mean() / atr.replace(0, np.nan))
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)).fillna(0)
    adx = dx.ewm(alpha=1 / window, adjust=False).mean()
    return adx.fillna(0)


@dataclass
class MomentumVolStrategy(Strategy):
    name: str = "momo_vol"
    params: dict[str, Any] = field(default_factory=dict)

    def generate_signals(self, data: MarketData) -> list[Signal]:
        df = data.df.copy()
        fast = int(self.params.get("ema_fast", 50))
        slow = int(self.params.get("ema_slow", 200))
        adx_win = int(self.params.get("adx_window", 14))
        adx_min = float(self.params.get("adx_min", 15))
        rsi_win = int(self.params.get("rsi_window", 14))
        rsi_ob = float(self.params.get("rsi_overbought", 70))
        rsi_os = float(self.params.get("rsi_oversold", 30))

        df["ema_fast"] = _ema(df["close"], fast)
        df["ema_slow"] = _ema(df["close"], slow)
        df["adx"] = _adx(df[["high", "low", "close"]], adx_win)
        df["rsi"] = _rsi(df["close"], rsi_win)
        spread = df["ema_fast"] - df["ema_slow"]
        strength = np.tanh((spread - spread.mean()) / (spread.std() + 1e-9))
        df["strength"] = strength.fillna(0.0)

        latest = df.iloc[-1]
        dirn = 0
        if (
            latest["ema_fast"] > latest["ema_slow"]
            and latest["adx"] >= adx_min
            and latest["rsi"] < rsi_ob
        ):
            dirn = 1
        elif (
            latest["ema_fast"] < latest["ema_slow"]
            and latest["adx"] >= adx_min
            and latest["rsi"] > rsi_os
        ):
            dirn = -1

        return [
            Signal(
                symbol=data.symbol,
                timestamp=df.index[-1].to_pydatetime(),
                direction=dirn,
                strength=float(latest["strength"]),
                meta={
                    "ema_fast": float(latest["ema_fast"]),
                    "ema_slow": float(latest["ema_slow"]),
                    "adx": float(latest["adx"]),
                    "rsi": float(latest["rsi"]),
                },
            )
        ]
