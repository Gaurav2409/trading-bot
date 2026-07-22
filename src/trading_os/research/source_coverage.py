"""Deterministic source coverage reconciliation.

Reconciles a decision cutoff and a sealed :class:`SourceRecord` set against an
effective-dated :class:`SourceCoveragePolicyRelease`, producing a
:class:`SourceCoverageReceipt` with a categorical :class:`CoverageStatus`.

Constitutional semantics (spec §15):

- An inapplicable channel is never counted as missing.
- All applicable mandatory channels captured is ``COMPLETE``.
- At least one applicable mandatory channel captured while at least one is
  missing is ``DEGRADED``.
- Every applicable mandatory channel missing is ``INSUFFICIENT``.
- Materially conflicting official records across applicable families are
  ``CONTRADICTORY``; every citation is preserved.
- A record is only captured when ``available_at <= cutoff``; a later record
  remains uncaptured (no silent resolution of newer state).
"""

from collections import defaultdict
from datetime import datetime

from pydantic import BaseModel

from trading_os.agents.models import CoverageStatus
from trading_os.research.watchers import SourceRecord


class SourceChannelPolicy(BaseModel, frozen=True):
    channel: str
    mandatory: bool
    applicable: bool


class SourceCoveragePolicyRelease(BaseModel, frozen=True):
    release_id: str
    effective_from: datetime
    channels: tuple[SourceChannelPolicy, ...]
    content_hash: str


class SourceCoverageReceipt(BaseModel, frozen=True):
    policy_release_id: str
    status: CoverageStatus
    captured_channels: tuple[str, ...]
    missing_channels: tuple[str, ...]
    inapplicable_channels: tuple[str, ...]
    contradictory_record_ids: tuple[str, ...] = ()


def reconcile_coverage(
    policy: SourceCoveragePolicyRelease,
    records: tuple[SourceRecord, ...],
    cutoff: datetime,
) -> SourceCoverageReceipt:
    applicable_channels = {
        item.channel for item in policy.channels if item.applicable
    }
    eligible = tuple(
        record
        for record in records
        if record.available_at <= cutoff
        and record.channel in applicable_channels
    )
    captured = {record.channel for record in eligible}
    mandatory = {
        item.channel
        for item in policy.channels
        if item.applicable and item.mandatory
    }
    missing = mandatory - captured
    inapplicable = {
        item.channel for item in policy.channels if not item.applicable
    }

    contradictory_record_ids = _contradictory_record_ids(eligible)

    status = CoverageStatus.COMPLETE
    if contradictory_record_ids:
        status = CoverageStatus.CONTRADICTORY
    elif mandatory and missing == mandatory:
        status = CoverageStatus.INSUFFICIENT
    elif missing:
        status = CoverageStatus.DEGRADED

    return SourceCoverageReceipt(
        policy_release_id=policy.release_id,
        status=status,
        captured_channels=tuple(sorted(captured)),
        missing_channels=tuple(sorted(missing)),
        inapplicable_channels=tuple(sorted(inapplicable)),
        contradictory_record_ids=contradictory_record_ids,
    )


def _contradictory_record_ids(
    eligible: tuple[SourceRecord, ...],
) -> tuple[str, ...]:
    """Return record IDs whose source family reports conflicting material facts.

    Records sharing a ``source_family_id`` describe the same issuer disclosure.
    If applicable official channels normalize that disclosure to more than one
    distinct material fact (``content``), the disclosure is contradictory and
    all conflicting citations are preserved.
    """
    by_family: dict[str, list[SourceRecord]] = defaultdict(list)
    for record in eligible:
        by_family[record.source_family_id].append(record)

    conflicting: set[str] = set()
    for family_records in by_family.values():
        contents = {record.content for record in family_records}
        if len(contents) > 1:
            conflicting.update(record.record_id for record in family_records)
    return tuple(sorted(conflicting))
