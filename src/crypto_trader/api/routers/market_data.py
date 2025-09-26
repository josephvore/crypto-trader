from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from crypto_trader.api.schemas import MarketDataResponse, OhlcvBar
from crypto_trader.data.ccxt_client import CCXTClient

router = APIRouter(tags=["market-data"])


@router.get("/market-data/ohlcv", response_model=MarketDataResponse)
async def get_ohlcv(
    symbol: str = Query(...),
    timeframe: str = Query(default="1m"),
    limit: int = Query(default=500, ge=1, le=2000),
) -> MarketDataResponse:
    try:
        client = CCXTClient(exchange_id="binance", config={"sandbox": True})
        async with client:
            ohlcv = await client.fetch_ohlcv(symbol, timeframe, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    bars = [
        OhlcvBar(
            timestamp=int(row[0]),
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume=float(row[5]),
        )
        for row in ohlcv
    ]
    return MarketDataResponse(symbol=symbol, timeframe=timeframe, ohlcv=bars)
