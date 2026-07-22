import json
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any

from trading_os.brokers.mapping import LiveWriteDisabled, canonical_equity_id
from trading_os.brokers.models import (
    BrokerSnapshotObservation,
    CashObservation,
    OpenOrderObservation,
    OrderAck,
    OrderRequest,
    OrderSide,
    OrderType,
    PositionObservation,
)
from trading_os.kernel.ids import AccountId, SnapshotId
from trading_os.policy.capability import AuthorityDecision

BROKER = "kite"


def _minor(value: Any) -> int | None:
    if value is None:
        return None
    return round(float(value) * 100)


def _hash(obj: Any) -> str:
    return sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def _map_holding(holding: dict[str, Any]) -> PositionObservation:
    # Kite holdings: `quantity` is settled/free delivery qty, `t1_quantity` is
    # unsettled T+1, `pledged_quantity` is pledged. These are non-overlapping and
    # must never be summed into "saleable"; `authorised_quantity` is saleable now.
    return PositionObservation(
        instrument_id=canonical_equity_id(holding["exchange"], holding["isin"]),
        settled_available_quantity=int(holding.get("quantity", 0)),
        unsettled_quantity=int(holding.get("t1_quantity", 0)),
        pledged_quantity=int(holding.get("pledged_quantity", 0)),
        authorization_blocked_quantity=0,
        broker_saleable_quantity=int(holding.get("authorised_quantity", 0)),
        average_cost_minor=_minor(holding.get("average_price")),
        last_price_minor=_minor(holding.get("last_price")),
        currency="INR",
        source_record_hash=_hash(holding),
    )


def _map_cash(margins: dict[str, Any]) -> tuple[CashObservation, ...]:
    equity = margins.get("equity")
    if not equity:
        return ()
    available = equity.get("available", {})
    return (
        CashObservation(
            currency="INR",
            settled_minor=_minor(available.get("cash", 0)) or 0,
            broker_available_minor=_minor(available.get("live_balance", 0)) or 0,
            unsettled_minor=0,
            source_record_hash=_hash(equity),
        ),
    )


def _map_orders(orders: list[dict[str, Any]]) -> tuple[OpenOrderObservation, ...]:
    mapped: list[OpenOrderObservation] = []
    for order in orders:
        mapped.append(
            OpenOrderObservation(
                broker_order_id=str(order["order_id"]),
                client_order_id=order.get("tag"),
                instrument_id=canonical_equity_id(order["exchange"], order["tradingsymbol"]),
                side=OrderSide(order["transaction_type"].lower()),
                remaining_quantity=int(order.get("pending_quantity", 0)),
                limit_price_minor=_minor(order.get("price")),
                status=str(order.get("status", "unknown")),
            )
        )
    return tuple(mapped)


def map_kite_snapshot(account_id: AccountId, payload: dict[str, Any]) -> BrokerSnapshotObservation:
    received_at = datetime.now(UTC)
    positions = tuple(_map_holding(h) for h in payload.get("holdings", []))
    cash = _map_cash(payload.get("margins", {}))
    open_orders = _map_orders(payload.get("orders", []))
    return BrokerSnapshotObservation(
        observation_id=SnapshotId(f"kite-obs-{account_id}-{received_at.isoformat()}"),
        account_id=account_id,
        broker=BROKER,
        observed_at=None,
        received_at=received_at,
        positions=positions,
        cash=cash,
        open_orders=open_orders,
    )


class KiteBroker:
    """Read-only Kite adapter. Live writes are enabled only in Task 15."""

    def __init__(self, account_id: AccountId, client: Any) -> None:
        self._account_id = account_id
        self._client = client

    async def observe_account(self) -> BrokerSnapshotObservation:
        import anyio

        received_at = datetime.now(UTC)
        missing: set[str] = set()
        payload: dict[str, Any] = {}
        for segment, call in (
            ("holdings", self._client.holdings),
            ("positions", self._client.positions),
            ("orders", self._client.orders),
            ("margins", self._client.margins),
        ):
            try:
                payload[segment] = await anyio.to_thread.run_sync(call)
            except Exception:  # noqa: BLE001 - a failed segment is recorded, not fatal
                missing.add(segment)
        snapshot = map_kite_snapshot(self._account_id, payload)
        return snapshot.model_copy(
            update={"received_at": received_at, "missing_segments": frozenset(missing)}
        )

    async def submit_order(
        self, request: OrderRequest, authority: AuthorityDecision | None = None
    ) -> OrderAck:
        if authority is None or not authority.allowed:
            reason = "no authority" if authority is None else authority.reason
            raise LiveWriteDisabled(f"Kite live write denied: {reason}")
        import anyio

        # India cash equity: only limit / stop-limit reach the SDK; never market.
        kite_order_type = "LIMIT" if request.order_type is OrderType.LIMIT else "SL"
        response = await anyio.to_thread.run_sync(
            lambda: self._client.place_order(
                variety="regular",
                exchange=str(request.instrument_id).split(":", 1)[0],
                tradingsymbol=str(request.instrument_id).split(":", 1)[1],
                transaction_type=request.side.value.upper(),
                quantity=request.quantity,
                product="CNC",
                order_type=kite_order_type,
                price=request.limit_price_minor / 100,
                tag=request.client_order_id[:20],
            )
        )
        return OrderAck(
            client_order_id=request.client_order_id,
            broker_order_id=str(response["order_id"]),
            accepted_at=datetime.now(UTC),
            status="accepted",
        )

    async def cancel_order(self, broker_order_id: str) -> None:
        import anyio

        await anyio.to_thread.run_sync(
            lambda: self._client.cancel_order(variety="regular", order_id=broker_order_id)
        )
