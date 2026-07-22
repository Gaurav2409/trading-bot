"""``DomainAgentHarness`` compatibility matrix and safety behavior (spec §16).

These tests bind at the unchanged ``ResearchAgentPort`` seam: they call
``harness.investigate(question)`` and assert only on the admitted
:class:`EvidencePacket` (or ``None``). They never inspect harness internals.

Expected values are an independent source of truth: the matrix rows fix the
categorical assessment and eligibility effect the port must expose for each
recorded fixture case, derived from the constitutional applicability and failure
rules (spec §15, §16), not recomputed the way the harness computes them.
"""

from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from trading_os.agents.harness import DomainAgentHarness, deterministic_run_id
from trading_os.agents.langgraph_engine import LangGraphTrajectoryEngine
from trading_os.agents.ledger import InMemoryAgentRunLedger
from trading_os.agents.llm import ExpectedLLMFailure, FixtureLLMRole
from trading_os.agents.capabilities import (
    ToolCapabilityRegistry,
    ToolCapabilityRelease,
)
from trading_os.agents.corporate_events import EventJudgement
from trading_os.agents.profiles import (
    corporate_event_profile_release,
    corporate_event_trajectory_release,
)
from trading_os.agents.registry import ReleaseRegistry
from trading_os.agents.trajectory import TrajectoryCompiler
from trading_os.research.models import EvidenceDomain
from trading_os.research.orchestrator import ResearchQuestion
from trading_os.research.source_coverage import (
    SourceChannelPolicy,
    SourceCoveragePolicyRelease,
)
from trading_os.research.watchers import SourceRecord

CUTOFF = datetime(2026, 7, 23, tzinfo=UTC)
INSTRUMENT = "instrument:1"
SNAPSHOT = "snapshot:1"

_SOURCE_QUERY_CAP = ToolCapabilityRelease(
    release_id="capability:source-record-query:v1",
    operation="source_record_query",
    input_schema_id="schema:source-record-query:v1",
    output_schema_id="schema:source-record:v1",
    read_only=True,
    max_result_bytes=65_536,
)


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


# Judge fixture: a supportive judgement keyed by the deterministic replay key
# the judge node derives (``judge:<issuer>:<event_type>``).
def _supportive_role() -> FixtureLLMRole:
    return FixtureLLMRole(
        {
            "judge:issuer:1:board_meeting": EventJudgement(
                assessment="material_event_supported",
                support_record_ids=("nse:1",),
                contradiction_record_ids=(),
                missing=(),
            )
        }
    )


@pytest.fixture
def harness_factory() -> Callable[[str], DomainAgentHarness]:
    def build(case: str) -> DomainAgentHarness:
        records: tuple[SourceRecord, ...]
        policy: SourceCoveragePolicyRelease
        role: FixtureLLMRole = _supportive_role()

        if case == "nse_only_complete":
            records = (_record("nse:1", "nse"),)
            policy = _policy(("nse",))
        elif case == "bse_only_complete":
            records = (_record("bse:1", "bse"),)
            policy = _policy(("bse",))
            role = FixtureLLMRole(
                {
                    "judge:issuer:1:board_meeting": EventJudgement(
                        assessment="material_event_supported",
                        support_record_ids=("bse:1",),
                        contradiction_record_ids=(),
                        missing=(),
                    )
                }
            )
        elif case == "dual_listed_one_missing":
            records = (_record("nse:1", "nse"),)
            policy = _policy(("nse", "bse"))
        elif case == "sec_not_applicable":
            records = (_record("nse:1", "nse"),)
            policy = _policy(("nse",), sec_applicable=False)
        elif case == "all_mandatory_missing":
            records = ()
            policy = _policy(("nse", "bse"))
        elif case == "official_conflict":
            records = (
                _record("nse:1", "nse", content="Agreement signed."),
                _record("bse:1", "bse", content="Agreement terminated."),
            )
            policy = _policy(("nse", "bse"))
        elif case == "late_record":
            records = (
                _record(
                    "nse:1",
                    "nse",
                    available_at=datetime(2026, 7, 24, tzinfo=UTC),
                ),
            )
            policy = _policy(("nse",))
        elif case == "provider_timeout":
            records = (_record("nse:1", "nse"),)
            policy = _policy(("nse",))
            role = FixtureLLMRole(
                {
                    "judge:issuer:1:board_meeting": ExpectedLLMFailure(
                        kind="timeout", retryable=True
                    )
                }
            )
        elif case == "malformed_output":
            records = (_record("nse:1", "nse"),)
            policy = _policy(("nse",))
            role = FixtureLLMRole({})  # unknown key -> malformed_output
        elif case == "budget_exhausted":
            records = (_record("nse:1", "nse"),)
            policy = _policy(("nse",))
            role = FixtureLLMRole(
                {
                    "judge:issuer:1:board_meeting": ExpectedLLMFailure(
                        kind="budget", retryable=False
                    )
                }
            )
        else:  # pragma: no cover
            raise AssertionError(f"unknown case {case!r}")

        registry = ReleaseRegistry(
            (corporate_event_profile_release(),),
            (corporate_event_trajectory_release(),),
        )
        ledger = InMemoryAgentRunLedger()
        engine = LangGraphTrajectoryEngine(ledger=ledger)
        compiler = TrajectoryCompiler(
            engine=engine, node_registry=_empty_registry()
        )
        snapshot_scope = {SNAPSHOT: tuple(r.record_id for r in records)}
        return DomainAgentHarness(
            releases=registry,
            compiler=compiler,
            engine=engine,
            capabilities=ToolCapabilityRegistry((_SOURCE_QUERY_CAP,)),
            llm=role,
            ledger=ledger,
            coverage_policy=policy,
            source_records=records,
            snapshot_scope=snapshot_scope,
        )

    return build


