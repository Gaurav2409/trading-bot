"""Effective-dated source applicability and coverage reconciliation tests.

These tests pin the constitutional applicability semantics from spec §15:
single-listing securities are not penalized for the inapplicable exchange,
one missing applicable mandatory channel is degraded, all missing is
insufficient, materially conflicting official records are contradictory, and
records only become available at their ``available_at`` relative to the run
cutoff.
"""

from datetime import UTC, datetime

import pytest

from trading_os.agents.models import CoverageStatus
from trading_os.research.source_coverage import (
    SourceChannelPolicy,
    SourceCoveragePolicyRelease,
    reconcile_coverage,
)
from trading_os.research.watchers import SourceRecord

CUTOFF = datetime(2026, 7, 23, tzinfo=UTC)
AVAILABLE = datetime(2026, 7, 22, tzinfo=UTC)
PUBLISHED = datetime(2026, 7, 22, tzinfo=UTC)
RECEIVED = datetime(2026, 7, 22, 12, tzinfo=UTC)

_JURISDICTION = {"nse": "IN", "bse": "IN", "sec": "US"}


def policy(
    applicable_channels: tuple[str, ...],
    *,
    sec_applicable: bool = True,
) -> SourceCoveragePolicyRelease:
    """Build a policy where every applicable channel is mandatory.

    ``sec`` is always declared as a channel so its inapplicability can be
    asserted; it is applicable only when requested.
    """
    channels: list[SourceChannelPolicy] = []
    for channel in ("nse", "bse"):
        channels.append(
            SourceChannelPolicy(
                channel=channel,
                mandatory=True,
                applicable=channel in applicable_channels,
            )
        )
    channels.append(
        SourceChannelPolicy(
            channel="sec",
            mandatory=True,
            applicable=sec_applicable and "sec" in applicable_channels,
        )
    )
    return SourceCoveragePolicyRelease(
        release_id="source-policy:corporate-event:v1",
        effective_from=CUTOFF,
        channels=tuple(channels),
        content_hash="sha256:policy-v1",
    )


def _record(
    channel: str,
    *,
    record_id: str | None = None,
    available_at: datetime = AVAILABLE,
    content: str = "material_agreement",
) -> SourceRecord:
    return SourceRecord(
        record_id=record_id or f"{channel}:1",
        source_id=f"source:{channel}",
        source_family_id="issuer:1:material_agreement:2026-07-22",
        channel=channel,
        jurisdiction=_JURISDICTION[channel],
        published_at=PUBLISHED,
        available_at=available_at,
        received_at=RECEIVED,
        kind="board_meeting",
        is_issuer_submission=True,
        payload_hash="sha256:record",
        content=content,
    )


def records(captured_channels: tuple[str, ...]) -> tuple[SourceRecord, ...]:
    return tuple(_record(channel) for channel in captured_channels)


@pytest.mark.parametrize(
    ("applicable", "captured", "expected"),
    [
        (("nse",), ("nse",), CoverageStatus.COMPLETE),
        (("bse",), ("bse",), CoverageStatus.COMPLETE),
        (("nse", "bse"), ("nse",), CoverageStatus.DEGRADED),
        (("nse", "bse"), (), CoverageStatus.INSUFFICIENT),
        (("nse",), (), CoverageStatus.INSUFFICIENT),
    ],
)
def test_exchange_applicability_does_not_penalize_single_listing(
    applicable: tuple[str, ...],
    captured: tuple[str, ...],
    expected: CoverageStatus,
) -> None:
    receipt = reconcile_coverage(policy(applicable), records(captured), CUTOFF)
    assert receipt.status is expected
    if applicable == ("nse",):
        assert "bse" not in receipt.missing_channels
        assert "bse" in receipt.inapplicable_channels


def test_sec_is_not_missing_when_issuer_is_not_sec_applicable() -> None:
    receipt = reconcile_coverage(
        policy(("nse",), sec_applicable=False),
        records(("nse",)),
        CUTOFF,
    )
    assert receipt.status is CoverageStatus.COMPLETE
    assert "sec" in receipt.inapplicable_channels
    assert "sec" not in receipt.missing_channels


def test_conflicting_official_families_are_contradictory() -> None:
    conflicting = (
        _record("nse", record_id="nse:1", content="material_agreement"),
        _record("bse", record_id="bse:1", content="agreement_terminated"),
    )
    receipt = reconcile_coverage(policy(("nse", "bse")), conflicting, CUTOFF)
    assert receipt.status is CoverageStatus.CONTRADICTORY
    assert set(receipt.contradictory_record_ids) == {"nse:1", "bse:1"}


def test_matching_official_families_are_not_contradictory() -> None:
    matching = (
        _record("nse", record_id="nse:1", content="material_agreement"),
        _record("bse", record_id="bse:1", content="material_agreement"),
    )
    receipt = reconcile_coverage(policy(("nse", "bse")), matching, CUTOFF)
    assert receipt.status is CoverageStatus.COMPLETE
    assert receipt.contradictory_record_ids == ()


def test_record_available_after_cutoff_is_not_captured() -> None:
    late = (
        _record(
            "nse",
            record_id="nse:late",
            available_at=datetime(2026, 7, 24, tzinfo=UTC),
        ),
    )
    receipt = reconcile_coverage(policy(("nse",)), late, CUTOFF)
    assert receipt.status is CoverageStatus.INSUFFICIENT
    assert "nse" not in receipt.captured_channels
    assert "nse" in receipt.missing_channels
