# Live NSE/BSE SourceWatcher + Early-Signal Tier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add live NSE/BSE official-announcement ingestion (evidence-bearing) plus an early-signal calendar tier (attention-only), behind one transport seam, all offline-testable, with the live HTTP fetch integration-tagged.

**Architecture:** A `SourceFetchPort` abstracts transport (real integration-tagged `HttpSourceFetcher` + deterministic `FixtureSourceFetcher`). A `LiveSourceWatcher` polls the exchange-wide official feed, normalizes via a shared core extracted from the recorded adapters, seals `SourceRecord`s, and dedups. A `CalendarWatcher` polls the board-meeting calendar and emits `WatchScheduled` intents that can never become evidence. Both consume the existing `SourceRecord`, coverage, and scheduler types.

**Tech Stack:** Python 3.11+ (venv 3.13), Pydantic v2 (frozen models), httpx (already a dependency), pytest / pytest-asyncio (`asyncio_mode=auto`), ruff, mypy --strict.

## Global Constraints

- Keep the analysis seam, `admit_packet`, decision hot path, live-authority, and ontology promotion path **unchanged**.
- Agents never fetch; the watcher seals records **before** any analysis run (spec §14).
- No early-signal source may carry positive evidentiary weight; `WatchScheduled` has **no path** to `EvidencePacket` (type boundary).
- No executable number is introduced anywhere; no secrets/tokens/account numbers committed.
- All watcher **logic** is offline-deterministic (tested via `FixtureSourceFetcher`); the live HTTP fetcher is `@pytest.mark.integration` and excluded from the default gate.
- Cutoff integrity: `received_at` stamped at seal time from an injected clock; `available_at` = disclosure dissemination time. No look-ahead.
- Sealed live records are byte-identical in shape to the recorded adapters' output (shared normalizer; parity test enforces it).
- Follow existing patterns: frozen Pydantic models, `Protocol` ports, tests under `tests/unit/research/` and `tests/integration/research/`.
- `pytest` markers live in `pyproject.toml` under `[tool.pytest.ini_options] markers`; `integration` is already registered.

---

### Task 1: Extract the shared corporate-event normalizer

Refactor the recorded adapters so the field-normalization logic (issuer/category/dissem-time/content → `_NormalizedRecord` → sealed `SourceRecord`) is reusable by the live path, with **no behavioural change** to the recorded adapters.

**Files:**
- Modify: `src/trading_os/research/corporate_event_sources.py`
- Test: `tests/unit/research/test_corporate_event_sources.py` (existing — must stay green)
- Test: `tests/unit/research/test_normalizer_core.py` (create)

**Interfaces:**
- Consumes: `SourceRecord` from `trading_os.research.watchers`.
- Produces:
  - `normalize_nse_fields(payload: dict[str, object]) -> _NormalizedRecord`
  - `normalize_bse_fields(payload: dict[str, object]) -> _NormalizedRecord`
  - `seal_record(normalized: _NormalizedRecord, *, channel: str, received_at: datetime, payload_hash: str) -> SourceRecord`
  - existing `RecordedNseAnnouncementAdapter` / `RecordedBseAnnouncementAdapter` / `RecordedSec8KAdapter` unchanged in behaviour.

- [ ] **Step 1: Write the failing test for the standalone normalizer + sealer**

