from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from trading_os.agents.models import (
    AgentProfileRelease,
    NodeKind,
    RunBudget,
    TrajectoryEdge,
    TrajectoryNodeRelease,
    TrajectoryRelease,
)
from trading_os.research.models import EvidenceDomain


def test_agent_profile_is_immutable_and_references_releases_only() -> None:
    profile = AgentProfileRelease(
        release_id="profile:corporate-event:v1",
        status="shadow",
        effective_from=datetime(2026, 7, 23, tzinfo=UTC),
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
    with pytest.raises(ValidationError):
        profile.domain = EvidenceDomain.FUNDAMENTAL


def test_trajectory_rejects_cycle_without_monotonic_budget_gate() -> None:
    with pytest.raises(ValidationError, match="cycle requires a budget gate"):
        TrajectoryRelease(
            release_id="trajectory:bad:v1",
            status="shadow",
            effective_from=datetime(2026, 7, 23, tzinfo=UTC),
            input_schema_id="schema:research-question:v1",
            output_schema_id="schema:evidence-packet:v1",
            nodes=(
                TrajectoryNodeRelease(node_id="gather", kind=NodeKind.AGENT_LOOP),
                TrajectoryNodeRelease(node_id="judge", kind=NodeKind.AGENT_LOOP),
            ),
            edges=(
                TrajectoryEdge(source="gather", target="judge"),
                TrajectoryEdge(source="judge", target="gather"),
            ),
            terminal_node_ids=("judge",),
            content_hash="sha256:bad",
        )


def test_trajectory_allows_cycle_with_budget_gate() -> None:
    # The budget gate must sit ON the cycle and carry a RunBudget.
    trajectory = TrajectoryRelease(
        release_id="trajectory:good:v1",
        status="shadow",
        effective_from=datetime(2026, 7, 23, tzinfo=UTC),
        input_schema_id="schema:research-question:v1",
        output_schema_id="schema:evidence-packet:v1",
        nodes=(
            TrajectoryNodeRelease(node_id="gather", kind=NodeKind.AGENT_LOOP),
            TrajectoryNodeRelease(
                node_id="gate",
                kind=NodeKind.BUDGET_GATE,
                budget=RunBudget(max_turns=2, max_tokens=1_000, max_tool_calls=2),
            ),
            TrajectoryNodeRelease(node_id="judge", kind=NodeKind.AGENT_LOOP),
        ),
        edges=(
            TrajectoryEdge(source="gather", target="gate"),
            TrajectoryEdge(source="gate", target="judge"),
            TrajectoryEdge(source="judge", target="gather"),
        ),
        terminal_node_ids=("judge",),
        content_hash="sha256:good",
    )
    assert trajectory.release_id == "trajectory:good:v1"


def test_trajectory_rejects_three_node_cycle_without_gate() -> None:
    # Regression (workflow critic): a >=3-node cycle a->b->c->a was NOT detected
    # by pairwise-reciprocal cycle detection and was admitted with no gate.
    with pytest.raises(ValidationError, match="cycle requires a budget gate"):
        TrajectoryRelease(
            release_id="trajectory:three-cycle:v1",
            status="shadow",
            effective_from=datetime(2026, 7, 23, tzinfo=UTC),
            input_schema_id="schema:research-question:v1",
            output_schema_id="schema:evidence-packet:v1",
            nodes=(
                TrajectoryNodeRelease(node_id="a", kind=NodeKind.AGENT_LOOP),
                TrajectoryNodeRelease(node_id="b", kind=NodeKind.AGENT_LOOP),
                TrajectoryNodeRelease(node_id="c", kind=NodeKind.AGENT_LOOP),
            ),
            edges=(
                TrajectoryEdge(source="a", target="b"),
                TrajectoryEdge(source="b", target="c"),
                TrajectoryEdge(source="c", target="a"),
            ),
            terminal_node_ids=("c",),
            content_hash="sha256:three-cycle",
        )


def test_trajectory_rejects_gate_off_the_cycle() -> None:
    # Regression (workflow critic): a BUDGET_GATE disconnected from the cycle
    # (edges only connect the cycle nodes) does not bound the loop.
    with pytest.raises(ValidationError, match="budget gate.*on the cycle"):
        TrajectoryRelease(
            release_id="trajectory:gate-off-cycle:v1",
            status="shadow",
            effective_from=datetime(2026, 7, 23, tzinfo=UTC),
            input_schema_id="schema:research-question:v1",
            output_schema_id="schema:evidence-packet:v1",
            nodes=(
                TrajectoryNodeRelease(node_id="gather", kind=NodeKind.AGENT_LOOP),
                TrajectoryNodeRelease(node_id="judge", kind=NodeKind.AGENT_LOOP),
                TrajectoryNodeRelease(
                    node_id="dead_gate",
                    kind=NodeKind.BUDGET_GATE,
                    budget=RunBudget(
                        max_turns=2, max_tokens=1_000, max_tool_calls=2
                    ),
                ),
            ),
            edges=(
                TrajectoryEdge(source="gather", target="judge"),
                TrajectoryEdge(source="judge", target="gather"),
            ),
            terminal_node_ids=("judge",),
            content_hash="sha256:gate-off-cycle",
        )


def test_trajectory_rejects_gate_on_cycle_without_budget() -> None:
    # A gate on the cycle that carries no RunBudget does not bound anything.
    with pytest.raises(ValidationError, match="budget gate.*RunBudget"):
        TrajectoryRelease(
            release_id="trajectory:gate-no-budget:v1",
            status="shadow",
            effective_from=datetime(2026, 7, 23, tzinfo=UTC),
            input_schema_id="schema:research-question:v1",
            output_schema_id="schema:evidence-packet:v1",
            nodes=(
                TrajectoryNodeRelease(node_id="gather", kind=NodeKind.AGENT_LOOP),
                TrajectoryNodeRelease(
                    node_id="gate", kind=NodeKind.BUDGET_GATE
                ),
                TrajectoryNodeRelease(node_id="judge", kind=NodeKind.AGENT_LOOP),
            ),
            edges=(
                TrajectoryEdge(source="gather", target="gate"),
                TrajectoryEdge(source="gate", target="judge"),
                TrajectoryEdge(source="judge", target="gather"),
            ),
            terminal_node_ids=("judge",),
            content_hash="sha256:gate-no-budget",
        )


def test_trajectory_rejects_unknown_terminal_node() -> None:
    with pytest.raises(ValidationError, match="terminal node is not registered"):
        TrajectoryRelease(
            release_id="trajectory:bad-terminal:v1",
            status="shadow",
            effective_from=datetime(2026, 7, 23, tzinfo=UTC),
            input_schema_id="schema:research-question:v1",
            output_schema_id="schema:evidence-packet:v1",
            nodes=(TrajectoryNodeRelease(node_id="gather", kind=NodeKind.AGENT_LOOP),),
            edges=(),
            terminal_node_ids=("missing",),
            content_hash="sha256:bad-terminal",
        )


def test_run_budget_is_frozen_and_bounded() -> None:
    budget = RunBudget(max_turns=4, max_tokens=8_000, max_tool_calls=8)
    with pytest.raises(ValidationError):
        budget.max_turns = 99
    with pytest.raises(ValidationError):
        RunBudget(max_turns=0, max_tokens=8_000, max_tool_calls=8)
