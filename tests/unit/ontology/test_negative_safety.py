from datetime import UTC, datetime, timedelta

from trading_os.ontology.instance_validation import (
    detects_false_identity_merge,
    detects_future_data_leak,
    detects_stale_snapshot,
)


def test_future_data_leak_is_detected() -> None:
    cutoff = datetime(2026, 7, 22, 10, 0, tzinfo=UTC)
    leaked = cutoff + timedelta(seconds=1)
    assert detects_future_data_leak(received_at=leaked, cutoff=cutoff) is True
    assert detects_future_data_leak(received_at=cutoff, cutoff=cutoff) is False


def test_false_identity_merge_without_governed_assertion_is_detected() -> None:
    # Two distinct securities asserted equal with no governed identity assertion.
    assert (
        detects_false_identity_merge(
            left="NSE:INE000000001",
            right="BSE:INE000000002",
            governed_assertion=None,
        )
        is True
    )
    assert (
        detects_false_identity_merge(
            left="NSE:INE000000001",
            right="NSE:INE000000001",
            governed_assertion="identity-assertion-1",
        )
        is False
    )


def test_stale_snapshot_is_detected() -> None:
    now = datetime(2026, 7, 22, 10, 0, tzinfo=UTC)
    built = now - timedelta(minutes=30)
    assert detects_stale_snapshot(built_at=built, now=now, max_age_seconds=600) is True
    assert detects_stale_snapshot(built_at=now, now=now, max_age_seconds=600) is False
