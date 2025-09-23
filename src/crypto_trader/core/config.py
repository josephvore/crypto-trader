from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import AnyUrl, BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    database_url: AnyUrl | str = "postgresql+asyncpg://trader:trader@localhost:5432/trader"
    redis_url: AnyUrl | str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    dry_run: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class ExchangeConfig(BaseModel):
    name: str
    api_key: str | None = None
    api_secret: str | None = None
    password: str | None = None
    sandbox: bool = True
    rate_limit_budget_per_min: int = 60
    timeout_ms: int = 10000


class StrategyConfig(BaseModel):
    class_path: str
    params: dict[str, Any] = Field(default_factory=dict)


class RiskConfig(BaseModel):
    max_drawdown_pct: float = 25.0
    max_position_pct: float = 20.0
    kill_switch_enabled: bool = True
    volatility_target_annual: float | None = None
    kelly_fraction_cap: float | None = None


class BacktestConfig(BaseModel):
    symbol: str
    timeframe: str = "1m"
    start: str
    end: str | None = None
    fee_bps: float = 10.0
    slippage_bps: float = 5.0
    latency_ms: int = 200
    leverage: float = 1.0
    data_source: Literal["ccxt", "csv"] = "ccxt"
    data_path: str | None = None


class AppConfig(BaseModel):
    mode: Literal["backtest", "tune", "paper", "live"] = "backtest"
    exchange: ExchangeConfig
    strategy: StrategyConfig
    risk: RiskConfig = Field(default_factory=RiskConfig)
    backtest: BacktestConfig | None = None
    database_url: AnyUrl | str | None = None
    redis_url: AnyUrl | str | None = None
    dry_run: bool | None = None


def load_config(path: str | Path) -> AppConfig:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    if p.suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    elif p.suffix == ".toml":
        data = tomllib.loads(p.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"Unsupported config format: {p.suffix}")
    return AppConfig.model_validate(data)
