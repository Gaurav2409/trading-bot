"""Snapshot-scoped, node-scoped, read-only capability binding tests.

These tests pin the deny-by-default containment model (spec §12): the effective
authority for a bound capability is the intersection of the profile allowlist,
the node allowlist, the immutable capability release, the frozen snapshot scope,
and the question's cited source-record set. A model calling a bound proxy sees
only records inside every layer of that intersection; anything outside fails
closed. The registry itself rejects any capability release that is not
read-only, that duplicates an operation name, or that lacks a fixture adapter,
and rejects any binding whose profile/node intersection is empty.
"""

from datetime import UTC, datetime

import pytest

from trading_os.agents.capabilities import (
    SOURCE_RECORD_QUERY,
    BoundCapabilities,
    CapabilityBinding,
    CapabilityDenied,
    CapabilityRegistryError,
    ToolCapabilityRegistry,
    ToolCapabilityRelease,
)
from trading_os.research.watchers import SourceRecord

SOURCE_QUERY_ID = "capability:source-record-query:v1"
OTHER_ID = "capability:coverage-lookup:v1"
OTHER_OPERATION = "coverage_lookup"


def _record(record_id: str) -> SourceRecord:
    return SourceRecord(
        record_id=record_id,
        source_id="source:1",
        source_family_id="issuer:1:material_agreement:2026-07-22",
        channel="sec",
        jurisdiction="US",
        published_at=datetime(2026, 7, 22, 14, 30, tzinfo=UTC),
        available_at=datetime(2026, 7, 22, 14, 30, tzinfo=UTC),
        received_at=datetime(2026, 7, 22, 15, tzinfo=UTC),
        kind="8-K",
        is_issuer_submission=True,
        payload_hash="sha256:abc",
        content="Registrant entered into a material definitive agreement.",
    )


def _source_query_release() -> ToolCapabilityRelease:
    return ToolCapabilityRelease(
        release_id=SOURCE_QUERY_ID,
        operation=SOURCE_RECORD_QUERY,
        input_schema_id="schema:source-record-query:v1",
        output_schema_id="schema:source-record:v1",
        read_only=True,
        max_result_bytes=65_536,
        has_fixture_adapter=True,
    )


def _other_release() -> ToolCapabilityRelease:
    return ToolCapabilityRelease(
        release_id=OTHER_ID,
        operation=OTHER_OPERATION,
        input_schema_id="schema:coverage-lookup:v1",
        output_schema_id="schema:coverage-receipt:v1",
        read_only=True,
        max_result_bytes=4_096,
        has_fixture_adapter=True,
    )


def _records() -> tuple[SourceRecord, ...]:
    return (_record("sec:1"), _record("sec:2"), _record("sec:3"))


def _registry() -> ToolCapabilityRegistry:
    return ToolCapabilityRegistry((_source_query_release(),))


@pytest.mark.asyncio
async def test_binding_exposes_only_profile_node_and_snapshot_intersection() -> None:
    records = _records()
    registry = _registry()
    snapshot = {"snapshot:1": ("sec:1", "sec:2")}
    bound = registry.bind(
        CapabilityBinding(
            profile_release_id="profile:corporate-event:v1",
            node_id="gather",
            profile_capability_ids=(SOURCE_QUERY_ID,),
            node_capability_ids=(SOURCE_QUERY_ID,),
            source_record_ids=("sec:1",),
            data_snapshot_id="snapshot:1",
        ),
        records=records,
        snapshot_scope=snapshot,
    )
    # Requested sec:1 (in citation set + snapshot) and sec:2 (in snapshot but not
    # cited); only sec:1 survives the full intersection.
    result = await bound.query_source_records(("sec:1", "sec:2"))
    assert tuple(item.record_id for item in result) == ("sec:1",)


