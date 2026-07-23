"""Replay identity and production/replay caller parity (spec §12, §16, §18).

The shadow-only corporate-event tracer must be composable *only* from injected
dependencies and must present the unchanged ``ResearchAgentPort`` to both
production and replay callers. Because P0 is offline and deterministic, the two
compositions differ only in which recorded fixtures they carry; the packet they
admit and the canonical ledger event stream they produce must be byte-identical.

These tests bind at the public port seam (``investigate``) and at the canonical
ledger, never at harness internals. Expected values come from the recorded
fixtures and the constitutional applicability rules, not from re-running the
harness's own computation.
"""

from datetime import UTC, datetime
from pathlib import Path

from trading_os.agents.composition import (
    DomainAgentDependencies,
    build_shadow_domain_agent,
)
from trading_os.agents.corporate_events import EventJudgement
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
from trading_os.research.orchestrator import ResearchAgentPort, ResearchQuestion
from trading_os.research.source_coverage import (
    SourceChannelPolicy,
    SourceCoveragePolicyRelease,
)
from trading_os.research.watchers import SourceRecord

FIXTURES = Path(__file__).parents[2] / "fixtures" / "research" / "corporate_events"
CUTOFF = datetime(2026, 7, 23, tzinfo=UTC)
RECEIVED = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)
SNAPSHOT = "snapshot:1"

QUESTION = ResearchQuestion(
    question_id="question:1",
    instrument_id="instrument:1",
    domain=EvidenceDomain.CORPORATE_EVENT,
    source_record_ids=("nse:board-meeting:2026-07-22", "bse:board-meeting:2026-07-22"),
    cutoff=CUTOFF,
    data_snapshot_id=SNAPSHOT,
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


def _question(records: tuple[SourceRecord, ...]) -> ResearchQuestion:
    return QUESTION.model_copy(
        update={"source_record_ids": tuple(r.record_id for r in records)}
    )


def _dependencies() -> DomainAgentDependencies:
    """Build a fresh, fully independent dependency set.

    Every call constructs its own registry, ledger, engine, compiler, and LLM
    role from the same recorded fixtures, so two builds are structurally
    identical but share no mutable state. This is exactly the production/replay
    distinction under P0: the caller path is one and the same; only the
    dependency instances differ.
    """

    records = _dual_listed_records()
    ledger = InMemoryAgentRunLedger()
    engine = LangGraphTrajectoryEngine(ledger=ledger)
    return DomainAgentDependencies(
        releases=ReleaseRegistry(
            (corporate_event_profile_release(),),
            (corporate_event_trajectory_release(),),
        ),
        compiler=TrajectoryCompiler(engine=engine, node_registry=NodeRegistry()),
        engine=engine,
        capabilities=DomainAgentDependencies.default_capability_registry(),
        llm=_judge_role(records),
        ledger=ledger,
        coverage_policy=_policy(),
        source_records=records,
        snapshot_scope={SNAPSHOT: tuple(r.record_id for r in records)},
    )


def production_dependencies() -> DomainAgentDependencies:
    return _dependencies()


def replay_dependencies() -> DomainAgentDependencies:
    return _dependencies()


async def test_production_and_replay_use_the_same_port_call() -> None:
    production: ResearchAgentPort = build_shadow_domain_agent(production_dependencies())
    replay: ResearchAgentPort = build_shadow_domain_agent(replay_dependencies())
    records = _dual_listed_records()
    production_packet = await production.investigate(_question(records))
    replay_packet = await replay.investigate(_question(records))
    assert isinstance(production_packet, EvidencePacket)
    assert production_packet == replay_packet
    assert production_packet.assessment == "material_event_supported"
    assert production_packet.eligibility_effect == "supportive"


async def test_replay_reproduces_identical_ledger_event_hashes() -> None:
    records = _dual_listed_records()
    question = _question(records)

    first_deps = production_dependencies()
    first_agent = build_shadow_domain_agent(first_deps)
    first_packet = await first_agent.investigate(question)

    second_deps = replay_dependencies()
    second_agent = build_shadow_domain_agent(second_deps)
    second_packet = await second_agent.investigate(question)

    assert first_packet == second_packet

    from trading_os.agents.harness import deterministic_run_id

    run_id = deterministic_run_id(question)
    first_events = await first_deps.ledger.events_for(run_id)
    second_events = await second_deps.ledger.events_for(run_id)
    assert first_events == second_events
    assert first_events  # a run actually happened


def test_build_shadow_domain_agent_returns_research_agent_port() -> None:
    agent: ResearchAgentPort = build_shadow_domain_agent(production_dependencies())
    assert hasattr(agent, "investigate")
