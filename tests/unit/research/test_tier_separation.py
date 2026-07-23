from datetime import UTC, datetime

from trading_os.research.calendar_watcher import WatchScheduled
from trading_os.research.live_watcher import WatchCycleResult

AT = datetime(2026, 7, 21, tzinfo=UTC)


def test_watch_scheduled_is_not_a_source_record() -> None:
    intent = WatchScheduled(
        issuer_id="issuer:tanla", event_kind="results", expected_at=AT,
        authority_tier="official_calendar", provenance_endpoint="nse/calendar",
    )
    # It has none of the SourceRecord sealing fields, so it cannot be reconciled
    # or admitted as evidence.
    for sealing_field in ("payload_hash", "available_at", "received_at", "channel", "content"):
        assert not hasattr(intent, sealing_field), sealing_field


def test_only_sealed_records_flow_from_the_official_tier() -> None:
    # The Tier-1 result type carries SourceRecords; there is no field on it that
    # accepts a WatchScheduled.
    assert "new_records" in WatchCycleResult.model_fields
    assert "intents" not in WatchCycleResult.model_fields
