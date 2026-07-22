from hashlib import sha256

from pydantic import BaseModel

from trading_os.kernel.events import new_event
from trading_os.ledger.store import EventStore


class CycleResult(BaseModel, frozen=True):
    cycle_id: str
    account_id: str
    cycle_key: str
    order_intent_ids: tuple[str, ...]


class TradingApp:
    """Application wiring for one idempotent decision cycle per (account,
    cycle_key, policy set). Re-running the same key produces one economic effect:
    the recorded cycle is returned instead of acting again."""

    def __init__(self, event_store: EventStore, *, live_writes_enabled: bool = False) -> None:
        self._events = event_store
        self._live_writes_enabled = live_writes_enabled

    def _cycle_stream(self, account_id: str, cycle_key: str) -> str:
        return f"cycle:{account_id}:{cycle_key}"

    def _cycle_id(self, account_id: str, cycle_key: str) -> str:
        return sha256(f"{account_id}:{cycle_key}".encode()).hexdigest()

    async def run_cycle(self, *, account_id: str, cycle_key: str) -> CycleResult:
        stream = self._cycle_stream(account_id, cycle_key)
        existing = await self._events.read_stream(stream)
        if existing:
            payload = existing[0].payload
            return CycleResult(
                cycle_id=payload["cycle_id"],
                account_id=account_id,
                cycle_key=cycle_key,
                order_intent_ids=tuple(payload.get("order_intent_ids", [])),
            )

        cycle_id = self._cycle_id(account_id, cycle_key)
        # V1 test cycle: observe -> reconcile -> project -> discover -> size ->
        # risk/compliance -> reserve -> execute only with live authority. With
        # live writes disabled, the cycle is deterministic and produces no order.
        order_intent_ids: tuple[str, ...] = ()
        event = new_event(
            "CycleCompleted",
            {
                "cycle_id": cycle_id,
                "account_id": account_id,
                "cycle_key": cycle_key,
                "order_intent_ids": list(order_intent_ids),
                "live_writes_enabled": self._live_writes_enabled,
            },
        )
        await self._events.append(stream, 0, [event])
        return CycleResult(
            cycle_id=cycle_id,
            account_id=account_id,
            cycle_key=cycle_key,
            order_intent_ids=order_intent_ids,
        )
