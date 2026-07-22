"""End-to-end corporate-event tracer through the unchanged ``ResearchAgentPort``.

This drives the generic :class:`DomainAgentHarness` with recorded SEC/NSE/BSE
source fixtures sealed by the real adapters, through the same
``ResearchOrchestrator.run`` caller path production uses. It proves the shadow
tracer preserves the port contract, admits categorical evidence, and never
touches a network or credential.
"""

from datetime import UTC, datetime
from pathlib import Path

from trading_os.agents.capabilities import (
    ToolCapabilityRegistry,
    ToolCapabilityRelease,
)
from trading_os.agents.corporate_events import EventJudgement
from trading_os.agents.harness import DomainAgentHarness
from trading_os.agents.langgraph_engine import LangGraphTrajectoryEngine
from trading_os.agents.ledger import InMemoryAgentRunLedger
from trading_os.agents.llm import FixtureLLMRole
from trading_os.agents.profiles import (
    corporate_event_profile_release,
    corporate_event_trajectory_release,
)
from trading_os.agents.registry import ReleaseRegistry
from trading_os.agents.trajectory import NodeRegistry, TrajectoryCompiler
from trading_os.research.corporate_event_sources import (
    RecordedBseAnnouncementAdapter,
    RecordedNseAnnouncementAdapter,
)
from trading_os.research.models import EvidenceDomain, EvidencePacket
from trading_os.research.orchestrator import ResearchOrchestrator, ResearchQuestion
from trading_os.research.source_coverage import (
    SourceChannelPolicy,
    SourceCoveragePolicyRelease,
)
from trading_os.research.watchers import SourceRecord

FIXTURES = Path(__file__).parents[2] / "fixtures" / "research" / "corporate_events"
CUTOFF = datetime(2026, 7, 23, tzinfo=UTC)
RECEIVED = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)
SNAPSHOT = "snapshot:1"

_SOURCE_QUERY_CAP = ToolCapabilityRelease(
    release_id="capability:source-record-query:v1",
    operation="source_record_query",
    input_schema_id="schema:source-record-query:v1",
    output_schema_id="schema:source-record:v1",
    read_only=True,
    max_result_bytes=65_536,
)


def _dual_listed_records() -> tuple[SourceRecord, ...]:
    nse = RecordedNseAnnouncementAdapter().capture(
        FIXTURES / "nse_board_meeting.json", RECEIVED
    )
    bse = RecordedBseAnnouncementAdapter().capture(
        FIXTURES / "bse_board_meeting.json", RECEIVED
    )
    return (nse, bse)


def _policy() -> SourceCoveragePolicyRelease:
    return SourceCoveragePolicyRelease(
        release_id="source-policy:corporate-event:v1",
        effective_from=CUTOFF,
        channels=(
            SourceChannelPolicy(channel="nse", mandatory=True, applicable=True),
            SourceChannelPolicy(channel="bse", mandatory=True, applicable=True),
            SourceChannelPolicy(channel="sec", mandatory=False, applicable=False),
        ),
        content_hash="sha256:policy",
    )


def _build_harness(
    records: tuple[SourceRecord, ...], role: FixtureLLMRole
) -> DomainAgentHarness:
    registry = ReleaseRegistry(
        (corporate_event_profile_release(),),
        (corporate_event_trajectory_release(),),
    )
    ledger = InMemoryAgentRunLedger()
    engine = LangGraphTrajectoryEngine(ledger=ledger)
    compiler = TrajectoryCompiler(engine=engine, node_registry=NodeRegistry())
    return DomainAgentHarness(
        releases=registry,
        compiler=compiler,
        engine=engine,
        capabilities=ToolCapabilityRegistry((_SOURCE_QUERY_CAP,)),
        llm=role,
        ledger=ledger,
        coverage_policy=_policy(),
        source_records=records,
        snapshot_scope={SNAPSHOT: tuple(r.record_id for r in records)},
    )


def _question(records: tuple[SourceRecord, ...]) -> ResearchQuestion:
    return ResearchQuestion(
        question_id="question:1",
        instrument_id="instrument:1",
        domain=EvidenceDomain.CORPORATE_EVENT,
        source_record_ids=tuple(r.record_id for r in records),
        cutoff=CUTOFF,
        data_snapshot_id=SNAPSHOT,
    )


def _judge_role(records: tuple[SourceRecord, ...]) -> FixtureLLMRole:
    return FixtureLLMRole(
        {
            "judge:issuer:1:board_meeting": EventJudgement(
                assessment="material_event_supported",
                support_record_ids=tuple(r.record_id for r in records),
                contradiction_record_ids=(),
                missing=(),
            )
        }
    )


async def test_dual_listed_complete_admits_supportive_categorical_packet() -> None:
    records = _dual_listed_records()
    harness = _build_harness(records, _judge_role(records))
    orchestrator = ResearchOrchestrator(harness)
    packet = await orchestrator.run(_question(records))
    assert isinstance(packet, EvidencePacket)
    assert packet.domain is EvidenceDomain.CORPORATE_EVENT
    assert packet.assessment == "material_event_supported"
    assert packet.eligibility_effect == "supportive"
    assert set(packet.source_record_ids).issubset(
        {r.record_id for r in records}
    )


async def test_orchestrator_path_is_recompute_deterministic() -> None:
    # Two independent harnesses (each with its own fresh ledger) produce the
    # identical packet — fresh-recompute determinism. This is NOT resume: a
    # genuine same-ledger replay is covered by the catastrophe test below.
    records = _dual_listed_records()
    first = await ResearchOrchestrator(
        _build_harness(records, _judge_role(records))
    ).run(_question(records))
    second = await ResearchOrchestrator(
        _build_harness(records, _judge_role(records))
    ).run(_question(records))
    assert first == second


async def test_same_ledger_replay_is_catastrophic_none_with_observability() -> None:
    # A genuine replay through the port against the SAME canonical ledger (same
    # deterministic run_id) is a checkpoint-vs-ledger disagreement: spec §9
    # catastrophic infrastructure failure. It must return None WITH catastrophic
    # observability, not be silently swallowed. The P0 harness does not resume
    # in-port; replay uses a fresh ledger via the replay composition.
    records = _dual_listed_records()
    harness = _build_harness(records, _judge_role(records))
    question = _question(records)
    first = await harness.investigate(question)
    assert isinstance(first, EvidencePacket)
    # Second investigate reuses the same ledger -> run_started at sequence 0
    # conflicts with the existing run.
    second = await harness.investigate(question)
    assert second is None
    assert any(
        reason == "ledger_conflict_on_start" for _run, reason in harness.catastrophes
    )
