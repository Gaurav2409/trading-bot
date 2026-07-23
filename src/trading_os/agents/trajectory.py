"""Project-owned trajectory compiler seam (spec §8.1, §8.2).

``TrajectoryRelease`` is the executable source of truth. This module compiles a
release into an opaque :class:`CompiledTrajectory` and executes it through a
:class:`TrajectoryEngine` whose only public operation is
:meth:`TrajectoryEngine.execute`. LangGraph — or any future substrate — lives
behind that seam; framework state, checkpoints, and runnables never cross it.

The compiler enforces the structural safety rules that the release model cannot
express on its own:

* every registered node ID has a project-owned handler in the node registry;
* every terminal path crosses a categorical-seam node and then an admission node
  before it can produce a packet.

Node handlers are project code, not part of the release. They receive an
immutable :class:`NodeContext` (the frozen invocation, the accumulated typed
node artifacts, and the candidate packet) and return a new context. Handlers
cannot write the canonical ledger; the engine wraps them and emits the events.
"""

from collections.abc import Awaitable, Callable, Mapping
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from trading_os.agents.models import NodeKind, TrajectoryRelease
from trading_os.research.models import EvidencePacket


class TrajectoryCompileError(RuntimeError):
    """Raised when a release cannot be compiled to a safe executable graph."""


# Only these node kinds invoke a model or a tool and may therefore reference a
# capability release (spec §12). Every other kind is pure project code.
_AGENTIC_NODE_KINDS: frozenset[NodeKind] = frozenset(
    {NodeKind.AGENT_LOOP, NodeKind.JUDGE, NodeKind.FAN_OUT}
)


class TrajectoryInvocation(BaseModel, frozen=True):
    run_id: str
    question_id: str
    release_closure_hash: str
    data_snapshot_id: str
    source_record_ids: tuple[str, ...]


class NodeContext(BaseModel, frozen=True):
    """Immutable state threaded between node handlers.

    ``artifacts`` holds the typed-but-opaque outputs of completed nodes keyed by
    node ID; ``packet`` is the candidate evidence packet, populated by the
    admission node. Numeric intermediates stay inside ``artifacts`` and never
    reach the packet except through the categorical seam and admission.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    node_id: str
    invocation: TrajectoryInvocation
    artifacts: tuple[tuple[str, str], ...] = ()
    packet: EvidencePacket | None = None

    def for_node(self, node_id: str) -> "NodeContext":
        return self.model_copy(update={"node_id": node_id})

    def with_artifact(self, node_id: str, artifact: Mapping[str, object]) -> "NodeContext":
        rendered = _render_artifact(artifact)
        return self.model_copy(update={"artifacts": (*self.artifacts, (node_id, rendered))})

    def with_packet(self, packet: EvidencePacket) -> "NodeContext":
        return self.model_copy(update={"packet": packet})


def _render_artifact(artifact: Mapping[str, object]) -> str:
    """Deterministic canonical string for a node artifact (order-independent)."""

    return ";".join(f"{key}={artifact[key]!r}" for key in sorted(artifact))


NodeHandler = Callable[[NodeContext], Awaitable[NodeContext]]


class NodeRegistry:
    """Maps release node IDs to project-owned async handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, NodeHandler] = {}

    def register(self, node_id: str, handler: NodeHandler) -> None:
        if node_id in self._handlers:
            raise TrajectoryCompileError(f"duplicate handler for node {node_id!r}")
        self._handlers[node_id] = handler

    def get(self, node_id: str) -> NodeHandler:
        handler = self._handlers.get(node_id)
        if handler is None:
            raise TrajectoryCompileError(
                f"no registered handler for node {node_id!r}"
            )
        return handler

    def has(self, node_id: str) -> bool:
        return node_id in self._handlers


class TrajectoryResult(BaseModel, frozen=True):
    packet: EvidencePacket
    visited_node_ids: tuple[str, ...]
    artifact_hash: str


class CompiledTrajectory:
    """Opaque, project-owned handle over a compiled release.

    Callers never see the underlying graph. The engine that produced it knows
    how to interpret :attr:`graph`; nothing else does.
    """

    __slots__ = ("release_id", "_graph", "_node_order", "_node_registry")

    def __init__(
        self,
        release_id: str,
        graph: object,
        node_order: tuple[str, ...],
        node_registry: NodeRegistry,
    ) -> None:
        self.release_id = release_id
        self._graph = graph
        self._node_order = node_order
        self._node_registry = node_registry

    @property
    def graph(self) -> object:
        return self._graph

    @property
    def node_order(self) -> tuple[str, ...]:
        return self._node_order

    @property
    def node_registry(self) -> NodeRegistry:
        return self._node_registry


class TrajectoryEngine(Protocol):
    def compile(
        self, release: TrajectoryRelease, node_registry: NodeRegistry
    ) -> CompiledTrajectory: ...

    async def execute(
        self, compiled: CompiledTrajectory, invocation: TrajectoryInvocation
    ) -> TrajectoryResult: ...


class TrajectoryCompiler:
    """Validates a release and delegates graph construction to the engine."""

    def __init__(
        self, *, engine: TrajectoryEngine, node_registry: NodeRegistry
    ) -> None:
        self._engine = engine
        self._node_registry = node_registry

    def compile(self, release: TrajectoryRelease) -> CompiledTrajectory:
        self._validate_node_handlers(release)
        self._validate_capabilities(release)
        self._validate_terminal_paths(release)
        return self._engine.compile(release, self._node_registry)

    def _validate_node_handlers(self, release: TrajectoryRelease) -> None:
        for node in release.nodes:
            if not self._node_registry.has(node.node_id):
                raise TrajectoryCompileError(
                    f"no registered handler for node {node.node_id!r}"
                )

    def _validate_capabilities(self, release: TrajectoryRelease) -> None:
        """Deny-by-default (spec §12, constraint 6): only agentic node kinds may
        reference a tool capability. A deterministic transform, validation,
        branch, join, budget gate, categorical seam, admission, or explicit-
        missing node holding a capability is a compile-time containment
        violation — those nodes are pure project code and call no tools.
        """

        for node in release.nodes:
            if node.capability_release_ids and node.kind not in _AGENTIC_NODE_KINDS:
                raise TrajectoryCompileError(
                    f"only agentic nodes may declare capabilities; "
                    f"node {node.node_id!r} ({node.kind}) declares "
                    f"{node.capability_release_ids!r}"
                )

    def _validate_terminal_paths(self, release: TrajectoryRelease) -> None:
        kinds = {node.node_id: node.kind for node in release.nodes}
        successors: dict[str, list[str]] = {node.node_id: [] for node in release.nodes}
        predecessors: dict[str, list[str]] = {node.node_id: [] for node in release.nodes}
        for edge in release.edges:
            successors[edge.source].append(edge.target)
            predecessors[edge.target].append(edge.source)

        for terminal_id in release.terminal_node_ids:
            if kinds.get(terminal_id) is not NodeKind.ADMISSION:
                raise TrajectoryCompileError(
                    "terminal path must cross categorical seam and admission"
                )
            admission_predecessors = predecessors[terminal_id]
            if not admission_predecessors:
                raise TrajectoryCompileError(
                    "terminal path must cross categorical seam and admission"
                )
            # EVERY path into admission must cross the categorical seam — not
            # just one. A bypass edge that reaches admission without the seam is
            # a hole through which an unvalidated packet could be admitted.
            if any(
                kinds.get(pred) is not NodeKind.CATEGORICAL_SEAM
                for pred in admission_predecessors
            ):
                raise TrajectoryCompileError(
                    "every path into admission must cross the categorical seam"
                )
