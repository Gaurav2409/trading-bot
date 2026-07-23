"""Tier-1 live source watcher: official exchange feed, dedup, fail-safe.

Polls exchange-wide official feeds via the SourceFetchPort, normalizes and
seals each announcement into an immutable SourceRecord, deduplicates via the
injected SeenRecordStore, and returns only newly-seen records.

Fail-safe contract:
- SourceFetchError, JSON decode error, or a non-list payload: the whole channel
  is added to ``omitted_channels`` — no record is sealed, no fabrication occurs.
- Per-item RecordedSourceError (malformed field in a single announcement): that
  item is skipped silently; the rest of the channel proceeds normally.
"""

import json
from collections.abc import Callable
from datetime import datetime
from hashlib import sha256

from pydantic import BaseModel

from trading_os.research.corporate_event_sources import (
    RecordedSourceError,
    normalize_bse_fields,
    normalize_nse_fields,
    seal_record,
)
from trading_os.research.seen_store import SeenRecordStore
from trading_os.research.source_fetch import (
    SourceFetchError,
    SourceFetchPort,
)
from trading_os.research.watchers import SourceRecord

_NORMALIZERS = {"nse": normalize_nse_fields, "bse": normalize_bse_fields}


class ChannelSpec(BaseModel, frozen=True):
    channel: str
    endpoint: str


class WatchCycleResult(BaseModel, frozen=True):
    new_records: tuple[SourceRecord, ...]
    attempted_channels: tuple[str, ...]
    omitted_channels: tuple[str, ...]


class LiveSourceWatcher:
    """Tier 1 official watcher: seal new announcements, dedup, fail safe."""

    def __init__(
        self,
        fetch_port: SourceFetchPort,
        channels: tuple[ChannelSpec, ...],
        seen_store: SeenRecordStore,
        *,
        clock: Callable[[], datetime],
    ) -> None:
        self._fetch = fetch_port
        self._channels = channels
        self._seen = seen_store
        self._clock = clock

    async def poll(self, since: datetime) -> WatchCycleResult:
        new_records: list[SourceRecord] = []
        attempted: list[str] = []
        omitted: list[str] = []

        for spec in self._channels:
            attempted.append(spec.channel)
            normalizer = _NORMALIZERS.get(spec.channel)
            if normalizer is None:
                omitted.append(spec.channel)
                continue
            try:
                raw = await self._fetch.fetch(spec.endpoint, since=since)
                items = json.loads(raw.payload)
                if not isinstance(items, list):
                    raise RecordedSourceError("feed payload must be a JSON array")
            except (SourceFetchError, json.JSONDecodeError, RecordedSourceError):
                omitted.append(spec.channel)
                continue

            received_at = self._clock()
            for item in items:
                if not isinstance(item, dict):
                    continue
                try:
                    normalized = normalizer(item)
                except RecordedSourceError:
                    continue
                payload_hash = (
                    f"sha256:{sha256(json.dumps(item, sort_keys=True).encode()).hexdigest()}"
                )
                if not self._seen.is_new(spec.channel, normalized.record_id, payload_hash):
                    continue
                new_records.append(
                    seal_record(
                        normalized,
                        channel=spec.channel,
                        received_at=received_at,
                        payload_hash=payload_hash,
                    )
                )

        return WatchCycleResult(
            new_records=tuple(new_records),
            attempted_channels=tuple(attempted),
            omitted_channels=tuple(omitted),
        )
