"""Immutable P0 corporate-event profile and trajectory releases (spec §7, §8.2).

``corporate_event_profile_releases`` builds the frozen desired-state closure for
the shadow-only corporate-event tracer: an :class:`AgentProfileRelease`
referencing only other releases by ID, and its :class:`TrajectoryRelease`
declaring the exact governed node order

    gather -> normalize -> validate -> judge -> reconcile
        -> categorical_seam -> admission

The terminal ``admission`` node is preceded by the ``categorical_seam`` node so
the compiler's fail-closed rule (terminal path must cross the categorical seam
then admission) is satisfied. The closure ``content_hash`` is derived
deterministically from the profile and trajectory hashes, matching
``ReleaseRegistry.resolve``.
"""

from datetime import UTC, datetime
from hashlib import sha256

from trading_os.agents.models import (
    AgentProfileRelease,
    NodeKind,
    ReleaseClosure,
    ReleaseStatus,
    RunBudget,
    TrajectoryEdge,
    TrajectoryNodeRelease,
    TrajectoryRelease,
)
from trading_os.research.models import EvidenceDomain

CORPORATE_EVENT_EFFECTIVE_FROM = datetime(2026, 7, 23, tzinfo=UTC)

# The exact P0 governed node order (spec §8.2): two agent loops with a
# deterministic transform between them, then reconciliation, the categorical
# seam, and admission.
_P0_NODES: tuple[tuple[str, NodeKind], ...] = (
    ("gather", NodeKind.AGENT_LOOP),
    ("normalize", NodeKind.DETERMINISTIC_TRANSFORM),
    ("validate", NodeKind.VALIDATION),
    ("judge", NodeKind.JUDGE),
    ("reconcile", NodeKind.DETERMINISTIC_TRANSFORM),
    ("categorical_seam", NodeKind.CATEGORICAL_SEAM),
    ("admission", NodeKind.ADMISSION),
)

_SOURCE_QUERY_CAPABILITY_ID = "capability:source-record-query:v1"
_TRAJECTORY_RELEASE_ID = "trajectory:corporate-event:v1"
_PROFILE_RELEASE_ID = "profile:corporate-event:v1"


def corporate_event_trajectory_release() -> TrajectoryRelease:
    """The immutable P0 corporate-event trajectory release."""

    nodes = tuple(
        TrajectoryNodeRelease(
            node_id=node_id,
            kind=kind,
            capability_release_ids=(
                (_SOURCE_QUERY_CAPABILITY_ID,)
                if kind in {NodeKind.AGENT_LOOP, NodeKind.JUDGE}
                else ()
            ),
        )
        for node_id, kind in _P0_NODES
    )
    edges = tuple(
        TrajectoryEdge(source=_P0_NODES[i][0], target=_P0_NODES[i + 1][0])
        for i in range(len(_P0_NODES) - 1)
    )
    return TrajectoryRelease(
        release_id=_TRAJECTORY_RELEASE_ID,
        status=ReleaseStatus.SHADOW,
        effective_from=CORPORATE_EVENT_EFFECTIVE_FROM,
        input_schema_id="schema:research-question:v1",
        output_schema_id="schema:evidence-packet:v1",
        nodes=nodes,
        edges=edges,
        terminal_node_ids=("admission",),
        content_hash=f"sha256:{_TRAJECTORY_RELEASE_ID}",
    )


def corporate_event_profile_release() -> AgentProfileRelease:
    """The immutable P0 corporate-event profile release."""

    return AgentProfileRelease(
        release_id=_PROFILE_RELEASE_ID,
        status=ReleaseStatus.SHADOW,
        effective_from=CORPORATE_EVENT_EFFECTIVE_FROM,
        domain=EvidenceDomain.CORPORATE_EVENT,
        trajectory_release_id=_TRAJECTORY_RELEASE_ID,
        prompt_release_ids=("prompt:gather:v1", "prompt:judge:v1"),
        capability_release_ids=(_SOURCE_QUERY_CAPABILITY_ID,),
        source_policy_release_id="source-policy:corporate-event:v1",
        routing_policy_release_id="routing:fixture:v1",
        output_schema_release_id="schema:evidence-packet:v1",
        failure_policy_release_id="failure:explicit-missing:v1",
        evaluation_policy_release_id="evaluation:corporate-event:v1",
        budget=RunBudget(max_turns=4, max_tokens=8_000, max_tool_calls=8),
        content_hash=f"sha256:{_PROFILE_RELEASE_ID}",
    )


def corporate_event_profile_releases() -> ReleaseClosure:
    """Build the frozen P0 corporate-event desired-state closure."""

    profile = corporate_event_profile_release()
    trajectory = corporate_event_trajectory_release()
    digest = sha256(
        f"{profile.content_hash}\x00{trajectory.content_hash}".encode()
    ).hexdigest()
    return ReleaseClosure(
        profile=profile,
        trajectory=trajectory,
        content_hash=f"sha256:{digest}",
    )
