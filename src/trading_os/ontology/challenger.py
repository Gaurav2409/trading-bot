"""Projection parity and challenger evaluation (H13).

The relational champion is the null hypothesis. A graph challenger (RDF/Neo4j)
is eligible to influence decisioning only if it matches the champion on safety
and strictly improves at least one pre-specified metric out of sample. When the
three projections disagree on a snapshot, the answer degrades to the champion
and the disagreement is recorded — a graph never silently overrides truth.
"""

from pydantic import BaseModel, Field


class ChampionScore(BaseModel, frozen=True):
    precision: float = Field(ge=0, le=1)
    recall: float = Field(ge=0, le=1)
    p95_latency_ms: int = Field(ge=0)


class ChallengerScore(BaseModel, frozen=True):
    precision: float = Field(ge=0, le=1)
    recall: float = Field(ge=0, le=1)
    p95_latency_ms: int = Field(ge=0)
    new_cutoff_leaks: int = Field(ge=0)
    new_false_merges: int = Field(ge=0)
    out_of_sample_improvement: float


class ChallengerVerdict(BaseModel, frozen=True):
    eligible: bool
    reason: str


def evaluate_challenger(
    champion: ChampionScore, challenger: ChallengerScore, *, epsilon: float = 0.05
) -> ChallengerVerdict:
    """Eligibility gate. All must hold: recall >= champion; precision >= champion
    - epsilon; zero new cutoff leaks; zero new false merges; and at least one
    pre-specified metric improves out of sample."""
    if challenger.new_cutoff_leaks > 0:
        return ChallengerVerdict(eligible=False, reason="introduces new cutoff leakage")
    if challenger.new_false_merges > 0:
        return ChallengerVerdict(eligible=False, reason="introduces new false identity merges")
    if challenger.recall < champion.recall:
        return ChallengerVerdict(eligible=False, reason="recall below champion")
    if challenger.precision < champion.precision - epsilon:
        return ChallengerVerdict(
            eligible=False, reason=f"precision drop beyond epsilon {epsilon}"
        )
    if challenger.out_of_sample_improvement <= 0:
        return ChallengerVerdict(
            eligible=False, reason="no out-of-sample improvement over champion"
        )
    return ChallengerVerdict(eligible=True, reason="matches champion safety and improves out of sample")


class ProjectionResult(BaseModel, frozen=True):
    answer: tuple[str, ...]
    degraded: bool
    disagreements: tuple[str, ...]


def resolve_projection_answer(
    *,
    relational: tuple[str, ...],
    rdf: tuple[str, ...],
    neo4j: tuple[str, ...],
) -> ProjectionResult:
    """The relational answer is authoritative. If either graph projection
    disagrees, record it and degrade to the champion."""
    disagreements: list[str] = []
    if rdf != relational:
        disagreements.append("rdf")
    if neo4j != relational:
        disagreements.append("neo4j")
    return ProjectionResult(
        answer=relational,
        degraded=bool(disagreements),
        disagreements=tuple(disagreements),
    )
