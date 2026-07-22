"""Governed promotion and demotion (H14).

A semantic feature influences economics only after an immutable
DecisionFeatureActivation, which requires an eligible challenger verdict and a
frozen evaluation manifest stored as provenance before activation, plus a
cooldown. A DecisionFeatureDeactivation mirrors it. Any regression on a
protected safety metric auto-demotes the feature to research-only — turning a
feature off is a policy release, never a code change.
"""

from datetime import datetime, timedelta

from pydantic import BaseModel

from trading_os.ontology.challenger import ChallengerVerdict


class PromotionError(ValueError):
    pass


class DecisionFeatureActivation(BaseModel, frozen=True):
    activation_id: str
    feature_id: str
    evaluation_manifest_hash: str
    approved_by: str
    effective_from: datetime
    cooldown_days: int


class DecisionFeatureDeactivation(BaseModel, frozen=True):
    deactivation_id: str
    feature_id: str
    supersedes_activation: str
    reason: str
    effective_from: datetime


def activate_feature(
    *,
    feature_id: str,
    verdict: ChallengerVerdict,
    evaluation_manifest_hash: str,
    approved_by: str,
    effective_from: datetime,
    cooldown_days: int,
    prior_activation: DecisionFeatureActivation | None = None,
) -> DecisionFeatureActivation:
    if not verdict.eligible:
        raise PromotionError(f"challenger not eligible: {verdict.reason}")
    if not evaluation_manifest_hash:
        raise PromotionError("a frozen evaluation manifest hash is required before activation")
    if prior_activation is not None:
        cooldown_end = prior_activation.effective_from + timedelta(
            days=prior_activation.cooldown_days
        )
        if effective_from < cooldown_end:
            raise PromotionError(
                f"within cooldown window until {cooldown_end.isoformat()}"
            )
    return DecisionFeatureActivation(
        activation_id=f"act-{feature_id}-{effective_from.isoformat()}",
        feature_id=feature_id,
        evaluation_manifest_hash=evaluation_manifest_hash,
        approved_by=approved_by,
        effective_from=effective_from,
        cooldown_days=cooldown_days,
    )


def should_auto_demote(
    *,
    baseline_leaks: int = 0,
    current_leaks: int = 0,
    baseline_false_merges: int = 0,
    current_false_merges: int = 0,
) -> bool:
    """Auto-demote to research-only on ANY regression of a protected safety
    metric (cutoff leakage or false merges)."""
    return current_leaks > baseline_leaks or current_false_merges > baseline_false_merges
