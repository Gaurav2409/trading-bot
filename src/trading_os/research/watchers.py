"""Deterministic source watchers.

Capture immutable source records (NSE/BSE corporate announcements, SEC EDGAR
filings) with publication and receipt times. Exchange dissemination is primary
evidence but remains an issuer submission, not exchange verification — that
epistemic distinction is preserved on the record.
"""

from datetime import datetime
from typing import Protocol

from pydantic import BaseModel


class SourceRecord(BaseModel, frozen=True):
    record_id: str
    source_id: str
    source_family_id: str
    channel: str
    jurisdiction: str
    published_at: datetime
    available_at: datetime
    received_at: datetime
    kind: str
    is_issuer_submission: bool
    payload_hash: str
    content: str


class SourceWatcher(Protocol):
    async def poll(self, since: datetime) -> list[SourceRecord]:
        raise NotImplementedError


class FixtureSourceWatcher:
    """Offline watcher returning pre-seeded source records."""

    def __init__(self, records: list[SourceRecord]) -> None:
        self._records = records

    async def poll(self, since: datetime) -> list[SourceRecord]:
        return [r for r in self._records if r.received_at >= since]
