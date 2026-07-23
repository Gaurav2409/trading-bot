# tests/unit/research/test_seal_parity.py
import json
from datetime import UTC, datetime
from pathlib import Path

from trading_os.research.corporate_event_sources import RecordedNseAnnouncementAdapter
from trading_os.research.live_watcher import ChannelSpec, LiveSourceWatcher
from trading_os.research.seen_store import InMemorySeenRecordStore
from trading_os.research.source_fetch import FixtureSourceFetcher, RawFetchResult

NOW = datetime(2026, 7, 21, 14, 0, tzinfo=UTC)
ITEM = {
    "announcementId": "A1",
    "issuerId": "issuer:tanla",
    "category": "Financial Results",
    "dissemDateTime": "2026-07-21T18:30:00+05:30",
    "eventDate": "2026-07-21",
    "attachmentText": "Board approved audited results for Q1 FY27.",
}


async def test_live_and_recorded_seal_identically(tmp_path: Path) -> None:
    # Recorded path.
    fixture = tmp_path / "nse.json"
    fixture.write_text(json.dumps(ITEM))
    recorded = RecordedNseAnnouncementAdapter().capture(fixture, NOW)

    # Live path over the same item.
    fetcher = FixtureSourceFetcher(
        {"nse/latest": RawFetchResult(endpoint="nse/latest", status=200, fetched_at=NOW, payload=json.dumps([ITEM]))}
    )
    watcher = LiveSourceWatcher(
        fetcher, (ChannelSpec(channel="nse", endpoint="nse/latest"),),
        InMemorySeenRecordStore(), clock=lambda: NOW,
    )
    live = (await watcher.poll(since=datetime(2026, 7, 21, tzinfo=UTC))).new_records[0]

    # Identical in every field that describes the disclosure (payload_hash may
    # differ because the recorded adapter hashes file bytes and the live path
    # hashes the canonicalized item; everything else must match).
    for field in ("record_id", "source_id", "source_family_id", "channel",
                  "jurisdiction", "published_at", "available_at", "kind",
                  "is_issuer_submission", "content", "received_at"):
        assert getattr(live, field) == getattr(recorded, field), field
