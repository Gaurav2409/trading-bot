"""Canonical append-only agent run ledger (spec §9).

The ledger is the authoritative audit truth for a domain-agent run. LangGraph
checkpoints exist only to resume execution efficiently; the canonical ledger
records externally meaningful transitions. Appends are strictly sequential per
run, so the stream cannot be rewritten. Resume reconciles a checkpoint against
the recorded events: a hash disagreement fails closed as a ``LedgerConflict``
rather than letting the checkpoint overwrite canonical history, and a missing
run or sequence is a catastrophic ``LedgerUnavailable``.
"""

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class LedgerConflict(RuntimeError):
    """Raised when an append breaks append-only sequencing or a checkpoint
    disagrees with the canonical ledger hash."""


class LedgerUnavailable(RuntimeError):
    """Raised when the canonical ledger cannot serve a run it must know about;
    the harness treats this as a catastrophic infrastructure failure."""


class AgentRunEvent(BaseModel, frozen=True):
    run_id: str
    sequence: int = Field(ge=0)
    kind: str
    release_closure_hash: str
    data_snapshot_id: str
    source_record_ids: tuple[str, ...]
    artifact_hash: str | None = None


@runtime_checkable
class AgentRunLedger(Protocol):
    async def append(self, event: AgentRunEvent) -> None: ...

    async def events_for(self, run_id: str) -> tuple[AgentRunEvent, ...]: ...

    async def reconcile(
        self, run_id: str, *, checkpoint_sequence: int, artifact_hash: str | None
    ) -> None: ...


class InMemoryAgentRunLedger:
    """Deterministic, offline in-memory implementation of ``AgentRunLedger``."""

    def __init__(self) -> None:
        self._streams: dict[str, list[AgentRunEvent]] = {}

    async def append(self, event: AgentRunEvent) -> None:
        stream = self._streams.setdefault(event.run_id, [])
        if event.sequence != len(stream):
            raise LedgerConflict(
                f"agent run sequence conflict: expected {len(stream)}, "
                f"got {event.sequence}"
            )
        stream.append(event)

    async def events_for(self, run_id: str) -> tuple[AgentRunEvent, ...]:
        return tuple(self._streams.get(run_id, ()))

    async def reconcile(
        self, run_id: str, *, checkpoint_sequence: int, artifact_hash: str | None
    ) -> None:
        stream = self._streams.get(run_id)
        if stream is None:
            raise LedgerUnavailable(
                f"canonical ledger has no run {run_id!r}"
            )
        if not 0 <= checkpoint_sequence < len(stream):
            raise LedgerUnavailable(
                f"canonical ledger has no sequence {checkpoint_sequence} "
                f"for run {run_id!r}"
            )
        canonical = stream[checkpoint_sequence]
        if canonical.artifact_hash != artifact_hash:
            raise LedgerConflict("checkpoint does not match canonical ledger")
