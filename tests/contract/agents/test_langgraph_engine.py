"""The contained LangGraph engine satisfies the ``TrajectoryEngine`` contract.

These tests also cover the compiler's fail-closed rules (a terminal path must
cross the categorical seam then admission) and crash/resume at every node
boundary of the standard corporate-event trajectory.
"""

import pytest

from tests.contract.agents.trajectory_engine_contract import (
    P0_NODES,
    TrajectoryEngineContract,
    _CrashOnce,
    build_registry,
    bypass_admission_release,
    capability_on_deterministic_node_release,
    corporate_event_release,
    seam_without_admission_release,
    unsafe_release,
)

from trading_os.agents.ledger import AgentRunLedger, InMemoryAgentRunLedger
from trading_os.agents.langgraph_engine import LangGraphTrajectoryEngine
from trading_os.agents.trajectory import (
    TrajectoryCompileError,
    TrajectoryCompiler,
    TrajectoryEngine,
    TrajectoryInvocation,
)


class TestLangGraphTrajectoryEngine(TrajectoryEngineContract):
    def build_engine(self, ledger: AgentRunLedger) -> TrajectoryEngine:
        return LangGraphTrajectoryEngine(ledger=ledger)


def _invocation() -> TrajectoryInvocation:
    return TrajectoryInvocation(
        run_id="run:1",
        question_id="question:1",
        release_closure_hash="sha256:closure",
        data_snapshot_id="snapshot:1",
        source_record_ids=("sec:1",),
    )


def _compiler(ledger: AgentRunLedger) -> TrajectoryCompiler:
    return TrajectoryCompiler(
        engine=LangGraphTrajectoryEngine(ledger=ledger),
        node_registry=build_registry(),
    )


def test_compiler_rejects_terminal_path_without_seam_and_admission() -> None:
    compiler = _compiler(InMemoryAgentRunLedger())
    with pytest.raises(
        TrajectoryCompileError,
        match="terminal path must cross categorical seam and admission",
    ):
        compiler.compile(unsafe_release())


def test_compiler_rejects_seam_without_following_admission() -> None:
    compiler = _compiler(InMemoryAgentRunLedger())
    with pytest.raises(
        TrajectoryCompileError,
        match="terminal path must cross categorical seam and admission",
    ):
        compiler.compile(seam_without_admission_release())


def test_compiler_rejects_admission_with_a_bypass_edge_skipping_the_seam() -> None:
    # Regression (workflow critic): the terminal-path validator accepted an
    # admission node when ANY predecessor was the seam, so a bypass edge
    # (gather->admission) that skips the seam passed compiler validation.
    compiler = _compiler(InMemoryAgentRunLedger())
    with pytest.raises(
        TrajectoryCompileError,
        match="every path into admission must cross the categorical seam",
    ):
        compiler.compile(bypass_admission_release())


def test_compiler_rejects_capability_on_a_non_agentic_node() -> None:
    # Deny-by-default (spec §12): a deterministic/seam/admission node may not
    # declare a tool capability. Restores the plan-specified _validate_capabilities.
    compiler = _compiler(InMemoryAgentRunLedger())
    with pytest.raises(
        TrajectoryCompileError,
        match="only agentic nodes may declare capabilities",
    ):
        compiler.compile(capability_on_deterministic_node_release())


def test_compiler_rejects_release_with_unregistered_node() -> None:
    ledger = InMemoryAgentRunLedger()
    compiler = TrajectoryCompiler(
        engine=LangGraphTrajectoryEngine(ledger=ledger),
        node_registry=build_registry(),
    )
    # Drop the "judge" handler so the release references an unregistered node.
    compiler._node_registry._handlers.pop("judge")  # type: ignore[attr-defined]
    with pytest.raises(TrajectoryCompileError, match="no registered handler"):
        compiler.compile(corporate_event_release())


@pytest.mark.parametrize("crash_node_id", [node_id for node_id, _ in P0_NODES])
async def test_resume_at_every_boundary_does_not_duplicate_or_change_evidence(
    crash_node_id: str,
) -> None:
    ledger = InMemoryAgentRunLedger()
    crash = _CrashOnce(crash_node_id)
    compiler = TrajectoryCompiler(
        engine=LangGraphTrajectoryEngine(ledger=ledger),
        node_registry=build_registry(crash=crash),
    )
    compiled = compiler.compile(corporate_event_release())
    engine = LangGraphTrajectoryEngine(ledger=ledger)

    # First attempt crashes at the injected node.
    with pytest.raises(RuntimeError, match="injected crash"):
        await engine.execute(compiled, _invocation())

    # A clean run over the same trajectory to obtain the canonical packet hash.
    reference_ledger = InMemoryAgentRunLedger()
    reference_engine = LangGraphTrajectoryEngine(ledger=reference_ledger)
    reference_compiler = TrajectoryCompiler(
        engine=reference_engine, node_registry=build_registry()
    )
    reference_result = await reference_engine.execute(
        reference_compiler.compile(corporate_event_release()),
        _invocation().model_copy(update={"run_id": "run:reference"}),
    )

    # Resume with the same run ID and release closure.
    result = await engine.execute(compiled, _invocation())

    # Nodes before the crash node were completed on the first attempt and must
    # not be re-executed on resume.
    crash_index = [node_id for node_id, _ in P0_NODES].index(crash_node_id)
    completed_before_crash = [node_id for node_id, _ in P0_NODES][:crash_index]
    for node_id in completed_before_crash:
        assert crash.executions.count(node_id) == 1, node_id

    assert result.visited_node_ids == tuple(node_id for node_id, _ in P0_NODES)
    assert result.artifact_hash == reference_result.artifact_hash
    assert result.packet == reference_result.packet
