"""Corporate-event node behavior (spec §8.2, §9, §14).

These tests exercise the domain node artifacts and handlers directly at their
public seam:

* the deterministic normalizer sits between the gather agent loop and the judge
  agent loop, deriving channel-family keys and cutoff eligibility without
  emitting any executable number;
* the judge maps normalized evidence to a categorical assessment through the
  provider-neutral :class:`LLMRole`;
* reconciliation gives degraded and contradictory coverage no positive
  influence (``eligibility_effect == "neutral"``); and
* the P0 profile/trajectory releases declare the exact governed node order and
  compile to a safe terminal path (categorical seam then admission).
"""

from datetime import UTC, datetime

import pytest

from trading_os.agents.corporate_events import (
    CorporateEventDraft,
    EventExtraction,
    EventJudgement,
    NormalizedCorporateEvent,
    judge_event,
    normalize_event,
    reconcile_judgement,
)
from trading_os.agents.llm import FixtureLLMRole
from trading_os.agents.models import CoverageStatus, NodeKind, ReleaseStatus
from trading_os.agents.profiles import corporate_event_profile_releases
from trading_os.research.models import EvidenceDomain
from trading_os.research.source_coverage import SourceCoverageReceipt

CUTOFF = datetime(2026, 7, 23, tzinfo=UTC)

P0_NODE_ORDER: tuple[tuple[str, NodeKind], ...] = (
    ("gather", NodeKind.AGENT_LOOP),
    ("normalize", NodeKind.DETERMINISTIC_TRANSFORM),
    ("validate", NodeKind.VALIDATION),
    ("judge", NodeKind.JUDGE),
    ("reconcile", NodeKind.DETERMINISTIC_TRANSFORM),
    ("categorical_seam", NodeKind.CATEGORICAL_SEAM),
    ("admission", NodeKind.ADMISSION),
)


def _receipt(
    status: CoverageStatus,
    *,
    missing_channels: tuple[str, ...] = (),
    contradictory_record_ids: tuple[str, ...] = (),
) -> SourceCoverageReceipt:
    return SourceCoverageReceipt(
        policy_release_id="source-policy:corporate-event:v1",
        status=status,
        captured_channels=("nse",),
        missing_channels=missing_channels,
        inapplicable_channels=(),
        contradictory_record_ids=contradictory_record_ids,
    )


def _judgement() -> EventJudgement:
    return EventJudgement(
        assessment="material_event_supported",
        support_record_ids=("sec:1",),
        contradiction_record_ids=(),
        missing=(),
    )


async def test_normalizer_sits_between_gather_and_judge() -> None:
    gathered = EventExtraction(
        event_type="material_agreement",
        record_ids=("sec:1",),
        issuer_id="issuer:1",
        stated_effective_at=datetime(2026, 7, 22, tzinfo=UTC),
    )
    normalized = normalize_event(gathered, cutoff=CUTOFF)
    assert isinstance(normalized, NormalizedCorporateEvent)
    assert normalized.channel_families == (
        "issuer:1:material_agreement:2026-07-22",
    )
    assert normalized.within_cutoff is True

    role = FixtureLLMRole(
        {
            "judge:issuer:1:material_agreement": EventJudgement(
                assessment="material_event_supported",
                support_record_ids=("sec:1",),
                contradiction_record_ids=(),
                missing=(),
            )
        }
    )
    judged = await judge_event(normalized, role)
    assert isinstance(judged, EventJudgement)
    assert judged.assessment == "material_event_supported"


async def test_judge_maps_llm_failure_to_missing_assessment() -> None:
    normalized = normalize_event(
        EventExtraction(
            event_type="material_agreement",
            record_ids=("sec:1",),
            issuer_id="issuer:1",
        ),
        cutoff=CUTOFF,
    )
    role = FixtureLLMRole({})  # unknown replay key -> malformed_output failure
    judged = await judge_event(normalized, role)
    assert judged.assessment == "agent_malformed_output"
    assert judged.support_record_ids == ()


def test_complete_non_conflicting_evidence_is_supportive() -> None:
    draft = reconcile_judgement(_judgement(), _receipt(CoverageStatus.COMPLETE))
    assert isinstance(draft, CorporateEventDraft)
    assert draft.eligibility_effect == "supportive"
    assert draft.support_record_ids == ("sec:1",)


def test_degraded_and_contradictory_evidence_are_not_supportive() -> None:
    degraded = reconcile_judgement(
        _judgement(),
        _receipt(CoverageStatus.DEGRADED, missing_channels=("bse",)),
    )
    assert degraded.eligibility_effect == "neutral"
    assert "bse" in degraded.missing

    contradictory = reconcile_judgement(
        _judgement(),
        _receipt(
            CoverageStatus.CONTRADICTORY,
            contradictory_record_ids=("nse:1", "bse:1"),
        ),
    )
    assert contradictory.eligibility_effect == "neutral"


def test_contradiction_in_judgement_is_not_supportive_even_when_complete() -> None:
    judgement = _judgement().model_copy(
        update={"contradiction_record_ids": ("bse:1",)}
    )
    draft = reconcile_judgement(judgement, _receipt(CoverageStatus.COMPLETE))
    assert draft.eligibility_effect == "neutral"


def test_profile_releases_declare_exact_governed_node_order() -> None:
    closure_parts = corporate_event_profile_releases()
    profile = closure_parts.profile
    trajectory = closure_parts.trajectory

    assert profile.domain is EvidenceDomain.CORPORATE_EVENT
    assert profile.status is ReleaseStatus.SHADOW
    assert profile.trajectory_release_id == trajectory.release_id

    assert tuple((node.node_id, node.kind) for node in trajectory.nodes) == (
        P0_NODE_ORDER
    )
    assert trajectory.terminal_node_ids == ("admission",)


def test_profile_trajectory_terminal_path_crosses_seam_then_admission() -> None:
    trajectory = corporate_event_profile_releases().trajectory
    seam_to_admission = any(
        edge.source == "categorical_seam" and edge.target == "admission"
        for edge in trajectory.edges
    )
    assert seam_to_admission


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
