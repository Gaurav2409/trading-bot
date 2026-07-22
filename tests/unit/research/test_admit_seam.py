"""admit_packet categorical-seam enforcement (spec §4, §16).

admit_packet is the idempotent defence at the port boundary that no harness
node path can bypass. It must reject a packet whose assessment is not in the
closed categorical vocabulary for its domain, or that carries an executable
number — even one, like ``agent_2500``, that a substring blocklist of
field-name words would miss.
"""

from datetime import UTC, datetime

import pytest

from trading_os.research.models import EvidenceDomain, EvidencePacket
from trading_os.research.orchestrator import (
    AdmissionError,
    ResearchQuestion,
    admit_packet,
)

CUTOFF = datetime(2026, 7, 23, tzinfo=UTC)


def _question() -> ResearchQuestion:
    return ResearchQuestion(
        question_id="q:1",
        instrument_id="NSE:INE000000001",
        domain=EvidenceDomain.CORPORATE_EVENT,
        source_record_ids=("nse:1",),
        cutoff=CUTOFF,
        data_snapshot_id="snapshot:1",
    )


def _packet(assessment: str, **overrides: object) -> EvidencePacket:
    base: dict[str, object] = {
        "packet_id": "packet:q:1",
        "instrument_id": "NSE:INE000000001",
        "domain": EvidenceDomain.CORPORATE_EVENT,
        "assessment": assessment,
        "support": ("nse:1",),
        "contradictions": (),
        "missing": (),
        "as_of": CUTOFF,
        "cutoff": CUTOFF,
        "data_snapshot_id": "snapshot:1",
        "source_record_ids": ("nse:1",),
        "eligibility_effect": "supportive",
    }
    base.update(overrides)
    return EvidencePacket(**base)  # type: ignore[arg-type]


def test_registered_categorical_assessment_is_admitted() -> None:
    packet = admit_packet(_packet("material_event_supported"), _question())
    assert packet.assessment == "material_event_supported"


def test_bare_number_assessment_is_rejected() -> None:
    # Regression: "agent_2500" avoids every forbidden English word but carries a
    # bare number. The closed-vocabulary allowlist + numeric-run check reject it.
    with pytest.raises(AdmissionError, match="categorical seam"):
        admit_packet(_packet("agent_2500"), _question())


def test_unknown_assessment_outside_vocabulary_is_rejected() -> None:
    with pytest.raises(AdmissionError, match="categorical seam"):
        admit_packet(_packet("strong_buy"), _question())


def test_forbidden_token_in_missing_is_rejected() -> None:
    with pytest.raises(AdmissionError, match="categorical seam"):
        admit_packet(
            _packet("material_event_supported", missing=("target_price",)),
            _question(),
        )


def test_admitted_failure_assessment_is_allowed() -> None:
    packet = admit_packet(
        _packet(
            "agent_provider_timeout",
            support=(),
            source_record_ids=(),
            eligibility_effect="neutral",
        ),
        _question(),
    )
    assert packet.assessment == "agent_provider_timeout"
