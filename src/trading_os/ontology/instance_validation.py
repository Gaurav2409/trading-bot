from datetime import datetime

from pydantic import BaseModel


class InstanceValidationReport(BaseModel, frozen=True):
    conforms: bool
    text: str


def validate_instance_snapshot(instance_ttl: str, shapes_ttl: str) -> InstanceValidationReport:
    """Apply SHACL to actual canonical semantic facts (ADR-0004).

    This is the instance-snapshot stage, distinct from ontology-schema
    validation. RDFS inference is enabled so declared domains/ranges apply, but
    the focus nodes are real instances, not the vocabulary.
    """
    from pyshacl import validate
    from rdflib import Graph

    data = Graph().parse(data=instance_ttl, format="turtle")
    shapes = Graph().parse(data=shapes_ttl, format="turtle")
    conforms, _, text = validate(
        data_graph=data,
        shacl_graph=shapes,
        inference="rdfs",
        advanced=True,
    )
    return InstanceValidationReport(conforms=bool(conforms), text=str(text))


def detects_future_data_leak(*, received_at: datetime, cutoff: datetime) -> bool:
    """A fact received after the decision cutoff is a temporal leak."""
    return received_at > cutoff


def detects_false_identity_merge(
    *, left: str, right: str, governed_assertion: str | None
) -> bool:
    """Two distinct instrument identities asserted equal without a governed
    identity assertion is a false merge."""
    if left == right:
        return False
    return governed_assertion is None


def detects_stale_snapshot(*, built_at: datetime, now: datetime, max_age_seconds: int) -> bool:
    """A semantic snapshot older than its freshness policy is stale."""
    return (now - built_at).total_seconds() > max_age_seconds