```python
# tests/unit/research/test_normalizer_core.py
from datetime import UTC, datetime
from hashlib import sha256

from trading_os.research.corporate_event_sources import (
    normalize_bse_fields,
    normalize_nse_fields,
    seal_record,
)

NSE_PAYLOAD = {
    "announcementId": "A1",
    "issuerId": "issuer:tanla",
    "category": "Financial Results",
    "dissemDateTime": "2026-07-21T18:30:00+05:30",
    "eventDate": "2026-07-21",
    "attachmentText": "Board approved audited results for Q1 FY27.",
}


def test_normalize_nse_fields_yields_family_and_times() -> None:
    n = normalize_nse_fields(NSE_PAYLOAD)
    assert n.record_id == "nse:A1"
    assert n.source_family_id == "issuer:tanla:financial_results:2026-07-21"
    assert n.kind == "Financial Results"
    assert n.available_at == datetime(2026, 7, 21, 13, 0, tzinfo=UTC)  # 18:30 IST -> 13:00 UTC


def test_seal_record_stamps_received_at_and_channel() -> None:
    n = normalize_nse_fields(NSE_PAYLOAD)
    received = datetime(2026, 7, 21, 14, 0, tzinfo=UTC)
    record = seal_record(
        n, channel="nse", received_at=received, payload_hash=f"sha256:{sha256(b'x').hexdigest()}"
    )
    assert record.channel == "nse"
    assert record.received_at == received
    assert record.available_at == n.available_at
    assert record.is_issuer_submission is True
    assert record.payload_hash.startswith("sha256:")


def test_normalize_bse_fields_shares_family_with_nse() -> None:
    bse_payload = {
        "newsId": "B1",
        "issuerId": "issuer:tanla",
        "category": "Financial Results",
        "dissemDateTime": "2026-07-21T18:35:00+05:30",
        "eventDate": "2026-07-21",
        "attachmentText": "Board approved audited results for Q1 FY27.",
    }
    nse = normalize_nse_fields(NSE_PAYLOAD)
    bse = normalize_bse_fields(bse_payload)
    assert nse.source_family_id == bse.source_family_id
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/unit/research/test_normalizer_core.py -v`
Expected: FAIL with `ImportError: cannot import name 'normalize_nse_fields'`.

- [ ] **Step 3: Extract the shared functions and rewrite the recorded adapters on top of them**

In `src/trading_os/research/corporate_event_sources.py`, add module-level functions and rewrite the NSE/BSE adapters to call them (SEC adapter unchanged):

```python
def normalize_nse_fields(payload: dict[str, object]) -> _NormalizedRecord:
    announcement_id = _require_str(payload, "announcementId")
    issuer_id = _require_str(payload, "issuerId")
    category = _require_str(payload, "category")
    dissem = _require_time(payload, "dissemDateTime")
    event_date = _require_str(payload, "eventDate")
    content = _require_str(payload, "attachmentText")
    return _NormalizedRecord(
        record_id=f"nse:{announcement_id}",
        source_id="source:nse-announcements",
        source_family_id=_issuer_family(issuer_id, category, event_date),
        jurisdiction="IN",
        published_at=dissem,
        available_at=dissem,
        kind=category,
        content=content,
    )


def normalize_bse_fields(payload: dict[str, object]) -> _NormalizedRecord:
    news_id = _require_str(payload, "newsId")
    issuer_id = _require_str(payload, "issuerId")
    category = _require_str(payload, "category")
    dissem = _require_time(payload, "dissemDateTime")
    event_date = _require_str(payload, "eventDate")
    content = _require_str(payload, "attachmentText")
    return _NormalizedRecord(
        record_id=f"bse:{news_id}",
        source_id="source:bse-announcements",
        source_family_id=_issuer_family(issuer_id, category, event_date),
        jurisdiction="IN",
        published_at=dissem,
        available_at=dissem,
        kind=category,
        content=content,
    )


def seal_record(
    normalized: _NormalizedRecord,
    *,
    channel: str,
    received_at: datetime,
    payload_hash: str,
) -> SourceRecord:
    return SourceRecord(
        record_id=normalized.record_id,
        source_id=normalized.source_id,
        source_family_id=normalized.source_family_id,
        channel=channel,
        jurisdiction=normalized.jurisdiction,
        published_at=normalized.published_at,
        available_at=normalized.available_at,
        received_at=received_at,
        kind=normalized.kind,
        is_issuer_submission=True,
        payload_hash=payload_hash,
        content=normalized.content,
    )
```

Then rewrite `RecordedNseAnnouncementAdapter._normalize` to `return normalize_nse_fields(payload)` and `RecordedBseAnnouncementAdapter._normalize` to `return normalize_bse_fields(payload)`. Keep `RecordedCorporateEventAdapter.capture` sealing via `seal_record(normalized, channel=self.channel, received_at=received_at, payload_hash=f"sha256:{digest}")`.

- [ ] **Step 4: Run the new test AND the existing recorded-adapter tests**

