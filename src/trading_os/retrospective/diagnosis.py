from enum import StrEnum

from pydantic import BaseModel


class RootCause(StrEnum):
    DISCOVERY_COVERAGE = "discovery_coverage"
    IDENTITY = "identity"
    TEMPORAL = "temporal"
    DATA_QUALITY = "data_quality"
    EXTRACTION = "extraction"
    ONTOLOGY_QUERY = "ontology_query"
    PORTFOLIO_NORMALIZATION = "portfolio_normalization"
    RISK = "risk"
    COMPLIANCE = "compliance"
    EXECUTION = "execution"
    PROTECTION = "protection"
    COST = "cost"
    REGIME_SHIFT = "regime_shift"


_SYMPTOM_MAP: dict[str, RootCause] = {
    "missed_breakout_outside_index": RootCause.DISCOVERY_COVERAGE,
    "wrong_evidence_extraction": RootCause.EXTRACTION,
    "ticker_reuse_confusion": RootCause.IDENTITY,
    "future_data_leak": RootCause.TEMPORAL,
    "double_counted_custody": RootCause.PORTFOLIO_NORMALIZATION,
    "stop_never_filled": RootCause.PROTECTION,
}


class Diagnosis(BaseModel, frozen=True):
    root_cause: RootCause
    blamed_semantic_challenger: bool


class ImprovementProposal(BaseModel, frozen=True):
    """A non-executable proposal. It names a candidate release but can never
    activate it; activation is a separate governed, human-gated step."""

    target: str
    candidate_release_id: str
    rationale: str
    activated: bool = False


def diagnose(*, relational_baseline_agreed: bool, symptom: str) -> Diagnosis:
    """Classify a failure into a closed root-cause class. The semantic challenger
    is only blamed when the relational baseline agreed (i.e. relational was fine
    but the semantic path diverged)."""
    root_cause = _SYMPTOM_MAP.get(symptom, RootCause.DATA_QUALITY)
    blamed_semantic = relational_baseline_agreed and root_cause is RootCause.ONTOLOGY_QUERY
    return Diagnosis(root_cause=root_cause, blamed_semantic_challenger=blamed_semantic)


def propose_change(*, target: str, candidate_release_id: str, rationale: str) -> ImprovementProposal:
    return ImprovementProposal(
        target=target,
        candidate_release_id=candidate_release_id,
        rationale=rationale,
        activated=False,
    )
