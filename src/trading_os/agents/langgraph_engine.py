"""Contained LangGraph implementation of :class:`TrajectoryEngine` (spec §8.1, §9).

LangGraph is a private execution substrate here. This engine builds a
``StateGraph`` from the release's node IDs and edges, wraps every node handler
with canonical ledger ``node_started`` / ``node_finished`` events, and returns a
typed :class:`~trading_os.agents.trajectory.TrajectoryResult`. LangGraph state,
checkpoint objects, and runnables never leave this module.

Recovery follows spec §9: the LangGraph checkpointer is a *recovery projection*
that lets a resumed run skip already-completed nodes, while the append-only
ledger stays canonical audit truth. A node emits ``node_started`` and
``node_finished`` events exactly once. On resume with the same ``run_id`` and
release closure, completed nodes are restored from the checkpoint and their
handlers are not re-run, so their effects are neither duplicated nor changed. A
resume whose release closure disagrees with the recorded ledger fails closed.
"""

from hashlib import sha256
from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from trading_os.agents.ledger import (
    AgentRunEvent,
    AgentRunLedger,
    LedgerConflict,
)
from trading_os.agents.models import TrajectoryRelease
from trading_os.agents.trajectory import (
    CompiledTrajectory,
    NodeContext,
    NodeRegistry,
    TrajectoryInvocation,
    TrajectoryResult,
)


class _GraphState(TypedDict):
    context: NodeContext


class LangGraphTrajectoryEngine:
    """Executes compiled trajectories on a private LangGraph runtime."""

    def __init__(self, *, ledger: AgentRunLedger) -> None:
        self._ledger = ledger
        # Recovery-only projection, private to this engine and never returned.
        self._checkpointer = InMemorySaver()

    def compile(
        self, release: TrajectoryRelease, node_registry: NodeRegistry
    ) -> CompiledTrajectory:
        node_order = self._linear_order(release)
        builder: StateGraph[_GraphState, Any, _GraphState, _GraphState] = StateGraph(
            _GraphState
        )
        for node_id in node_order:
            builder.add_node(node_id, self._make_graph_node(node_id, node_registry))
        builder.add_edge(START, node_order[0])
        for source, target in zip(node_order, node_order[1:], strict=False):
            builder.add_edge(source, target)
        builder.add_edge(node_order[-1], END)
        graph = builder.compile(checkpointer=self._checkpointer)
        return CompiledTrajectory(
            release_id=release.release_id,
            graph=graph,
            node_order=node_order,
            node_registry=node_registry,
        )

    @staticmethod
    def _linear_order(release: TrajectoryRelease) -> tuple[str, ...]:
        successors = {edge.source: edge.target for edge in release.edges}
        targets = {edge.target for edge in release.edges}
        starts = [node.node_id for node in release.nodes if node.node_id not in targets]
        if len(starts) != 1:
            raise ValueError("trajectory must have exactly one entry node")
        order: list[str] = [starts[0]]
        while order[-1] in successors:
            order.append(successors[order[-1]])
        if len(order) != len(release.nodes):
            raise ValueError("trajectory graph is not a simple linear path")
        return tuple(order)

    def _make_graph_node(self, node_id: str, node_registry: NodeRegistry) -> Any:
        handler = node_registry.get(node_id)

        async def graph_node(state: _GraphState) -> _GraphState:
            context = state["context"].for_node(node_id)
            await self._append(context, kind="node_started", artifact_hash=None)
            result = await handler(context)
            await self._append(
                result, kind="node_finished", artifact_hash=self._context_hash(result)
            )
            return {"context": result}

        return graph_node

    async def _append(
        self, context: NodeContext, *, kind: str, artifact_hash: str | None
    ) -> None:
        events = await self._ledger.events_for(context.invocation.run_id)
        event = AgentRunEvent(
            run_id=context.invocation.run_id,
            sequence=len(events),
            kind=kind,
            release_closure_hash=context.invocation.release_closure_hash,
            data_snapshot_id=context.invocation.data_snapshot_id,
            source_record_ids=(context.node_id, *context.invocation.source_record_ids),
            artifact_hash=artifact_hash,
        )
        await self._ledger.append(event)

    async def _reconcile_resume(self, invocation: TrajectoryInvocation) -> None:
        """Fail closed if a prior ledger stream for this run bound a different
        release closure than the resuming invocation (spec §9)."""

        events = await self._ledger.events_for(invocation.run_id)
        for event in events:
            if event.release_closure_hash != invocation.release_closure_hash:
                raise LedgerConflict(
                    "checkpoint does not match canonical ledger closure"
                )

    @staticmethod
    def _context_hash(context: NodeContext) -> str:
        parts = [f"{node_id}:{artifact}" for node_id, artifact in context.artifacts]
        if context.packet is not None:
            parts.append(f"packet:{context.packet.model_dump_json()}")
        digest = sha256("\x00".join(parts).encode()).hexdigest()
        return f"sha256:{digest}"

    async def execute(
        self, compiled: CompiledTrajectory, invocation: TrajectoryInvocation
    ) -> TrajectoryResult:
        await self._reconcile_resume(invocation)
        graph = compiled.graph
        config = {"configurable": {"thread_id": invocation.run_id}}
        # If a checkpoint with pending work exists for this run, resume it
        # (``ainvoke(None, ...)``) so completed nodes are restored from the
        # recovery projection and their handlers are not re-run. Otherwise start
        # fresh from the bound invocation.
        existing = await graph.aget_state(config)  # type: ignore[attr-defined]
        if existing.next:
            graph_input: dict[str, NodeContext] | None = None
        else:
            graph_input = {"context": NodeContext(node_id=START, invocation=invocation)}
        final_state: _GraphState = await graph.ainvoke(  # type: ignore[attr-defined]
            graph_input, config
        )
        context = final_state["context"]
        if context.packet is None:
            raise ValueError("trajectory terminated without an admitted packet")
        # Record the terminal transition only once (first time we reach it).
        await self._maybe_complete(context)
        return TrajectoryResult(
            packet=context.packet,
            visited_node_ids=compiled.node_order,
            artifact_hash=self._context_hash(context),
        )

    async def _maybe_complete(self, context: NodeContext) -> None:
        events = await self._ledger.events_for(context.invocation.run_id)
        if any(event.kind == "run_completed" for event in events):
            return
        await self._append(context, kind="run_completed", artifact_hash=self._context_hash(context))
