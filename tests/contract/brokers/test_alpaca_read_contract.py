import json
from pathlib import Path

from trading_os.brokers.alpaca import map_alpaca_snapshot
from trading_os.kernel.ids import AccountId


def test_alpaca_preexisting_position_appears_without_os_client_order_id() -> None:
    payload = json.loads(Path("tests/fixtures/brokers/alpaca_portfolio.json").read_text())
    snapshot = map_alpaca_snapshot(AccountId("alpaca-1"), payload)
    assert len(snapshot.positions) == 1
    position = snapshot.positions[0]
    assert position.settled_available_quantity == 5
    assert position.currency == "USD"
    # A pre-existing broker position has no OS client order id; the open order may.
    assert snapshot.open_orders[0].client_order_id is None


def test_alpaca_snapshot_records_cash_and_utc_receipt() -> None:
    from datetime import UTC

    payload = json.loads(Path("tests/fixtures/brokers/alpaca_portfolio.json").read_text())
    snapshot = map_alpaca_snapshot(AccountId("alpaca-1"), payload)
    assert snapshot.received_at.tzinfo is UTC
    assert snapshot.cash[0].currency == "USD"
    assert snapshot.broker == "alpaca"
