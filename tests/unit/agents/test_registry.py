from datetime import UTC, datetime

import pytest

from trading_os.agents.models import (
    AgentProfileRelease,
    NodeKind,
    RunBudget,
    TrajectoryEdge,
    TrajectoryNodeRelease,
    TrajectoryRelease,
)
from trading_os.agents.registry import ReleaseRegistry, ReleaseResolutionError
from trading_os.research.models import EvidenceDomain

CUTOFF = datetime(2026, 7, 23, 12, 0, tzinfo=UTC)


def _trajectory() -> TrajectoryRelease:
    return TrajectoryRelease(
        release_id="trajectory:corporate-event:v1",
        status="shadow",
        effective_from=datetime(2026, 7, 1, tzinfo=UTC),
        input_schema_id="schema:research-question:v1",
        output_schema_id="schema:evidence-packet:v1",
        nodes=(
            TrajectoryNodeRelease(node_id="gather", kind=NodeKind.AGENT_LOOP),
            TrajectoryNodeRelease(node_id="admission", kind=NodeKind.ADMISSION),
        ),
        edges=(TrajectoryEdge(source="gather", target="admission"),),
        terminal_node_ids=("admission",),
        content_hash="sha256:trajectory-v1",
    )


def _profile() -> AgentProfileRelease:
    return AgentProfileRelease(
        release_id="profile:corporate-event:v1",
        status="shadow",
        effective_from=datetime(2026, 7, 1, tzinfo=UTC),
        domain=EvidenceDomain.CORPORATE_EVENT,
        trajectory_release_id="trajectory:corporate-event:v1",
        prompt_release_ids=("prompt:gather:v1", "prompt:judge:v1"),
        capability_release_ids=("capability:source-record-query:v1",),
        source_policy_release_id="source-policy:corporate-event:v1",
        routing_policy_release_id="routing:fixture:v1",
        output_schema_release_id="schema:evidence-packet:v1",
        failure_policy_release_id="failure:explicit-missing:v1",
        evaluation_policy_release_id="evaluation:corporate-event:v1",
        budget=RunBudget(max_turns=4, max_tokens=8_000, max_tool_calls=8),
        content_hash="sha256:profile-v1",
    )


@pytest.fixture
def corporate_event_releases() -> tuple[
    tuple[AgentProfileRelease, ...], tuple[TrajectoryRelease, ...]
]:
    return (_profile(),), (_trajectory(),)


def test_registry_resolves_one_effective_shadow_profile(
    corporate_event_releases: tuple[
        tuple[AgentProfileRelease, ...], tuple[TrajectoryRelease, ...]
    ],
) -> None:
    registry = ReleaseRegistry(*corporate_event_releases)
    closure = registry.resolve(EvidenceDomain.CORPORATE_EVENT, CUTOFF)
    assert closure.profile.release_id == "profile:corporate-event:v1"
    assert closure.trajectory.release_id == "trajectory:corporate-event:v1"
    assert closure.content_hash.startswith("sha256:")


def test_registry_fails_on_two_effective_profiles(
    corporate_event_releases: tuple[
        tuple[AgentProfileRelease, ...], tuple[TrajectoryRelease, ...]
    ],
) -> None:
    profiles, trajectories = corporate_event_releases
    profile = profiles[0]
    registry = ReleaseRegistry(
        (profile, profile.model_copy(update={"release_id": "duplicate"})),
        trajectories,
    )
    with pytest.raises(ReleaseResolutionError, match="exactly one effective profile"):
        registry.resolve(EvidenceDomain.CORPORATE_EVENT, CUTOFF)


def test_registry_fails_when_no_effective_profile(
    corporate_event_releases: tuple[
        tuple[AgentProfileRelease, ...], tuple[TrajectoryRelease, ...]
    ],
) -> None:
    profiles, trajectories = corporate_event_releases
    registry = ReleaseRegistry(profiles, trajectories)
    before = datetime(2026, 6, 1, tzinfo=UTC)
    with pytest.raises(ReleaseResolutionError, match="exactly one effective profile"):
        registry.resolve(EvidenceDomain.CORPORATE_EVENT, before)


def test_registry_fails_when_trajectory_unavailable(
    corporate_event_releases: tuple[
        tuple[AgentProfileRelease, ...], tuple[TrajectoryRelease, ...]
    ],
) -> None:
    profiles, _ = corporate_event_releases
    registry = ReleaseRegistry(profiles, ())
    with pytest.raises(ReleaseResolutionError, match="trajectory release is unavailable"):
        registry.resolve(EvidenceDomain.CORPORATE_EVENT, CUTOFF)


def test_registry_excludes_expired_and_wrong_status_profiles() -> None:
    expired = _profile().model_copy(
        update={
            "release_id": "profile:expired",
            "effective_until": datetime(2026, 7, 10, tzinfo=UTC),
        }
    )
    proposed = _profile().model_copy(
        update={"release_id": "profile:proposed", "status": "proposed"}
    )
    active = _profile().model_copy(
        update={"release_id": "profile:active", "status": "active"}
    )
    registry = ReleaseRegistry((expired, proposed, active), (_trajectory(),))
    closure = registry.resolve(EvidenceDomain.CORPORATE_EVENT, CUTOFF)
    assert closure.profile.release_id == "profile:active"
