"""Relational champion must answer competency questions with Fuseki and Neo4j
unavailable. This proves the permanent production baseline does not depend on
the rebuildable graph projections.
"""

from datetime import UTC, datetime

from trading_os.kernel.ids import InstrumentId, SnapshotId
from trading_os.ontology.relational import RelationalRetrievalBaseline
from trading_os.research.models import EvidenceDomain, EvidencePacket


def test_relational_baseline_answers_without_graph_projections() -> None:
    now = datetime.now(UTC)
    packet = EvidencePacket(
        packet_id="tech-1",
        instrument_id=InstrumentId("NSE:INE000000001"),
        domain=EvidenceDomain.TECHNICAL,
        assessment="breakout_confirmed",
        support=("source-1",),
        contradictions=(),
        missing=(),
        as_of=now,
        cutoff=now,
        data_snapshot_id=SnapshotId("data-1"),
        source_record_ids=("source-1",),
        eligibility_effect="supportive",
    )
    baseline = RelationalRetrievalBaseline(evidence=[packet])
    # No Fuseki/Neo4j connection is created; answers come from snapshot-scoped rows.
    answers = baseline.evidence_for(
        InstrumentId("NSE:INE000000001"), SnapshotId("data-1")
    )
    assert len(answers) == 1
    assert answers[0].assessment == "breakout_confirmed"

    # An instrument with no evidence returns an empty, non-fabricated answer.
    assert baseline.evidence_for(InstrumentId("NSE:UNKNOWN"), SnapshotId("data-1")) == ()
