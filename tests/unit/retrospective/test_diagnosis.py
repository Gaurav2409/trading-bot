from trading_os.retrospective.diagnosis import (
    ImprovementProposal,
    RootCause,
    diagnose,
    propose_change,
)


def test_diagnosis_uses_closed_root_cause_classes() -> None:
    result = diagnose(
        relational_baseline_agreed=True,
        symptom="missed_breakout_outside_index",
    )
    assert result.root_cause is RootCause.DISCOVERY_COVERAGE


def test_semantic_challenger_not_blamed_before_relational_baseline_checked() -> None:
    # If the relational baseline also failed, the fault is not the semantic layer.
    result = diagnose(
        relational_baseline_agreed=False,
        symptom="wrong_evidence_extraction",
    )
    assert result.root_cause is RootCause.EXTRACTION
    assert result.blamed_semantic_challenger is False


def test_proposal_cannot_activate_itself() -> None:
    proposal = propose_change(
        target="detector",
        candidate_release_id="momentum-v2",
        rationale="widen volume lookback",
    )
    assert isinstance(proposal, ImprovementProposal)
    assert proposal.activated is False
    assert not hasattr(proposal, "activate")
