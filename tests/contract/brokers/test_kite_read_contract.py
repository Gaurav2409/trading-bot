import json
from pathlib import Path

from trading_os.brokers.kite import map_kite_snapshot
from trading_os.kernel.ids import AccountId


def test_kite_t1_and_pledged_quantities_are_not_saleable_twice() -> None:
    payload = json.loads(Path("tests/fixtures/brokers/kite_portfolio.json").read_text())
    snapshot = map_kite_snapshot(AccountId("kite-1"), payload)
    line = snapshot.positions[0]
    assert line.unsettled_quantity == 2
    assert line.pledged_quantity == 1
    assert line.broker_saleable_quantity == 7


def test_kite_snapshot_preserves_raw_hash_and_utc_receipt() -> None:
    from datetime import UTC

    payload = json.loads(Path("tests/fixtures/brokers/kite_portfolio.json").read_text())
    snapshot = map_kite_snapshot(AccountId("kite-1"), payload)
    assert snapshot.received_at.tzinfo is UTC
    assert snapshot.positions[0].source_record_hash
    assert snapshot.broker == "kite"
