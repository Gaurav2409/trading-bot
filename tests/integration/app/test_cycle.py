from tests.integration.app.conftest import build_test_app


async def test_same_cycle_key_has_one_economic_effect(event_store_session: object) -> None:
    app = build_test_app(event_store_session)
    first = await app.run_cycle(account_id="kite-1", cycle_key="2026-07-22T10:00:00Z")
    second = await app.run_cycle(account_id="kite-1", cycle_key="2026-07-22T10:00:00Z")
    assert first.cycle_id == second.cycle_id
    assert first.order_intent_ids == second.order_intent_ids


async def test_two_accounts_are_partitioned(event_store_session: object) -> None:
    app = build_test_app(event_store_session)
    kite = await app.run_cycle(account_id="kite-1", cycle_key="2026-07-22T10:00:00Z")
    alpaca = await app.run_cycle(account_id="alpaca-1", cycle_key="2026-07-22T10:00:00Z")
    assert kite.cycle_id != alpaca.cycle_id
