from datetime import UTC, datetime

from trading_os.kernel.ids import InstrumentId, SnapshotId
from trading_os.research.models import DecisionFeatureSet, EvidenceDomain, EvidencePacket


def test_research_models_have_no_executable_fields() -> None:
    forbidden = {"quantity", "price", "target_weight", "target_position", "order", "broker"}
    for model in (EvidencePacket, DecisionFeatureSet):
        assert forbidden.isdisjoint(model.model_fields)


def test_sentiment_is_risk_only_without_primary_corroboration() -> None:
    now = datetime.now(UTC)
    packet = EvidencePacket(
        packet_id="sentiment-1",
        instrument_id=InstrumentId("NSE:INE000000001"),
        domain=EvidenceDomain.SENTIMENT,
        assessment="attention_accelerating_unverified",
        support=("source-1",),
        contradictions=(),
        missing=("primary_corroboration",),
        as_of=now,
        cutoff=now,
        data_snapshot_id=SnapshotId("data-1"),
        source_record_ids=("source-1",),
        eligibility_effect="risk_only",
    )
    assert packet.eligibility_effect == "risk_only"


def test_risk_overlay_multiplier_cannot_exceed_one() -> None:
    import pytest
    from pydantic import ValidationError

    from trading_os.research.models import RiskOverlaySet

    with pytest.raises(ValidationError):
        RiskOverlaySet(multiplier=1.5)
    ok = RiskOverlaySet(multiplier=0.5, veto=False, reason_codes=("liquidity",))
    assert ok.multiplier == 0.5
