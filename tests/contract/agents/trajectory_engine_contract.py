"""Reusable contract for a governed ``TrajectoryEngine`` (spec §8.1, §9).

Any engine implementation (the P0 LangGraph engine, a future replacement) must
satisfy the same behavior at the project-owned seam:

* it executes the exact node IDs of the compiled release in the declared order;
* it wraps every node in canonical ledger start/finish events and never lets a
  node write the ledger itself;
* it never returns framework state, checkpoint objects, or graph internals — only
  a typed :class:`~trading_os.agents.trajectory.TrajectoryResult`;
* resume with the same ``run_id`` and release closure replays completed node
  effects from the canonical ledger instead of re-running them, and yields an
  identical final packet hash;
* a checkpoint that disagrees with the canonical ledger fails closed.

The contract binds through the project-owned :class:`TrajectoryCompiler`, never
by constructing framework objects directly, so it stays framework-agnostic.
"""

from datetime import UTC, datetime

from trading_os.agents.ledger import (
    AgentRunLedger,
    InMemoryAgentRunLedger,
)
from trading_os.agents.models import (
    NodeKind,
    ReleaseStatus,
    TrajectoryEdge,
    TrajectoryNodeRelease,
    TrajectoryRelease,
)
from trading_os.agents.trajectory import (
    CompiledTrajectory,
    NodeContext,
    NodeRegistry,
    TrajectoryCompiler,
    TrajectoryEngine,
    TrajectoryInvocation,
    TrajectoryResult,
)
from trading_os.research.models import EvidenceDomain, EvidencePacket

CUTOFF = datetime(2026, 7, 23, tzinfo=UTC)

# The standard P0 corporate-event shape (spec §8.2): two agent loops with a
# deterministic transform between them, then reconciliation, the categorical
# seam, and admission.
P0_NODES: tuple[tuple[str, NodeKind], ...] = (
    ("gather", NodeKind.AGENT_LOOP),
    ("normalize", NodeKind.DETERMINISTIC_TRANSFORM),
    ("validate", NodeKind.VALIDATION),
    ("judge", NodeKind.JUDGE),
    ("reconcile", NodeKind.DETERMINISTIC_TRANSFORM),
    ("categorical_seam", NodeKind.CATEGORICAL_SEAM),
    ("admission", NodeKind.ADMISSION),
)


def _linear_release(
    nodes: tuple[tuple[str, NodeKind], ...],
    *,
    release_id: str = "trajectory:corporate-event:v1",
) -> TrajectoryRelease:
    node_releases = tuple(
        TrajectoryNodeRelease(node_id=node_id, kind=kind) for node_id, kind in nodes
    )
    edges = tuple(
        TrajectoryEdge(source=nodes[i][0], target=nodes[i + 1][0])
        for i in range(len(nodes) - 1)
    )
    return TrajectoryRelease(
        release_id=release_id,
        status=ReleaseStatus.SHADOW,
        effective_from=CUTOFF,
        input_schema_id="schema:research-question:v1",
        output_schema_id="schema:evidence-packet:v1",
        nodes=node_releases,
        edges=edges,
        terminal_node_ids=(nodes[-1][0],),
        content_hash=f"sha256:{release_id}",
    )


def corporate_event_release() -> TrajectoryRelease:
    return _linear_release(P0_NODES)


def unsafe_release() -> TrajectoryRelease:
    """A terminal path that never crosses the categorical seam and admission."""

    nodes = (
        ("gather", NodeKind.AGENT_LOOP),
        ("judge", NodeKind.JUDGE),
    )
    return _linear_release(nodes, release_id="trajectory:unsafe:v1")


def seam_without_admission_release() -> TrajectoryRelease:
    nodes = (
        ("gather", NodeKind.AGENT_LOOP),
        ("categorical_seam", NodeKind.CATEGORICAL_SEAM),
    )
    return _linear_release(nodes, release_id="trajectory:seam-only:v1")


def _packet_for(invocation: TrajectoryInvocation) -> EvidencePacket:
    return EvidencePacket(
        packet_id=f"packet:{invocation.question_id}",
        instrument_id="instrument:1",
        domain=EvidenceDomain.CORPORATE_EVENT,
        assessment="material_event_supported",
        support=invocation.source_record_ids,
        contradictions=(),
        missing=(),
        as_of=CUTOFF,
        cutoff=CUTOFF,
        data_snapshot_id=invocation.data_snapshot_id,
        source_record_ids=invocation.source_record_ids,
        eligibility_effect="supportive",
    )


class _CrashOnce:
    """Handler wrapper that raises the first time a given node runs, then
    succeeds. Used to prove resume does not re-run completed nodes."""

    def __init__(self, crash_node_id: str) -> None:
        self.crash_node_id = crash_node_id
        self.executions: list[str] = []
        self._crashed = False

    async def run(self, context: NodeContext) -> NodeContext:
        self.executions.append(context.node_id)
        if context.node_id == self.crash_node_id and not self._crashed:
            self._crashed = True
            raise RuntimeError(f"injected crash at {context.node_id}")
        return context


