"""Shadow-only domain-agent application composition (spec §12, §16, §18).

``build_shadow_domain_agent`` wires a :class:`DomainAgentHarness` from injected
dependencies *only*. It constructs no provider client, opens no network
connection, and reads no credentials: the LLM role, ledger, engine, capability
registry, coverage policy, and recorded source set are all passed in. Production
and replay therefore share exactly one caller path — the unchanged
``ResearchAgentPort.investigate`` — and differ only in which recorded
dependencies they carry.

This is the seam the application container uses when, and only when, shadow mode
is explicitly enabled. It cannot activate any decision or create executable
intent (P0 remains shadow-only).
"""

from collections.abc import Mapping
from dataclasses import dataclass

from trading_os.agents.capabilities import (
    ToolCapabilityRegistry,
    ToolCapabilityRelease,
)
from trading_os.agents.harness import DomainAgentHarness
from trading_os.agents.ledger import AgentRunLedger
from trading_os.agents.llm import LLMRole
from trading_os.agents.registry import ReleaseRegistry
from trading_os.agents.trajectory import TrajectoryCompiler, TrajectoryEngine
from trading_os.research.orchestrator import ResearchAgentPort
from trading_os.research.source_coverage import SourceCoveragePolicyRelease
from trading_os.research.watchers import SourceRecord

# The single node-scoped, read-only source-record query capability the P0
# corporate-event profile grants. It exposes no hosted tools and cannot be
# widened at composition time.
SOURCE_RECORD_QUERY_CAPABILITY = ToolCapabilityRelease(
    release_id="capability:source-record-query:v1",
    operation="source_record_query",
    input_schema_id="schema:source-record-query:v1",
    output_schema_id="schema:source-record:v1",
    read_only=True,
    max_result_bytes=65_536,
)


@dataclass(frozen=True)
class DomainAgentDependencies:
    """Injected, immutable dependency set for a shadow domain agent.

    Nothing here is provider- or environment-specific: the caller supplies a
    resolved :class:`LLMRole` (a fixture role in offline replay, a provider
    adapter in a future non-P0 rollout) and the recorded source set. The
    composition function does no I/O.
    """

    releases: ReleaseRegistry
    compiler: TrajectoryCompiler
    engine: TrajectoryEngine
    capabilities: ToolCapabilityRegistry
    llm: LLMRole
    ledger: AgentRunLedger
    coverage_policy: SourceCoveragePolicyRelease
    source_records: tuple[SourceRecord, ...]
    snapshot_scope: Mapping[str, tuple[str, ...]]

    @staticmethod
    def default_capability_registry() -> ToolCapabilityRegistry:
        """The P0 read-only capability registry (a single source-record query)."""

        return ToolCapabilityRegistry((SOURCE_RECORD_QUERY_CAPABILITY,))


def build_shadow_domain_agent(deps: DomainAgentDependencies) -> ResearchAgentPort:
    """Compose the shadow-only domain agent from injected dependencies.

    The returned object is a plain ``ResearchAgentPort``; the caller cannot tell
    a production wiring from a replay wiring by its type, which is the point:
    replay and production run the identical port call.
    """

    return DomainAgentHarness(
        releases=deps.releases,
        compiler=deps.compiler,
        engine=deps.engine,
        capabilities=deps.capabilities,
        llm=deps.llm,
        ledger=deps.ledger,
        coverage_policy=deps.coverage_policy,
        source_records=deps.source_records,
        snapshot_scope=deps.snapshot_scope,
    )