Run: `pytest tests/unit/research/test_normalizer_core.py tests/unit/research/test_corporate_event_sources.py -v`
Expected: all PASS (the refactor is behaviour-preserving).

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/research/corporate_event_sources.py tests/unit/research/test_normalizer_core.py
git commit -m "refactor(research): extract shared corporate-event normalizer and sealer"
```

---

### Task 2: SourceFetchPort transport seam + fixture fetcher

**Files:**
- Create: `src/trading_os/research/source_fetch.py`
- Test: `tests/unit/research/test_source_fetch.py`

**Interfaces:**
- Produces:
  - `RawFetchResult(BaseModel, frozen=True)` with `endpoint: str`, `status: int`, `fetched_at: datetime`, `payload: str` (raw text/JSON).
  - `SourceFetchError(RuntimeError)`.
  - `SourceFetchPort(Protocol)`: `async def fetch(self, endpoint: str, *, since: datetime) -> RawFetchResult`.
  - `FixtureSourceFetcher`: constructed with `dict[str, RawFetchResult | SourceFetchError]` keyed by endpoint; `fetch` returns the recorded result or raises the recorded error.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/research/test_source_fetch.py
from datetime import UTC, datetime

import pytest

from trading_os.research.source_fetch import (
    FixtureSourceFetcher,
    RawFetchResult,
    SourceFetchError,
)

AT = datetime(2026, 7, 21, tzinfo=UTC)


async def test_fixture_fetcher_returns_recorded_payload() -> None:
    fetcher = FixtureSourceFetcher(
        {"nse/latest": RawFetchResult(endpoint="nse/latest", status=200, fetched_at=AT, payload="[]")}
    )
    result = await fetcher.fetch("nse/latest", since=AT)
    assert result.status == 200
    assert result.payload == "[]"


async def test_fixture_fetcher_raises_recorded_error() -> None:
    fetcher = FixtureSourceFetcher({"bse/latest": SourceFetchError("blocked")})
    with pytest.raises(SourceFetchError):
        await fetcher.fetch("bse/latest", since=AT)
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest tests/unit/research/test_source_fetch.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'trading_os.research.source_fetch'`.

- [ ] **Step 3: Implement the port and fixture fetcher**

```python
# src/trading_os/research/source_fetch.py
from datetime import datetime
from typing import Protocol

from pydantic import BaseModel


class SourceFetchError(RuntimeError):
    """A transport-level failure (network, anti-bot block, timeout, bad status)."""


class RawFetchResult(BaseModel, frozen=True):
    endpoint: str
    status: int
    fetched_at: datetime
    payload: str


class SourceFetchPort(Protocol):
    async def fetch(self, endpoint: str, *, since: datetime) -> RawFetchResult: ...


class FixtureSourceFetcher:
    """Deterministic offline fetcher; replays recorded results by endpoint."""

    def __init__(self, results: dict[str, RawFetchResult | SourceFetchError]) -> None:
        self._results = dict(results)

    async def fetch(self, endpoint: str, *, since: datetime) -> RawFetchResult:
        recorded = self._results.get(endpoint)
        if recorded is None:
            raise SourceFetchError(f"no fixture for endpoint {endpoint!r}")
        if isinstance(recorded, SourceFetchError):
            raise recorded
        return recorded
```

- [ ] **Step 4: Run to verify it passes + mypy**

Run: `pytest tests/unit/research/test_source_fetch.py -v && mypy src/trading_os/research/source_fetch.py`
Expected: tests PASS, mypy success.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/research/source_fetch.py tests/unit/research/test_source_fetch.py
git commit -m "feat(research): add SourceFetchPort transport seam and fixture fetcher"
```

---

### Task 3: SeenRecordStore (idempotent dedup)

**Files:**
- Create: `src/trading_os/research/seen_store.py`
- Test: `tests/unit/research/test_seen_store.py`

**Interfaces:**
- Produces:
  - `SeenRecordStore(Protocol)`: `def is_new(self, channel: str, record_id: str, payload_hash: str) -> bool` (returns True and records it if unseen; False if already seen).
  - `InMemorySeenRecordStore` implementing it.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/research/test_seen_store.py
from trading_os.research.seen_store import InMemorySeenRecordStore


def test_first_sighting_is_new_then_duplicate_is_not() -> None:
    store = InMemorySeenRecordStore()
    assert store.is_new("nse", "nse:A1", "sha256:x") is True
    assert store.is_new("nse", "nse:A1", "sha256:x") is False


def test_same_id_different_hash_is_new_again() -> None:
    # A corrected/replaced payload for the same announcement id is a new sighting.
    store = InMemorySeenRecordStore()
    assert store.is_new("nse", "nse:A1", "sha256:x") is True
    assert store.is_new("nse", "nse:A1", "sha256:y") is True


def test_channels_are_independent() -> None:
    store = InMemorySeenRecordStore()
    assert store.is_new("nse", "id", "sha256:x") is True
    assert store.is_new("bse", "id", "sha256:x") is True
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest tests/unit/research/test_seen_store.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement the store**

```python
# src/trading_os/research/seen_store.py
from typing import Protocol


