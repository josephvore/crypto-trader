from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from crypto_trader.live.runner import LiveConfig, LiveRunner
from crypto_trader.portfolio.engine import PortfolioEngine
from crypto_trader.risk.model import RiskModel
from crypto_trader.strategies.momo_vol import MomentumVolStrategy


class _FakeCCXTClient:
    async def __aenter__(self) -> _FakeCCXTClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500):
        start = datetime.now(tz=UTC) - timedelta(minutes=limit)
        idx = pd.date_range(start=start, periods=limit, freq="1min", tz="UTC")
        prices = pd.Series(100 + 0.05 * np.arange(len(idx)), index=idx)
        ohlcv = []
        for ts in idx:
            ts_ms = int(ts.timestamp() * 1000)
            close = float(prices.loc[ts])
            ohlcv.append([ts_ms, close, close + 0.5, close - 0.5, close, 1.0])
        return ohlcv


@pytest.mark.asyncio
async def test_live_runner_start_once_smoke() -> None:
    strat = MomentumVolStrategy(params={"ema_fast": 5, "ema_slow": 20, "adx_min": 0})
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
    port = PortfolioEngine(cash=10_000.0)
    cfg = LiveConfig(
        exchange_id="binance",
        symbol="BTC/USDT",
        timeframe="1m",
        window=200,
        poll_secs=0.01,
        sandbox=True,
    )
    runner = LiveRunner(
        strategy=strat, risk=risk, portfolio=port, cfg=cfg, ccxt_client=_FakeCCXTClient()
    )
    await runner.start_once()
    assert port.cash >= 0.0


@pytest.mark.asyncio
async def test_live_runner_loop_stop() -> None:
    strat = MomentumVolStrategy(params={"ema_fast": 5, "ema_slow": 20, "adx_min": 0})
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
    port = PortfolioEngine(cash=10_000.0)
    cfg = LiveConfig(
        exchange_id="binance",
        symbol="BTC/USDT",
        timeframe="1m",
        window=100,
        poll_secs=0.01,
        sandbox=True,
    )
    runner = LiveRunner(
        strategy=strat, risk=risk, portfolio=port, cfg=cfg, ccxt_client=_FakeCCXTClient()
    )

    async def run_short():
        task = asyncio.create_task(runner.start())
        await asyncio.sleep(0.05)
        await runner.stop()
        await asyncio.wait_for(task, timeout=2.0)

    await run_short()
    assert port.cash >= 0.0
