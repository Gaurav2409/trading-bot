from trading_os.brokers.fake import FakeBroker
from trading_os.brokers.models import OrderRequest, OrderSide, OrderType
from trading_os.execution.coordinator import ExecutionCoordinator
from trading_os.kernel.ids import AccountId, InstrumentId
from trading_os.ledger.store import EventStore


def _request(client_order_id: str = "intent-1") -> OrderRequest:
    from datetime import UTC, datetime

    return OrderRequest(
        account_id=AccountId("acct-1"),
        client_order_id=client_order_id,
        instrument_id=InstrumentId("NSE:INE009A01021"),
        side=OrderSide.BUY,
        quantity=1,
        order_type=OrderType.LIMIT,
        limit_price_minor=150_000,
        submitted_after=datetime.now(UTC),
    )


async def test_crash_before_ack_does_not_duplicate_on_restart(event_store: EventStore) -> None:
    broker = FakeBroker.empty(AccountId("acct-1"), "INR")
    coordinator = ExecutionCoordinator(event_store=event_store, broker=broker)
    request = _request()

    # First attempt appends the intent then submits.
    ack1 = await coordinator.submit(request)
    # Simulate a crash + restart: a fresh coordinator replays and must not submit
    # a duplicate for the same client_order_id.
    restarted = ExecutionCoordinator(event_store=event_store, broker=broker)
    ack2 = await restarted.submit(request)
    assert ack1.broker_order_id == ack2.broker_order_id


async def test_intent_is_appended_before_broker_submission(event_store: EventStore) -> None:
    broker = FakeBroker.empty(AccountId("acct-1"), "INR")
    coordinator = ExecutionCoordinator(event_store=event_store, broker=broker)
    await coordinator.submit(_request("intent-2"))
    rows = await event_store.read_stream("order:intent-2")
    types = [r.event_type for r in rows]
    assert types[0] == "OrderIntentCreated"
    assert "OrderAcknowledged" in types
