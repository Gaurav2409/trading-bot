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
    PositionObservation,
)
from trading_os.kernel.ids import AccountId, SnapshotId
from trading_os.policy.capability import AuthorityDecision

BROKER = "alpaca"


def _minor(value: Any) -> int | None:
    if value is None:
        return None
    return round(float(value) * 100)


def _hash(obj: Any) -> str:
    return sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def _map_position(position: dict[str, Any]) -> PositionObservation:
    total = int(float(position["qty"]))
    available = int(float(position.get("qty_available", position["qty"])))
    return PositionObservation(
        instrument_id=canonical_equity_id(position["exchange"], position["symbol"]),
        settled_available_quantity=available,
        unsettled_quantity=max(0, total - available),
        pledged_quantity=0,
        authorization_blocked_quantity=0,
        broker_saleable_quantity=available,
        average_cost_minor=_minor(position.get("avg_entry_price")),
        last_price_minor=_minor(position.get("current_price")),
        currency="USD",
        source_record_hash=_hash(position),
    )


def _map_cash(account: dict[str, Any]) -> tuple[CashObservation, ...]:
    if not account:
        return ()
    return (
        CashObservation(
            currency=account.get("currency", "USD"),
            settled_minor=_minor(account.get("cash", 0)) or 0,
            broker_available_minor=_minor(account.get("buying_power", 0)) or 0,
            unsettled_minor=0,
            source_record_hash=_hash(account),
        ),
    )


def _map_orders(orders: list[dict[str, Any]]) -> tuple[OpenOrderObservation, ...]:
    mapped: list[OpenOrderObservation] = []
    for order in orders:
        filled = int(float(order.get("filled_qty", 0)))
        total = int(float(order["qty"]))
        mapped.append(
            OpenOrderObservation(
                broker_order_id=str(order["id"]),
                client_order_id=order.get("client_order_id"),
                instrument_id=canonical_equity_id(order["exchange"], order["symbol"]),
                side=OrderSide(order["side"].lower()),
                remaining_quantity=max(0, total - filled),
                limit_price_minor=_minor(order.get("limit_price")),
                status=str(order.get("status", "unknown")),
            )
        )
    return tuple(mapped)


def map_alpaca_snapshot(
    account_id: AccountId, payload: dict[str, Any]
) -> BrokerSnapshotObservation:
    received_at = datetime.now(UTC)
    positions = tuple(_map_position(p) for p in payload.get("positions", []))
    cash = _map_cash(payload.get("account", {}))
    open_orders = _map_orders(payload.get("open_orders", []))
    return BrokerSnapshotObservation(
        observation_id=SnapshotId(f"alpaca-obs-{account_id}-{received_at.isoformat()}"),
        account_id=account_id,
        broker=BROKER,
        observed_at=None,
        received_at=received_at,
        positions=positions,
        cash=cash,
        open_orders=open_orders,
    )


class AlpacaBroker:
    """Read-only Alpaca adapter. Live writes are enabled only in Task 15."""

    def __init__(self, account_id: AccountId, client: Any) -> None:
        self._account_id = account_id
        self._client = client

    async def observe_account(self) -> BrokerSnapshotObservation:
        import anyio

        received_at = datetime.now(UTC)
        missing: set[str] = set()
        payload: dict[str, Any] = {}
        for segment, call in (
            ("positions", self._client.get_all_positions),
            ("account", self._client.get_account),
            ("open_orders", self._client.get_orders),
        ):
            try:
                payload[segment] = await anyio.to_thread.run_sync(call)
            except Exception:  # noqa: BLE001 - a failed segment is recorded, not fatal
                missing.add(segment)
        snapshot = map_alpaca_snapshot(self._account_id, payload)
        return snapshot.model_copy(
            update={"received_at": received_at, "missing_segments": frozenset(missing)}
        )

    async def submit_order(
        self, request: OrderRequest, authority: AuthorityDecision | None = None
    ) -> OrderAck:
        if authority is None or not authority.allowed:
            reason = "no authority" if authority is None else authority.reason
            raise LiveWriteDisabled(f"Alpaca live write denied: {reason}")
        import anyio

        response = await anyio.to_thread.run_sync(
            lambda: self._client.submit_order(
                symbol=str(request.instrument_id).split(":", 1)[1],
                qty=request.quantity,
                side=request.side.value,
                type="limit",
                limit_price=request.limit_price_minor / 100,
                time_in_force="day",
                client_order_id=request.client_order_id,
            )
        )
        return OrderAck(
            client_order_id=request.client_order_id,
            broker_order_id=str(response["id"]),
            accepted_at=datetime.now(UTC),
            status="accepted",
        )

    async def cancel_order(self, broker_order_id: str) -> None:
        import anyio

        await anyio.to_thread.run_sync(
            lambda: self._client.cancel_order_by_id(broker_order_id)
        )
