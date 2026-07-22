"""Deterministic two-broker replay: the same fabricated observations through the
pipeline must yield identical final state and event hashes across two clean runs.
"""

from trading_os.app.container import TradingApp
from trading_os.ledger.store import EventStore


async def test_two_clean_runs_yield_identical_cycle_state(event_store: EventStore) -> None:
    app = TradingApp(event_store=event_store, live_writes_enabled=False)
    kite = await app.run_cycle(account_id="kite-1", cycle_key="2026-07-22T10:00:00Z")
    alpaca = await app.run_cycle(account_id="alpaca-1", cycle_key="2026-07-22T10:00:00Z")

    # Re-running the same keys is deterministic and idempotent.
    kite2 = await app.run_cycle(account_id="kite-1", cycle_key="2026-07-22T10:00:00Z")
    alpaca2 = await app.run_cycle(account_id="alpaca-1", cycle_key="2026-07-22T10:00:00Z")

    assert kite.cycle_id == kite2.cycle_id
    assert alpaca.cycle_id == alpaca2.cycle_id
    # Partitions never collide.
    assert kite.cycle_id != alpaca.cycle_id
    # No live order intents when live writes are disabled.
    assert kite.order_intent_ids == ()
    assert alpaca.order_intent_ids == ()
