import json
from datetime import UTC, datetime

from trading_os.research.calendar_watcher import CalendarWatcher, WatchScheduled
from trading_os.research.source_fetch import (
    FixtureSourceFetcher,
    RawFetchResult,
    SourceFetchError,
)

AT = datetime(2026, 7, 18, tzinfo=UTC)


def _calendar_feed() -> str:
    return json.dumps([
        {"issuerId": "issuer:tanla", "eventKind": "results", "expectedDateTime": "2026-07-21T00:00:00+00:00"}
    ])


async def test_calendar_emits_watch_scheduled_intent() -> None:
    fetcher = FixtureSourceFetcher(
        {"nse/calendar": RawFetchResult(endpoint="nse/calendar", status=200, fetched_at=AT, payload=_calendar_feed())}
    )
    watcher = CalendarWatcher(fetcher, "nse/calendar")
    intents = await watcher.poll(since=AT)
    assert len(intents) == 1
    assert intents[0].issuer_id == "issuer:tanla"
    assert intents[0].event_kind == "results"
    assert intents[0].expected_at == datetime(2026, 7, 21, tzinfo=UTC)
    assert intents[0].authority_tier == "official_calendar"


async def test_calendar_fetch_failure_yields_no_intents() -> None:
    fetcher = FixtureSourceFetcher({"nse/calendar": SourceFetchError("blocked")})
    watcher = CalendarWatcher(fetcher, "nse/calendar")
    assert await watcher.poll(since=AT) == ()


async def test_non_list_calendar_payload_yields_no_intents() -> None:
    fetcher = FixtureSourceFetcher(
        {"nse/calendar": RawFetchResult(endpoint="nse/calendar", status=200, fetched_at=AT, payload='{"key": "val"}')}
    )
    watcher = CalendarWatcher(fetcher, "nse/calendar")
    assert await watcher.poll(since=AT) == ()


async def test_bad_item_is_skipped_but_valid_items_emit() -> None:
    payload = json.dumps([
        {"eventKind": "results", "expectedDateTime": "2026-07-21T00:00:00+00:00"},  # missing issuerId
        {"issuerId": "issuer:tanla", "eventKind": "results", "expectedDateTime": "2026-07-21T00:00:00+00:00"},
    ])
    fetcher = FixtureSourceFetcher(
        {"nse/calendar": RawFetchResult(endpoint="nse/calendar", status=200, fetched_at=AT, payload=payload)}
    )
    watcher = CalendarWatcher(fetcher, "nse/calendar")
    intents = await watcher.poll(since=AT)
    assert len(intents) == 1
    assert intents[0].issuer_id == "issuer:tanla"


def test_watch_scheduled_has_no_evidence_fields() -> None:
    # Tier boundary: a WatchScheduled cannot masquerade as evidence.
    fields = set(WatchScheduled.model_fields)
    forbidden = {"assessment", "support", "contradictions", "eligibility_effect",
                 "source_record_ids", "packet_id"}
    assert fields.isdisjoint(forbidden)
