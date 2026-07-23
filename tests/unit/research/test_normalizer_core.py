# tests/unit/research/test_normalizer_core.py
from datetime import UTC, datetime
from hashlib import sha256

from trading_os.research.corporate_event_sources import (
    normalize_bse_fields,
    normalize_nse_fields,
    seal_record,
)

NSE_PAYLOAD: dict[str, object] = {
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
    bse_payload: dict[str, object] = {
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
