from __future__ import annotations

from fastapi import APIRouter

from crypto_trader.api.schemas import StrategyConfigUpdate, StrategyResponse

router = APIRouter(tags=["strategies"])


_current_strategy: StrategyResponse | None = None


@router.get("/strategies", response_model=list[StrategyResponse])
async def list_strategies() -> list[StrategyResponse]:
    return [
        StrategyResponse(
            name="MomentumVolStrategy",
            class_path="crypto_trader.strategies.momo_vol:MomentumVolStrategy",
            params={},
        )
    ]


@router.get("/strategies/active", response_model=StrategyResponse | None)
async def get_active_strategy() -> StrategyResponse | None:
    return _current_strategy


@router.post("/strategies/config", response_model=StrategyResponse)
async def set_strategy_config(cfg: StrategyConfigUpdate) -> StrategyResponse:
    name = cfg.class_path.split(":")[-1]
    strategy = StrategyResponse(name=name, class_path=cfg.class_path, params=cfg.params)
    globals()["_current_strategy"] = strategy
    return strategy
