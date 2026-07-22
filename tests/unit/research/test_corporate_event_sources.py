"""Recorded SEC/NSE/BSE corporate-event adapter tests.

These tests pin the sealing semantics for recorded corporate-event source
adapters (spec §19): each adapter reads recorded JSON bytes plus a
deterministic receipt time and returns a sealed :class:`SourceRecord` on its
official channel, hashing the raw payload, marking the disclosure an issuer
submission, and binding ``available_at`` to the recorded dissemination time
rather than inferring the current clock. Malformed records fail closed with
:class:`RecordedSourceError`.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from trading_os.research.corporate_event_sources import (
    RecordedBseAnnouncementAdapter,
    RecordedNseAnnouncementAdapter,
    RecordedSec8KAdapter,
    RecordedSourceError,
)

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "research" / "corporate_events"
SEC_FIXTURE = FIXTURES / "sec_8k_material_agreement.json"
NSE_FIXTURE = FIXTURES / "nse_board_meeting.json"
BSE_FIXTURE = FIXTURES / "bse_board_meeting.json"
RECEIVED = datetime(2026, 7, 22, 15, tzinfo=UTC)


def _write(tmp_path: Path, name: str, payload: dict[str, object]) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_sec_fixture_is_sealed_with_official_channel_and_hash() -> None:
    record = RecordedSec8KAdapter().capture(SEC_FIXTURE, RECEIVED)
    assert record.channel == "sec"
    assert record.kind == "8-K"
    assert record.jurisdiction == "US"
    assert record.available_at == datetime(2026, 7, 22, 14, 30, tzinfo=UTC)
    assert record.received_at == RECEIVED
    assert record.payload_hash.startswith("sha256:")
    assert record.is_issuer_submission is True
    assert record.content == "Registrant entered into a material definitive agreement."


def test_nse_fixture_is_sealed_on_nse_channel() -> None:
    record = RecordedNseAnnouncementAdapter().capture(NSE_FIXTURE, RECEIVED)
    assert record.channel == "nse"
    assert record.jurisdiction == "IN"
    assert record.kind == "Board Meeting"
    assert record.is_issuer_submission is True
    assert record.payload_hash.startswith("sha256:")


def test_bse_fixture_is_sealed_on_bse_channel() -> None:
    record = RecordedBseAnnouncementAdapter().capture(BSE_FIXTURE, RECEIVED)
    assert record.channel == "bse"
    assert record.jurisdiction == "IN"
    assert record.kind == "Board Meeting"
    assert record.is_issuer_submission is True
    assert record.payload_hash.startswith("sha256:")


def test_nse_and_bse_same_issuer_notice_share_a_source_family() -> None:
    nse = RecordedNseAnnouncementAdapter().capture(NSE_FIXTURE, RECEIVED)
    bse = RecordedBseAnnouncementAdapter().capture(BSE_FIXTURE, RECEIVED)
    assert nse.source_family_id == bse.source_family_id
    assert {nse.channel, bse.channel} == {"nse", "bse"}
    assert nse.record_id != bse.record_id


def test_payload_hash_is_deterministic_over_raw_bytes() -> None:
    first = RecordedSec8KAdapter().capture(SEC_FIXTURE, RECEIVED)
    second = RecordedSec8KAdapter().capture(SEC_FIXTURE, RECEIVED)
    assert first.payload_hash == second.payload_hash


def test_sec_missing_official_identifier_fails_closed(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "no_accession.json",
        {
            "cik": "0000000000",
            "form": "8-K",
            "acceptanceDateTime": "2026-07-22T14:30:00Z",
            "text": "Registrant entered into a material definitive agreement.",
        },
    )
    with pytest.raises(RecordedSourceError):
        RecordedSec8KAdapter().capture(path, RECEIVED)


def test_sec_missing_acceptance_time_fails_closed(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "no_time.json",
        {
            "accessionNumber": "0000000000-26-000001",
            "cik": "0000000000",
            "form": "8-K",
            "text": "Registrant entered into a material definitive agreement.",
        },
    )
    with pytest.raises(RecordedSourceError):
        RecordedSec8KAdapter().capture(path, RECEIVED)


def test_sec_missing_form_fails_closed(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "no_form.json",
        {
            "accessionNumber": "0000000000-26-000001",
            "cik": "0000000000",
            "acceptanceDateTime": "2026-07-22T14:30:00Z",
            "text": "Registrant entered into a material definitive agreement.",
        },
    )
    with pytest.raises(RecordedSourceError):
        RecordedSec8KAdapter().capture(path, RECEIVED)


def test_sec_missing_content_fails_closed(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "no_text.json",
        {
            "accessionNumber": "0000000000-26-000001",
            "cik": "0000000000",
            "form": "8-K",
            "acceptanceDateTime": "2026-07-22T14:30:00Z",
        },
    )
    with pytest.raises(RecordedSourceError):
        RecordedSec8KAdapter().capture(path, RECEIVED)


def test_nse_missing_dissem_time_fails_closed(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "nse_no_time.json",
        {
            "announcementId": "NSE-2026-0001",
            "issuerId": "issuer:1",
            "category": "Board Meeting",
            "eventDate": "2026-07-22",
            "attachmentText": "Board meeting.",
        },
    )
    with pytest.raises(RecordedSourceError):
        RecordedNseAnnouncementAdapter().capture(path, RECEIVED)


def test_bse_missing_identifier_fails_closed(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "bse_no_id.json",
        {
            "issuerId": "issuer:1",
            "category": "Board Meeting",
            "dissemDateTime": "2026-07-22T09:21:00+05:30",
            "eventDate": "2026-07-22",
            "attachmentText": "Board meeting.",
        },
    )
    with pytest.raises(RecordedSourceError):
        RecordedBseAnnouncementAdapter().capture(path, RECEIVED)
