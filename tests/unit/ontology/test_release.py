from pathlib import Path

from trading_os.ontology.releases import OntologyReleaseBuilder


def test_ontology_release_validates_and_is_content_addressed() -> None:
    builder = OntologyReleaseBuilder(
        core_ttl=Path("ontology/core.ttl"),
        shapes_ttl=Path("ontology/shapes/core.shacl.ttl"),
    )
    release = builder.build(version="v1")
    assert release.conforms is True
    assert release.release_hash.startswith("sha256:")
    # Same inputs -> same hash (rebuildable, deterministic).
    assert builder.build(version="v1").release_hash == release.release_hash


def test_term_iris_are_release_independent() -> None:
    builder = OntologyReleaseBuilder(
        core_ttl=Path("ontology/core.ttl"),
        shapes_ttl=Path("ontology/shapes/core.shacl.ttl"),
    )
    v1 = builder.build(version="v1")
    v2 = builder.build(version="v2")
    # Term IRIs stay stable across releases; only the version IRI differs.
    assert v1.version_iri != v2.version_iri
    assert v1.release_hash == v2.release_hash
