from hashlib import sha256
from pathlib import Path

from pydantic import BaseModel
from rdflib import OWL, RDF, Graph
from rdflib.namespace import Namespace

_TERM_BASE_IRI = "https://trading-os.example/ontology/trading-world#"
_ONTOLOGY_IRI = "https://trading-os.example/ontology/trading-world"
_VERSION_BASE_IRI = "https://trading-os.example/ontology/trading-world/release/"

TW = Namespace(_TERM_BASE_IRI)


class OntologySchemaError(ValueError):
    """Raised when the ontology document violates build-time conventions."""


class OntologyRelease(BaseModel, frozen=True):
    version: str
    version_iri: str
    manifest_hash: str
    schema_valid: bool
    term_base_iri: str = _TERM_BASE_IRI


class OntologyReleaseBuilder:
    """Builds an immutable ontology release.

    ADR-0004: this validates the ontology DOCUMENT (parse + version metadata +
    lint) only. It never applies instance-targeted SHACL to the vocabulary;
    instance facts are validated separately by ``validate_instance_snapshot``.
    Release identity is a manifest hash over the parsed (canonical) graphs of the
    meaning-bearing artifacts, so comment/whitespace churn does not change it.
    """

    def __init__(self, core_ttl: Path, shapes_ttl: Path) -> None:
        self._core_ttl = core_ttl
        self._shapes_ttl = shapes_ttl

    def build(self, version: str) -> OntologyRelease:
        core_graph = Graph().parse(data=self._core_ttl.read_text(), format="turtle")
        shapes_graph = Graph().parse(data=self._shapes_ttl.read_text(), format="turtle")

        self._validate_schema(core_graph)

        manifest_hash = _manifest_hash([core_graph, shapes_graph])
        return OntologyRelease(
            version=version,
            version_iri=f"{_VERSION_BASE_IRI}{version}",
            manifest_hash=manifest_hash,
            schema_valid=True,
        )

    @staticmethod
    def _validate_schema(core_graph: Graph) -> None:
        # Require an ontology IRI and an owl:versionIRI (document conventions).
        ontologies = list(core_graph.subjects(RDF.type, OWL.Ontology))
        if not ontologies:
            raise OntologySchemaError("no owl:Ontology declaration found")
        has_version = any(
            core_graph.value(subject=o, predicate=OWL.versionIRI) is not None
            for o in ontologies
        )
        if not has_version:
            raise OntologySchemaError("ontology is missing an owl:versionIRI")


def _manifest_hash(graphs: list[Graph]) -> str:
    """Hash the canonical form of each meaning-bearing graph, so semantically
    equal documents share a hash regardless of formatting or blank-node labels.

    Uses rdflib's canonicalization (blank-node-stable) rather than raw N-Triples,
    which would otherwise vary by blank-node id across parses.
    """
    from rdflib.compare import to_canonical_graph

    parts: list[str] = []
    for graph in graphs:
        canonical = to_canonical_graph(graph)
        triples = sorted(canonical.serialize(format="nt").splitlines())
        parts.append("\n".join(t for t in triples if t.strip()))
    digest = sha256("\x00".join(parts).encode()).hexdigest()
    return f"sha256:{digest}"