class SeenRecordStore(Protocol):
    def is_new(self, channel: str, record_id: str, payload_hash: str) -> bool: ...


class InMemorySeenRecordStore:
    def __init__(self) -> None:
        self._seen: set[tuple[str, str, str]] = set()

    def is_new(self, channel: str, record_id: str, payload_hash: str) -> bool:
        key = (channel, record_id, payload_hash)
        if key in self._seen:
            return False
        self._seen.add(key)
        return True
```

- [ ] **Step 4: Run to verify it passes**

Run: `pytest tests/unit/research/test_seen_store.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/research/seen_store.py tests/unit/research/test_seen_store.py
git commit -m "feat(research): add idempotent SeenRecordStore for watcher dedup"
```

---

### Task 4: LiveSourceWatcher (Tier 1, official, evidence-bearing)

Polls the exchange-wide official feed via the port, parses the feed payload into per-announcement dicts, normalizes+seals via Task 1, dedups via Task 3, and returns new `SourceRecord`s. A fetch/parse failure returns an `attempted-omitted` signal, never a record.

**Files:**
- Create: `src/trading_os/research/live_watcher.py`
- Test: `tests/unit/research/test_live_watcher.py`

**Interfaces:**
- Consumes: `SourceFetchPort`, `RawFetchResult`, `SourceFetchError` (Task 2); `normalize_nse_fields`, `normalize_bse_fields`, `seal_record` (Task 1); `SeenRecordStore` (Task 3); `SourceRecord` (watchers).
- Produces:
  - `ChannelSpec(BaseModel, frozen=True)`: `channel: str`, `endpoint: str`.
  - `WatchCycleResult(BaseModel, frozen=True)`: `new_records: tuple[SourceRecord, ...]`, `attempted_channels: tuple[str, ...]`, `omitted_channels: tuple[str, ...]`.
  - `LiveSourceWatcher(fetch_port, channels: tuple[ChannelSpec, ...], seen_store, *, clock: Callable[[], datetime])` with `async def poll(self, since: datetime) -> WatchCycleResult`.
  - Feed payload contract: each channel endpoint returns a JSON array of announcement objects using the same field names the Task-1 normalizers expect (`announcementId`/`newsId`, `issuerId`, `category`, `dissemDateTime`, `eventDate`, `attachmentText`).

- [ ] **Step 1: Write the failing tests (happy path, dedup, fail-safe)**

```python
# tests/unit/research/test_live_watcher.py
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
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest tests/unit/research/test_live_watcher.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement the watcher**

```python
# src/trading_os/research/live_watcher.py
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
                payload_hash = f"sha256:{sha256(json.dumps(item, sort_keys=True).encode()).hexdigest()}"
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
```

- [ ] **Step 4: Run tests + mypy**

Run: `pytest tests/unit/research/test_live_watcher.py -v && mypy src/trading_os/research/live_watcher.py`
Expected: 4 tests PASS, mypy success.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/research/live_watcher.py tests/unit/research/test_live_watcher.py
git commit -m "feat(research): add Tier-1 LiveSourceWatcher with dedup and fail-safe"
```

---

### Task 5: Live-vs-recorded sealing parity test

Prove the refactor's safety net: the live path and the recorded adapter seal a byte-identical `SourceRecord` (ignoring `received_at`, which is intentionally the receipt clock) from the same source fields.

**Files:**
- Test: `tests/unit/research/test_seal_parity.py` (create)

**Interfaces:**
- Consumes: `RecordedNseAnnouncementAdapter` (writes a temp fixture file), `LiveSourceWatcher` output.

- [ ] **Step 1: Write the parity test**

```python
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
```

- [ ] **Step 2: Run to verify it passes** (both paths already exist)

Run: `pytest tests/unit/research/test_seal_parity.py -v`
Expected: PASS. If it fails, the normalizer diverged — fix `live_watcher`/`corporate_event_sources` until identical.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/research/test_seal_parity.py
git commit -m "test(research): assert live and recorded paths seal identical records"
```

---

### Task 6: WatchScheduled intent + CalendarWatcher (Tier 2, early-signal, never evidence)

