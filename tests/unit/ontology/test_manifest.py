from pathlib import Path

from trading_os.ontology.manifest import (
    ModuleClosureError,
    build_module_manifest,
    verify_import_closure,
)


def test_manifest_lists_modules_with_version_iris() -> None:
    manifest = build_module_manifest(Path("ontology"))
    # Every registered module has an ontology IRI and a versionIRI.
    assert manifest.modules, "expected at least the core module"
    for module in manifest.modules:
        assert module.ontology_iri.startswith("https://trading-os.example/ontology/")
        assert module.version_iri.startswith(module.ontology_iri)
        assert module.manifest_hash.startswith("sha256:")


def test_manifest_hash_is_deterministic() -> None:
    a = build_module_manifest(Path("ontology"))
    b = build_module_manifest(Path("ontology"))
    assert a.manifest_hash == b.manifest_hash


def test_import_closure_accepts_terms_within_declared_imports() -> None:
    manifest = build_module_manifest(Path("ontology"))
    # The shipped modules must satisfy their own declared import closures.
    verify_import_closure(manifest)  # must not raise


def test_out_of_closure_reference_fails(tmp_path: Path) -> None:
    # A module that uses a term from a namespace it does not import must fail.
    base = tmp_path / "ontology"
    (base / "modules").mkdir(parents=True)
    (base / "core.ttl").write_text(
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix tw: <https://trading-os.example/ontology/trading-world#> .\n"
        "<https://trading-os.example/ontology/trading-world> a owl:Ontology ;\n"
        "  owl:versionIRI <https://trading-os.example/ontology/trading-world/release/v1> .\n"
        "tw:Security a owl:Class .\n"
    )
    # A rogue module references tw:Security but declares NO owl:imports of core.
    (base / "modules" / "rogue.ttl").write_text(
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix tw: <https://trading-os.example/ontology/trading-world#> .\n"
        "@prefix rg: <https://trading-os.example/ontology/rogue#> .\n"
        "<https://trading-os.example/ontology/rogue> a owl:Ontology ;\n"
        "  owl:versionIRI <https://trading-os.example/ontology/rogue/release/v1> .\n"
        "rg:Thing a owl:Class ; owl:subClassOf tw:Security .\n"  # tw: not imported
    )
    manifest = build_module_manifest(base)
    import pytest

    with pytest.raises(ModuleClosureError):
        verify_import_closure(manifest)
