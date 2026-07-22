from hashlib import sha256
from pathlib import Path

from pydantic import BaseModel
from rdflib import OWL, RDF, Graph, URIRef
from rdflib.compare import to_canonical_graph

# Namespaces that are always in scope without an explicit import.
_BUILTIN_PREFIXES: tuple[str, ...] = (
    "http://www.w3.org/2002/07/owl#",
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "http://www.w3.org/2000/01/rdf-schema#",
    "http://www.w3.org/2001/XMLSchema#",
    "http://www.w3.org/ns/shacl#",
    "http://www.w3.org/ns/prov#",
    "http://www.w3.org/2006/time#",
)


class ModuleClosureError(ValueError):
    """Raised when a module references a term outside its declared import closure."""


class OntologyModule(BaseModel, frozen=True):
    path: str
    ontology_iri: str
    version_iri: str
    imports: tuple[str, ...]
    namespace: str
    manifest_hash: str


class ModuleManifest(BaseModel, frozen=True):
    modules: tuple[OntologyModule, ...]
    manifest_hash: str


def _canonical_hash(graph: Graph) -> str:
    triples = sorted(to_canonical_graph(graph).serialize(format="nt").splitlines())
    digest = sha256("\n".join(t for t in triples if t.strip()).encode()).hexdigest()
    return f"sha256:{digest}"


def _module_namespace(ontology_iri: str) -> str:
    # Convention: term namespace is the ontology IRI with a '#' terminator.
    return ontology_iri if ontology_iri.endswith(("#", "/")) else ontology_iri + "#"


def _read_module(path: Path) -> OntologyModule:
    graph = Graph().parse(data=path.read_text(), format="turtle")
    ontologies = list(graph.subjects(RDF.type, OWL.Ontology))
    if not ontologies:
        raise ModuleClosureError(f"{path.name}: no owl:Ontology declaration")
    ontology = ontologies[0]
    version = graph.value(subject=ontology, predicate=OWL.versionIRI)
    if version is None:
        raise ModuleClosureError(f"{path.name}: missing owl:versionIRI")
    imports = tuple(sorted(str(o) for o in graph.objects(ontology, OWL.imports)))
    return OntologyModule(
        path=str(path),
        ontology_iri=str(ontology),
        version_iri=str(version),
        imports=imports,
        namespace=_module_namespace(str(ontology)),
        manifest_hash=_canonical_hash(graph),
    )


def build_module_manifest(ontology_root: Path) -> ModuleManifest:
    paths = sorted(ontology_root.rglob("*.ttl"))
    # Exclude SHACL shape files from the module DAG; they are validated separately.
    modules = tuple(
        _read_module(p) for p in paths if not p.name.endswith(".shacl.ttl")
    )
    combined = "\x00".join(m.manifest_hash for m in modules)
    digest = sha256(combined.encode()).hexdigest()
    return ModuleManifest(modules=modules, manifest_hash=f"sha256:{digest}")


def verify_import_closure(manifest: ModuleManifest) -> None:
    """Fail if any module uses a term whose namespace is neither built-in, its
    own, nor reachable through its declared owl:imports DAG."""
    iri_to_ns = {m.ontology_iri: m.namespace for m in manifest.modules}

    for module in manifest.modules:
        # Compute the set of namespaces reachable from this module's imports.
        allowed = {module.namespace, *_BUILTIN_PREFIXES}
        for imported_iri in module.imports:
            ns = iri_to_ns.get(imported_iri)
            if ns is not None:
                allowed.add(ns)

        graph = Graph().parse(data=Path(module.path).read_text(), format="turtle")
        for subject, predicate, obj in graph:
            for term in (subject, predicate, obj):
                if not isinstance(term, URIRef):
                    continue
                iri = str(term)
                if "#" in iri:
                    ns = iri.rsplit("#", 1)[0] + "#"
                else:
                    continue
                # The module's own ontology IRI and versionIRI are self-references.
                if iri in {module.ontology_iri, module.version_iri}:
                    continue
                if ns not in allowed:
                    raise ModuleClosureError(
                        f"{Path(module.path).name} references {iri} "
                        f"outside its import closure {sorted(allowed)}"
                    )
