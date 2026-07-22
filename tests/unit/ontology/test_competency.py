from datetime import UTC, datetime

from trading_os.ontology.competency import (
    CompetencyQueryPack,
    QueryCase,
    validate_pack_coverage,
)
from trading_os.research.models import EvidenceDomain, EvidencePacket


def _packet(instrument: str, snapshot: str, received_offset: int, cutoff: datetime) -> EvidencePacket:
    from datetime import timedelta

    return EvidencePacket(
        packet_id=f"{instrument}-{snapshot}",
        instrument_id=instrument,
        domain=EvidenceDomain.TECHNICAL,
        assessment="breakout_confirmed",
        support=("src-1",),
        contradictions=(),
        missing=(),
        as_of=cutoff + timedelta(seconds=received_offset),
        cutoff=cutoff,
        data_snapshot_id=snapshot,
        source_record_ids=("src-1",),
        eligibility_effect="supportive",
    )


def test_pack_has_required_case_coverage() -> None:
    pack = CompetencyQueryPack.default()
    # Every query must carry a positive golden, an expected-empty counterexample,
    # and a cutoff-exclusion case, plus a p95 latency budget.
    validate_pack_coverage(pack)  # must not raise
    for query in pack.queries:
        kinds = {c.kind for c in query.cases}
        assert {"positive_golden", "expected_empty", "cutoff_exclusion"} <= kinds
        assert query.p95_latency_ms > 0


def test_missing_cutoff_case_fails_coverage() -> None:
    import pytest

    from trading_os.ontology.competency import CompetencyQuery, CompetencyQueryPackError

    bad = CompetencyQueryPack(
        queries=(
            CompetencyQuery(
                query_id="q-bad",
                module="evidence",
                question="evidence for instrument at snapshot",
                p95_latency_ms=50,
                cases=(
                    QueryCase(kind="positive_golden", note="has a match"),
                    QueryCase(kind="expected_empty", note="no match"),
                ),
            ),
        )
    )
    with pytest.raises(CompetencyQueryPackError):
        validate_pack_coverage(bad)


def test_evidence_query_answers_from_relational_champion_and_excludes_future() -> None:
    cutoff = datetime(2026, 7, 22, 10, 0, tzinfo=UTC)
    pack = CompetencyQueryPack.default()
    evidence = [
        _packet("NSE:INE0001", "snap-1", received_offset=-10, cutoff=cutoff),  # in-time
        _packet("NSE:INE0001", "snap-1", received_offset=+10, cutoff=cutoff),  # future leak
    ]
    answers = pack.run_evidence_for(
        evidence, instrument_id="NSE:INE0001", data_snapshot_id="snap-1", cutoff=cutoff
    )
    # The relational champion returns only the in-time packet; the future-leaked
    # packet is excluded (cutoff safety).
    assert len(answers) == 1
    assert answers[0].as_of <= cutoff
