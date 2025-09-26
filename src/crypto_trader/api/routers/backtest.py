from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException

from crypto_trader.api.schemas import BacktestRequest, BacktestResponse, EquityPoint
from crypto_trader.backtest.engine import BacktestEngine
from crypto_trader.data.ccxt_client import CCXTClient
from crypto_trader.risk.model import RiskModel
from crypto_trader.strategies.momo_vol import MomentumVolStrategy

router = APIRouter(tags=["backtest"])


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(req: BacktestRequest) -> BacktestResponse:
    try:
        client = CCXTClient(exchange_id="binance", config={"sandbox": True})
        async with client:
            ohlcv = await client.fetch_ohlcv(req.symbol, req.timeframe, limit=2000)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.set_index("timestamp").sort_index()
        strat = MomentumVolStrategy(params={"ema_fast": 10, "ema_slow": 30, "adx_min": 5})
        risk = RiskModel(params={})
        engine = BacktestEngine(strategy=strat, risk_model=risk)
        res = engine.run(df=df, symbol=req.symbol)
        equity_points = [
            EquityPoint(ts=int(ts.timestamp() * 1000), equity=float(val))
            for ts, val in res.equity_curve.items()
        ]
        return BacktestResponse(trades=res.trades, pnl=res.pnl, equity_curve=equity_points)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