def build_registry(crash: _CrashOnce | None = None) -> NodeRegistry:
    """A node registry whose handlers thread a categorical draft through the
    graph and construct the packet at the admission node."""

    async def gather(context: NodeContext) -> NodeContext:
        return context.with_artifact("gather", {"event_type": "material_agreement"})

    async def normalize(context: NodeContext) -> NodeContext:
        return context.with_artifact("normalize", {"within_cutoff": True})

    async def validate(context: NodeContext) -> NodeContext:
        return context.with_artifact("validate", {"ok": True})

    async def judge(context: NodeContext) -> NodeContext:
        return context.with_artifact("judge", {"assessment": "material_event_supported"})

    async def reconcile(context: NodeContext) -> NodeContext:
        return context.with_artifact("reconcile", {"eligibility_effect": "supportive"})

    async def categorical_seam(context: NodeContext) -> NodeContext:
        # The seam would reject executable numbers; the fixture draft carries none.
        return context.with_artifact("categorical_seam", {"seam_ok": True})

    async def admission(context: NodeContext) -> NodeContext:
        return context.with_packet(_packet_for(context.invocation))

    registry = NodeRegistry()
    handlers = {
        "gather": gather,
        "normalize": normalize,
        "validate": validate,
        "judge": judge,
        "reconcile": reconcile,
        "categorical_seam": categorical_seam,
        "admission": admission,
    }
    for node_id, handler in handlers.items():
        if crash is not None:

            def wrap(
                inner: object = handler,
            ):  # bind current handler
                async def wrapped(context: NodeContext) -> NodeContext:
                    context = await crash.run(context)
                    return await inner(context)  # type: ignore[operator]

                return wrapped

            registry.register(node_id, wrap())
        else:
            registry.register(node_id, handler)
    return registry


class TrajectoryEngineContract:
    def build_ledger(self) -> AgentRunLedger:
        return InMemoryAgentRunLedger()

    def build_engine(self, ledger: AgentRunLedger) -> TrajectoryEngine:
        raise NotImplementedError

    def build_compiler(
        self, engine: TrajectoryEngine, registry: NodeRegistry
    ) -> TrajectoryCompiler:
        return TrajectoryCompiler(engine=engine, node_registry=registry)

    def _invocation(self) -> TrajectoryInvocation:
        return TrajectoryInvocation(
            run_id="run:1",
            question_id="question:1",
            release_closure_hash="sha256:closure",
            data_snapshot_id="snapshot:1",
            source_record_ids=("sec:1",),
        )

    async def test_compile_produces_opaque_compiled_trajectory(self) -> None:
        engine = self.build_engine(self.build_ledger())
        compiler = self.build_compiler(engine, build_registry())
        compiled = compiler.compile(corporate_event_release())
        assert isinstance(compiled, CompiledTrajectory)
        assert compiled.release_id == "trajectory:corporate-event:v1"

    async def test_engine_runs_deterministic_node_between_agent_loops(self) -> None:
        engine = self.build_engine(self.build_ledger())
        compiler = self.build_compiler(engine, build_registry())
        compiled = compiler.compile(corporate_event_release())
        result = await engine.execute(compiled, self._invocation())
        assert isinstance(result, TrajectoryResult)
        assert result.visited_node_ids == (
            "gather",
            "normalize",
            "validate",
            "judge",
            "reconcile",
            "categorical_seam",
            "admission",
        )
        assert isinstance(result.packet, EvidencePacket)
        assert result.packet.eligibility_effect == "supportive"

    async def test_engine_records_ledger_events_and_never_returns_state(self) -> None:
        ledger = self.build_ledger()
        engine = self.build_engine(ledger)
        compiler = self.build_compiler(engine, build_registry())
        compiled = compiler.compile(corporate_event_release())
        result = await engine.execute(compiled, self._invocation())
        events = await ledger.events_for("run:1")
        kinds = [event.kind for event in events]
        # Each node produces a start and a finish, plus a terminal event.
        assert kinds.count("node_started") == 7
        assert kinds.count("node_finished") == 7
        assert kinds[-1] == "run_completed"
        # The public result is a typed value object, not framework state.
        assert not hasattr(result, "graph")
        assert not hasattr(result, "checkpoint")

    async def test_result_artifact_hash_is_deterministic(self) -> None:
        engine_a = self.build_engine(self.build_ledger())
        engine_b = self.build_engine(self.build_ledger())
        compiler_a = self.build_compiler(engine_a, build_registry())
        compiler_b = self.build_compiler(engine_b, build_registry())
        first = await engine_a.execute(
            compiler_a.compile(corporate_event_release()), self._invocation()
        )
        second = await engine_b.execute(
            compiler_b.compile(corporate_event_release()), self._invocation()
        )
        assert first.artifact_hash == second.artifact_hash
        assert first.packet == second.packet
