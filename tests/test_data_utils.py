from __future__ import annotations

import pandas as pd

from crypto_trader.data.utils import forward_fill_gaps, ohlcv_to_dataframe, resample_ohlcv


def test_ohlcv_to_dataframe_and_resample() -> None:
    base = 1_700_000_000_000  # ms epoch
    ohlcv = [
        [base, 100.0, 101.0, 99.5, 100.5, 10.0],
        [base + 30_000, 100.5, 102.0, 100.0, 101.0, 12.0],
    ]
    df = ohlcv_to_dataframe(ohlcv)
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    out = resample_ohlcv(df, "1min")
    assert len(out) == 1
    row = out.iloc[0]
    assert row["open"] == 100.0
    assert row["high"] == 102.0
    assert row["low"] == 99.5
    assert row["close"] == 101.0
    assert row["volume"] == 22.0


def test_forward_fill_gaps() -> None:
    idx = pd.to_datetime(
        [1_700_000_000_000, 1_700_000_060_000, 1_700_000_120_000], unit="ms", utc=True
    )
    df = pd.DataFrame(
        {
            "open": [100, 100.5, 101],
            "high": [101, 101.5, 102],
            "low": [99.5, 100, 100.5],
            "close": [100.2, 100.7, 101.2],
            "volume": [10, 11, 9],
        },
        index=idx,
    )
    df = df.iloc[[0, 2]]
    out = forward_fill_gaps(df, "1min")
    assert len(out) == 3
    assert out.iloc[1]["close"] == df.iloc[0]["close"]
    assert out.iloc[1]["volume"] == 0
