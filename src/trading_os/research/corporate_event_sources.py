"""Recorded corporate-event source adapters.

Seal recorded SEC 8-K filings and NSE/BSE corporate announcements into
immutable :class:`SourceRecord`s for offline, deterministic P0 tracer runs.

Constitutional semantics (spec §14, §19):

- Each adapter emits on exactly one official ``channel`` (``sec``/``nse``/
  ``bse``) and marks the disclosure an issuer submission — exchange
  dissemination is primary evidence but not exchange verification.
- ``available_at`` is bound to the recorded dissemination/acceptance time. The
  adapter never infers the current clock, so resume/replay cannot silently
  resolve newer state.
- ``payload_hash`` is a ``sha256`` digest of the raw recorded bytes, so
  identical recordings seal identically.
- NSE and BSE deliveries of the same issuer disclosure share a
  ``source_family_id`` (issuer + normalized category + event date) so coverage
  reconciliation can recognize duplicate/same-origin official deliveries.
- A recorded payload missing an official identifier, dissemination time,
  form/category, or content fails closed with :class:`RecordedSourceError`.
"""

import json
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel

from trading_os.research.watchers import SourceRecord


class RecordedSourceError(ValueError):
    """A recorded corporate-event payload is malformed or incomplete."""


class _NormalizedRecord(BaseModel, frozen=True):
    record_id: str
    source_id: str
    source_family_id: str
    jurisdiction: str
    published_at: datetime
    available_at: datetime
    kind: str
    content: str


class RecordedCorporateEventAdapter:
    """Base adapter: read recorded bytes, normalize, and seal a record."""

    channel: ClassVar[str]

    def capture(self, path: Path, received_at: datetime) -> SourceRecord:
        raw = path.read_bytes()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RecordedSourceError(f"invalid recorded JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise RecordedSourceError("recorded payload must be a JSON object")
        normalized = self._normalize(payload)
        digest = sha256(raw).hexdigest()
        return SourceRecord(
            record_id=normalized.record_id,
            source_id=normalized.source_id,
            source_family_id=normalized.source_family_id,
            channel=self.channel,
            jurisdiction=normalized.jurisdiction,
            published_at=normalized.published_at,
            available_at=normalized.available_at,
            received_at=received_at,
            kind=normalized.kind,
            is_issuer_submission=True,
            payload_hash=f"sha256:{digest}",
            content=normalized.content,
        )

    def _normalize(self, payload: dict[str, object]) -> _NormalizedRecord:
        raise NotImplementedError


def _require_str(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RecordedSourceError(f"missing required field: {key}")
    return value


def _require_time(payload: dict[str, object], key: str) -> datetime:
    value = _require_str(payload, key)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RecordedSourceError(f"invalid timestamp for {key}: {value}") from exc
    if parsed.tzinfo is None:
        raise RecordedSourceError(f"timestamp must be timezone-aware: {key}")
    return parsed


def _issuer_family(issuer_id: str, category: str, event_date: str) -> str:
    normalized_category = category.strip().lower().replace(" ", "_")
    return f"{issuer_id}:{normalized_category}:{event_date}"


class RecordedSec8KAdapter(RecordedCorporateEventAdapter):
    channel = "sec"

    def _normalize(self, payload: dict[str, object]) -> _NormalizedRecord:
        accession = _require_str(payload, "accessionNumber")
        form = _require_str(payload, "form")
        acceptance = _require_time(payload, "acceptanceDateTime")
        content = _require_str(payload, "text")
        cik = _require_str(payload, "cik")
        return _NormalizedRecord(
            record_id=f"sec:{accession}",
            source_id="source:sec-edgar",
            source_family_id=_issuer_family(f"cik:{cik}", form, acceptance.date().isoformat()),
            jurisdiction="US",
            published_at=acceptance,
            available_at=acceptance,
            kind=form,
            content=content,
        )


class RecordedNseAnnouncementAdapter(RecordedCorporateEventAdapter):
    channel = "nse"

    def _normalize(self, payload: dict[str, object]) -> _NormalizedRecord:
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


class RecordedBseAnnouncementAdapter(RecordedCorporateEventAdapter):
    channel = "bse"

    def _normalize(self, payload: dict[str, object]) -> _NormalizedRecord:
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