@pytest.mark.asyncio
async def test_binding_never_returns_records_outside_snapshot_scope() -> None:
    records = _records()
    registry = _registry()
    snapshot = {"snapshot:1": ("sec:1",)}
    bound = registry.bind(
        CapabilityBinding(
            profile_release_id="profile:corporate-event:v1",
            node_id="gather",
            profile_capability_ids=(SOURCE_QUERY_ID,),
            node_capability_ids=(SOURCE_QUERY_ID,),
            source_record_ids=("sec:1", "sec:3"),
            data_snapshot_id="snapshot:1",
        ),
        records=records,
        snapshot_scope=snapshot,
    )
    # sec:3 is cited by the question but not in the frozen snapshot scope.
    result = await bound.query_source_records(("sec:1", "sec:3"))
    assert tuple(item.record_id for item in result) == ("sec:1",)


@pytest.mark.asyncio
async def test_ungranted_capability_fails_closed() -> None:
    records = _records()
    registry = ToolCapabilityRegistry((_source_query_release(), _other_release()))
    snapshot = {"snapshot:1": ("sec:1",)}
    # The node is granted a different read-only capability, so the profile/node
    # intersection is non-empty, but source_record_query is never granted.
    no_grants = registry.bind(
        CapabilityBinding(
            profile_release_id="profile:corporate-event:v1",
            node_id="gather",
            profile_capability_ids=(OTHER_ID,),
            node_capability_ids=(OTHER_ID,),
            source_record_ids=("sec:1",),
            data_snapshot_id="snapshot:1",
        ),
        records=records,
        snapshot_scope=snapshot,
    )
    with pytest.raises(CapabilityDenied):
        await no_grants.query_source_records(("sec:1",))


def test_binding_requires_a_registered_snapshot() -> None:
    records = _records()
    registry = _registry()
    with pytest.raises(CapabilityRegistryError, match="snapshot"):
        registry.bind(
            CapabilityBinding(
                profile_release_id="profile:corporate-event:v1",
                node_id="gather",
                profile_capability_ids=(SOURCE_QUERY_ID,),
                node_capability_ids=(SOURCE_QUERY_ID,),
                source_record_ids=("sec:1",),
                data_snapshot_id="snapshot:missing",
            ),
            records=records,
            snapshot_scope={"snapshot:1": ("sec:1",)},
        )


def test_registry_rejects_writable_capability() -> None:
    writable = _source_query_release().model_copy(update={"read_only": False})
    with pytest.raises(CapabilityRegistryError, match="read-only"):
        ToolCapabilityRegistry((writable,))


def test_registry_rejects_duplicate_operation() -> None:
    duplicate = _source_query_release().model_copy(
        update={"release_id": "capability:source-record-query:v2"}
    )
    with pytest.raises(CapabilityRegistryError, match="duplicate operation"):
        ToolCapabilityRegistry((_source_query_release(), duplicate))


def test_registry_rejects_capability_without_fixture_adapter() -> None:
    no_adapter = _source_query_release().model_copy(
        update={"has_fixture_adapter": False}
    )
    with pytest.raises(CapabilityRegistryError, match="fixture adapter"):
        ToolCapabilityRegistry((no_adapter,))


def test_registry_rejects_binding_with_empty_intersection() -> None:
    records = _records()
    registry = _registry()
    with pytest.raises(CapabilityRegistryError, match="intersection"):
        registry.bind(
            CapabilityBinding(
                profile_release_id="profile:corporate-event:v1",
                node_id="gather",
                profile_capability_ids=(),
                node_capability_ids=(),
                source_record_ids=("sec:1",),
                data_snapshot_id="snapshot:1",
            ),
            records=records,
            snapshot_scope={"snapshot:1": ("sec:1",)},
        )


def test_bound_capabilities_type_is_exposed() -> None:
    records = _records()
    registry = _registry()
    bound = registry.bind(
        CapabilityBinding(
            profile_release_id="profile:corporate-event:v1",
            node_id="gather",
            profile_capability_ids=(SOURCE_QUERY_ID,),
            node_capability_ids=(SOURCE_QUERY_ID,),
            source_record_ids=("sec:1",),
            data_snapshot_id="snapshot:1",
        ),
        records=records,
        snapshot_scope={"snapshot:1": ("sec:1",)},
    )
    assert isinstance(bound, BoundCapabilities)
