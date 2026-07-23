from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from trading_os.research.models import EvidenceDomain


class ReleaseStatus(StrEnum):
    PROPOSED = "proposed"
    EXPERIMENTAL = "experimental"
    SHADOW = "shadow"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    RETIRED = "retired"


class NodeKind(StrEnum):
    AGENT_LOOP = "agent_loop"
    DETERMINISTIC_TRANSFORM = "deterministic_transform"
    VALIDATION = "validation"
    BRANCH = "branch"
    FAN_OUT = "fan_out"
    JOIN = "join"
    JUDGE = "judge"
    CATEGORICAL_SEAM = "categorical_seam"
    ADMISSION = "admission"
    EXPLICIT_MISSING = "explicit_missing"
    BUDGET_GATE = "budget_gate"


class CoverageStatus(StrEnum):
    COMPLETE = "complete"
    DEGRADED = "degraded"
    CONTRADICTORY = "contradictory"
    INSUFFICIENT = "insufficient"
    SUSPENDED = "suspended"
    INAPPLICABLE = "inapplicable"


class RunOutcome(StrEnum):
    ADMITTED = "admitted"
    EXPLICIT_MISSING = "explicit_missing"
    CATASTROPHIC = "catastrophic"


class ExpectedAgentFailure(RuntimeError):
    def __init__(self, kind: str, *, retryable: bool = False) -> None:
        super().__init__(kind)
        self.kind = kind
        self.retryable = retryable


class RunBudget(BaseModel, frozen=True):
    max_turns: int = Field(ge=1)
    max_tokens: int = Field(ge=1)
    max_tool_calls: int = Field(ge=0)
    max_elapsed_ms: int = Field(default=30_000, ge=1)
    max_cost_microunits: int = Field(default=0, ge=0)


class TrajectoryNodeRelease(BaseModel, frozen=True):
    node_id: str
    kind: NodeKind
    capability_release_ids: tuple[str, ...] = ()
    budget: RunBudget | None = None


class TrajectoryEdge(BaseModel, frozen=True):
    source: str
    target: str
    condition: str | None = None


class TrajectoryRelease(BaseModel, frozen=True):
    release_id: str
    status: ReleaseStatus
    effective_from: datetime
    effective_until: datetime | None = None
    supersedes: str | None = None
    input_schema_id: str
    output_schema_id: str
    nodes: tuple[TrajectoryNodeRelease, ...]
    edges: tuple[TrajectoryEdge, ...]
    terminal_node_ids: tuple[str, ...]
    content_hash: str

    @model_validator(mode="after")
    def validate_graph(self) -> "TrajectoryRelease":
        node_ids = {node.node_id for node in self.nodes}
        if len(node_ids) != len(self.nodes):
            raise ValueError("node IDs must be unique")
        if not set(self.terminal_node_ids).issubset(node_ids):
            raise ValueError("terminal node is not registered")
        if any(
            edge.source not in node_ids or edge.target not in node_ids
            for edge in self.edges
        ):
            raise ValueError("edge references an unknown node")
        # Bounded-cycle safety (spec §8, constraint 5). A trajectory may contain
        # cycles only if EVERY cycle is bounded by a budget gate that sits ON the
        # cycle and carries a RunBudget. Cycle detection must catch cycles of any
        # length (a->b->c->a), not just 2-node reciprocal pairs.
        gate_ids = {
            node.node_id
            for node in self.nodes
            if node.kind is NodeKind.BUDGET_GATE
        }
        budgeted_gate_ids = {
            node.node_id
            for node in self.nodes
            if node.kind is NodeKind.BUDGET_GATE and node.budget is not None
        }
        for cycle in self._cycles():
            on_cycle_gates = cycle & gate_ids
            if not on_cycle_gates:
                # Matches both "cycle requires a budget gate" (no gate at all)
                # and "budget gate ... on the cycle" (gate exists but off-cycle).
                raise ValueError(
                    "cycle requires a budget gate on the cycle path"
                )
            if not (on_cycle_gates & budgeted_gate_ids):
                raise ValueError(
                    "budget gate on the cycle must carry a RunBudget"
                )
        return self

    def _cycles(self) -> list[set[str]]:
        """Return the node sets of each strongly connected component that is a
        cycle (an SCC of size > 1, or a self-loop). Tarjan's algorithm.
        """

        adjacency: dict[str, list[str]] = {
            node.node_id: [] for node in self.nodes
        }
        for edge in self.edges:
            adjacency[edge.source].append(edge.target)

        index_counter = [0]
        stack: list[str] = []
        on_stack: set[str] = set()
        indices: dict[str, int] = {}
        low: dict[str, int] = {}
        components: list[set[str]] = []
        self_loops = {edge.source for edge in self.edges if edge.source == edge.target}

        def strongconnect(node: str) -> None:
            indices[node] = index_counter[0]
            low[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack.add(node)
            for successor in adjacency[node]:
                if successor not in indices:
                    strongconnect(successor)
                    low[node] = min(low[node], low[successor])
                elif successor in on_stack:
                    low[node] = min(low[node], indices[successor])
            if low[node] == indices[node]:
                component: set[str] = set()
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component.add(member)
                    if member == node:
                        break
                if len(component) > 1 or component & self_loops:
                    components.append(component)

        for node_id in adjacency:
            if node_id not in indices:
                strongconnect(node_id)
        return components


class AgentProfileRelease(BaseModel, frozen=True):
    release_id: str
    status: ReleaseStatus
    effective_from: datetime
    effective_until: datetime | None = None
    supersedes: str | None = None
    domain: EvidenceDomain
    trajectory_release_id: str
    prompt_release_ids: tuple[str, ...]
    capability_release_ids: tuple[str, ...]
    source_policy_release_id: str
    routing_policy_release_id: str
    output_schema_release_id: str
    failure_policy_release_id: str
    evaluation_policy_release_id: str
    budget: RunBudget
    content_hash: str


class ReleaseClosure(BaseModel, frozen=True):
    profile: AgentProfileRelease
    trajectory: TrajectoryRelease
    content_hash: str
