"""Rebuildable graph projection ports.

Fuseki (RDF) and Neo4j projections rebuild from one semantic manifest and emit
content hashes. Application credentials cannot write arbitrary graph data. If a
graph is unavailable or disagrees with the relational baseline, decisioning uses
the relational answer and records degradation.
"""

from hashlib import sha256
from typing import Protocol

from pydantic import BaseModel


class SemanticContentManifest(BaseModel, frozen=True):
    ontology_release_hash: str
    admitted_assertion_ids: tuple[str, ...]
    inference_policy_id: str
    decision_cutoff: str
    build_version: str

    def snapshot_id(self) -> str:
        payload = "\x00".join(
            [
                self.ontology_release_hash,
                *sorted(self.admitted_assertion_ids),
                self.inference_policy_id,
                self.decision_cutoff,
                self.build_version,
            ]
        )
        return f"sha256:{sha256(payload.encode()).hexdigest()}"


class SemanticProjectionReceipt(BaseModel, frozen=True):
    projection: str
    semantic_snapshot_id: str
    projected_hash: str
    degraded: bool = False


class GraphProjectionPort(Protocol):
    def rebuild(self, manifest: SemanticContentManifest) -> SemanticProjectionReceipt:
        raise NotImplementedError


class UnavailableProjection:
    """Represents a graph store that is not reachable; rebuild reports degradation
    rather than raising, so the relational baseline keeps serving decisions."""

    def __init__(self, projection: str) -> None:
        self._projection = projection

    def rebuild(self, manifest: SemanticContentManifest) -> SemanticProjectionReceipt:
        return SemanticProjectionReceipt(
            projection=self._projection,
            semantic_snapshot_id=manifest.snapshot_id(),
            projected_hash="",
            degraded=True,
        )
