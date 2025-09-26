from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query

from crypto_trader.api.schemas import OrderRequest, OrderResponse

router = APIRouter(tags=["orders"])

_orders: dict[int, OrderResponse] = {}
_next_id = 1


@router.get("/orders", response_model=list[OrderResponse])
async def list_orders(status: str | None = Query(default=None)) -> list[OrderResponse]:
    if status:
        return [o for o in _orders.values() if o.status == status]
    return list(_orders.values())


@router.post("/orders", response_model=OrderResponse)
async def place_order(req: OrderRequest) -> OrderResponse:
    now = datetime.now(tz=UTC)
    oid = _next_id = max(_orders.keys(), default=0) + 1
    resp = OrderResponse(
        id=oid,
        client_order_id=req.client_order_id or f"cid-{oid}",
        exchange=req.exchange,
        symbol=req.symbol,
        side=req.side,
        type=req.type,
        qty=req.qty,
        price=req.price,
        status="new",
        created_at=now,
        updated_at=now,
    )
    _orders[oid] = resp
    return resp


@router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(order_id: int) -> OrderResponse:
    if order_id not in _orders:
        raise HTTPException(status_code=404, detail="order not found")
    o = _orders[order_id]
    o = OrderResponse(
        **{**o.model_dump(), "status": "canceled", "updated_at": datetime.now(tz=UTC)}
    )
    _orders[order_id] = o
    return o
