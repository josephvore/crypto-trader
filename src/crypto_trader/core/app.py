from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_trader.backtest.engine import BacktestEngine
from crypto_trader.core.config import AppConfig, Settings, load_config
from crypto_trader.core.plugins import build_from_path
from crypto_trader.live.runner import LiveConfig, LiveRunner
from crypto_trader.portfolio.engine import PortfolioEngine
from crypto_trader.risk.model import RiskModel
from crypto_trader.strategies.momo_vol import MomentumVolStrategy


class App:
    def __init__(self) -> None:
        self.settings: Settings = Settings()

    def init_project(self) -> None:
        Path("templates/configs").mkdir(parents=True, exist_ok=True)

    def _load_components(self, cfg: AppConfig) -> tuple[Any, Any]:
        strat_cfg = cfg.strategy
        risk_cfg = cfg.risk
        strategy = (
            build_from_path(strat_cfg.class_path, strat_cfg.params)
            if getattr(strat_cfg, "class_path", None)
            else MomentumVolStrategy(params=strat_cfg.params)
        )
        risk = (
            build_from_path(
                getattr(risk_cfg, "class_path", "crypto_trader.risk.model:RiskModel"),
                risk_cfg.model_dump(),
            )
            if hasattr(risk_cfg, "class_path")
            else RiskModel(params=risk_cfg.model_dump())
        )
        return strategy, risk

    def run_backtest(self, config_path: str) -> None:
        cfg = load_config(config_path)
        strategy, risk = self._load_components(cfg)
        bt = BacktestEngine(strategy, risk)
        bt_cfg = cfg.backtest
        if bt_cfg is None:
            raise ValueError("backtest section required in config")
        idx = pd.date_range("2024-01-01", periods=500, freq="1min", tz="UTC")
        prices = pd.Series(100 + 0.05 * np.arange(len(idx)), index=idx)
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
        res = bt.run(df, bt_cfg.symbol, starting_cash=10_000.0)
        print(
            {"pnl": res.pnl, "trades": res.trades, "last_equity": float(res.equity_curve.iloc[-1])}
        )

    def run_tuning(self, config_path: str) -> None:
        _ = config_path

    def run_paper(self, config_path: str) -> None:
        cfg = load_config(config_path)
        strategy, risk = self._load_components(cfg)
        runner = LiveRunner(
            strategy=strategy,
            risk=risk,
            portfolio=PortfolioEngine(
                cash=cfg.starting_cash if hasattr(cfg, "starting_cash") else 10_000.0
            ),
            cfg=LiveConfig(
                exchange_id=getattr(cfg, "exchange_id", "binance"),
                symbol=getattr(cfg.backtest, "symbol", "BTC/USDT") if cfg.backtest else "BTC/USDT",
                timeframe=getattr(cfg, "timeframe", "1m"),
                window=500,
                poll_secs=1.0,
                sandbox=True,
            ),
        )
        import asyncio

        asyncio.run(runner.start_once())

    def run_live(self, config_path: str) -> None:
        cfg = load_config(config_path)
        strategy, risk = self._load_components(cfg)
        runner = LiveRunner(
            strategy=strategy,
            risk=risk,
            portfolio=PortfolioEngine(
                cash=cfg.starting_cash if hasattr(cfg, "starting_cash") else 10_000.0
            ),
            cfg=LiveConfig(
                exchange_id=getattr(cfg, "exchange_id", "binance"),
                symbol=getattr(cfg.backtest, "symbol", "BTC/USDT") if cfg.backtest else "BTC/USDT",
                timeframe=getattr(cfg, "timeframe", "1m"),
                window=500,
                poll_secs=60.0,
                sandbox=bool(getattr(cfg, "sandbox", True)),
            ),
        )
        import asyncio

        with contextlib.suppress(KeyboardInterrupt):
            asyncio.run(runner.start())
