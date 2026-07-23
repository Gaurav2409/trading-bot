import json
from datetime import UTC, datetime

from trading_os.research.live_watcher import ChannelSpec, LiveSourceWatcher
from trading_os.research.seen_store import InMemorySeenRecordStore
from trading_os.research.source_fetch import (
    FixtureSourceFetcher,
    RawFetchResult,
    SourceFetchError,
)

NOW = datetime(2026, 7, 21, 14, 0, tzinfo=UTC)
SINCE = datetime(2026, 7, 21, tzinfo=UTC)


def _nse_feed() -> str:
    return json.dumps([
        {
            "announcementId": "A1",
            "issuerId": "issuer:tanla",
            "category": "Financial Results",
            "dissemDateTime": "2026-07-21T18:30:00+05:30",
            "eventDate": "2026-07-21",
            "attachmentText": "Board approved audited results for Q1 FY27.",
        }
    ])


def _clock() -> datetime:
    return NOW


CHANNELS = (ChannelSpec(channel="nse", endpoint="nse/latest"),)


async def test_poll_seals_new_official_record() -> None:
    fetcher = FixtureSourceFetcher(
        {"nse/latest": RawFetchResult(endpoint="nse/latest", status=200, fetched_at=NOW, payload=_nse_feed())}
    )
    watcher = LiveSourceWatcher(fetcher, CHANNELS, InMemorySeenRecordStore(), clock=_clock)
    result = await watcher.poll(since=SINCE)
    assert len(result.new_records) == 1
    rec = result.new_records[0]
    assert rec.channel == "nse" and rec.record_id == "nse:A1"
    assert rec.received_at == NOW                       # stamped from clock
    assert rec.available_at == datetime(2026, 7, 21, 13, 0, tzinfo=UTC)  # dissem time, not now
    assert result.omitted_channels == ()


async def test_repoll_is_idempotent() -> None:
    fetcher = FixtureSourceFetcher(
        {"nse/latest": RawFetchResult(endpoint="nse/latest", status=200, fetched_at=NOW, payload=_nse_feed())}
    )
    store = InMemorySeenRecordStore()
    watcher = LiveSourceWatcher(fetcher, CHANNELS, store, clock=_clock)
    first = await watcher.poll(since=SINCE)
    second = await watcher.poll(since=SINCE)
    assert len(first.new_records) == 1
    assert second.new_records == ()                     # deduped, no duplicate


async def test_fetch_failure_is_omitted_not_fabricated() -> None:
    fetcher = FixtureSourceFetcher({"nse/latest": SourceFetchError("blocked")})
    watcher = LiveSourceWatcher(fetcher, CHANNELS, InMemorySeenRecordStore(), clock=_clock)
    result = await watcher.poll(since=SINCE)
    assert result.new_records == ()
    assert result.omitted_channels == ("nse",)          # attempted-but-omitted, no record


async def test_malformed_feed_is_omitted_not_fabricated() -> None:
    fetcher = FixtureSourceFetcher(
        {"nse/latest": RawFetchResult(endpoint="nse/latest", status=200, fetched_at=NOW, payload="not json")}
    )
    watcher = LiveSourceWatcher(fetcher, CHANNELS, InMemorySeenRecordStore(), clock=_clock)
    result = await watcher.poll(since=SINCE)
    assert result.new_records == ()
    assert result.omitted_channels == ("nse",)
