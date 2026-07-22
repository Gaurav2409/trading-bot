import pytest

from trading_os.kernel.events import new_event
from trading_os.ledger.store import ConcurrencyError, EventStore


async def test_append_is_idempotent_and_version_checked(event_store: EventStore) -> None:
    event = new_event("CapitalEnvelopeReleased", {"release_id": "capital-1"})
    assert await event_store.append("account:acct-1", 0, [event]) == 1
    assert await event_store.append("account:acct-1", 1, [event]) == 1
    with pytest.raises(ConcurrencyError):
        await event_store.append("account:acct-1", 0, [new_event("Other", {})])


async def test_replay_reads_stream_in_order(event_store: EventStore) -> None:
    first = new_event("A", {"n": 1})
    second = new_event("B", {"n": 2})
    await event_store.append("account:acct-2", 0, [first, second])
    rows = await event_store.read_stream("account:acct-2")
    assert [row.event_type for row in rows] == ["A", "B"]
    assert [row.stream_version for row in rows] == [1, 2]


async def test_replay_twice_yields_identical_state(event_store: EventStore) -> None:
    events = [new_event("X", {"i": i}) for i in range(3)]
    await event_store.append("account:acct-3", 0, events)
    first = [(r.event_id, r.stream_version, r.event_type) for r in await event_store.read_stream("account:acct-3")]
    second = [(r.event_id, r.stream_version, r.event_type) for r in await event_store.read_stream("account:acct-3")]
    assert first == second


async def test_conflicting_stream_version_is_rejected(event_store: EventStore) -> None:
    await event_store.append("account:acct-4", 0, [new_event("A", {})])
    with pytest.raises(ConcurrencyError):
        await event_store.append("account:acct-4", 0, [new_event("B", {})])


async def test_event_log_rejects_update_and_delete(event_store: EventStore, apply_migrations: None) -> None:
    from sqlalchemy import text

    await event_store.append("account:acct-5", 0, [new_event("A", {})])
    session = event_store._session  # noqa: SLF001 - integration test asserts DB-level guard
    with pytest.raises(Exception, match="append-only"):
        await session.execute(text("UPDATE event_log SET event_type='X' WHERE stream_id='account:acct-5'"))
    await session.rollback()
    with pytest.raises(Exception, match="append-only"):
        await session.execute(text("DELETE FROM event_log WHERE stream_id='account:acct-5'"))
    await session.rollback()

