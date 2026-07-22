from pathlib import Path

from trading_os.ontology.releases import (
    OntologyReleaseBuilder,
    OntologySchemaError,
)


def test_schema_validation_requires_version_metadata() -> None:
    builder = OntologyReleaseBuilder(
        core_ttl=Path("ontology/core.ttl"),
        shapes_ttl=Path("ontology/shapes/core.shacl.ttl"),
    )
    release = builder.build(version="v1")
    # core.ttl now declares an ontology IRI + owl:versionIRI, so schema validation
    # passes on document conventions (NOT by applying instance shapes to the vocab).
    assert release.schema_valid is True
    assert release.version_iri.endswith("/v1")


def test_missing_version_iri_is_a_schema_error(tmp_path: Path) -> None:
    bad = tmp_path / "no_version.ttl"
    bad.write_text(
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "<https://trading-os.example/ontology/trading-world> a owl:Ontology .\n"
    )
    builder = OntologyReleaseBuilder(
        core_ttl=bad,
        shapes_ttl=Path("ontology/shapes/core.shacl.ttl"),
    )
    import pytest

    with pytest.raises(OntologySchemaError):
        builder.build(version="v1")


def test_release_identity_is_a_manifest_hash_over_meaning() -> None:
    builder = OntologyReleaseBuilder(
        core_ttl=Path("ontology/core.ttl"),
        shapes_ttl=Path("ontology/shapes/core.shacl.ttl"),
    )
    a = builder.build(version="v1")
    b = builder.build(version="v1")
    assert a.manifest_hash == b.manifest_hash
    assert a.manifest_hash.startswith("sha256:")


def test_comment_only_change_does_not_change_manifest_hash(tmp_path: Path) -> None:
    core = Path("ontology/core.ttl").read_text()
    shapes = Path("ontology/shapes/core.shacl.ttl")
    original = tmp_path / "core.ttl"
    original.write_text(core)
    commented = tmp_path / "core_commented.ttl"
    commented.write_text(core + "\n# a trailing comment that changes no meaning\n")

    a = OntologyReleaseBuilder(core_ttl=original, shapes_ttl=shapes).build(version="v1")
    b = OntologyReleaseBuilder(core_ttl=commented, shapes_ttl=shapes).build(version="v1")
    # Manifest hashes the parsed graph canonically, so a comment-only edit is equal.
    assert a.manifest_hash == b.manifest_hash


def test_term_iris_are_release_independent() -> None:
    builder = OntologyReleaseBuilder(
        core_ttl=Path("ontology/core.ttl"),
        shapes_ttl=Path("ontology/shapes/core.shacl.ttl"),
    )
    v1 = builder.build(version="v1")
    v2 = builder.build(version="v2")
    assert v1.version_iri != v2.version_iri
    assert v1.manifest_hash == v2.manifest_hash
