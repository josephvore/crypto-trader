from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from crypto_trader.core.config import AppConfig, Settings, load_config

router = APIRouter(tags=["config"])

DEFAULT_CFG = Path(__file__).resolve().parents[3] / "templates" / "configs" / "example.yaml"


@router.get("/config/settings")
async def get_settings() -> dict[str, Any]:
    s = Settings()
    return {
        "env": s.env,
        "log_level": s.log_level,
        "database_url": str(s.database_url),
        "redis_url": str(s.redis_url),
        "api_host": s.api_host,
        "api_port": s.api_port,
        "dry_run": s.dry_run,
        "api_password_set": bool(getattr(s, "api_password", None)),
    }


@router.get("/config/app", response_model=AppConfig)
async def get_app_config() -> AppConfig:
    try:
        return load_config(DEFAULT_CFG)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/config/app", response_model=AppConfig)
async def put_app_config(cfg: AppConfig) -> AppConfig:
    return cfg
