"""Competency-query pack (H12).

A versioned set of the questions the reasoning layer must answer, each answered
by the permanent relational champion (snapshot-scoped structured records), and
each shipping the test cases that make it CI-enforceable: a positive golden, an
expected-empty counterexample, and a cutoff-exclusion case. This extends the
baseline beyond a single `evidence_for` lookup.
"""

from datetime import datetime

from pydantic import BaseModel

from trading_os.research.models import EvidencePacket

_REQUIRED_CASE_KINDS = frozenset({"positive_golden", "expected_empty", "cutoff_exclusion"})


class CompetencyQueryPackError(ValueError):
    pass


class QueryCase(BaseModel, frozen=True):
    kind: str  # positive_golden | expected_empty | cutoff_exclusion
    note: str


class CompetencyQuery(BaseModel, frozen=True):
    query_id: str
    module: str
    question: str
    p95_latency_ms: int
    cases: tuple[QueryCase, ...]


class CompetencyQueryPack(BaseModel, frozen=True):
    queries: tuple[CompetencyQuery, ...]

    @classmethod
    def default(cls) -> "CompetencyQueryPack":
        def full_cases(match: str, empty: str) -> tuple[QueryCase, ...]:
            return (
                QueryCase(kind="positive_golden", note=match),
                QueryCase(kind="expected_empty", note=empty),
                QueryCase(kind="cutoff_exclusion", note="future-received fact excluded"),
            )

        return cls(
            queries=(
                CompetencyQuery(
                    query_id="evidence.for_instrument",
                    module="evidence",
                    question="admitted evidence for an instrument at a snapshot",
                    p95_latency_ms=50,
                    cases=full_cases("in-time packet returned", "unknown instrument -> empty"),
                ),
                CompetencyQuery(
                    query_id="identity.disambiguation",
                    module="identity",
                    question="are two listings the same security under a governed assertion?",
                    p95_latency_ms=50,
                    cases=full_cases("governed-equal pair", "distinct securities -> empty"),
                ),
                CompetencyQuery(
                    query_id="events.contradictions",
                    module="events",
                    question="contradictions against a claim at a snapshot",
                    p95_latency_ms=50,
                    cases=full_cases("contradiction present", "uncontested claim -> empty"),
                ),
                CompetencyQuery(
                    query_id="provenance.corrections",
                    module="provenance",
                    question="records superseded by a correction",
                    p95_latency_ms=50,
                    cases=full_cases("superseded record", "no correction -> empty"),
                ),
                CompetencyQuery(
                    query_id="portfolio.completeness",
                    module="portfolio",
                    question="completeness dimensions blocking new exposure",
                    p95_latency_ms=50,
                    cases=full_cases("degraded dimension", "all complete -> empty"),
                ),
            )
        )

    def run_evidence_for(
        self,
        evidence: list[EvidencePacket],
        *,
        instrument_id: str,
        data_snapshot_id: str,
        cutoff: datetime,
    ) -> tuple[EvidencePacket, ...]:
        """Relational-champion answer for the evidence competency query, with
        cutoff safety: a packet received after the cutoff is excluded."""
        return tuple(
            p
            for p in evidence
            if p.instrument_id == instrument_id
            and p.data_snapshot_id == data_snapshot_id
            and p.as_of <= cutoff
        )


def validate_pack_coverage(pack: CompetencyQueryPack) -> None:
    """Fail if any query lacks a required case kind or a positive latency budget."""
    if not pack.queries:
        raise CompetencyQueryPackError("pack has no queries")
    for query in pack.queries:
        kinds = {c.kind for c in query.cases}
        missing = _REQUIRED_CASE_KINDS - kinds
        if missing:
            raise CompetencyQueryPackError(
                f"{query.query_id} missing required cases: {sorted(missing)}"
            )
        if query.p95_latency_ms <= 0:
            raise CompetencyQueryPackError(f"{query.query_id} needs a positive p95 budget")
