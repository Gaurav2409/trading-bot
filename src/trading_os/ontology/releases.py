from hashlib import sha256
from pathlib import Path

from pydantic import BaseModel

_TERM_BASE_IRI = "https://trading-os.example/ontology/trading-world#"
_VERSION_BASE_IRI = "https://trading-os.example/ontology/trading-world/release/"


class OntologyRelease(BaseModel, frozen=True):
    version: str
    version_iri: str
    release_hash: str
    conforms: bool
    term_base_iri: str = _TERM_BASE_IRI


class OntologyReleaseBuilder:
    def __init__(self, core_ttl: Path, shapes_ttl: Path) -> None:
        self._core_ttl = core_ttl
        self._shapes_ttl = shapes_ttl

    def build(self, version: str) -> OntologyRelease:
        core_text = self._core_ttl.read_text()
        shapes_text = self._shapes_ttl.read_text()

        conforms = self._validate(core_text, shapes_text)

        # Release hash is content-addressed over the Git-owned Turtle/SHACL only,
        # so term IRIs stay release-independent; the version only names the IRI.
        digest = sha256((core_text + "\x00" + shapes_text).encode()).hexdigest()
        return OntologyRelease(
            version=version,
            version_iri=f"{_VERSION_BASE_IRI}{version}",
            release_hash=f"sha256:{digest}",
            conforms=conforms,
        )

    @staticmethod
    def _validate(core_text: str, shapes_text: str) -> bool:
        from pyshacl import validate
        from rdflib import Graph

        data = Graph().parse(data=core_text, format="turtle")
        shapes = Graph().parse(data=shapes_text, format="turtle")
        conforms, _, _ = validate(
            data_graph=data,
            shacl_graph=shapes,
            inference="rdfs",
            advanced=True,
        )
        return bool(conforms)
