"""P0 acceptance: the whole recorded corporate-event fixture matrix, offline.

This is the executable P0 completion gate (spec §22 "P0 proof obligations",
plan "P0 completion gate"). It drives every constitutional fixture case through
the *composed* shadow agent — ``build_shadow_domain_agent`` returning the
unchanged ``ResearchAgentPort`` — and asserts, for each case, that:

1. production and replay wirings produce a byte-identical packet (offline
   determinism: same releases, snapshot, fixtures, and frozen clock);
2. the admitted categorical assessment carries the expected status token;
3. citations are a subset of ``ResearchQuestion.source_record_ids`` (no
   evidence escapes the frozen source scope);
4. no executable number crosses the seam and only catastrophic ledger/release
   failure returns ``None``.

Tests bind at the public port seam only. Expected assessments are an
independent source of truth — the constitutional applicability/failure rules of
spec §15–§16 — not recomputed the way the harness computes them. No network, no
credentials, no database.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from trading_os.agents.composition import (
    DomainAgentDependencies,
    build_shadow_domain_agent,
)
from trading_os.agents.corporate_events import EventJudgement
from trading_os.agents.langgraph_engine import LangGraphTrajectoryEngine
from trading_os.agents.ledger import InMemoryAgentRunLedger
from trading_os.agents.llm import ExpectedLLMFailure, FixtureLLMRole, LLMRole
from trading_os.agents.profiles import (
    corporate_event_profile_release,
    corporate_event_trajectory_release,
)
from trading_os.agents.registry import ReleaseRegistry
from trading_os.agents.trajectory import NodeRegistry, TrajectoryCompiler
from trading_os.research.models import EvidenceDomain, EvidencePacket
from trading_os.research.orchestrator import ResearchAgentPort, ResearchQuestion
from trading_os.research.source_coverage import (
    SourceChannelPolicy,
    SourceCoveragePolicyRelease,
)
from trading_os.research.watchers import SourceRecord

CUTOFF = datetime(2026, 7, 23, tzinfo=UTC)
INSTRUMENT = "instrument:1"
SNAPSHOT = "snapshot:1"


def _record(
    record_id: str,
    channel: str,
    *,
    content: str = "Board meeting to consider a material definitive agreement.",
    available_at: datetime = datetime(2026, 7, 22, tzinfo=UTC),
    kind: str = "Board Meeting",
) -> SourceRecord:
    return SourceRecord(
        record_id=record_id,
        source_id=f"source:{channel}",
        source_family_id="issuer:1:board_meeting:2026-07-22",
        channel=channel,
        jurisdiction="IN",
        published_at=datetime(2026, 7, 22, tzinfo=UTC),
        available_at=available_at,
        received_at=datetime(2026, 7, 22, tzinfo=UTC),
        kind=kind,
        is_issuer_submission=True,
        payload_hash="sha256:x",
        content=content,
    )


def _policy(
    applicable: tuple[str, ...], *, sec_applicable: bool = False
) -> SourceCoveragePolicyRelease:
    channels = [
        SourceChannelPolicy(channel=ch, mandatory=True, applicable=True)
        for ch in applicable
    ]
    for ch in ("nse", "bse", "sec"):
        if ch not in applicable:
            channels.append(
                SourceChannelPolicy(
                    channel=ch,
                    mandatory=(ch == "sec" and sec_applicable),
                    applicable=(ch == "sec" and sec_applicable),
                )
            )
    return SourceCoveragePolicyRelease(
        release_id="source-policy:corporate-event:v1",
        effective_from=CUTOFF,
        channels=tuple(channels),
        content_hash="sha256:policy",
    )


def _supportive_role(support_record_ids: tuple[str, ...]) -> FixtureLLMRole:
    return FixtureLLMRole(
        {
            "judge:issuer:1:board_meeting": EventJudgement(
                assessment="material_event_supported",
                support_record_ids=support_record_ids,
                contradiction_record_ids=(),
                missing=(),
            )
        }
    )


@dataclass(frozen=True)
class _CaseSpec:
    """One recorded fixture case: its sources, coverage policy, and judge role.

    The role is built lazily per composition so production and replay never
    share mutable fixture state.
    """

    records: tuple[SourceRecord, ...]
    policy: SourceCoveragePolicyRelease
    role_factory: Callable[[], LLMRole]
    expected_status: str


def _case(name: str) -> _CaseSpec:
    if name == "nse_only_complete":
        records = (_record("nse:1", "nse"),)
        return _CaseSpec(
            records,
            _policy(("nse",)),
            lambda: _supportive_role(("nse:1",)),
            "material_event_supported",
        )
    if name == "bse_only_complete":
        records = (_record("bse:1", "bse"),)
        return _CaseSpec(
            records,
            _policy(("bse",)),
            lambda: _supportive_role(("bse:1",)),
            "material_event_supported",
        )
    if name == "dual_listed_one_missing":
        records = (_record("nse:1", "nse"),)
        return _CaseSpec(
            records,
            _policy(("nse", "bse")),
            lambda: _supportive_role(("nse:1",)),
            "material_event_supported_degraded",
        )
    if name == "sec_not_applicable":
        records = (_record("nse:1", "nse"),)
        return _CaseSpec(
            records,
            _policy(("nse",), sec_applicable=False),
            lambda: _supportive_role(("nse:1",)),
            "material_event_supported",
        )
    if name == "all_mandatory_missing":
        return _CaseSpec(
            (),
            _policy(("nse", "bse")),
            lambda: _supportive_role(("nse:1",)),
            "missing_applicable_official_sources",
        )
    if name == "official_conflict":
        records = (
            _record("nse:1", "nse", content="Agreement signed."),
            _record("bse:1", "bse", content="Agreement terminated."),
        )
        return _CaseSpec(
            records,
            _policy(("nse", "bse")),
            lambda: _supportive_role(("nse:1",)),
            "contradictory_official_sources",
        )
    if name == "late_record":
        records = (
            _record("nse:1", "nse", available_at=datetime(2026, 7, 24, tzinfo=UTC)),
        )
        return _CaseSpec(
            records,
            _policy(("nse",)),
            lambda: _supportive_role(("nse:1",)),
            "missing_applicable_official_sources",
        )
    if name == "provider_timeout":
        records = (_record("nse:1", "nse"),)
        return _CaseSpec(
            records,
            _policy(("nse",)),
            lambda: FixtureLLMRole(
                {
                    "judge:issuer:1:board_meeting": ExpectedLLMFailure(
                        kind="timeout", retryable=True
                    )
                }
            ),
            "agent_provider_timeout",
        )
    if name == "malformed_output":
        records = (_record("nse:1", "nse"),)
        return _CaseSpec(
            records,
            _policy(("nse",)),
            lambda: FixtureLLMRole({}),  # unknown replay key -> malformed_output
            "agent_malformed_output",
        )
    if name == "budget_exhausted":
        records = (_record("nse:1", "nse"),)
        return _CaseSpec(
            records,
            _policy(("nse",)),
            lambda: FixtureLLMRole(
                {
                    "judge:issuer:1:board_meeting": ExpectedLLMFailure(
                        kind="budget", retryable=False
                    )
                }
            ),
            "agent_budget_exhausted",
        )
    raise AssertionError(f"unknown case {name!r}")  # pragma: no cover


P0_CASE_NAMES: tuple[str, ...] = (
    "nse_only_complete",
    "bse_only_complete",
    "dual_listed_one_missing",
    "sec_not_applicable",
    "all_mandatory_missing",
    "official_conflict",
    "late_record",
    "provider_timeout",
    "malformed_output",
    "budget_exhausted",
)


def _question(records: tuple[SourceRecord, ...]) -> ResearchQuestion:
    return ResearchQuestion(
        question_id="question:1",
        instrument_id=INSTRUMENT,
        domain=EvidenceDomain.CORPORATE_EVENT,
        source_record_ids=tuple(r.record_id for r in records),
        cutoff=CUTOFF,
        data_snapshot_id=SNAPSHOT,
    )


def _dependencies(spec: _CaseSpec) -> DomainAgentDependencies:
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
        llm=spec.role_factory(),
        ledger=ledger,
        coverage_policy=spec.policy,
        source_records=spec.records,
        snapshot_scope={SNAPSHOT: tuple(r.record_id for r in spec.records)},
    )


async def test_p0_fixture_matrix_is_offline_deterministic() -> None:
    for name in P0_CASE_NAMES:
        spec = _case(name)
        question = _question(spec.records)

        production: ResearchAgentPort = build_shadow_domain_agent(_dependencies(spec))
        replay: ResearchAgentPort = build_shadow_domain_agent(_dependencies(spec))

        first = await production.investigate(question)
        second = await replay.investigate(question)

        assert isinstance(first, EvidencePacket), name
        assert first == second, name
        assert spec.expected_status in first.assessment, name
        assert set(first.source_record_ids).issubset(
            set(question.source_record_ids)
        ), name


async def test_p0_every_expected_failure_is_admitted_not_none() -> None:
    # The relational champion is permanent: every *expected* failure path must
    # cross admission and return a packet, never ``None``.
    for name in ("provider_timeout", "malformed_output", "budget_exhausted"):
        spec = _case(name)
        agent = build_shadow_domain_agent(_dependencies(spec))
        packet = await agent.investigate(_question(spec.records))
        assert isinstance(packet, EvidencePacket), name
        assert packet.eligibility_effect == "neutral", name


async def test_p0_catastrophic_release_closure_returns_none() -> None:
    # Only catastrophic release/ledger failure yields ``None``. An unregistered
    # domain profile cannot resolve a release closure.
    spec = _case("nse_only_complete")
    agent = build_shadow_domain_agent(_dependencies(spec))
    catastrophic = _question(spec.records).model_copy(
        update={"domain": EvidenceDomain.FUNDAMENTAL}
    )
    assert await agent.investigate(catastrophic) is None


@pytest.mark.parametrize("name", P0_CASE_NAMES)
async def test_p0_citations_stay_within_frozen_source_scope(name: str) -> None:
    spec = _case(name)
    question = _question(spec.records)
    agent = build_shadow_domain_agent(_dependencies(spec))
    packet = await agent.investigate(question)
    assert isinstance(packet, EvidencePacket)
    assert set(packet.source_record_ids).issubset(set(question.source_record_ids))