def _empty_registry() -> object:
    from trading_os.agents.trajectory import NodeRegistry

    return NodeRegistry()


def _question(record_ids: tuple[str, ...]) -> ResearchQuestion:
    return ResearchQuestion(
        question_id="question:1",
        instrument_id=INSTRUMENT,
        domain=EvidenceDomain.CORPORATE_EVENT,
        source_record_ids=record_ids,
        cutoff=CUTOFF,
        data_snapshot_id=SNAPSHOT,
    )


_CASE_RECORDS: dict[str, tuple[str, ...]] = {
    "nse_only_complete": ("nse:1",),
    "bse_only_complete": ("bse:1",),
    "dual_listed_one_missing": ("nse:1",),
    "sec_not_applicable": ("nse:1",),
    "all_mandatory_missing": (),
    "official_conflict": ("nse:1", "bse:1"),
    "late_record": ("nse:1",),
    "provider_timeout": ("nse:1",),
    "malformed_output": ("nse:1",),
    "budget_exhausted": ("nse:1",),
}


def question_for(case: str) -> ResearchQuestion:
    return _question(_CASE_RECORDS[case])


@pytest.mark.parametrize(
    ("case", "expected_assessment", "expected_effect"),
    [
        ("nse_only_complete", "material_event_supported", "supportive"),
        ("bse_only_complete", "material_event_supported", "supportive"),
        (
            "dual_listed_one_missing",
            "material_event_supported_degraded",
            "neutral",
        ),
        ("sec_not_applicable", "material_event_supported", "supportive"),
        ("all_mandatory_missing", "missing_applicable_official_sources", "neutral"),
        ("official_conflict", "contradictory_official_sources", "neutral"),
        ("late_record", "missing_applicable_official_sources", "neutral"),
        ("provider_timeout", "agent_provider_timeout", "neutral"),
        ("malformed_output", "agent_malformed_output", "neutral"),
        ("budget_exhausted", "agent_budget_exhausted", "neutral"),
    ],
)
async def test_corporate_event_compatibility_matrix(
    case: str,
    expected_assessment: str,
    expected_effect: str,
    harness_factory: Callable[[str], DomainAgentHarness],
) -> None:
    packet = await harness_factory(case).investigate(question_for(case))
    assert packet is not None
    assert packet.assessment == expected_assessment
    assert packet.eligibility_effect == expected_effect
    assert set(packet.source_record_ids).issubset(
        set(question_for(case).source_record_ids)
    )


async def test_investigate_returns_none_when_release_closure_unresolved(
    harness_factory: Callable[[str], DomainAgentHarness],
) -> None:
    harness = harness_factory("nse_only_complete")
    question = _question(("nse:1",)).model_copy(
        update={"domain": EvidenceDomain.FUNDAMENTAL}
    )
    # No fundamental profile is registered -> catastrophic release resolution.
    assert await harness.investigate(question) is None


async def test_malicious_target_price_becomes_explicit_missing(
    harness_factory: Callable[[str], DomainAgentHarness],
) -> None:
    # A judge result that smuggles an executable-number token in its assessment
    # must be rejected at the categorical seam and become explicit missing.
    role = FixtureLLMRole(
        {
            "judge:issuer:1:board_meeting": EventJudgement(
                assessment="target_price_2500",
                support_record_ids=("nse:1",),
                contradiction_record_ids=(),
                missing=(),
            )
        }
    )
    harness = harness_factory("nse_only_complete")
    harness._llm = role  # type: ignore[attr-defined]
    packet = await harness.investigate(question_for("nse_only_complete"))
    assert packet is not None
    assert packet.assessment == "categorical_seam_violation"
    assert packet.eligibility_effect == "neutral"
    assert packet.source_record_ids == ()


async def test_out_of_scope_citation_becomes_explicit_missing(
    harness_factory: Callable[[str], DomainAgentHarness],
) -> None:
    role = FixtureLLMRole(
        {
            "judge:issuer:1:board_meeting": EventJudgement(
                assessment="material_event_supported",
                support_record_ids=("nse:1", "sec:999"),
                contradiction_record_ids=(),
                missing=(),
            )
        }
    )
    harness = harness_factory("nse_only_complete")
    harness._llm = role  # type: ignore[attr-defined]
    packet = await harness.investigate(question_for("nse_only_complete"))
    assert packet is not None
    assert packet.assessment == "categorical_seam_violation"


def test_deterministic_run_id_is_stable() -> None:
    question = question_for("nse_only_complete")
    assert deterministic_run_id(question) == deterministic_run_id(question)


async def test_seam_violation_records_safety_ledger_event(
    harness_factory: Callable[[str], DomainAgentHarness],
) -> None:
    role = FixtureLLMRole(
        {
            "judge:issuer:1:board_meeting": EventJudgement(
                assessment="target_price_2500",
                support_record_ids=("nse:1",),
                contradiction_record_ids=(),
                missing=(),
            )
        }
    )
    harness = harness_factory("nse_only_complete")
    harness._llm = role  # type: ignore[attr-defined]
    question = question_for("nse_only_complete")
    await harness.investigate(question)
    events = await harness._ledger.events_for(  # type: ignore[attr-defined]
        deterministic_run_id(question)
    )
    assert any(e.kind == "categorical_seam_violation" for e in events)
