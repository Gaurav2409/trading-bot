"""Snapshot-scoped, node-scoped, read-only capability containment.

The tracer exposes tools to a model only through project-owned, immutable
capability releases. ``ToolCapabilityRegistry.bind`` returns a
:class:`BoundCapabilities` proxy whose effective authority is the intersection
of the profile allowlist, the node allowlist, the capability release, the frozen
snapshot scope, and the question's cited source-record set (spec §12).

Deny by default: an ungranted operation fails closed with
:class:`CapabilityDenied`, and no bound proxy can return a record outside the
frozen snapshot scope or the cited source set. The registry itself refuses any
release that is not read-only, that duplicates an operation name, or that lacks
a fixture adapter, and any binding whose profile/node grant intersection is
empty or whose snapshot is unknown.
"""

from collections.abc import Mapping

from pydantic import BaseModel, Field

from trading_os.research.watchers import SourceRecord

SOURCE_RECORD_QUERY = "source_record_query"


class CapabilityRegistryError(RuntimeError):
    """Raised when a capability release set or binding is structurally invalid."""


class CapabilityDenied(RuntimeError):
    """Raised when a bound proxy is asked to exercise an ungranted operation."""


class ToolCapabilityRelease(BaseModel, frozen=True):
    release_id: str
    operation: str
    input_schema_id: str
    output_schema_id: str
    read_only: bool
    max_result_bytes: int = Field(gt=0)
    has_fixture_adapter: bool = True


class CapabilityBinding(BaseModel, frozen=True):
    profile_release_id: str
    node_id: str
    profile_capability_ids: tuple[str, ...]
    node_capability_ids: tuple[str, ...]
    source_record_ids: tuple[str, ...]
    data_snapshot_id: str


class BoundCapabilities:
    """Node-scoped read-only proxy over a frozen source snapshot."""

    def __init__(
        self,
        binding: CapabilityBinding,
        granted_operations: frozenset[str],
        records: Mapping[str, SourceRecord],
        snapshot_record_ids: frozenset[str],
    ) -> None:
        self._binding = binding
        self._granted_operations = granted_operations
        self._records = dict(records)
        self._snapshot_record_ids = snapshot_record_ids

    def _require(self, operation: str) -> None:
        if operation not in self._granted_operations:
            raise CapabilityDenied(
                f"operation {operation!r} is not granted to node "
                f"{self._binding.node_id!r}"
            )

    async def query_source_records(
        self, record_ids: tuple[str, ...]
    ) -> tuple[SourceRecord, ...]:
        self._require(SOURCE_RECORD_QUERY)
        cited = set(self._binding.source_record_ids)
        return tuple(
            self._records[record_id]
            for record_id in record_ids
            if record_id in cited
            and record_id in self._snapshot_record_ids
            and record_id in self._records
        )


class ToolCapabilityRegistry:
    """Validates immutable capability releases and binds node-scoped proxies."""

    def __init__(self, releases: tuple[ToolCapabilityRelease, ...]) -> None:
        seen_operations: set[str] = set()
        for release in releases:
            if not release.read_only:
                raise CapabilityRegistryError(
                    f"capability {release.release_id!r} must be read-only"
                )
            if not release.has_fixture_adapter:
                raise CapabilityRegistryError(
                    f"capability {release.release_id!r} requires a fixture adapter"
                )
            if release.operation in seen_operations:
                raise CapabilityRegistryError(
                    f"duplicate operation {release.operation!r}"
                )
            seen_operations.add(release.operation)
        self._releases = {release.release_id: release for release in releases}

    def bind(
        self,
        binding: CapabilityBinding,
        *,
        records: tuple[SourceRecord, ...],
        snapshot_scope: Mapping[str, tuple[str, ...]],
    ) -> BoundCapabilities:
        granted_release_ids = frozenset(binding.profile_capability_ids) & frozenset(
            binding.node_capability_ids
        )
        if not granted_release_ids:
            raise CapabilityRegistryError(
                "profile/node capability intersection is empty"
            )
        granted_operations: set[str] = set()
        for release_id in granted_release_ids:
            release = self._releases.get(release_id)
            if release is None:
                raise CapabilityRegistryError(
                    f"capability release {release_id!r} is not registered"
                )
            granted_operations.add(release.operation)
        if binding.data_snapshot_id not in snapshot_scope:
            raise CapabilityRegistryError(
                f"snapshot {binding.data_snapshot_id!r} is not registered"
            )
        snapshot_record_ids = frozenset(snapshot_scope[binding.data_snapshot_id])
        record_index = {record.record_id: record for record in records}
        return BoundCapabilities(
            binding=binding,
            granted_operations=frozenset(granted_operations),
            records=record_index,
            snapshot_record_ids=snapshot_record_ids,
        )