**Files:**
- Create: `src/trading_os/research/calendar_watcher.py`
- Test: `tests/unit/research/test_calendar_watcher.py`

**Interfaces:**
- Consumes: `SourceFetchPort`, `RawFetchResult`, `SourceFetchError` (Task 2).
- Produces:
  - `WatchScheduled(BaseModel, frozen=True)`: `issuer_id: str`, `event_kind: str`, `expected_at: datetime`, `authority_tier: str`, `provenance_endpoint: str`. **No evidentiary fields** (no assessment, no support, no eligibility).
  - `CalendarWatcher(fetch_port, endpoint: str, *, authority_tier: str = "official_calendar")` with `async def poll(self, since: datetime) -> tuple[WatchScheduled, ...]`.
  - Calendar payload contract: JSON array of objects with `issuerId`, `eventKind`, `expectedDateTime`.

- [ ] **Step 1: Write the failing tests (emit intent; fail-safe; tier boundary)**

```python
# tests/unit/research/test_calendar_watcher.py
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


def test_watch_scheduled_has_no_evidence_fields() -> None:
    # Tier boundary: a WatchScheduled cannot masquerade as evidence.
    fields = set(WatchScheduled.model_fields)
    forbidden = {"assessment", "support", "contradictions", "eligibility_effect",
                 "source_record_ids", "packet_id"}
    assert fields.isdisjoint(forbidden)
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest tests/unit/research/test_calendar_watcher.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement the calendar watcher and intent**

```python
# src/trading_os/research/calendar_watcher.py
import json
from datetime import datetime

from pydantic import BaseModel

from trading_os.research.source_fetch import SourceFetchError, SourceFetchPort


class WatchScheduled(BaseModel, frozen=True):
    """Tier-2 early signal: an event is expected. Attention-only; this can never
    become an EvidencePacket. It carries no assessment, citation, or effect."""

    issuer_id: str
    event_kind: str
    expected_at: datetime
    authority_tier: str
    provenance_endpoint: str


class CalendarWatcher:
    def __init__(
        self, fetch_port: SourceFetchPort, endpoint: str, *, authority_tier: str = "official_calendar"
    ) -> None:
        self._fetch = fetch_port
        self._endpoint = endpoint
        self._authority_tier = authority_tier

    async def poll(self, since: datetime) -> tuple[WatchScheduled, ...]:
        try:
            raw = await self._fetch.fetch(self._endpoint, since=since)
            items = json.loads(raw.payload)
            if not isinstance(items, list):
                return ()
        except (SourceFetchError, json.JSONDecodeError):
            return ()
        intents: list[WatchScheduled] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                issuer_id = str(item["issuerId"])
                event_kind = str(item["eventKind"])
                expected_at = datetime.fromisoformat(
                    str(item["expectedDateTime"]).replace("Z", "+00:00")
                )
            except (KeyError, ValueError):
                continue
            intents.append(
                WatchScheduled(
                    issuer_id=issuer_id,
                    event_kind=event_kind,
                    expected_at=expected_at,
                    authority_tier=self._authority_tier,
                    provenance_endpoint=self._endpoint,
                )
            )
        return tuple(intents)
```

- [ ] **Step 4: Run tests + mypy**

Run: `pytest tests/unit/research/test_calendar_watcher.py -v && mypy src/trading_os/research/calendar_watcher.py`
Expected: 3 tests PASS, mypy success.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/research/calendar_watcher.py tests/unit/research/test_calendar_watcher.py
git commit -m "feat(research): add Tier-2 CalendarWatcher emitting non-evidence WatchScheduled"
```

---

### Task 7: Tier-separation guard (WatchScheduled has no path to EvidencePacket)

A focused test that documents and enforces the type boundary end to end: a `WatchScheduled` cannot be fed into coverage reconciliation or packet construction.

**Files:**
- Test: `tests/unit/research/test_tier_separation.py` (create)

**Interfaces:**
- Consumes: `WatchScheduled` (Task 6), `reconcile_coverage`/`SourceRecord` (existing), `LiveSourceWatcher.WatchCycleResult` (Task 4).

- [ ] **Step 1: Write the boundary test**

```python
# tests/unit/research/test_tier_separation.py
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
```

- [ ] **Step 2: Run to verify it passes**

