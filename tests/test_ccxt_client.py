from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from crypto_trader.data.ccxt_client import CCXTClient


@pytest.mark.asyncio
async def test_fetch_ohlcv_success() -> None:
    with patch("crypto_trader.data.ccxt_client.ccxt") as mock_ccxt:
        mock_exch_cls = mock_ccxt.binance
        mock_exchange = AsyncMock()
        mock_exch_cls.return_value = mock_exchange
        mock_exchange.fetch_ohlcv = AsyncMock(return_value=[[1, 2, 3, 4, 5, 6]])

        client = CCXTClient("binance", {"sandbox": True})
        out = await client.fetch_ohlcv("BTC/USDT", "1m")
        assert out == [[1, 2, 3, 4, 5, 6]]
        await client.close()
        mock_exchange.close.assert_awaited()


@pytest.mark.asyncio
async def test_fetch_trades_success() -> None:
    with patch("crypto_trader.data.ccxt_client.ccxt") as mock_ccxt:
        mock_exch_cls = mock_ccxt.kraken
        mock_exchange = AsyncMock()
        mock_exch_cls.return_value = mock_exchange
        mock_exchange.fetch_trades = AsyncMock(return_value=[{"id": "t1"}])

        client = CCXTClient("kraken", {"sandbox": True})
        out = await client.fetch_trades("ETH/USDT")
        assert out == [{"id": "t1"}]
        await client.close()


@pytest.mark.asyncio
async def test_unknown_exchange_raises() -> None:
    with patch("crypto_trader.data.ccxt_client.ccxt") as mock_ccxt:
        if hasattr(mock_ccxt, "doesnotexist"):
            delattr(mock_ccxt, "doesnotexist")
        with pytest.raises(ValueError):
            CCXTClient("doesnotexist")
