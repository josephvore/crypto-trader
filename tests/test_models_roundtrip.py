from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncEngine

from crypto_trader.data.db import get_engine, get_session
from crypto_trader.data.models import Base, EquityCurve, Fill, OhlcvBar, Order, Position


@pytest.mark.asyncio
async def test_models_create_and_roundtrip() -> None:
    db_path = Path("./test_roundtrip.db")
    if db_path.exists():
        db_path.unlink()
    url = "sqlite+aiosqlite:///./test_roundtrip.db"
    engine: AsyncEngine = get_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    now = datetime.now(tz=UTC)
    async with get_session(url=url) as sess:
        sess.add(
            OhlcvBar(
                exchange="binance",
                symbol="BTC/USDT",
                timeframe="1m",
                timestamp=now,
                open=100.0,
                high=101.0,
                low=99.5,
                close=100.5,
                volume=10.0,
            )
        )
        await sess.commit()

    async with get_session(url=url) as sess:
        bar = (await sess.execute(OhlcvBar.__table__.select())).first()
        assert bar is not None

    async with get_session(url=url) as sess:
        order = Order(
            client_order_id="c1",
            exchange="binance",
            symbol="BTC/USDT",
            side="buy",
            type="market",
            qty=1.0,
            price=None,
            status="filled",
            created_at=now,
            updated_at=now,
        )
        sess.add(order)
        await sess.flush()
        sess.add(
            Fill(
                order_id=order.id,
                trade_id="t1",
                symbol="BTC/USDT",
                side="buy",
                qty=1.0,
                price=100.5,
                fee=0.05,
                timestamp=now,
            )
        )
        sess.add(
            Position(
                exchange="binance",
                symbol="BTC/USDT",
                qty=1.0,
                avg_price=100.5,
                realized_pnl=0.0,
                updated_at=now,
            )
        )
        sess.add(EquityCurve(timestamp=now, equity=10000.0))
        await sess.commit()

    async with get_session(url=url) as sess:
        cnt = (await sess.execute(select(func.count()).select_from(Order.__table__))).scalar_one()
        assert cnt == 1
        fills_cnt = (
            await sess.execute(select(func.count()).select_from(Fill.__table__))
        ).scalar_one()
        assert fills_cnt == 1
        pos_cnt = (
            await sess.execute(select(func.count()).select_from(Position.__table__))
        ).scalar_one()
        assert pos_cnt == 1
        eq_cnt = (
            await sess.execute(select(func.count()).select_from(EquityCurve.__table__))
        ).scalar_one()
        assert eq_cnt == 1