Run: `pytest tests/unit/research/test_tier_separation.py -v`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/research/test_tier_separation.py
git commit -m "test(research): enforce the evidence/early-signal tier boundary"
```

---

### Task 8: Real HttpSourceFetcher (integration-tagged, out of the default gate)

The thin live transport. Implements `SourceFetchPort` over httpx with a session/cookie warm-up, timeout, rate-limit delay, result-size cap, and status-to-`SourceFetchError` mapping. Its tests are `@pytest.mark.integration` and hit the network — excluded from the default gate.

**Files:**
- Modify: `src/trading_os/research/source_fetch.py` (add `HttpSourceFetcher`)
- Test: `tests/integration/research/test_http_source_fetcher.py` (create)

**Interfaces:**
- Consumes: `RawFetchResult`, `SourceFetchError`, `SourceFetchPort` (Task 2); `httpx`.
- Produces: `HttpSourceFetcher(base_headers: dict[str, str] | None = None, *, timeout_s: float = 10.0, max_bytes: int = 2_000_000, warmup_url: str | None = None)` implementing `fetch`.

- [ ] **Step 1: Write the integration test (tagged; skipped by default gate)**

```python
# tests/integration/research/test_http_source_fetcher.py
from datetime import UTC, datetime

import httpx
import pytest

from trading_os.research.source_fetch import HttpSourceFetcher, SourceFetchError


@pytest.mark.integration
async def test_http_fetcher_maps_transport_and_returns_raw(monkeypatch: pytest.MonkeyPatch) -> None:
    # Uses a stub transport so the shape is proven without a live exchange; the
    # marker keeps it out of the default gate where the real endpoints are used.
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text='[]')

    fetcher = HttpSourceFetcher()
    fetcher._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))  # type: ignore[attr-defined]
    result = await fetcher.fetch("https://example.test/latest", since=datetime(2026, 7, 21, tzinfo=UTC))
    assert result.status == 200
    assert result.payload == "[]"


@pytest.mark.integration
async def test_http_fetcher_maps_bad_status_to_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="blocked")

    fetcher = HttpSourceFetcher()
    fetcher._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))  # type: ignore[attr-defined]
    with pytest.raises(SourceFetchError):
        await fetcher.fetch("https://example.test/latest", since=datetime(2026, 7, 21, tzinfo=UTC))
```

- [ ] **Step 2: Run to verify it fails (with the marker explicitly selected)**

Run: `pytest tests/integration/research/test_http_source_fetcher.py -v -m integration`
Expected: FAIL with `ImportError: cannot import name 'HttpSourceFetcher'`.

- [ ] **Step 3: Implement HttpSourceFetcher**

Add to `src/trading_os/research/source_fetch.py`:

```python
import httpx


class HttpSourceFetcher:
    """Live transport for NSE/BSE endpoints. Integration-only; not exercised by
    the default offline gate. Maps non-2xx and transport errors to SourceFetchError.
    """

    def __init__(
        self,
        base_headers: dict[str, str] | None = None,
        *,
        timeout_s: float = 10.0,
        max_bytes: int = 2_000_000,
        warmup_url: str | None = None,
    ) -> None:
        self._headers = base_headers or {
            "User-Agent": "Mozilla/5.0 (compatible; trading-os/1.0)",
            "Accept": "application/json,text/plain,*/*",
        }
        self._timeout_s = timeout_s
        self._max_bytes = max_bytes
        self._warmup_url = warmup_url
        self._client = httpx.AsyncClient(headers=self._headers, timeout=timeout_s)

    async def fetch(self, endpoint: str, *, since: datetime) -> RawFetchResult:
        try:
            if self._warmup_url is not None:
                await self._client.get(self._warmup_url)  # establishes cookies
            response = await self._client.get(endpoint)
        except httpx.HTTPError as exc:
            raise SourceFetchError(f"transport error for {endpoint}: {exc}") from exc
        if response.status_code >= 400:
            raise SourceFetchError(f"bad status {response.status_code} for {endpoint}")
        text = response.text
        if len(text.encode()) > self._max_bytes:
            raise SourceFetchError(f"result exceeds {self._max_bytes} bytes for {endpoint}")
        return RawFetchResult(
            endpoint=endpoint,
            status=response.status_code,
            fetched_at=since,
            payload=text,
        )
