from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from crypto_trader.core.interfaces import ExecutionEngine as ExecutionProto
from crypto_trader.core.interfaces import Fill, Order


@dataclass
class PaperExecution(ExecutionProto):
    fee_bps: float = 5.0
    latency_ms: int = 50
    orders: dict[str, Order] = field(default_factory=dict)

    async def submit(self, order: Order) -> Order:
        self.orders[order.client_order_id] = order
        return order

    async def cancel(self, client_order_id: str) -> None:
        self.orders.pop(client_order_id, None)

    async def reconcile(self, price: float) -> list[Fill]:
        fills: list[Fill] = []
        for coid, o in list(self.orders.items()):
            fee = abs(o.qty) * price * (self.fee_bps / 10000.0)
            fills.append(
                Fill(
                    order_id=0,
                    trade_id=f"paper-{coid}",
                    symbol=o.symbol,
                    side=o.side,
                    qty=o.qty,
                    price=price,
                    fee=fee,
                    timestamp=datetime.now(tz=UTC),
                )
            )
            del self.orders[coid]
        return fills
