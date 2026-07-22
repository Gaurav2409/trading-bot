import pytest

from trading_os.agents.ledger import (
    AgentRunEvent,
    InMemoryAgentRunLedger,
    LedgerConflict,
    LedgerUnavailable,
)


def event(
    run_id: str,
    *,
    sequence: int,
    kind: str,
    artifact_hash: str | None = None,
) -> AgentRunEvent:
    return AgentRunEvent(
        run_id=run_id,
        sequence=sequence,
        kind=kind,
        release_closure_hash="sha256:closure",
        data_snapshot_id="snapshot:1",
        source_record_ids=("sec:1",),
        artifact_hash=artifact_hash,
    )


@pytest.mark.asyncio
async def test_ledger_is_append_only_and_sequence_checked() -> None:
    ledger = InMemoryAgentRunLedger()
    await ledger.append(event("run:1", sequence=0, kind="run_started"))
    await ledger.append(event("run:1", sequence=1, kind="node_started"))
    with pytest.raises(LedgerConflict):
        await ledger.append(event("run:1", sequence=1, kind="node_finished"))


@pytest.mark.asyncio
async def test_events_replay_in_append_order() -> None:
    ledger = InMemoryAgentRunLedger()
    await ledger.append(event("run:1", sequence=0, kind="run_started"))
    await ledger.append(event("run:1", sequence=1, kind="node_started"))
    await ledger.append(event("run:1", sequence=2, kind="node_finished"))

    events = await ledger.events_for("run:1")

    assert tuple(item.sequence for item in events) == (0, 1, 2)
    assert tuple(item.kind for item in events) == (
        "run_started",
        "node_started",
        "node_finished",
    )


@pytest.mark.asyncio
async def test_events_are_scoped_per_run() -> None:
    ledger = InMemoryAgentRunLedger()
    await ledger.append(event("run:1", sequence=0, kind="run_started"))
    await ledger.append(event("run:2", sequence=0, kind="run_started"))

    assert len(await ledger.events_for("run:1")) == 1
    assert len(await ledger.events_for("run:2")) == 1
    assert await ledger.events_for("run:absent") == ()


@pytest.mark.asyncio
async def test_first_event_must_start_at_zero() -> None:
    ledger = InMemoryAgentRunLedger()
    with pytest.raises(LedgerConflict):
        await ledger.append(event("run:1", sequence=1, kind="run_started"))


@pytest.mark.asyncio
async def test_checkpoint_must_reconcile_with_ledger_hash() -> None:
    ledger = InMemoryAgentRunLedger()
    await ledger.append(
        event("run:1", sequence=0, kind="run_started", artifact_hash="sha256:a")
    )
    with pytest.raises(
        LedgerConflict, match="checkpoint does not match canonical ledger"
    ):
        await ledger.reconcile(
            "run:1", checkpoint_sequence=0, artifact_hash="sha256:b"
        )


@pytest.mark.asyncio
async def test_matching_checkpoint_reconciles() -> None:
    ledger = InMemoryAgentRunLedger()
    await ledger.append(
        event("run:1", sequence=0, kind="run_started", artifact_hash="sha256:a")
    )
    await ledger.reconcile("run:1", checkpoint_sequence=0, artifact_hash="sha256:a")


@pytest.mark.asyncio
async def test_reconcile_unknown_run_is_unavailable() -> None:
    ledger = InMemoryAgentRunLedger()
    with pytest.raises(LedgerUnavailable):
        await ledger.reconcile(
            "run:absent", checkpoint_sequence=0, artifact_hash="sha256:a"
        )


@pytest.mark.asyncio
async def test_reconcile_missing_sequence_is_unavailable() -> None:
    ledger = InMemoryAgentRunLedger()
    await ledger.append(
        event("run:1", sequence=0, kind="run_started", artifact_hash="sha256:a")
    )
    with pytest.raises(LedgerUnavailable):
        await ledger.reconcile(
            "run:1", checkpoint_sequence=5, artifact_hash="sha256:a"
        )