```

Note: `fetched_at` is set to the injected `since` clock (not a wall-clock call) to keep the model deterministic; the real fetch time is recorded by the caller's ledger event, not here.

- [ ] **Step 4: Run the integration tests (marker selected) + mypy**

Run: `pytest tests/integration/research/test_http_source_fetcher.py -v -m integration && mypy src/trading_os/research/source_fetch.py`
Expected: 2 tests PASS, mypy success.

- [ ] **Step 5: Confirm the default gate does NOT run them**

Run: `pytest tests/unit tests/contract -q`
Expected: PASS; the integration tests are not collected (no `-m integration`).

- [ ] **Step 6: Commit**

```bash
git add src/trading_os/research/source_fetch.py tests/integration/research/test_http_source_fetcher.py
git commit -m "feat(research): add integration-tagged HttpSourceFetcher for live NSE/BSE"
```

---

### Task 9: Credible-source catalog

**Files:**
- Create: `docs/research/19-india-event-source-catalog.md`

**Interfaces:** none (documentation).

- [ ] **Step 1: Write the catalog**

Create `docs/research/19-india-event-source-catalog.md` with a header describing the tiering rule (only official records carry evidentiary weight; early-signal sources schedule attention only), then a table per tier. Columns: `Source | Channel/endpoint | Access method | Authority tier | Typical latency vs event | Entitlement/legal | Parser difficulty | source_family mapping`.

Populate:
- **Official (evidence-bearing):** NSE corporate announcements; BSE corporate announcements; NSE/BSE board-meeting & results calendar; exchange RSS; SEBI (SCORES / UDiFF / intermediary filings).
- **Aggregators (early-signal, catalog-only):** Trendlyne; Screener.in; Tickertape; MoneyControl earnings/board-meeting calendars.
- **Wires (early-signal, catalog-only):** PTI; Reuters; Bloomberg corporate-action feeds.

For each row give the concrete endpoint or access note, the realistic latency, and the entitlement/legal caveat (NSE/BSE market-data policy, rate limits, subscription requirements). End with a "Wired live now" line naming only: NSE official announcements, BSE official announcements, NSE/BSE board-meeting calendar. State explicitly that no credentials/tokens are stored and production exchange-feed use may require a data subscription.

- [ ] **Step 2: Commit**

```bash
git add docs/research/19-india-event-source-catalog.md
git commit -m "docs(research): add ranked catalog of credible India event sources"
```

---

### Task 10: Final verification

**Files:** none (verification only).

- [ ] **Step 1: Run the full offline gate**

Run: `pytest tests/unit tests/contract tests/integration/research tests/integration/agents -q -m "not integration"`
Expected: all PASS (new watcher/fetch/store/calendar/parity/tier tests included; the integration-tagged HTTP tests are excluded).

- [ ] **Step 2: Static checks**

Run: `ruff check src tests && mypy src`
Expected: both exit 0.

- [ ] **Step 3: Confirm integration tests still pass when explicitly selected**

Run: `pytest tests/integration/research/test_http_source_fetcher.py -m integration -q`
Expected: PASS.

- [ ] **Step 4: Commit any lint/type fixups**

```bash
git add -A
git commit -m "chore(research): final verify for live source watcher" || echo "nothing to commit"
```

## Completion gate

Complete when: live official NSE/BSE announcements are sealed identically to the recorded adapters (parity test green), exchange-wide polling seals new records and dedups on re-poll, fetch/parse failure degrades to attempted-omitted (never a fabricated record), the calendar tier emits `WatchScheduled` intents that provably cannot become evidence (tier-separation test green), the live HTTP fetcher passes under `-m integration` and is excluded from the default gate, and the credible-source catalog is committed. No analysis-seam, decision, live-authority, or promotion code changed.

## Specification coverage

| Spec section | Implemented by |
|---|---|
| §3 two tiers | Tasks 4 (Tier 1), 6 (Tier 2), 7 (boundary) |
| §4 components / shared normalizer | Tasks 1, 2, 3, 4, 6 |
| §5 Tanla data flow | Tasks 4 + 6 (calendar arms watch; live watcher seals the filing) |
| §6 error handling / cutoff / idempotency / entitlement | Tasks 4 (fail-safe, cutoff, dedup), 8 (rate/size caps), 9 (entitlement notes) |
| §7 testing (offline-first; integration-tagged live) | Tasks 4–8, 10 |
| §8 credible-source catalog | Task 9 |
| §9 type-boundary / exchange-wide | Tasks 4 (universe), 7 (type boundary) |
