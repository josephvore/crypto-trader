from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

OHLCV_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def ohlcv_to_dataframe(
    ohlcv: Iterable[Iterable[int | float]], columns: list[str] | None = None
) -> pd.DataFrame:
    cols = columns or OHLCV_COLUMNS
    df = pd.DataFrame(list(ohlcv), columns=cols)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.set_index("timestamp").sort_index()
    return df


def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    agg = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    out = df.resample(timeframe).agg(agg).dropna()
    return out


def forward_fill_gaps(df: pd.DataFrame, expected_freq: str) -> pd.DataFrame:
    idx = pd.date_range(start=df.index.min(), end=df.index.max(), freq=expected_freq, tz="UTC")
    out = df.reindex(idx)
    for col in ("open", "high", "low", "close"):
        if col in out.columns:
            out[col] = out[col].ffill()
    if "volume" in out.columns:
        out["volume"] = out["volume"].fillna(0)
    return out
