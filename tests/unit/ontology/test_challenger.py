from trading_os.ontology.challenger import (
    ChallengerScore,
    ChampionScore,
    evaluate_challenger,
    resolve_projection_answer,
)


def _champion() -> ChampionScore:
    return ChampionScore(precision=0.90, recall=0.80, p95_latency_ms=40)


def test_challenger_eligible_when_it_beats_or_matches_champion_safely() -> None:
    score = ChallengerScore(
        precision=0.90,
        recall=0.85,  # recall improves
        p95_latency_ms=60,
        new_cutoff_leaks=0,
        new_false_merges=0,
        out_of_sample_improvement=0.05,
    )
    verdict = evaluate_challenger(_champion(), score, epsilon=0.05)
    assert verdict.eligible is True


def test_precision_drop_beyond_epsilon_is_ineligible() -> None:
    score = ChallengerScore(
        precision=0.80,  # champion 0.90, epsilon 0.05 -> floor 0.85, this is below
        recall=0.85,
        p95_latency_ms=60,
        new_cutoff_leaks=0,
        new_false_merges=0,
        out_of_sample_improvement=0.05,
    )
    verdict = evaluate_challenger(_champion(), score, epsilon=0.05)
    assert verdict.eligible is False
    assert "precision" in verdict.reason


def test_any_new_cutoff_leak_is_ineligible() -> None:
    score = ChallengerScore(
        precision=0.95,
        recall=0.90,
        p95_latency_ms=50,
        new_cutoff_leaks=1,  # a single new leak disqualifies
        new_false_merges=0,
        out_of_sample_improvement=0.10,
    )
    verdict = evaluate_challenger(_champion(), score, epsilon=0.05)
    assert verdict.eligible is False
    assert "cutoff" in verdict.reason


def test_no_out_of_sample_improvement_is_ineligible() -> None:
    score = ChallengerScore(
        precision=0.90,
        recall=0.80,  # merely matches, improves nothing
        p95_latency_ms=40,
        new_cutoff_leaks=0,
        new_false_merges=0,
        out_of_sample_improvement=0.0,
    )
    verdict = evaluate_challenger(_champion(), score, epsilon=0.05)
    assert verdict.eligible is False
    assert "improvement" in verdict.reason


def test_projection_disagreement_degrades_to_champion_and_records() -> None:
    result = resolve_projection_answer(
        relational=("a", "b"),
        rdf=("a", "b"),
        neo4j=("a",),  # disagrees
    )
    assert result.answer == ("a", "b")  # champion wins
    assert result.degraded is True
    assert "neo4j" in result.disagreements


def test_projection_agreement_is_not_degraded() -> None:
    result = resolve_projection_answer(
        relational=("a", "b"), rdf=("a", "b"), neo4j=("a", "b")
    )
    assert result.answer == ("a", "b")
    assert result.degraded is False
    assert result.disagreements == ()
