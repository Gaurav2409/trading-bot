from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from trading_os.ontology.challenger import ChallengerVerdict
from trading_os.ontology.promotion import (
    DecisionFeatureActivation,
    DecisionFeatureDeactivation,
    PromotionError,
    activate_feature,
    should_auto_demote,
)


def _now() -> datetime:
    return datetime(2026, 7, 23, tzinfo=UTC)


def test_activation_requires_eligible_verdict_and_frozen_manifest() -> None:
    eligible = ChallengerVerdict(eligible=True, reason="ok")
    activation = activate_feature(
        feature_id="ontology.exposure_path",
        verdict=eligible,
        evaluation_manifest_hash="sha256:frozen",
        approved_by="owner-1",
        effective_from=_now(),
        cooldown_days=7,
    )
    assert isinstance(activation, DecisionFeatureActivation)
    assert activation.evaluation_manifest_hash == "sha256:frozen"


def test_ineligible_verdict_cannot_activate() -> None:
    verdict = ChallengerVerdict(eligible=False, reason="recall below champion")
    with pytest.raises(PromotionError):
        activate_feature(
            feature_id="f",
            verdict=verdict,
            evaluation_manifest_hash="sha256:frozen",
            approved_by="owner-1",
            effective_from=_now(),
            cooldown_days=7,
        )


def test_activation_without_frozen_manifest_is_rejected() -> None:
    eligible = ChallengerVerdict(eligible=True, reason="ok")
    with pytest.raises(PromotionError):
        activate_feature(
            feature_id="f",
            verdict=eligible,
            evaluation_manifest_hash="",  # no frozen manifest
            approved_by="owner-1",
            effective_from=_now(),
            cooldown_days=7,
        )


def test_deactivation_is_immutable_release_mirroring_activation() -> None:
    deact = DecisionFeatureDeactivation(
        deactivation_id="deact-1",
        feature_id="ontology.exposure_path",
        supersedes_activation="act-1",
        reason="safety_metric_regression",
        effective_from=_now(),
    )
    assert deact.feature_id == "ontology.exposure_path"
    with pytest.raises(ValidationError):
        deact.reason = "changed"  # frozen


def test_auto_demote_on_any_protected_safety_regression() -> None:
    # A regression on any protected metric demotes to research-only.
    assert should_auto_demote(baseline_leaks=0, current_leaks=1) is True
    assert should_auto_demote(baseline_false_merges=0, current_false_merges=2) is True
    assert should_auto_demote(baseline_leaks=0, current_leaks=0) is False


def test_cooldown_blocks_reactivation_within_window() -> None:
    eligible = ChallengerVerdict(eligible=True, reason="ok")
    first = activate_feature(
        feature_id="f",
        verdict=eligible,
        evaluation_manifest_hash="sha256:frozen",
        approved_by="owner-1",
        effective_from=_now(),
        cooldown_days=7,
    )
    # Re-activating within the cooldown window is rejected.
    with pytest.raises(PromotionError):
        activate_feature(
            feature_id="f",
            verdict=eligible,
            evaluation_manifest_hash="sha256:frozen2",
            approved_by="owner-1",
            effective_from=_now() + timedelta(days=3),
            cooldown_days=7,
            prior_activation=first,
        )
