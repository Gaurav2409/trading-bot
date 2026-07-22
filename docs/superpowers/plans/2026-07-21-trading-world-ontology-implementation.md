# Trading World Ontology Implementation Plan

> **Do not execute this plan as the Day-9 critical path.** The live-V1 scope and sequencing were
> amended on 2026-07-22 by
> `docs/superpowers/specs/2026-07-22-live-v1-architecture-amendment.md`. The successor nine-day plan
> selects only the ontology kernel needed for the first vertical slice; this file remains the
> detailed post-V1 expansion plan.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Validated amendment:** This plan implements the approved post-review design at
> `docs/superpowers/specs/2026-07-21-trading-world-ontology-design.md`. The controlling review is
> `docs/research/12a-trading-world-ontology-moa-validation.md`; rejected raw-review claims listed in
> design §20 must not be reintroduced.

**Goal:** Build the versioned, full-hybrid semantic reasoning layer that converts snapshot-scoped technical, fundamental, sentiment, macro, relationship, and portfolio evidence into auditable `InstrumentBeliefState` objects while permanently benchmarking against relational retrieval.

**Architecture:** Git-owned OWL/SHACL releases and append-only factual history are canonical. A final `SemanticSnapshotId` is derived before Apache Jena Fuseki/TDB2 and Neo4j are built; a separate immutable projection receipt seals their equivalence. Governed query, reasoning-policy, and feature-policy releases feed deterministic evidence and belief builders, while a separate activation state machine prevents semantic promotion from granting economic authority.

**Tech Stack:** Python 3.11+, `uv`, Pydantic v2, SQLAlchemy 2 + asyncpg/Postgres/TimescaleDB, RDFLib, pySHACL, OWL-RL, Apache Jena Fuseki 6.1.0/TDB2, Neo4j Community 2026.06.0, httpx, structlog, pytest/Hypothesis/mypy/ruff.

## Global Constraints

- Execute Trading OS plan Tasks 1–14 first. This plan augments its Tasks 12–13, replaces Tasks 15–17, and preserves the independent rule-null from Task 14. After this plan passes, resume the Trading OS plan at Task 18 with the integration rules in Task 15 below.
- Term IRIs are stable and release-independent; `owl:versionIRI` identifies immutable releases. Never reuse a released IRI with a new meaning.
- Git ontology source and append-only factual history are canonical. Fuseki and Neo4j reject application-level direct writes and are rebuildable from one manifest.
- Use SHACL Core plus approved SPARQL constraints and bounded RDFS/OWL 2 RL-style entailments. Jena's full OWL reasoner is prohibited.
- Every decision-consumable query binds `ValidatedDataSnapshotId`, final `SemanticSnapshotId`, sealed `SemanticProjectionReceiptId`, `OntologyReleaseId`, `QueryPackReleaseId`, and `decision_cutoff`.
- `LegalEntity`, `IssuerRole`, `Security`, `Listing`, `Venue`, and `TickerAlias` use typed IDs. Aliases are temporal and venue-scoped; fuzzy matches create candidates and never merge automatically.
- Corrections append new facts and supersession links. No source, observation, claim, identity, or admission row is updated in place.
- LLMs may propose Claims, identity candidates, closed classifications, and approved query-template selections. They cannot admit facts, merge identity, emit numeric causal strength, write graph stores, promote releases, or emit trade parameters.
- External documents are untrusted data. Raw bytes never become system instructions, query text, ontology source, graph properties, or experiment-trace prose.
- Projection builders allowlist endpoint types/properties and omit secrets, personal data, raw content, and span text/hash; traces retain governed artifact IDs and hashes only.
- Source reads enforce the recorded licence's principal, transformation, retention, and redistribution policy before bytes are returned.
- The relational retrieval path is a permanent champion and fallback. It cannot import RDF, Neo4j, LLM, or ontology-reasoner modules.
- `InstrumentBeliefState` contains evidence status, provenance, contradictions, freshness, and missingness—not target price, quantity, risk budget, or order instructions.
- `DecisionFeatureProjector` allowlists deterministic fields. Raw narrative, raw LLM JSON, arbitrary graph handles, and unrestricted queries are structurally unreachable from the trading hot path.
- Unknown or unapproved feature keys are excluded by each strategy's positive allowlist; the plan never requires every producer key to be allowlisted somewhere.
- `RiskOverlaySet` replaces the skipped legacy `ExposureVector` and may only tighten or veto risk.
- The improvement loop is offline. High-impact semantic changes always require human approval; an author cannot approve its own proposal. Role identities must be independent where required, but distinct model IDs are not mandatory.
- Semantic promotion never activates decision features. Economic influence requires an immutable `DecisionFeatureActivation` and cannot skip `SHADOW → PAPER_CANARY → PAPER_ACTIVE` or the later `LIVE_CANARY → LIVE_ACTIVE` transition.
- Historical LLM evaluation runs retrieval/no-retrieval/masked contamination probes; contaminated cells are non-promotable.
- There is no universal `occurred_at <= published_at` rule. Eligibility is based on actual availability at the cutoff.
- The migration chain is single-headed and explicit: `20260721_0001_event_log → 20260721_0002_ontology_release → 20260721_0003_semantic_evidence → 20260721_0004_semantic_improvement → 20260721_0005_market_data → 20260721_0006_accounting → 20260721_0007_calibration`.
- All implementation follows red-green-refactor, strict typing, deterministic tests, and one reviewable commit per task.

---

## Planned File Structure

```text
ontology/
  modules/                       # immutable OWL/Turtle source modules
  shapes/                        # SHACL constraints
  mappings/                      # selective FIBO/PROV-O/OWL-Time/identifier mappings
  queries/competency/            # baseline and semantic competency queries
  queries/decision/              # approved decision query templates
  releases/                      # immutable release manifests
  policies/                      # reasoning/support/feature policy releases
src/trading_os/
  ontology/                      # release builder, compatibility, registry
  semantic/
    models/                      # identity, time, evidence, snapshots, queries, beliefs
    evidence/                    # source blobs, ledger, admission, identity resolution
    projections/                 # Fuseki and Neo4j adapters/builders
    retrieval/                   # relational champion and governed templates
    packets/                     # six bounded evidence-domain builders
    reasoning/                   # hypotheses, belief builder, decision/risk projectors
    improvement/                 # failures, experiments, promotion, activation/canary/rollback
  ports/                         # ontology/evidence/blob/semantic-graph protocol additions
alembic/versions/                # append-only evidence and improvement schemas
config/semantic/                 # frozen admission, query, evaluation, and promotion policy
infra/fuseki/                    # pinned Apache Jena 6.1.0 Docker build/config
tests/
  fixtures/ontology/             # valid/invalid releases and migration fixtures
  fixtures/semantic/             # identity, temporal, contradiction, and query cases
  unit/semantic/                 # pure semantic/reasoning rules
  contract/semantic/             # port and graph projection contracts
  integration/semantic/          # Postgres/Fuseki/Neo4j snapshot equivalence
```

## Normative Post-Review Task Amendments

The amendments in this section are acceptance criteria for the numbered tasks below. When an
abbreviated example later in the plan omits a field or uses an older name, this section controls.
An implementation task is not complete until its amendment tests pass.

| Task | Required amendment | Required proof |
|---|---|---|
| 1 | Version every meaning-bearing artifact: `OntologyRelease`, `QueryPackRelease`, `ReasoningPolicyRelease` (including hypothesis support rules), and `FeaturePolicyRelease`. The ontology compatibility contract hashes modules, SHACL shapes, mappings, bounded inference rules, and the canonical IRI scheme. | Changing any one artifact changes its release ID; changing an IRI rule, mapping, or inference rule without the required compatibility/migration declaration fails publication. Registry repeats the author/approver separation check. |
| 2 | Use typed `LegalEntityId`, `IssuerRoleId`, `SecurityId`, `ListingId`, `VenueId`, and `TickerAliasId`; typed crosswalks; temporal, venue-scoped aliases; and one validating `CanonicalIriEncoder`. Model actual availability with `AvailabilityState`; do not impose a universal occurred-before-published rule. | Same ticker on two venues and ticker reuse over time resolve without overwrite; malformed IDs cannot become `URIRef`s; a restatement may occur after publication while remaining cutoff-safe. |
| 3 | Persist source-origin clusters and extraction activity references alongside append-only evidence, so independence checks use ledger facts rather than caller-supplied strings. | Two documents from one syndicated origin count once; a correction appends and supersedes; all UPDATE/DELETE attempts fail. Migration has `down_revision = "20260721_0002"`. |
| 4 | Keep the ordinary snapshot-scoped relational retriever independent and permanent. It is the champion, operational fallback, and control arm for every differential evaluation. | It runs with Fuseki, Neo4j, and all LLM services unavailable and produces a sealed retrieval receipt. |
| 5 | Build RDF only with the final precomputed `SemanticSnapshotId`, the `urn:trading-os:ontology#` vocabulary, and IDs encoded by `CanonicalIriEncoder`. Runtime credentials are query-only; builder credentials exist only in the offline build job. | SHACL targets the exact emitted predicates; malformed IDs fail before serialization; runtime Graph Store writes are denied. |
| 6 | Create `semantic/projections/neo4j.py` without modifying the skipped Trading OS Task 15 file. Stamp every node/relationship with the final snapshot ID and apply the same offline-builder/runtime-reader credential split. | A fresh checkout that executed only Trading OS Tasks 1–14 can implement this task; runtime Cypher writes are denied. |
| 7 | Compute `SemanticSnapshotId = SHA256(canonical(SemanticContentManifest))` before either graph projection. After builds, compare Postgres/RDF/Neo4j assertion and entailment fingerprints and issue a separate immutable `SemanticProjectionReceipt`. Only a snapshot with a sealed receipt is queryable. | No preliminary snapshot-ID field exists; the same final ID is present in the manifest, graph IRI, Neo4j stamps, and receipt; unsealed or mismatched projections fail closed. |
| 8 | Replace flat strings/dicts with `CanonicalIdentityPort`, `IdentityCrosswalkPort`, and temporal `AliasResolutionPort`. Admission derives independent-source counts from persisted origin clusters. | Colliding aliases return explicit candidates; no dictionary overwrite or automatic fuzzy merge is possible; caller-supplied independence counts are ignored. |
| 9 | Bind every request and cache key to data snapshot, semantic snapshot, projection receipt, ontology release, query-pack release, and cutoff. Emit an immutable `RetrievalReceipt`. Normalize timeout, transport, HTTP, decode, schema, snapshot-mismatch, and projection-integrity errors into a closed semantic error taxonomy. | Cache reuse fails when any binding differs; fallback occurs only for a declared equivalent relational template; otherwise the query fails closed. |
| 10–11 | Every `EvidencePacket` carries supporting and refuting `ObservationId`s plus typed `Decimal` numeric features. Source text and arbitrary LLM output never enter a packet. | A packet cannot be constructed from unsupported scalar values; provenance reaches its sealed retrieval receipt and observations. |
| 12 | Evaluate hypotheses through a versioned `HypothesisSupportRuleRelease`, not packet presence alone. Produce both `DecisionFeatureSet` and tighten-only `RiskOverlaySet`; a versioned `DeterministicStrategyPolicy` is the sole adapter from activated decision features to `HotPathCandidate`. | Conflicting observation sets produce `CONTESTED`; missing requirements produce `INSUFFICIENT`; unknown feature keys are dropped; every risk multiplier is in `[0, 1]`; the adapter remains deterministic. |
| 13 | Compare relational/RDF/Neo4j paths on frozen cases with a declared primary metric, minimum material effect, multiplicity correction, and fixed retirement horizon. Historical LLM cells run retrieval, no-retrieval, and masked-knowledge probes and record model knowledge-cutoff metadata. | Contaminated cells are excluded from promotion; safety failures, corrected significance failures, or effect-size failures block promotion. |
| 14 | Use a closed `RootCauseClass`. Keep semantic release promotion separate from immutable `DecisionFeatureActivation` states: `DISABLED`, `SHADOW`, `PAPER_CANARY`, `PAPER_ACTIVE`, `LIVE_CANARY`, `LIVE_ACTIVE`. Canary scope, capital/risk caps, horizon, success gates, rollback target, and approver are sealed. | A promoted semantic release has no economic effect; state transitions cannot skip canary; cap breach or rollback trigger immediately returns to the prior safe activation. Migration has `down_revision = "20260721_0003"`. |
| 15 | Bind the complete context before any cache return. `SemanticDecisionHandoff` returns an `ActivatedDecisionInputs` envelope containing the allowed `DecisionFeatureSet`, tighten-only `RiskOverlaySet`, activation ID/mode, and audit receipt; `SHADOW` returns empty economic inputs. | End-to-end tests prove relational degradation, semantic fail-closed behavior, activation isolation, deterministic replay, and the exact Trading OS Task 18/19/32/34/35/36 splice. |

The separately versioned artifact types use a common frozen envelope:

```python
class ArtifactRelease(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    release_id: str                    # SHA-256 of canonical content
    artifact_kind: ArtifactKind
    semantic_version: str
    content_hashes: Mapping[str, str]
    compatibility_report_hash: str
    authored_by: str
    reviewed_by: str
    approved_by: str


class SemanticQueryBinding(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    data_snapshot_id: ValidatedDataSnapshotId
    semantic_snapshot_id: SemanticSnapshotId
    projection_receipt_id: SemanticProjectionReceiptId
    ontology_release_id: OntologyReleaseId
    query_pack_release_id: QueryPackReleaseId
    decision_cutoff: datetime
```

Do not collapse these release IDs into the ontology release. Their independent histories are what
make an old decision exactly replayable after query, support-rule, or feature-policy evolution.

---

## Milestone 1 — Canonical Ontology and Evidence History

### Task 1: Add the ontology toolchain and immutable release builder

**Files:**
- Modify: `pyproject.toml`
- Modify: `compose.yaml`
- Create: `infra/fuseki/Dockerfile`
- Create: `infra/fuseki/config.ttl`
- Create: `infra/fuseki/build-config.ttl`
- Create: `ontology/modules/core.ttl`
- Create: `ontology/modules/identity.ttl`
- Create: `ontology/modules/time.ttl`
- Create: `ontology/modules/provenance.ttl`
- Create: `ontology/modules/evidence.ttl`
- Create: `ontology/modules/events.ttl`
- Create: `ontology/modules/reasoning.ttl`
- Create: `ontology/modules/technical.ttl`
- Create: `ontology/modules/fundamental.ttl`
- Create: `ontology/modules/sentiment.ttl`
- Create: `ontology/modules/macro.ttl`
- Create: `ontology/modules/relationships.ttl`
- Create: `ontology/modules/portfolio-context.ttl`
- Create: `ontology/shapes/core.shacl.ttl`
- Create: `ontology/shapes/identity.shacl.ttl`
- Create: `ontology/shapes/evidence.shacl.ttl`
- Create: `ontology/shapes/domains.shacl.ttl`
- Create: `ontology/shapes/belief-state.shacl.ttl`
- Create: `ontology/mappings/fibo.ttl`
- Create: `ontology/mappings/prov-o.ttl`
- Create: `ontology/mappings/owl-time.ttl`
- Create: `ontology/mappings/identifiers.ttl`
- Create: `ontology/policies/canonical-iri-scheme-v1.json`
- Create: `ontology/policies/inference/approved-owl-rl-v1.ttl`
- Create: `ontology/policies/query-pack-1.0.0.json`
- Create: `ontology/policies/reasoning-policy-1.0.0.json`
- Create: `ontology/policies/feature-policy-1.0.0.json`
- Create: `ontology/releases/1.0.0.json`
- Create: `src/trading_os/ontology/models.py`
- Create: `src/trading_os/ontology/compatibility.py`
- Create: `src/trading_os/ontology/release.py`
- Create: `src/trading_os/ontology/registry.py`
- Modify: `src/trading_os/domain/events.py`
- Modify: `src/trading_os/persistence/postgres_event_store.py`
- Create: `alembic/versions/20260721_0002_ontology_release.py`
- Test: `tests/unit/semantic/test_ontology_release.py`
- Test: `tests/unit/semantic/test_ontology_compatibility.py`
- Test: `tests/integration/semantic/test_ontology_registry.py`

**Interfaces:**
- Consumes: immutable ID/hash conventions from Trading OS Tasks 1–2.
- Produces: `OntologyReleaseId`, `QueryPackReleaseId`, `ReasoningPolicyReleaseId`,
  `FeaturePolicyReleaseId`, their immutable release envelopes, `CompatibilityReport`,
  `build_release(root: Path, *, version: str, authored_by: str, reviewed_by: str, approved_by: str,
  migration_ref: str | None = None, previous_root: Path | None = None,
  previous_version: str | None = None) -> OntologyRelease`, `write_release_manifest(...)`, and
  append-only artifact registries.

- [ ] **Step 1: Write release reproducibility and validation tests**

```python
# tests/unit/semantic/test_ontology_release.py
from pathlib import Path

import pytest

from trading_os.ontology.release import OntologyValidationError, build_release, write_release_manifest


def test_release_hash_is_reproducible() -> None:
    root = Path("tests/fixtures/ontology/valid")
    first = build_release(
        root,
        version="1.0.0",
        authored_by="agent:test",
        reviewed_by="human:reviewer",
        approved_by="human:approver",
    )
    second = build_release(
        root,
        version="1.0.0",
        authored_by="agent:test",
        reviewed_by="human:reviewer",
        approved_by="human:approver",
    )
    assert first.release_id == second.release_id
    assert first.module_hashes == second.module_hashes


def test_invalid_shape_fixture_blocks_release() -> None:
    with pytest.raises(OntologyValidationError):
        build_release(
            Path("tests/fixtures/ontology/invalid"),
            version="1.0.0",
            authored_by="agent:test",
            reviewed_by="human:reviewer",
            approved_by="human:approver",
        )


def test_release_manifest_cannot_be_overwritten(tmp_path, valid_release) -> None:
    destination = tmp_path / "1.0.0.json"
    write_release_manifest(valid_release, destination)
    with pytest.raises(FileExistsError):
        write_release_manifest(valid_release, destination)
```

```python
# tests/unit/semantic/test_ontology_compatibility.py
from pathlib import Path

import pytest

from trading_os.ontology.compatibility import BreakingReleaseVersion, check_compatibility


def test_breaking_change_requires_major_release() -> None:
    with pytest.raises(BreakingReleaseVersion):
        check_compatibility(
            Path("tests/fixtures/ontology/compatibility/v1"),
            Path("tests/fixtures/ontology/compatibility/breaking"),
            previous_version="1.2.0",
            new_version="1.3.0",
        )


@pytest.mark.parametrize("changed_artifact", ["breaking-mapping", "breaking-shape", "breaking-inference", "breaking-iri-scheme"])
def test_breaking_meaning_artifact_requires_major_release(changed_artifact: str) -> None:
    with pytest.raises(BreakingReleaseVersion):
        check_compatibility(
            Path("tests/fixtures/ontology/compatibility/v1"),
            Path(f"tests/fixtures/ontology/compatibility/changed-{changed_artifact}"),
            previous_version="1.2.0",
            new_version="1.3.0",
        )
```

```python
# tests/integration/semantic/test_ontology_registry.py
async def test_publication_registers_release_and_event_atomically(
    ontology_registry,
    built_release,
    event_store,
) -> None:
    await ontology_registry.publish(built_release)
    assert await ontology_registry.get_exact(built_release.release_id) == built_release
    events = await event_store.read_stream("ontology:releases")
    assert events[-1].payload.release_id == built_release.release_id.value
```

- [ ] **Step 2: Run the tests and verify the ontology package is absent**

Run: `uv run pytest tests/unit/semantic/test_ontology_release.py tests/unit/semantic/test_ontology_compatibility.py -v`

Expected: FAIL during collection with `ModuleNotFoundError: No module named 'trading_os.ontology'`.

- [ ] **Step 3: Add pinned services, RDF dependencies, core ontology, and release builder**

Add `rdflib`, `pyshacl`, `owlrl`, `neo4j`, and `packaging` with `uv add`; commit the resulting lockfile. Build
Fuseki from the official Jena 6.1.0 distribution with its SHA-512 verified in the Docker build.
Configure a TDB2 dataset named `semantic` with query, Graph Store, and SHACL endpoints; expose it
only on the compose network in non-development profiles.

```dockerfile
# infra/fuseki/Dockerfile
FROM eclipse-temurin:21-jre
ARG JENA_VERSION=6.1.0
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt
RUN curl -fsSLO "https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-${JENA_VERSION}.tar.gz" \
    && curl -fsSLO "https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-${JENA_VERSION}.tar.gz.sha512" \
    && sha512sum -c "apache-jena-fuseki-${JENA_VERSION}.tar.gz.sha512" \
    && tar -xzf "apache-jena-fuseki-${JENA_VERSION}.tar.gz" \
    && mv "apache-jena-fuseki-${JENA_VERSION}" fuseki \
    && rm "apache-jena-fuseki-${JENA_VERSION}.tar.gz" "apache-jena-fuseki-${JENA_VERSION}.tar.gz.sha512"
RUN useradd --system --uid 10001 --home /nonexistent fuseki \
    && mkdir -p /fuseki/databases \
    && chown -R fuseki:fuseki /opt/fuseki /fuseki
USER 10001:10001
EXPOSE 3030
ENTRYPOINT ["/opt/fuseki/fuseki-server"]
CMD ["--config=/fuseki/config.ttl"]
```

```turtle
# infra/fuseki/config.ttl
@prefix fuseki: <http://jena.apache.org/fuseki#> .
@prefix ja: <http://jena.hpl.hp.com/2005/11/Assembler#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix tdb2: <http://jena.apache.org/2016/tdb#> .

<#service> rdf:type fuseki:Service ;
  fuseki:name "semantic" ;
  fuseki:endpoint [ fuseki:operation fuseki:query ; fuseki:name "query" ] ;
  fuseki:endpoint [ fuseki:operation fuseki:gsp_r ; fuseki:name "get" ] ;
  fuseki:endpoint [ fuseki:operation fuseki:shacl ; fuseki:name "shacl" ] ;
  fuseki:dataset <#dataset> .

<#dataset> rdf:type tdb2:DatasetTDB2 ;
  tdb2:location "/fuseki/databases/semantic" .
```

```turtle
# infra/fuseki/build-config.ttl — used only by the isolated projection-builder profile
@prefix fuseki: <http://jena.apache.org/fuseki#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix tdb2: <http://jena.apache.org/2016/tdb#> .

<#builder> rdf:type fuseki:Service ;
  fuseki:name "semantic-build" ;
  fuseki:endpoint [ fuseki:operation fuseki:gsp_rw ; fuseki:name "data" ] ;
  fuseki:endpoint [ fuseki:operation fuseki:shacl ; fuseki:name "shacl" ] ;
  fuseki:dataset <#dataset> .

<#dataset> rdf:type tdb2:DatasetTDB2 ;
  tdb2:location "/fuseki/databases/semantic" .
```

The compose file places the builder in an explicit `semantic-build` profile on a dedicated build
network; application containers attach only to the read-only Fuseki service network.

Create the ontology files below with stable, release-independent term IRIs. Each additional module
declares its own `owl:Ontology` header and imports `<urn:trading-os:ontology>`; only `core.ttl`
declares the release-specific `owl:versionIRI`.

```turtle
# ontology/modules/core.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix tos: <urn:trading-os:ontology#> .

<urn:trading-os:ontology> a owl:Ontology ;
  owl:versionIRI <urn:trading-os:ontology:1.0.0> .

tos:SemanticEntity a owl:Class .
tos:Assertion a owl:Class .
tos:InstrumentBeliefState a owl:Class .
tos:hasStableId a owl:DatatypeProperty .
tos:aboutInstrument a owl:ObjectProperty .
```

```turtle
# ontology/modules/identity.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tos: <urn:trading-os:ontology#> .
<urn:trading-os:module:identity> a owl:Ontology ; owl:imports <urn:trading-os:ontology> .
tos:LegalEntity a owl:Class ; rdfs:subClassOf tos:SemanticEntity .
tos:Security a owl:Class ; rdfs:subClassOf tos:SemanticEntity .
tos:Listing a owl:Class ; rdfs:subClassOf tos:SemanticEntity .
tos:TickerSymbol a owl:Class .
tos:issuedBy a owl:ObjectProperty .
tos:listsSecurity a owl:ObjectProperty .
tos:venueMic a owl:DatatypeProperty .
tos:tickerText a owl:DatatypeProperty .
```

```turtle
# ontology/modules/time.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix tos: <urn:trading-os:ontology#> .
<urn:trading-os:module:time> a owl:Ontology ; owl:imports <urn:trading-os:ontology> .
tos:ValidityInterval a owl:Class .
tos:occurredAt a owl:DatatypeProperty .
tos:publishedAt a owl:DatatypeProperty .
tos:receivedAt a owl:DatatypeProperty .
tos:recordedAt a owl:DatatypeProperty .
tos:validFrom a owl:DatatypeProperty .
tos:validTo a owl:DatatypeProperty .
tos:supersededAt a owl:DatatypeProperty .
```

```turtle
# ontology/modules/provenance.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix tos: <urn:trading-os:ontology#> .
<urn:trading-os:module:provenance> a owl:Ontology ; owl:imports <urn:trading-os:ontology> .
tos:SourceRecord a owl:Class .
tos:EvidenceSpan a owl:Class .
tos:derivedFromSpan a owl:ObjectProperty .
tos:licencePolicyId a owl:DatatypeProperty .
```

```turtle
# ontology/modules/evidence.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tos: <urn:trading-os:ontology#> .
<urn:trading-os:module:evidence> a owl:Ontology ; owl:imports <urn:trading-os:ontology> .
tos:Observation a owl:Class .
tos:Claim a owl:Class ; rdfs:subClassOf tos:Assertion .
tos:AdmissionDecision a owl:Class .
tos:admissionState a owl:DatatypeProperty .
tos:supersedes a owl:ObjectProperty .
tos:contradicts a owl:ObjectProperty .
```

```turtle
# ontology/modules/events.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix tos: <urn:trading-os:ontology#> .
<urn:trading-os:module:events> a owl:Ontology ; owl:imports <urn:trading-os:ontology> .
tos:MarketEvent a owl:Class .
```

```turtle
# ontology/modules/reasoning.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix tos: <urn:trading-os:ontology#> .
<urn:trading-os:module:reasoning> a owl:Ontology ; owl:imports <urn:trading-os:ontology> .
tos:InstrumentHypothesis a owl:Class .
tos:HypothesisAssessment a owl:Class .
tos:EvidencePacket a owl:Class .
tos:supports a owl:ObjectProperty .
tos:refutes a owl:ObjectProperty .
```

```turtle
# ontology/modules/technical.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tos: <urn:trading-os:ontology#> .
<urn:trading-os:module:technical> a owl:Ontology ; owl:imports <urn:trading-os:ontology> .
tos:TechnicalObservation a owl:Class ; rdfs:subClassOf tos:Observation .
```

```turtle
# ontology/modules/fundamental.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tos: <urn:trading-os:ontology#> .
<urn:trading-os:module:fundamental> a owl:Ontology ; owl:imports <urn:trading-os:ontology> .
tos:FundamentalObservation a owl:Class ; rdfs:subClassOf tos:Observation .
```

```turtle
# ontology/modules/sentiment.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tos: <urn:trading-os:ontology#> .
<urn:trading-os:module:sentiment> a owl:Ontology ; owl:imports <urn:trading-os:ontology> .
tos:NarrativeObservation a owl:Class ; rdfs:subClassOf tos:Observation .
```

```turtle
# ontology/modules/macro.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tos: <urn:trading-os:ontology#> .
<urn:trading-os:module:macro> a owl:Ontology ; owl:imports <urn:trading-os:ontology> .
tos:MacroRelease a owl:Class ; rdfs:subClassOf tos:MarketEvent .
```

```turtle
# ontology/modules/relationships.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tos: <urn:trading-os:ontology#> .
<urn:trading-os:module:relationships> a owl:Ontology ; owl:imports <urn:trading-os:ontology> .
tos:EconomicRelationship a owl:Class ; rdfs:subClassOf tos:Assertion .
```

```turtle
# ontology/modules/portfolio-context.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix tos: <urn:trading-os:ontology#> .
<urn:trading-os:module:portfolio-context> a owl:Ontology ; owl:imports <urn:trading-os:ontology> .
tos:PortfolioContext a owl:Class .
```

```turtle
# ontology/mappings/prov-o.ttl
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tos: <urn:trading-os:ontology#> .
tos:SourceRecord rdfs:subClassOf prov:Entity .
tos:Claim rdfs:subClassOf prov:Entity .
tos:derivedFromSpan rdfs:subPropertyOf prov:wasDerivedFrom .
```

```turtle
# ontology/mappings/owl-time.ttl
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix time: <http://www.w3.org/2006/time#> .
@prefix tos: <urn:trading-os:ontology#> .
tos:ValidityInterval rdfs:subClassOf time:Interval .
```

```turtle
# ontology/mappings/identifiers.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix tos: <urn:trading-os:ontology#> .
tos:lei a owl:DatatypeProperty .
tos:isin a owl:DatatypeProperty .
tos:venueMic a owl:DatatypeProperty .
```

```turtle
# ontology/mappings/fibo.ttl
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix tos: <urn:trading-os:ontology#> .
tos:LegalEntity skos:closeMatch <https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/LegalEntity> .
tos:Security skos:closeMatch <https://spec.edmcouncil.org/fibo/ontology/FBC/FinancialInstruments/FinancialInstruments/FinancialInstrument> .
```

These are one-way local mappings; do not import FIBO's dependency closure.

```turtle
# ontology/shapes/core.shacl.ttl
@prefix owl: <http://www.w3.org/2002/07/owl#> .
<urn:trading-os:shapes> a owl:Ontology .
```

```turtle
# ontology/shapes/identity.shacl.ttl
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix tos: <urn:trading-os:ontology#> .
tos:ListingShape a sh:NodeShape ; sh:targetClass tos:Listing ;
  sh:property [ sh:path tos:listsSecurity ; sh:minCount 1 ; sh:maxCount 1 ] ;
  sh:property [ sh:path tos:venueMic ; sh:minCount 1 ; sh:maxCount 1 ] ;
  sh:property [ sh:path tos:tickerText ; sh:minCount 1 ; sh:maxCount 1 ] .
```

```turtle
# ontology/shapes/evidence.shacl.ttl
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix tos: <urn:trading-os:ontology#> .
tos:ClaimShape a sh:NodeShape ; sh:targetClass tos:Claim ;
  sh:property [ sh:path tos:derivedFromSpan ; sh:minCount 1 ] ;
  sh:property [ sh:path tos:receivedAt ; sh:minCount 1 ; sh:maxCount 1 ] .
```

```turtle
# ontology/shapes/domains.shacl.ttl
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix tos: <urn:trading-os:ontology#> .
tos:EvidencePacketShape a sh:NodeShape ; sh:targetClass tos:EvidencePacket ;
  sh:property [ sh:path tos:aboutInstrument ; sh:minCount 1 ; sh:maxCount 1 ] .
```

```turtle
# ontology/shapes/belief-state.shacl.ttl
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix tos: <urn:trading-os:ontology#> .
tos:BeliefStateShape a sh:NodeShape ; sh:targetClass tos:InstrumentBeliefState ;
  sh:property [ sh:path tos:targetPrice ; sh:maxCount 0 ] ;
  sh:property [ sh:path tos:orderQuantity ; sh:maxCount 0 ] .
```

The release fixtures use the same module graph as production.

```python
# src/trading_os/ontology/models.py
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class OntologyReleaseId(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    value: Sha256


class OntologyRelease(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    release_id: OntologyReleaseId
    semantic_version: str
    module_hashes: dict[str, Sha256]
    mapping_hashes: dict[str, Sha256]
    shapes_hash: Sha256
    inference_ruleset_hash: Sha256
    canonical_iri_scheme_hash: Sha256
    semantic_contract_hash: Sha256
    validation_report_hash: Sha256
    compatibility_report_hash: Sha256
    migration_ref: str | None
    authored_by: str
    reviewed_by: str
    approved_by: str
```

```python
# src/trading_os/domain/events.py (inside the existing EventType)
ONTOLOGY_RELEASE_PUBLISHED = "ontology_release_published"


class OntologyReleasePublished(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    release_id: str
    semantic_version: str
    manifest_hash: str
    approved_by: str
```

```python
# src/trading_os/ontology/compatibility.py
import hashlib
from decimal import Decimal
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict
from rdflib import Graph
from rdflib.compare import to_canonical_graph
from rdflib.namespace import OWL, RDF, RDFS, SH


class BreakingReleaseVersion(ValueError):
    pass


class CompatibilityReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    breaking_changes: tuple[str, ...]
    report_hash: str


TERM_TYPES = frozenset((OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty))
SCHEMA_PREDICATES = frozenset((RDFS.domain, RDFS.range))
SHAPE_PREDICATES = frozenset((SH.minCount, SH.maxCount, SH.datatype, SH["class"], SH.nodeKind, SH.closed))


def _load(root: Path) -> Graph:
    graph = Graph()
    for path in sorted(
        (*root.glob("modules/*.ttl"), *root.glob("shapes/*.ttl"), *root.glob("mappings/*.ttl"))
    ):
        graph.parse(path, format="turtle")
    return to_canonical_graph(graph)


def _meaning_artifacts(root: Path) -> dict[str, str]:
    paths = sorted((*root.glob("mappings/*"), *root.glob("policies/**/*")))
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
        if path.is_file()
    }


def _major(version: str) -> int:
    return int(version.split(".", maxsplit=1)[0])


def check_compatibility(
    previous_root: Path,
    new_root: Path,
    *,
    previous_version: str,
    new_version: str,
) -> CompatibilityReport:
    previous = _load(previous_root)
    current = _load(new_root)
    previous_terms = {(subject, object_) for subject, _, object_ in previous.triples((None, RDF.type, None)) if object_ in TERM_TYPES}
    current_terms = {(subject, object_) for subject, _, object_ in current.triples((None, RDF.type, None)) if object_ in TERM_TYPES}
    removed_terms = previous_terms - current_terms
    previous_constraints = {
        tuple(map(str, triple))
        for triple in previous
        if triple[1] in SCHEMA_PREDICATES | SHAPE_PREDICATES
    }
    current_constraints = {
        tuple(map(str, triple))
        for triple in current
        if triple[1] in SCHEMA_PREDICATES | SHAPE_PREDICATES
    }
    previous_artifacts = _meaning_artifacts(previous_root)
    current_artifacts = _meaning_artifacts(new_root)
    breaking_artifact_changes = classify_breaking_artifact_changes(
        previous_root=previous_root,
        new_root=new_root,
        previous_hashes=previous_artifacts,
        new_hashes=current_artifacts,
    )
    changes = tuple(
        sorted(
            [f"removed-term:{subject}:{term_type}" for subject, term_type in removed_terms]
            + [f"changed-constraint:{item}" for item in previous_constraints ^ current_constraints]
            + [f"breaking-artifact:{path}" for path in breaking_artifact_changes]
        )
    )
    if changes and _major(new_version) <= _major(previous_version):
        raise BreakingReleaseVersion("breaking ontology changes require a new MAJOR version")
    payload = json.dumps(changes, sort_keys=True, separators=(",", ":")).encode()
    return CompatibilityReport(
        breaking_changes=changes,
        report_hash=hashlib.sha256(payload).hexdigest(),
    )
```

```python
# src/trading_os/ontology/release.py
import hashlib
import json
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, URIRef
from rdflib.compare import to_canonical_graph
from rdflib.namespace import OWL

from trading_os.ontology.compatibility import check_compatibility
from trading_os.ontology.models import OntologyRelease, OntologyReleaseId


class OntologyValidationError(ValueError):
    pass


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_ntriples(graph: Graph) -> bytes:
    canonical = to_canonical_graph(graph).serialize(format="nt", encoding="utf-8")
    return b"\n".join(sorted(canonical.splitlines())) + b"\n"


def build_release(
    root: Path,
    *,
    version: str,
    authored_by: str,
    reviewed_by: str,
    approved_by: str,
    migration_ref: str | None = None,
    previous_root: Path | None = None,
    previous_version: str | None = None,
) -> OntologyRelease:
    if authored_by == approved_by:
        raise ValueError("ontology author cannot approve its own release")
    modules = sorted(root.glob("modules/*.ttl"))
    mappings = sorted(root.glob("mappings/*.ttl"))
    shapes = sorted(root.glob("shapes/*.ttl"))
    inference_rules = sorted(root.glob("policies/inference/*.ttl"))
    iri_scheme = root / "policies/canonical-iri-scheme-v1.json"
    graph = Graph()
    shape_graph = Graph()
    for path in modules:
        graph.parse(path, format="turtle")
    for path in mappings:
        graph.parse(path, format="turtle")
    for path in shapes:
        shape_graph.parse(path, format="turtle")
    version_triple = (
        URIRef("urn:trading-os:ontology"),
        OWL.versionIRI,
        URIRef(f"urn:trading-os:ontology:{version}"),
    )
    if version_triple not in graph:
        raise OntologyValidationError("release must declare its exact owl:versionIRI")
    conforms, report, _ = validate(graph, shacl_graph=shape_graph, inference="rdfs")
    if not conforms:
        raise OntologyValidationError(str(report.serialize(format="turtle")))
    module_hashes = {str(path.relative_to(root)): _hash(path.read_bytes()) for path in modules}
    mapping_hashes = {str(path.relative_to(root)): _hash(path.read_bytes()) for path in mappings}
    inference_ruleset_hash = _hash(
        b"".join(path.read_bytes() for path in inference_rules)
    )
    canonical_iri_scheme_hash = _hash(iri_scheme.read_bytes())
    shape_bytes = _canonical_ntriples(shape_graph)
    validation_report_hash = _hash(_canonical_ntriples(report))
    if (previous_root is None) != (previous_version is None):
        raise ValueError("previous_root and previous_version must be supplied together")
    compatibility_hash = _hash(b"initial-release")
    if previous_root is not None and previous_version is not None:
        compatibility = check_compatibility(
            previous_root,
            root,
            previous_version=previous_version,
            new_version=version,
        )
        if compatibility.breaking_changes and migration_ref is None:
            raise ValueError("breaking ontology release requires a migration reference")
        compatibility_hash = compatibility.report_hash
    payload = json.dumps(
        {
            "version": version,
            "modules": module_hashes,
            "mappings": mapping_hashes,
            "shapes": _hash(shape_bytes),
            "inference_ruleset": inference_ruleset_hash,
            "canonical_iri_scheme": canonical_iri_scheme_hash,
            "validation_report": validation_report_hash,
            "compatibility": compatibility_hash,
            "migration_ref": migration_ref,
            "authored_by": authored_by,
            "reviewed_by": reviewed_by,
            "approved_by": approved_by,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    release_id = OntologyReleaseId(value=_hash(payload))
    return OntologyRelease(
        release_id=release_id,
        semantic_version=version,
        module_hashes=module_hashes,
        mapping_hashes=mapping_hashes,
        shapes_hash=_hash(shape_bytes),
        inference_ruleset_hash=inference_ruleset_hash,
        canonical_iri_scheme_hash=canonical_iri_scheme_hash,
        semantic_contract_hash=_hash(
            json.dumps(
                {
                    "modules": module_hashes,
                    "mappings": mapping_hashes,
                    "shapes": _hash(shape_bytes),
                    "inference": inference_ruleset_hash,
                    "iri_scheme": canonical_iri_scheme_hash,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ),
        validation_report_hash=validation_report_hash,
        compatibility_report_hash=compatibility_hash,
        migration_ref=migration_ref,
        authored_by=authored_by,
        reviewed_by=reviewed_by,
        approved_by=approved_by,
    )


def write_release_manifest(release: OntologyRelease, destination: Path) -> None:
    payload = json.dumps(
        release.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )
    with destination.open("x", encoding="utf-8") as handle:
        handle.write(payload + "\n")
```

Generate the checked-in first release with the same production code:

Run: `uv run python -c 'from pathlib import Path; from trading_os.ontology.release import build_release, write_release_manifest; release = build_release(Path("ontology"), version="1.0.0", authored_by="agent:ontology-steward", reviewed_by="human:ontology-reviewer", approved_by="human:release-approver"); write_release_manifest(release, Path("ontology/releases/1.0.0.json"))'`

Expected: creates `ontology/releases/1.0.0.json`; rerunning exits non-zero with `FileExistsError`.

```python
# src/trading_os/ontology/registry.py
from typing import Protocol

from sqlalchemy import JSON, String, insert, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class RegistryBase(DeclarativeBase):
    pass


class OntologyReleaseRow(RegistryBase):
    __tablename__ = "ontology_release"
    release_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    semantic_version: Mapped[str] = mapped_column(String(32), unique=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON)


class TransactionalEventWriterPort(Protocol):
    async def current_version(self, session: AsyncSession, stream_id: str) -> int: ...
    async def append_in_transaction(
        self,
        session: AsyncSession,
        event: EventEnvelope,
        *,
        expected_stream_version: int,
    ) -> int: ...


class OntologyReleaseRegistry:
    def __init__(
        self,
        sessions: async_sessionmaker[AsyncSession],
        events: TransactionalEventWriterPort,
    ) -> None:
        self._sessions = sessions
        self._events = events

    async def publish(self, release: OntologyRelease) -> None:
        if release.authored_by == release.approved_by:
            raise ValueError("artifact author cannot approve its own release")
        event = EventEnvelope.new(
            stream_id="ontology:releases",
            event_type=EventType.ONTOLOGY_RELEASE_PUBLISHED,
            payload=OntologyReleasePublished(
                release_id=release.release_id.value,
                semantic_version=release.semantic_version,
                manifest_hash=release.release_id.value,
                approved_by=release.approved_by,
            ),
        )
        async with self._sessions.begin() as session:
            current_version = await self._events.current_version(session, "ontology:releases")
            await session.execute(
                insert(OntologyReleaseRow).values(
                    release_id=release.release_id.value,
                    semantic_version=release.semantic_version,
                    payload=release.model_dump(mode="json"),
                )
            )
            await self._events.append_in_transaction(
                session,
                event,
                expected_stream_version=current_version,
            )

    async def get_exact(self, release_id: OntologyReleaseId) -> OntologyRelease:
        async with self._sessions() as session:
            payload = await session.scalar(
                select(OntologyReleaseRow.payload).where(
                    OntologyReleaseRow.release_id == release_id.value
                )
            )
        if payload is None:
            raise KeyError(release_id.value)
        return OntologyRelease.model_validate(payload)
```

```python
# src/trading_os/persistence/postgres_event_store.py (methods on PostgresEventStore)
async def current_version(self, session: AsyncSession, stream_id: str) -> int:
    value = await session.scalar(
        select(func.max(EventLogRow.stream_version)).where(EventLogRow.stream_id == stream_id)
    )
    return int(value) if value is not None else -1


async def append_in_transaction(
    self,
    session: AsyncSession,
    event: EventEnvelope,
    *,
    expected_stream_version: int,
) -> int:
    await session.execute(
        text("SELECT pg_advisory_xact_lock(hashtextextended(:stream_id, 0))"),
        {"stream_id": event.stream_id},
    )
    current = await self.current_version(session, event.stream_id)
    if current != expected_stream_version:
        raise StreamConflict(event.stream_id, expected_stream_version, current)
    next_version = current + 1
    await session.execute(
        insert(EventLogRow).values(
            event_id=event.event_id,
            stream_id=event.stream_id,
            stream_version=next_version,
            event_type=event.event_type.value,
            occurred_at=event.occurred_at,
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
            schema_version=event.schema_version,
            payload=event.payload.model_dump(mode="json"),
        )
    )
    return next_version
```

`append()` keeps its public contract: it opens a transaction and delegates to
`append_in_transaction`. `20260721_0002_ontology_release.py` declares `revision = "20260721_0002"`
and `down_revision = "20260721_0001"`, and creates the `ontology_release` table shown by
`OntologyReleaseRow`, plus the same UPDATE/DELETE rejection trigger used for the evidence tables.

- [ ] **Step 4: Verify release, type, and container configuration**

Run: `uv run pytest tests/unit/semantic/test_ontology_release.py tests/unit/semantic/test_ontology_compatibility.py -v && uv run mypy src/trading_os/ontology`

Run: `docker compose config --quiet`

Run: `uv run alembic upgrade head && uv run pytest tests/integration/semantic/test_ontology_registry.py -v -m integration`

Expected: unit/integration tests PASS, mypy exits 0, and compose configuration exits 0.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock compose.yaml infra/fuseki ontology src/trading_os/ontology src/trading_os/domain/events.py src/trading_os/persistence/postgres_event_store.py alembic/versions/20260721_0002_ontology_release.py tests/fixtures/ontology tests/unit/semantic/test_ontology_release.py tests/unit/semantic/test_ontology_compatibility.py tests/integration/semantic/test_ontology_registry.py
git commit -m "feat: publish immutable ontology releases"
```

### Task 2: Model identity, availability time, evidence, and epistemic state

**Files:**
- Create: `src/trading_os/semantic/models/identity.py`
- Create: `src/trading_os/semantic/models/iri.py`
- Create: `src/trading_os/semantic/models/time.py`
- Create: `src/trading_os/semantic/models/evidence.py`
- Create: `src/trading_os/semantic/models/licensing.py`
- Create: `tests/unit/semantic/test_identity_models.py`
- Create: `tests/unit/semantic/test_evidence_models.py`

**Interfaces:**
- Consumes: `OntologyReleaseId` from Task 1 and UUID value-object convention from Trading OS Task 2.
- Produces: typed `LegalEntityId`, `IssuerRoleId`, `SecurityId`, `ListingId`, `VenueId`,
  `TickerAliasId`, `CanonicalIdentityKey`, `IdentityCrosswalk`, `TemporalAlias`, validating
  `CanonicalIriEncoder`, `SourceRecord`, `EvidenceSpan`, typed-numeric `Observation`, `Claim`,
  `AdmissionState`, `AdmissionDecision`, `LicencePolicy`, `AvailabilityState`, and
  `AvailabilityWindow`.

- [ ] **Step 1: Write strict identity and temporal tests**

```python
# tests/unit/semantic/test_identity_models.py
import pytest
from pydantic import ValidationError

from trading_os.semantic.models.identity import ListingIdentity, SecurityId
from trading_os.semantic.models.iri import CanonicalIriEncoder


def test_ticker_requires_a_validity_interval() -> None:
    with pytest.raises(ValidationError):
        ListingIdentity.model_validate({"security_id": str(SecurityId.new()), "ticker": "INFY"})


def test_same_ticker_can_exist_on_two_venues_without_overwrite(alias_registry) -> None:
    candidates = alias_registry.resolve("ABC", at=DECISION_CUTOFF)
    assert {candidate.venue_id.value for candidate in candidates} == {"XNSE", "XBOM"}


def test_canonical_iri_encoder_rejects_untyped_or_malformed_ids() -> None:
    with pytest.raises(ValueError):
        CanonicalIriEncoder().encode_untyped("../../not-an-id")
```

```python
# tests/unit/semantic/test_evidence_models.py
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from trading_os.semantic.models.licensing import LicencePolicy, PermittedTransformation
from trading_os.semantic.models.time import AvailabilityState, AvailabilityWindow


def test_received_time_cannot_precede_publication() -> None:
    with pytest.raises(ValidationError):
        AvailabilityWindow(
            state=AvailabilityState.KNOWN,
            published_at=datetime(2026, 7, 21, 12, tzinfo=UTC),
            received_at=datetime(2026, 7, 21, 11, tzinfo=UTC),
            recorded_at=datetime(2026, 7, 21, 13, tzinfo=UTC),
        )


def test_advance_announcement_may_precede_occurrence() -> None:
    window = AvailabilityWindow(
        state=AvailabilityState.KNOWN,
        occurred_at=datetime(2026, 8, 1, tzinfo=UTC),
        published_at=datetime(2026, 7, 21, 12, tzinfo=UTC),
        received_at=datetime(2026, 7, 21, 12, 1, tzinfo=UTC),
        recorded_at=datetime(2026, 7, 21, 12, 2, tzinfo=UTC),
    )
    assert window.occurred_at > window.published_at


def test_redistribution_requires_explicit_permission() -> None:
    with pytest.raises(ValidationError):
        LicencePolicy(
            policy_id="vendor-x-v1",
            allowed_principal_ids=frozenset({"extractor"}),
            permitted_transformations=frozenset({PermittedTransformation.EXTRACT_FACTS}),
            retain_until=None,
            redistribution_allowed=True,
        )
```

- [ ] **Step 2: Run tests and confirm the semantic models are absent**

Run: `uv run pytest tests/unit/semantic/test_identity_models.py tests/unit/semantic/test_evidence_models.py -v`

Expected: FAIL during collection on missing `trading_os.semantic.models`.

- [ ] **Step 3: Implement closed, immutable models**

```python
# src/trading_os/semantic/models/identity.py
from datetime import datetime
from enum import StrEnum
from typing import Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, RootModel, model_validator


class UUIDIdentity(RootModel[UUID]):
    model_config = ConfigDict(frozen=True)

    @classmethod
    def new(cls) -> Self:
        return cls(uuid4())


class LegalEntityId(UUIDIdentity):
    pass


class IssuerRoleId(UUIDIdentity):
    pass


class SecurityId(UUIDIdentity):
    pass


class ListingId(UUIDIdentity):
    pass


class VenueId(RootModel[str]):
    model_config = ConfigDict(frozen=True)


class TickerAliasId(UUIDIdentity):
    pass


class EntityKind(StrEnum):
    LEGAL_ENTITY = "legal_entity"
    ISSUER_ROLE = "issuer_role"
    SECURITY = "security"
    LISTING = "listing"
    VENUE = "venue"
    TICKER_ALIAS = "ticker_alias"


class CanonicalIdentityKey(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    entity_kind: EntityKind
    canonical_id: str


class ListingIdentity(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    listing_id: ListingId
    security_id: SecurityId
    venue_id: VenueId
    ticker_alias_id: TickerAliasId
    normalized_ticker: str
    valid_from: datetime
    valid_to: datetime | None = None

    @model_validator(mode="after")
    def nonempty_interval(self) -> "ListingIdentity":
        if self.valid_to is not None and self.valid_from >= self.valid_to:
            raise ValueError("listing validity must be half-open and non-empty")
        return self
```

`IdentityCrosswalk` and `TemporalAlias` are append-only many-to-many records. Each crosswalk types
both endpoint kinds and records source authority, evidence IDs, review state, and a validity
interval. Each alias records alias kind, normalized value, optional venue, and a half-open validity
interval. Resolution returns a tuple of candidates and never stores aliases in a value-keyed dict.

```python
# src/trading_os/semantic/models/iri.py
from urllib.parse import quote

from rdflib import URIRef

from trading_os.semantic.models.identity import CanonicalIdentityKey


class CanonicalIriEncoder:
    _BASE = "urn:trading-os:entity"

    def encode(self, key: CanonicalIdentityKey) -> URIRef:
        value = key.canonical_id.strip()
        if not value or value != key.canonical_id or any(c in value for c in ("/", "#", "..")):
            raise ValueError("canonical ID is not valid for IRI encoding")
        return URIRef(f"{self._BASE}:{key.entity_kind.value}:{quote(value, safe='')}")

    def canonical_string(self, key: CanonicalIdentityKey) -> str:
        self.encode(key)
        return f"{key.entity_kind.value}:{key.canonical_id}"
```

```python
# src/trading_os/semantic/models/time.py
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, model_validator


class AvailabilityState(StrEnum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    INCONSISTENT = "inconsistent"


class AvailabilityWindow(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    state: AvailabilityState
    occurred_at: datetime | None = None
    published_at: datetime | None = None
    received_at: datetime | None = None
    recorded_at: datetime
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    superseded_at: datetime | None = None

    @model_validator(mode="after")
    def ordered(self) -> "AvailabilityWindow":
        if self.state is AvailabilityState.KNOWN:
            if self.published_at is None or self.received_at is None:
                raise ValueError("known availability requires publication and receipt times")
            if not self.published_at <= self.received_at <= self.recorded_at:
                raise ValueError("publication, receipt, and record times must be ordered")
        if self.valid_from and self.valid_to and self.valid_from >= self.valid_to:
            raise ValueError("valid interval must be half-open and non-empty")
        return self
```

```python
# src/trading_os/semantic/models/evidence.py
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, model_validator

from trading_os.semantic.models.time import AvailabilityWindow


class AdmissionState(StrEnum):
    PROPOSED = "proposed"
    ADMITTED = "admitted"
    CONTESTED = "contested"
    REFUTED = "refuted"
    DEPRECATED = "deprecated"
    REJECTED = "rejected"


class SourceRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    source_record_id: UUID
    publisher_id: str
    content_hash: str
    media_type: str
    availability: AvailabilityWindow
    licence_policy_id: str


class EvidenceSpan(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    source_record_id: UUID
    start_offset: int
    end_offset: int
    span_hash: str


class Claim(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    claim_id: UUID
    subject_key: CanonicalIdentityKey
    subject_type_iri: str
    predicate_iri: str
    object_key: CanonicalIdentityKey
    object_type_iri: str
    evidence_spans: tuple[EvidenceSpan, ...]
    supersedes_claim_id: UUID | None = None
    contradicts_claim_ids: tuple[UUID, ...] = ()
    state: AdmissionState = AdmissionState.PROPOSED
    availability: AvailabilityWindow


class Observation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    observation_id: UUID
    target_id: str
    method_id: str
    method_version: str
    unit_iri: str
    numeric_value: Decimal
    availability: AvailabilityWindow


class AdmissionDecision(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    decision_id: UUID
    claim_id: UUID
    state: AdmissionState
    reason: str
    independent_source_count: int
    decided_by: str
    decided_at: datetime

    @classmethod
    def rejected(cls, claim_id: UUID, *, reason: str, decided_by: str, decided_at: datetime) -> "AdmissionDecision":
        return cls(
            decision_id=uuid4(),
            claim_id=claim_id,
            state=AdmissionState.REJECTED,
            reason=reason,
            independent_source_count=0,
            decided_by=decided_by,
            decided_at=decided_at,
        )
```

Parse vendor text at the ingestion boundary. `Observation.numeric_value` remains a typed `Decimal`
paired with its unit and method version; raw numeric strings never cross into reasoning packets.

```python
# src/trading_os/semantic/models/licensing.py
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, model_validator


class PermittedTransformation(StrEnum):
    EXTRACT_FACTS = "extract_facts"
    DERIVE_FEATURES = "derive_features"
    RETAIN_RAW = "retain_raw"
    REDISTRIBUTE = "redistribute"


class LicencePolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    policy_id: str
    allowed_principal_ids: frozenset[str]
    permitted_transformations: frozenset[PermittedTransformation]
    retain_until: datetime | None
    redistribution_allowed: bool

    @model_validator(mode="after")
    def redistribution_is_explicit(self) -> "LicencePolicy":
        has_permission = PermittedTransformation.REDISTRIBUTE in self.permitted_transformations
        if self.redistribution_allowed != has_permission:
            raise ValueError("redistribution flag and permission must agree")
        return self
```

- [ ] **Step 4: Verify models and forbidden extra fields**

Run: `uv run pytest tests/unit/semantic/test_identity_models.py tests/unit/semantic/test_evidence_models.py -v && uv run mypy src/trading_os/semantic/models`

Expected: all tests PASS and mypy exits 0.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/semantic/models tests/unit/semantic/test_identity_models.py tests/unit/semantic/test_evidence_models.py
git commit -m "feat: model semantic identity time and evidence"
```

### Task 3: Persist immutable sources and the append-only evidence ledger

**Files:**
- Create: `src/trading_os/ports/source_blob.py`
- Create: `src/trading_os/ports/evidence_ledger.py`
- Create: `src/trading_os/semantic/evidence/blob_store.py`
- Create: `src/trading_os/semantic/evidence/licensed_reader.py`
- Create: `src/trading_os/semantic/evidence/ledger.py`
- Create: `alembic/versions/20260721_0003_semantic_evidence.py`
- Create: `tests/unit/semantic/test_source_blob.py`
- Create: `tests/unit/semantic/test_licensed_source_reader.py`
- Create: `tests/integration/semantic/test_evidence_ledger.py`

**Interfaces:**
- Consumes: Task 2 evidence models and SQLAlchemy session factory from Trading OS Task 7.
- Produces: `SourceBlobPort.put/get`, `LicensedSourceReader.read(request)`,
  `EvidenceLedgerPort.append_claim`, `append_admission`, `append_extraction_activity`,
  `append_source_origin_membership`, `origin_clusters_for_claim`, `claims_as_of`, and
  content-addressed filesystem/Postgres adapters.

- [ ] **Step 1: Write immutability and as-of tests**

```python
# tests/unit/semantic/test_source_blob.py
import pytest

from trading_os.semantic.evidence.blob_store import ContentHashMismatch, FileSourceBlobStore


async def test_blob_key_is_content_hash(tmp_path) -> None:
    store = FileSourceBlobStore(tmp_path)
    blob_id = await store.put(b"source text")
    assert await store.get(blob_id) == b"source text"


async def test_declared_hash_must_match(tmp_path) -> None:
    store = FileSourceBlobStore(tmp_path)
    with pytest.raises(ContentHashMismatch):
        await store.put(b"source text", expected_hash="0" * 64)
```

```python
# tests/unit/semantic/test_licensed_source_reader.py
from datetime import UTC, datetime

import pytest

from trading_os.semantic.evidence.licensed_reader import LicenceDenied, SourceUseRequest
from trading_os.semantic.models.licensing import PermittedTransformation


async def test_unlicensed_transformation_is_denied(licensed_reader, restricted_blob_id) -> None:
    request = SourceUseRequest(
        content_hash=restricted_blob_id,
        licence_policy_id="restricted-v1",
        principal_id="experiment-runner",
        transformation=PermittedTransformation.REDISTRIBUTE,
        requested_at=datetime(2026, 7, 21, tzinfo=UTC),
    )
    with pytest.raises(LicenceDenied):
        await licensed_reader.read(request)
```

```python
# tests/integration/semantic/test_evidence_ledger.py
async def test_correction_appends_and_preserves_historical_view(evidence_ledger, original_claim, correction) -> None:
    await evidence_ledger.append_claim(original_claim)
    await evidence_ledger.append_claim(correction)
    before = await evidence_ledger.claims_as_of(original_claim.availability.recorded_at)
    after = await evidence_ledger.claims_as_of(correction.availability.recorded_at)
    assert [item.claim_id for item in before] == [original_claim.claim_id]
    assert correction.claim_id in {item.claim_id for item in after}


async def test_syndicated_sources_share_one_persisted_origin_cluster(
    evidence_ledger,
    syndicated_claim,
) -> None:
    clusters = await evidence_ledger.origin_clusters_for_claim(syndicated_claim.claim_id)
    assert clusters == (syndicated_claim.shared_origin_cluster_id,)
```

- [ ] **Step 2: Run tests and observe missing ports/adapters**

Run: `uv run pytest tests/unit/semantic/test_source_blob.py tests/unit/semantic/test_licensed_source_reader.py -v`

Expected: FAIL on missing `source_blob` and `blob_store` modules.

- [ ] **Step 3: Implement content addressing and insert-only tables**

```python
# src/trading_os/ports/source_blob.py
from typing import Protocol


class SourceBlobPort(Protocol):
    async def put(self, content: bytes, expected_hash: str | None = None) -> str: ...
    async def get(self, content_hash: str) -> bytes: ...
```

```python
# src/trading_os/ports/evidence_ledger.py
from datetime import datetime
from typing import Protocol

from trading_os.semantic.models.evidence import AdmissionDecision, Claim, SourceRecord


class EvidenceLedgerPort(Protocol):
    async def append_source(self, source: SourceRecord) -> None: ...
    async def append_claim(self, claim: Claim) -> None: ...
    async def append_admission(self, decision: AdmissionDecision) -> None: ...
    async def append_extraction_activity(self, activity: ExtractionActivity) -> None: ...
    async def append_source_origin_membership(self, membership: SourceOriginMembership) -> None: ...
    async def origin_clusters_for_claim(self, claim_id: UUID) -> tuple[str, ...]: ...
    async def claims_as_of(self, cutoff: datetime) -> tuple[Claim, ...]: ...
    async def admitted_claims_as_of(self, cutoff: datetime) -> tuple[Claim, ...]: ...
```

```python
# src/trading_os/semantic/evidence/blob_store.py
import hashlib
import re
from pathlib import Path


class ContentHashMismatch(ValueError):
    pass


class FileSourceBlobStore:
    def __init__(self, root: Path) -> None:
        self._root = root

    async def put(self, content: bytes, expected_hash: str | None = None) -> str:
        digest = hashlib.sha256(content).hexdigest()
        if expected_hash is not None and (
            re.fullmatch(r"[0-9a-f]{64}", expected_hash) is None or expected_hash != digest
        ):
            raise ContentHashMismatch(digest)
        path = self._root / digest[:2] / digest[2:]
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(content)
        return digest

    async def get(self, content_hash: str) -> bytes:
        if re.fullmatch(r"[0-9a-f]{64}", content_hash) is None:
            raise ContentHashMismatch(content_hash)
        return (self._root / content_hash[:2] / content_hash[2:]).read_bytes()
```

```python
# src/trading_os/semantic/evidence/licensed_reader.py
from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from trading_os.ports.source_blob import SourceBlobPort
from trading_os.semantic.models.licensing import LicencePolicy, PermittedTransformation


class LicenceDenied(PermissionError):
    pass


class SourceUseRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    content_hash: str
    licence_policy_id: str
    principal_id: str
    transformation: PermittedTransformation
    requested_at: datetime


class LicencePolicyPort(Protocol):
    async def get_exact(self, policy_id: str) -> LicencePolicy: ...


class LicensedSourceReader:
    def __init__(self, blobs: SourceBlobPort, policies: LicencePolicyPort) -> None:
        self._blobs = blobs
        self._policies = policies

    async def read(self, request: SourceUseRequest) -> bytes:
        policy = await self._policies.get_exact(request.licence_policy_id)
        if request.principal_id not in policy.allowed_principal_ids:
            raise LicenceDenied("principal is not allowed")
        if request.transformation not in policy.permitted_transformations:
            raise LicenceDenied("transformation is not allowed")
        if policy.retain_until is not None and request.requested_at > policy.retain_until:
            raise LicenceDenied("retention period has expired")
        return await self._blobs.get(request.content_hash)
```

Migration `20260721_0003_semantic_evidence.py` declares `revision = "20260721_0003"` and
`down_revision = "20260721_0002"`, then creates insert-only `source_record`, `observation`, `claim`,
`evidence_span`, `extraction_activity`, `source_origin_cluster`, `source_origin_membership`,
`admission_decision`, `identity_candidate`, and `supersession` tables. Add database
triggers that reject UPDATE and DELETE for these tables. Repository queries require an explicit
cutoff and resolve supersessions without deleting prior records.

```python
# src/trading_os/semantic/evidence/ledger.py
from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, DateTime, String, Uuid, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from trading_os.semantic.models.evidence import AdmissionDecision, AdmissionState, Claim, SourceRecord


class Base(DeclarativeBase):
    pass


class SourceRecordRow(Base):
    __tablename__ = "source_record"
    source_record_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON)


class ClaimRow(Base):
    __tablename__ = "claim"
    claim_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON)


class AdmissionDecisionRow(Base):
    __tablename__ = "admission_decision"
    decision_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    claim_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    state: Mapped[str] = mapped_column(String)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON)


class PostgresEvidenceLedger:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def append_source(self, source: SourceRecord) -> None:
        async with self._sessions.begin() as session:
            await session.execute(
                insert(SourceRecordRow).values(
                    source_record_id=source.source_record_id,
                    received_at=source.availability.received_at,
                    recorded_at=source.availability.recorded_at,
                    payload=source.model_dump(mode="json"),
                )
            )

    async def append_claim(self, claim: Claim) -> None:
        async with self._sessions.begin() as session:
            await session.execute(
                insert(ClaimRow).values(
                    claim_id=claim.claim_id,
                    received_at=claim.availability.received_at,
                    recorded_at=claim.availability.recorded_at,
                    payload=claim.model_dump(mode="json"),
                )
            )

    async def append_admission(self, decision: AdmissionDecision) -> None:
        async with self._sessions.begin() as session:
            await session.execute(
                insert(AdmissionDecisionRow).values(
                    decision_id=decision.decision_id,
                    claim_id=decision.claim_id,
                    state=decision.state.value,
                    decided_at=decision.decided_at,
                    payload=decision.model_dump(mode="json"),
                )
            )

    async def claims_as_of(self, cutoff: datetime) -> tuple[Claim, ...]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(ClaimRow)
                    .where(ClaimRow.received_at <= cutoff, ClaimRow.recorded_at <= cutoff)
                    .order_by(ClaimRow.claim_id)
                )
            ).all()
        return tuple(Claim.model_validate(row.payload) for row in rows)

    async def admitted_claims_as_of(self, cutoff: datetime) -> tuple[Claim, ...]:
        claims = await self.claims_as_of(cutoff)
        states = await self._admission_states_as_of(cutoff)
        admitted = tuple(claim for claim in claims if claim.claim_id in states)
        superseded_ids = frozenset(
            claim.supersedes_claim_id
            for claim in admitted
            if claim.supersedes_claim_id is not None
        )
        return tuple(
            claim.model_copy(update={"state": states[claim.claim_id]})
            for claim in admitted
            if claim.claim_id not in superseded_ids
        )

    async def _admission_states_as_of(self, cutoff: datetime) -> dict[UUID, AdmissionState]:
        ranked = (
            select(
                AdmissionDecisionRow.claim_id,
                AdmissionDecisionRow.state,
                func.row_number()
                .over(
                    partition_by=AdmissionDecisionRow.claim_id,
                    order_by=(
                        AdmissionDecisionRow.decided_at.desc(),
                        AdmissionDecisionRow.decision_id.desc(),
                    ),
                )
                .label("rank"),
            )
            .where(AdmissionDecisionRow.decided_at <= cutoff)
            .subquery()
        )
        async with self._sessions() as session:
            rows = await session.execute(
                select(ranked.c.claim_id, ranked.c.state).where(
                    ranked.c.rank == 1,
                    ranked.c.state.in_((AdmissionState.ADMITTED.value, AdmissionState.CONTESTED.value)),
                )
            )
        return {claim_id: AdmissionState(state) for claim_id, state in rows}
```

- [ ] **Step 4: Verify unit and Postgres integration behavior**

Run: `uv run pytest tests/unit/semantic/test_source_blob.py tests/unit/semantic/test_licensed_source_reader.py -v`

Run: `uv run pytest tests/integration/semantic/test_evidence_ledger.py -v -m integration`

Expected: all tests PASS, including rejected UPDATE/DELETE integration fixtures.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/ports src/trading_os/semantic/evidence alembic/versions/20260721_0003_semantic_evidence.py tests/unit/semantic/test_source_blob.py tests/unit/semantic/test_licensed_source_reader.py tests/integration/semantic/test_evidence_ledger.py
git commit -m "feat: persist immutable semantic evidence"
```

### Task 4: Build the permanent relational retrieval champion

**Files:**
- Create: `src/trading_os/semantic/retrieval/models.py`
- Create: `src/trading_os/semantic/retrieval/relational.py`
- Create: `ontology/queries/competency/identity-exposure.yaml`
- Create: `tests/unit/semantic/test_relational_champion.py`
- Create: `tests/fixtures/semantic/competency_cases.json`

**Interfaces:**
- Consumes: `EvidenceLedgerPort`, explicit cutoff, and canonical entity IDs.
- Produces: `CompetencyQuestion`, `EvidenceAnswer`, and `RelationalRetrieval.answer(question)`; the cutoff is mandatory inside `CompetencyQuestion`.

- [ ] **Step 1: Write baseline independence and abstention tests**

```python
# tests/unit/semantic/test_relational_champion.py
import inspect

from trading_os.semantic.retrieval.relational import RelationalRetrieval


def test_relational_champion_has_no_graph_or_llm_dependencies() -> None:
    parameters = set(inspect.signature(RelationalRetrieval).parameters)
    assert parameters.isdisjoint({"rdf", "neo4j", "llm", "ontology_reasoner"})


async def test_missing_required_fact_returns_unknown(relational_retrieval, missing_fact_question) -> None:
    answer = await relational_retrieval.answer(missing_fact_question)
    assert answer.status == "unknown"
    assert answer.missingness == ("required_relationship",)
```

- [ ] **Step 2: Run and confirm retrieval modules are absent**

Run: `uv run pytest tests/unit/semantic/test_relational_champion.py -v`

Expected: FAIL on missing retrieval modules.

- [ ] **Step 3: Implement typed competency questions and bounded SQL joins**

```python
# src/trading_os/semantic/retrieval/models.py
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class AnswerStatus(StrEnum):
    ANSWERED = "answered"
    CONTESTED = "contested"
    UNKNOWN = "unknown"


class CompetencyQuestion(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    question_id: str
    validated_data_snapshot_id: str
    semantic_snapshot_id: str
    ontology_release_id: str
    target_ids: tuple[str, ...]
    decision_cutoff: datetime
    maximum_depth: int
    allowed_predicates: tuple[str, ...]


class EvidencePath(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    result_id: str
    assertion_ids: tuple[str, ...]
    motif_id: str
    depth: int


class EvidenceAnswer(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    status: AnswerStatus
    result_ids: tuple[str, ...]
    assertion_ids: tuple[str, ...]
    contradiction_ids: tuple[str, ...]
    missingness: tuple[str, ...]
    provenance_ids: tuple[str, ...]
    paths: tuple[EvidencePath, ...]
    template_id: str
    template_version: str
    semantic_snapshot_id: str
    decision_cutoff: datetime
    retrieval_path: str
    degraded: bool
```

Implement allowlisted one- and two-hop SQL joins over admitted claims and identity records. Every
query requires `decision_cutoff`, filters `published_at` and `received_at`, returns assertion IDs,
and reports unknown rather than inferring over a missing row.

```python
# src/trading_os/semantic/retrieval/relational.py
from trading_os.semantic.models.evidence import AdmissionState, Claim


class RelationalRetrieval:
    def __init__(self, ledger: EvidenceLedgerPort) -> None:
        self._ledger = ledger

    async def answer(self, question: CompetencyQuestion) -> EvidenceAnswer:
        cutoff = question.decision_cutoff
        claims = await self._ledger.admitted_claims_as_of(cutoff)
        allowed = tuple(claim for claim in claims if claim.predicate_iri in question.allowed_predicates)
        paths = bounded_relational_paths(allowed, question.target_ids, question.maximum_depth)
        if not paths:
            return EvidenceAnswer(
                status=AnswerStatus.UNKNOWN,
                result_ids=(),
                assertion_ids=(),
                contradiction_ids=(),
                missingness=("required_relationship",),
                provenance_ids=(),
                paths=(),
                template_id=question.question_id,
                template_version="relational-champion-v1",
                semantic_snapshot_id=question.semantic_snapshot_id,
                decision_cutoff=question.decision_cutoff,
                retrieval_path="relational",
                degraded=False,
            )
        return answer_from_paths(question, allowed, paths)


def bounded_relational_paths(
    claims: tuple[Claim, ...],
    targets: tuple[str, ...],
    maximum_depth: int,
) -> tuple[EvidencePath, ...]:
    by_subject: dict[str, list[Claim]] = {}
    for claim in claims:
        by_subject.setdefault(iri_encoder.canonical_string(claim.subject_key), []).append(claim)
    frontier = [(target, tuple()) for target in targets]
    results: list[EvidencePath] = []
    for depth in range(1, min(maximum_depth, 2) + 1):
        next_frontier: list[tuple[str, tuple[Claim, ...]]] = []
        for node_id, path in frontier:
            for claim in sorted(by_subject.get(node_id, ()), key=lambda item: str(item.claim_id)):
                new_path = path + (claim,)
                results.append(
                    EvidencePath(
                        result_id=iri_encoder.canonical_string(claim.object_key),
                        assertion_ids=tuple(str(item.claim_id) for item in new_path),
                        motif_id="relational-direct" if depth == 1 else "relational-two-hop",
                        depth=depth,
                    )
                )
                next_frontier.append((iri_encoder.canonical_string(claim.object_key), new_path))
        frontier = next_frontier
    return tuple(results)


def answer_from_paths(
    question: CompetencyQuestion,
    claims: tuple[Claim, ...],
    paths: tuple[EvidencePath, ...],
) -> EvidenceAnswer:
    assertion_ids = tuple(sorted({item for path in paths for item in path.assertion_ids}))
    included = frozenset(assertion_ids)
    included_claims = tuple(claim for claim in claims if str(claim.claim_id) in included)
    contradiction_ids = tuple(
        sorted({str(item) for claim in included_claims for item in claim.contradicts_claim_ids})
    )
    status = (
        AnswerStatus.CONTESTED
        if contradiction_ids or any(claim.state is AdmissionState.CONTESTED for claim in included_claims)
        else AnswerStatus.ANSWERED
    )
    return EvidenceAnswer(
        status=status,
        result_ids=tuple(sorted({path.result_id for path in paths})),
        assertion_ids=assertion_ids,
        contradiction_ids=contradiction_ids,
        missingness=(),
        provenance_ids=tuple(
            sorted(
                {
                    str(span.source_record_id)
                    for claim in claims
                    if str(claim.claim_id) in included
                    for span in claim.evidence_spans
                }
            )
        ),
        paths=paths,
        template_id=question.question_id,
        template_version="relational-champion-v1",
        semantic_snapshot_id=question.semantic_snapshot_id,
        decision_cutoff=question.decision_cutoff,
        retrieval_path="relational",
        degraded=False,
    )
```

- [ ] **Step 4: Verify the champion against frozen competency cases**

Run: `uv run pytest tests/unit/semantic/test_relational_champion.py -v`

Expected: all tests PASS and every fixture has a deterministic answer hash.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/semantic/retrieval ontology/queries/competency tests/unit/semantic/test_relational_champion.py tests/fixtures/semantic/competency_cases.json
git commit -m "feat: add permanent relational reasoning champion"
```

---

## Milestone 2 — Rebuildable Semantic Projections

### Task 5: Implement the Fuseki semantic graph port and RDF projection

**Files:**
- Create: `src/trading_os/ports/semantic_graph.py`
- Create: `src/trading_os/semantic/projections/rdf.py`
- Create: `src/trading_os/semantic/projections/rdf_mapping.py`
- Create: `src/trading_os/semantic/projections/fingerprint.py`
- Create: `tests/unit/semantic/test_rdf_mapping.py`
- Create: `tests/contract/semantic/test_fuseki_graph.py`

**Interfaces:**
- Consumes: admitted Task 2/3 records, Task 1 release, and the final Task 7
  `SemanticSnapshotId` computed from `SemanticContentManifest`.
- Produces: `SemanticGraphPort`,
  `RdfProjectionBuilder.build(release, assertions, *, snapshot_id) -> ProjectionFingerprintSet`,
  and read-only `FusekiSemanticGraph`.

- [ ] **Step 1: Write deterministic mapping and read-only contract tests**

```python
# tests/unit/semantic/test_rdf_mapping.py
from trading_os.semantic.projections.rdf_mapping import claim_to_quads


def test_claim_mapping_includes_provenance_and_validity(admitted_claim, iri_encoder) -> None:
    quads = claim_to_quads(
        admitted_claim,
        graph_iri="urn:snapshot:test",
        iri_encoder=iri_encoder,
    )
    predicates = {str(predicate) for _, predicate, _, _ in quads}
    assert "urn:trading-os:ontology#assertionId" in predicates
    assert "http://www.w3.org/ns/prov#wasDerivedFrom" in predicates
    assert "urn:trading-os:ontology#receivedAt" in predicates


def test_raw_source_content_is_never_projected(admitted_claim, iri_encoder) -> None:
    serialized = "\n".join(
        map(
            str,
            claim_to_quads(
                admitted_claim,
                graph_iri="urn:snapshot:test",
                iri_encoder=iri_encoder,
            ),
        )
    )
    assert "ignore all previous instructions" not in serialized
    assert admitted_claim.evidence_spans[0].span_hash not in serialized
```

```python
# tests/contract/semantic/test_fuseki_graph.py
async def test_runtime_adapter_rejects_sparql_update(fuseki_graph) -> None:
    assert not hasattr(fuseki_graph, "update")


async def test_runtime_credentials_cannot_write(runtime_fuseki_http_client, graph_store_url) -> None:
    response = await runtime_fuseki_http_client.put(graph_store_url, content=b"<s> <p> <o> .")
    assert response.status_code in {401, 403, 405}
```

- [ ] **Step 2: Run and observe missing semantic graph modules**

Run: `uv run pytest tests/unit/semantic/test_rdf_mapping.py -v`

Expected: FAIL on missing `semantic_graph` and RDF projection modules.

- [ ] **Step 3: Implement canonical quads and bounded query access**

```python
# src/trading_os/ports/semantic_graph.py
from typing import Protocol

from trading_os.semantic.retrieval.models import EvidenceAnswer


class SemanticGraphPort(Protocol):
    async def select_assertion_ids(self, *, graph_iri: str) -> frozenset[str]: ...
    async def select_projection_fingerprints(self, *, graph_iri: str) -> frozenset[str]: ...
    async def execute_template(self, *, template_text: str, parameters: dict[str, object]) -> EvidenceAnswer: ...
```

`RdfProjectionBuilder` maps each admitted assertion to stable IRIs and a named graph, emits
PROV-O-aligned derivation triples, time predicates, admission state, and source IDs, sorts canonical
N-Triples for that explicitly bound named graph, and computes the graph-IRI-plus-content hash before
upload through a build-only Graph Store client. The runtime
adapter exposes SPARQL SELECT through reviewed templates only and has no update method.

```python
# src/trading_os/semantic/projections/fingerprint.py
import hashlib
from datetime import datetime


def projection_fingerprint(
    *,
    assertion_id: str,
    subject_id: str,
    subject_type_iri: str,
    predicate_iri: str,
    object_id: str,
    object_type_iri: str,
    admission_state: str,
    received_at: datetime,
    valid_from: datetime | None,
    valid_to: datetime | None,
) -> str:
    fields = (
        assertion_id,
        subject_id,
        subject_type_iri,
        predicate_iri,
        object_id,
        object_type_iri,
        admission_state,
        received_at.isoformat(),
        valid_from.isoformat() if valid_from is not None else "",
        valid_to.isoformat() if valid_to is not None else "",
    )
    return hashlib.sha256("\x1f".join(fields).encode()).hexdigest()
```

```python
# src/trading_os/semantic/projections/rdf_mapping.py
from rdflib import Literal, URIRef
from rdflib.namespace import PROV, RDF, XSD


def claim_to_quads(
    claim: Claim,
    *,
    graph_iri: str,
    iri_encoder: CanonicalIriEncoder,
) -> tuple[tuple[URIRef, URIRef, object, URIRef], ...]:
    assertion = URIRef(f"urn:assertion:{claim.claim_id}")
    graph = URIRef(graph_iri)
    base = (
        (assertion, RDF.type, URIRef("urn:trading-os:ontology#AdmittedAssertion"), graph),
        (assertion, URIRef("urn:trading-os:ontology#assertionId"), Literal(str(claim.claim_id)), graph),
        (assertion, URIRef("urn:trading-os:ontology#subject"), iri_encoder.encode(claim.subject_key), graph),
        (assertion, URIRef("urn:trading-os:ontology#subjectType"), URIRef(claim.subject_type_iri), graph),
        (assertion, URIRef("urn:trading-os:ontology#predicate"), URIRef(claim.predicate_iri), graph),
        (assertion, URIRef("urn:trading-os:ontology#object"), iri_encoder.encode(claim.object_key), graph),
        (assertion, URIRef("urn:trading-os:ontology#objectType"), URIRef(claim.object_type_iri), graph),
        (assertion, URIRef("urn:trading-os:ontology#admissionState"), Literal(claim.state.value), graph),
        (assertion, URIRef("urn:trading-os:ontology#receivedAt"), Literal(claim.availability.received_at, datatype=XSD.dateTime), graph),
    )
    provenance = tuple(
        (
            assertion,
            PROV.wasDerivedFrom,
            URIRef(f"urn:source:{span.source_record_id}"),
            graph,
        )
        for span in claim.evidence_spans
    )
    validity = tuple(
        item
        for item in (
            (
                assertion,
                URIRef("urn:trading-os:ontology#validFrom"),
                Literal(claim.availability.valid_from, datatype=XSD.dateTime),
                graph,
            )
            if claim.availability.valid_from is not None
            else None,
            (
                assertion,
                URIRef("urn:trading-os:ontology#validTo"),
                Literal(claim.availability.valid_to, datatype=XSD.dateTime),
                graph,
            )
            if claim.availability.valid_to is not None
            else None,
        )
        if item is not None
    )
    return base + provenance + validity
```

```python
# src/trading_os/semantic/projections/rdf.py
import hashlib
from datetime import datetime
from typing import Protocol

import httpx
from rdflib import Graph, URIRef

from trading_os.semantic.projections.fingerprint import projection_fingerprint


class RdfBuildPort(Protocol):
    async def replace_named_graph(self, graph_iri: str, ntriples: bytes) -> None: ...


class SparqlBindingRenderer(Protocol):
    def bind(self, template_text: str, parameters: dict[str, object]) -> str: ...


class SparqlAnswerDecoder(Protocol):
    def decode(self, payload: dict[str, object]) -> EvidenceAnswer: ...


class RdfProjectionBuilder:
    def __init__(self, build_client: RdfBuildPort) -> None:
        self._build_client = build_client

    async def build(
        self,
        release: OntologyRelease,
        assertions: tuple[Claim, ...],
        *,
        snapshot_id: SemanticSnapshotId,
    ) -> str:
        graph_iri = f"urn:trading-os:semantic-snapshot:{snapshot_id.value}"
        graph = Graph()
        for claim in sorted(assertions, key=lambda item: str(item.claim_id)):
            for subject, predicate, object_, _ in claim_to_quads(
                claim,
                graph_iri=graph_iri,
                iri_encoder=self._iri_encoder,
            ):
                graph.add((subject, predicate, object_))
        release_subject = URIRef(f"urn:ontology-release:{release.release_id.value}")
        graph.add(
            (
                URIRef(graph_iri),
                URIRef("urn:trading-os:ontology#builtFromOntologyRelease"),
                release_subject,
            )
        )
        lines = sorted(graph.serialize(format="nt", encoding="utf-8").splitlines())
        canonical_graph = b"\n".join(lines) + b"\n"
        await self._build_client.replace_named_graph(graph_iri, canonical_graph)
        return hashlib.sha256(graph_iri.encode() + b"\n" + canonical_graph).hexdigest()


class FusekiBuildClient:
    def __init__(self, client: httpx.AsyncClient, graph_store_url: str) -> None:
        self._client = client
        self._graph_store_url = graph_store_url

    async def replace_named_graph(self, graph_iri: str, ntriples: bytes) -> None:
        response = await self._client.put(
            self._graph_store_url,
            params={"graph": graph_iri},
            content=ntriples,
            headers={"Content-Type": "application/n-triples"},
        )
        response.raise_for_status()


class FusekiSemanticGraph:
    def __init__(
        self,
        client: httpx.AsyncClient,
        query_url: str,
        renderer: SparqlBindingRenderer,
        decoder: SparqlAnswerDecoder,
    ) -> None:
        self._client = client
        self._query_url = query_url
        self._renderer = renderer
        self._decoder = decoder

    async def select_assertion_ids(self, *, graph_iri: str) -> frozenset[str]:
        graph = URIRef(graph_iri).n3()
        query = f"SELECT ?id WHERE {{ GRAPH {graph} {{ ?assertion <urn:trading-os:ontology#assertionId> ?id }} }} ORDER BY ?id"
        response = await self._client.post(
            self._query_url,
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
        )
        response.raise_for_status()
        rows = response.json()["results"]["bindings"]
        return frozenset(row["id"]["value"] for row in rows)

    async def select_projection_fingerprints(self, *, graph_iri: str) -> frozenset[str]:
        graph = URIRef(graph_iri).n3()
        query = (
            "SELECT ?id ?subject ?subjectType ?predicate ?object ?objectType ?state "
            "?received ?validFrom ?validTo WHERE { "
            f"GRAPH {graph} {{ "
            "?assertion <urn:trading-os:ontology#assertionId> ?id ; "
            "<urn:trading-os:ontology#subject> ?subject ; <urn:trading-os:ontology#subjectType> ?subjectType ; "
            "<urn:trading-os:ontology#predicate> ?predicate ; <urn:trading-os:ontology#object> ?object ; "
            "<urn:trading-os:ontology#objectType> ?objectType ; <urn:trading-os:ontology#admissionState> ?state ; "
            "<urn:trading-os:ontology#receivedAt> ?received . "
            "OPTIONAL { ?assertion <urn:trading-os:ontology#validFrom> ?validFrom } "
            "OPTIONAL { ?assertion <urn:trading-os:ontology#validTo> ?validTo } } } ORDER BY ?id"
        )
        response = await self._client.post(
            self._query_url,
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
        )
        response.raise_for_status()
        rows = response.json()["results"]["bindings"]
        return frozenset(
            projection_fingerprint(
                assertion_id=row["id"]["value"],
                subject_id=row["subject"]["value"],
                subject_type_iri=row["subjectType"]["value"],
                predicate_iri=row["predicate"]["value"],
                object_id=row["object"]["value"],
                object_type_iri=row["objectType"]["value"],
                admission_state=row["state"]["value"],
                received_at=datetime.fromisoformat(row["received"]["value"]),
                valid_from=datetime.fromisoformat(row["validFrom"]["value"])
                if "validFrom" in row
                else None,
                valid_to=datetime.fromisoformat(row["validTo"]["value"])
                if "validTo" in row
                else None,
            )
            for row in rows
        )

    async def execute_template(
        self,
        *,
        template_text: str,
        parameters: dict[str, object],
    ) -> EvidenceAnswer:
        query = self._renderer.bind(template_text, parameters)
        response = await self._client.post(
            self._query_url,
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
        )
        response.raise_for_status()
        return self._decoder.decode(response.json())
```

- [ ] **Step 4: Verify mapping and Fuseki contract**

Run: `uv run pytest tests/unit/semantic/test_rdf_mapping.py -v`

Run: `docker compose up -d fuseki && uv run pytest tests/contract/semantic/test_fuseki_graph.py -v`

Expected: unit and contract tests PASS; the graph hash is identical across two rebuilds.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/ports/semantic_graph.py src/trading_os/semantic/projections tests/unit/semantic/test_rdf_mapping.py tests/contract/semantic/test_fuseki_graph.py
git commit -m "feat: build read-only rdf semantic projections"
```

### Task 6: Generalize Neo4j into the bounded operational projection

**Files:**
- Modify: `src/trading_os/ports/graph.py`
- Create: `src/trading_os/semantic/projections/neo4j.py`
- Create: `tests/unit/semantic/test_neo4j_mapping.py`
- Create: `tests/contract/semantic/test_neo4j_projection.py`

**Interfaces:**
- Consumes: the same release/assertion batch and final precomputed `SemanticSnapshotId` as Task 5.
- Produces: `Neo4jProjectionBuilder.build(snapshot_id: str, rows: tuple[ProjectionRelationship, ...]) -> str`, `GraphStorePort.assertion_ids(snapshot_id: str)`, `GraphStorePort.projection_fingerprints(snapshot_id: str)`, and approved motif reads through Task 9 templates.

- [ ] **Step 1: Write endpoint-type and independent-write tests**

```python
# tests/unit/semantic/test_neo4j_mapping.py
import pytest

from trading_os.semantic.projections.neo4j import ProjectionTypeError, map_relationship


def test_issuer_cannot_be_mapped_as_listing(issuer_claim) -> None:
    with pytest.raises(ProjectionTypeError):
        map_relationship(issuer_claim, expected_source_type="Listing")
```

```python
# tests/contract/semantic/test_neo4j_projection.py
async def test_runtime_graph_exposes_no_generic_write(neo4j_graph) -> None:
    assert not hasattr(neo4j_graph, "execute_write")


async def test_runtime_credentials_are_denied_cypher_writes(runtime_neo4j_driver) -> None:
    with pytest.raises(Neo4jError):
        await runtime_neo4j_driver.execute_query("CREATE (:ForbiddenRuntimeWrite)")
```

- [ ] **Step 2: Run and observe absent projection builder**

Run: `uv run pytest tests/unit/semantic/test_neo4j_mapping.py -v`

Expected: FAIL on missing `semantic.projections.neo4j`.

- [ ] **Step 3: Implement typed bulk projection and constraints**

Build canonical nodes by stable identity ID and relationships by assertion ID. Install uniqueness
constraints for identity and assertion keys. Each relationship stores `valid_from`, `valid_to`,
`received_at`, `admission_state`, `source_record_ids`, `ontology_release_id`, and
`semantic_snapshot_id`. Build through a privileged builder adapter; expose only bounded motif reads
at runtime. Keep the existing depth ≤3, relation allowlist, anti-hub, and as-of rules.

```python
# src/trading_os/semantic/projections/neo4j.py
import hashlib
from datetime import datetime

import orjson
from neo4j import AsyncDriver
from pydantic import BaseModel, ConfigDict

from trading_os.semantic.projections.fingerprint import projection_fingerprint


class ProjectionRelationship(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    assertion_id: str
    source_id: str
    source_type: str
    predicate_iri: str
    target_id: str
    target_type: str
    valid_from: datetime | None
    valid_to: datetime | None
    received_at: datetime
    admission_state: str
    source_record_ids: tuple[str, ...]
    ontology_release_id: str
    semantic_snapshot_id: str


class ProjectionClaim(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    claim: Claim
    source_type: str
    target_type: str
    source_record_ids: tuple[str, ...]
    ontology_release_id: str
    semantic_snapshot_id: str


class ProjectionTypeError(ValueError):
    pass


def map_relationship(
    value: ProjectionClaim,
    *,
    expected_source_type: str,
) -> ProjectionRelationship:
    if (
        value.source_type != expected_source_type
        or value.source_type != value.claim.subject_type_iri
        or value.target_type != value.claim.object_type_iri
    ):
        raise ProjectionTypeError(
            f"expected {expected_source_type}, received {value.source_type}"
        )
    return ProjectionRelationship(
        assertion_id=str(value.claim.claim_id),
        source_id=iri_encoder.canonical_string(value.claim.subject_key),
        source_type=value.source_type,
        predicate_iri=value.claim.predicate_iri,
        target_id=iri_encoder.canonical_string(value.claim.object_key),
        target_type=value.target_type,
        valid_from=value.claim.availability.valid_from,
        valid_to=value.claim.availability.valid_to,
        received_at=value.claim.availability.received_at,
        admission_state=value.claim.state.value,
        source_record_ids=value.source_record_ids,
        ontology_release_id=value.ontology_release_id,
        semantic_snapshot_id=value.semantic_snapshot_id,
    )


def projection_key(snapshot_id: str, assertion_id: str) -> str:
    return f"{snapshot_id}:{assertion_id}"


class Neo4jProjectionBuilder:
    def __init__(self, driver: AsyncDriver) -> None:
        self._driver = driver

    async def build(self, snapshot_id: str, rows: tuple[ProjectionRelationship, ...]) -> str:
        if any(row.semantic_snapshot_id != snapshot_id for row in rows):
            raise ProjectionTypeError("every row must carry the final semantic snapshot ID")
        payload = [
            row.model_dump(mode="python")
            | {"projection_key": projection_key(snapshot_id, row.assertion_id)}
            for row in sorted(rows, key=lambda item: item.assertion_id)
        ]
        async with self._driver.session() as session:
            await session.run(
                "UNWIND $rows AS row "
                "MERGE (s:SemanticEntity {canonical_id: row.source_id}) "
                "MERGE (o:SemanticEntity {canonical_id: row.target_id}) "
                "MERGE (s)-[r:ADMITTED_RELATION {projection_key: row.projection_key}]->(o) "
                "SET r += row",
                rows=payload,
            )
        canonical = orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)
        return hashlib.sha256(canonical).hexdigest()


class Neo4jSemanticGraph:
    def __init__(self, driver: AsyncDriver) -> None:
        self._driver = driver

    async def assertion_ids(self, snapshot_id: str) -> frozenset[str]:
        async with self._driver.session() as session:
            result = await session.run(
                "MATCH ()-[r:ADMITTED_RELATION {semantic_snapshot_id: $snapshot_id}]->() "
                "RETURN r.assertion_id AS assertion_id ORDER BY assertion_id",
                snapshot_id=snapshot_id,
            )
            return frozenset(record["assertion_id"] async for record in result)

    async def projection_fingerprints(self, snapshot_id: str) -> frozenset[str]:
        async with self._driver.session() as session:
            result = await session.run(
                "MATCH (s)-[r:ADMITTED_RELATION {semantic_snapshot_id: $snapshot_id}]->(o) "
                "RETURN r.assertion_id AS assertion_id, s.canonical_id AS subject_id, "
                "r.source_type AS subject_type_iri, r.predicate_iri AS predicate_iri, "
                "o.canonical_id AS object_id, r.target_type AS object_type_iri, "
                "r.admission_state AS admission_state, r.received_at AS received_at, "
                "r.valid_from AS valid_from, r.valid_to AS valid_to "
                "ORDER BY assertion_id",
                snapshot_id=snapshot_id,
            )
            rows = [record.data() async for record in result]
        return frozenset(
            projection_fingerprint(
                assertion_id=row["assertion_id"],
                subject_id=row["subject_id"],
                subject_type_iri=row["subject_type_iri"],
                predicate_iri=row["predicate_iri"],
                object_id=row["object_id"],
                object_type_iri=row["object_type_iri"],
                admission_state=row["admission_state"],
                received_at=row["received_at"].to_native(),
                valid_from=row["valid_from"].to_native() if row["valid_from"] is not None else None,
                valid_to=row["valid_to"].to_native() if row["valid_to"] is not None else None,
            )
            for row in rows
        )
```

- [ ] **Step 4: Verify Neo4j mapping and container contract**

Run: `uv run pytest tests/unit/semantic/test_neo4j_mapping.py -v`

Run: `docker compose up -d neo4j && uv run pytest tests/contract/semantic/test_neo4j_projection.py -v`

Expected: all tests PASS; repeated builds produce identical assertion-ID sets.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/ports/graph.py src/trading_os/semantic/projections/neo4j.py tests/unit/semantic/test_neo4j_mapping.py tests/contract/semantic/test_neo4j_projection.py
git commit -m "feat: project admitted semantics into neo4j"
```

### Task 7: Seal SemanticSnapshots and prove projection equivalence

**Files:**
- Create: `src/trading_os/semantic/models/snapshot.py`
- Create: `src/trading_os/semantic/projections/snapshot_builder.py`
- Modify: `src/trading_os/data/snapshot.py`
- Create: `tests/unit/semantic/test_semantic_snapshot.py`
- Create: `tests/integration/semantic/test_projection_equivalence.py`

**Interfaces:**
- Consumes: Task 1 release, Task 3 cutoff-scoped assertions, Tasks 5/6 projections, and `ValidatedDataSnapshotId`.
- Produces: `SemanticContentManifest`, final `SemanticSnapshotId`, logical `SemanticSnapshot`,
  immutable `SemanticProjectionReceipt`, and `SemanticSnapshotBuilder.build(request)`.

- [ ] **Step 1: Write mismatch rejection and reproducibility tests**

```python
# tests/unit/semantic/test_semantic_snapshot.py
import pytest

from trading_os.semantic.projections.snapshot_builder import ProjectionMismatch


async def test_projection_mismatch_rejects_snapshot(snapshot_builder, mismatched_graphs) -> None:
    with pytest.raises(ProjectionMismatch):
        await snapshot_builder.build(mismatched_graphs)


async def test_identical_inputs_produce_identical_snapshot_id(snapshot_builder, valid_build_request) -> None:
    assert await snapshot_builder.build(valid_build_request) == await snapshot_builder.build(valid_build_request)


async def test_final_id_is_stamped_into_both_projections(snapshot_builder, valid_build_request) -> None:
    result = await snapshot_builder.build(valid_build_request)
    assert result.snapshot.snapshot_id == result.receipt.semantic_snapshot_id
    assert result.receipt.rdf_graph_iri.endswith(result.snapshot.snapshot_id)
    assert result.receipt.neo4j_snapshot_id == result.snapshot.snapshot_id


async def test_unsealed_snapshot_is_not_queryable(snapshot_registry, logical_snapshot) -> None:
    with pytest.raises(ProjectionMismatch):
        await snapshot_registry.require_queryable(logical_snapshot.snapshot_id)
```

- [ ] **Step 2: Run and verify snapshot modules are absent**

Run: `uv run pytest tests/unit/semantic/test_semantic_snapshot.py -v`

Expected: FAIL on missing semantic snapshot modules.

- [ ] **Step 3: Implement canonical manifest and exact equivalence gate**

```python
# src/trading_os/semantic/models/snapshot.py
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class SemanticContentManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    validated_data_snapshot_id: str
    ontology_release_id: str
    decision_cutoff: datetime
    admitted_assertion_ids: tuple[str, ...]
    source_manifest_hash: str
    inference_ruleset_id: str
    builder_version: str


class SemanticSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    snapshot_id: str
    content_manifest: SemanticContentManifest
    created_at: datetime


class ProjectionSealStatus(StrEnum):
    SEALED = "sealed"
    REJECTED = "rejected"


class SemanticProjectionReceipt(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    receipt_id: str
    semantic_snapshot_id: str
    status: ProjectionSealStatus
    rdf_graph_iri: str
    neo4j_snapshot_id: str
    rdf_projection_hash: str
    neo4j_projection_hash: str
    assertion_fingerprint_hash: str
    entailment_fixture_hash: str
    validation_report_hash: str


class SemanticSnapshotBuildRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    validated_data_snapshot_id: str
    ontology_release_id: str
    decision_cutoff: datetime
    created_at: datetime
    source_manifest_hash: str
    inference_ruleset_id: str
    builder_version: str
```

`SemanticSnapshotBuilder` first reads eligible admitted assertions, canonicalizes the logical
manifest, and computes the final snapshot ID. It passes that exact ID to both projection builders.
Only after build completion does it compare assertion, endpoint/type/validity, and approved
entailment-fixture fingerprints and append a projection receipt. `ValidatedDataSnapshotManifest`
replaces its bare KG edge-set field with the exact `SemanticSnapshotId`. No `latest()` accessor is
added.

```python
# src/trading_os/semantic/projections/snapshot_builder.py
import hashlib

import orjson

from trading_os.semantic.models.snapshot import (
    ProjectionSealStatus,
    SemanticContentManifest,
    SemanticProjectionReceipt,
    SemanticSnapshot,
    SemanticSnapshotBuildRequest,
)
from trading_os.semantic.projections.fingerprint import projection_fingerprint


class ProjectionMismatch(RuntimeError):
    pass


def _sha256(payload: object) -> str:
    return hashlib.sha256(orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)).hexdigest()


class SemanticSnapshotBuilder:
    def __init__(
        self,
        ledger,
        ontology_registry,
        relationship_mapper,
        rdf_builder,
        neo4j_builder,
        rdf_reader,
        neo4j_reader,
        registry,
    ) -> None:
        self._ledger = ledger
        self._ontology_registry = ontology_registry
        self._relationship_mapper = relationship_mapper
        self._rdf_builder = rdf_builder
        self._neo4j_builder = neo4j_builder
        self._rdf_reader = rdf_reader
        self._neo4j_reader = neo4j_reader
        self._registry = registry

    async def build(self, request: SemanticSnapshotBuildRequest) -> SemanticSnapshotBuildResult:
        claims = await self._ledger.admitted_claims_as_of(request.decision_cutoff)
        ledger_ids = tuple(sorted(str(item.claim_id) for item in claims))
        ledger_id_set = frozenset(ledger_ids)
        manifest = SemanticContentManifest(
            validated_data_snapshot_id=request.validated_data_snapshot_id,
            ontology_release_id=request.ontology_release_id,
            decision_cutoff=request.decision_cutoff,
            admitted_assertion_ids=ledger_ids,
            source_manifest_hash=request.source_manifest_hash,
            inference_ruleset_id=request.inference_ruleset_id,
            builder_version=request.builder_version,
        )
        snapshot_id = _sha256(manifest.model_dump(mode="json"))
        snapshot = SemanticSnapshot(
            snapshot_id=snapshot_id,
            content_manifest=manifest,
            created_at=request.created_at,
        )
        await self._registry.append_logical(snapshot)
        release = await self._ontology_registry.get_exact(request.ontology_release_id)
        rdf_hash = await self._rdf_builder.build(release, claims, snapshot_id=snapshot_id)
        relationships = self._relationship_mapper.map_all(
            release=release,
            claims=claims,
            snapshot_id=snapshot_id,
        )
        neo4j_hash = await self._neo4j_builder.build(snapshot_id, relationships)
        ledger_fingerprints = frozenset(
            projection_fingerprint(
                assertion_id=str(item.claim_id),
                subject_id=iri_encoder.canonical_string(item.subject_key),
                subject_type_iri=item.subject_type_iri,
                predicate_iri=item.predicate_iri,
                object_id=iri_encoder.canonical_string(item.object_key),
                object_type_iri=item.object_type_iri,
                admission_state=item.state.value,
                received_at=item.availability.received_at,
                valid_from=item.availability.valid_from,
                valid_to=item.availability.valid_to,
            )
            for item in claims
        )
        graph_iri = f"urn:trading-os:semantic-snapshot:{snapshot_id}"
        rdf_ids = await self._rdf_reader.select_assertion_ids(graph_iri=graph_iri)
        graph_ids = await self._neo4j_reader.assertion_ids(snapshot_id=snapshot_id)
        rdf_fingerprints = await self._rdf_reader.select_projection_fingerprints(graph_iri=graph_iri)
        graph_fingerprints = await self._neo4j_reader.projection_fingerprints(snapshot_id=snapshot_id)
        if (
            ledger_id_set != rdf_ids
            or ledger_id_set != graph_ids
            or ledger_fingerprints != rdf_fingerprints
            or ledger_fingerprints != graph_fingerprints
        ):
            raise ProjectionMismatch(
                {
                    "ledger_ids": ledger_ids,
                    "rdf_ids": rdf_ids,
                    "neo4j_ids": graph_ids,
                    "ledger_fingerprints": ledger_fingerprints,
                    "rdf_fingerprints": rdf_fingerprints,
                    "neo4j_fingerprints": graph_fingerprints,
                }
            )
        entailment_hash = await compare_approved_entailment_fixtures(
            snapshot_id=snapshot_id,
            rdf=self._rdf_reader,
            graph=self._neo4j_reader,
        )
        receipt_payload = {
            "semantic_snapshot_id": snapshot_id,
            "rdf_projection_hash": rdf_hash,
            "neo4j_projection_hash": neo4j_hash,
            "assertion_fingerprint_hash": _sha256(sorted(ledger_fingerprints)),
            "entailment_fixture_hash": entailment_hash,
        }
        receipt = SemanticProjectionReceipt(
            receipt_id=_sha256(receipt_payload),
            status=ProjectionSealStatus.SEALED,
            rdf_graph_iri=graph_iri,
            neo4j_snapshot_id=snapshot_id,
            validation_report_hash=_sha256({"equivalent": True}),
            **receipt_payload,
        )
        await self._registry.append_receipt(receipt)
        return SemanticSnapshotBuildResult(snapshot=snapshot, receipt=receipt)
```

- [ ] **Step 4: Verify unit and three-store integration equivalence**

Run: `uv run pytest tests/unit/semantic/test_semantic_snapshot.py -v`

Run: `uv run pytest tests/integration/semantic/test_projection_equivalence.py -v -m integration`

Expected: all tests PASS; planted missing/extra assertions fail snapshot sealing.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/semantic/models/snapshot.py src/trading_os/semantic/projections/snapshot_builder.py src/trading_os/data/snapshot.py tests/unit/semantic/test_semantic_snapshot.py tests/integration/semantic/test_projection_equivalence.py
git commit -m "feat: seal equivalent semantic snapshots"
```

---

## Milestone 3 — Governed Knowledge and Multi-domain Beliefs

### Task 8: Resolve identity candidates and admit claims safely

**Files:**
- Create: `src/trading_os/semantic/evidence/identity_resolver.py`
- Create: `src/trading_os/semantic/evidence/admission.py`
- Create: `config/semantic/admission.yaml`
- Create: `tests/unit/semantic/test_identity_resolution.py`
- Create: `tests/unit/semantic/test_claim_admission.py`

**Interfaces:**
- Consumes: Task 2 models, Task 3 ledger, authoritative SecurityMaster mappings, human decisions.
- Produces: `IdentityCandidate`, `IdentityResolution`, `IdentityResolver.resolve(value: IdentityInput) -> IdentityResolution`, and `AdmissionPolicy.evaluate(proposal: ClaimProposal, *, cutoff: datetime) -> AdmissionDecision`.

- [ ] **Step 1: Write false-merge, syndication, and future-fact tests**

```python
# tests/unit/semantic/test_identity_resolution.py
def test_fuzzy_name_match_never_auto_merges(identity_resolver, fuzzy_only_record) -> None:
    result = identity_resolver.resolve(fuzzy_only_record)
    assert result.canonical_key is None
    assert result.candidates
    assert result.requires_human_review is True
```

```python
# tests/unit/semantic/test_claim_admission.py
async def test_syndicated_sources_count_as_one_origin(admission_policy, syndicated_claim) -> None:
    decision = await admission_policy.evaluate(syndicated_claim, cutoff=syndicated_claim.decision_cutoff)
    assert decision.independent_source_count == 1


async def test_received_after_cutoff_is_rejected(admission_policy, late_claim) -> None:
    decision = await admission_policy.evaluate(late_claim, cutoff=late_claim.decision_cutoff)
    assert decision.reason == "received_after_cutoff"
```

- [ ] **Step 2: Run and observe missing admission components**

Run: `uv run pytest tests/unit/semantic/test_identity_resolution.py tests/unit/semantic/test_claim_admission.py -v`

Expected: FAIL on missing resolver/admission modules.

- [ ] **Step 3: Implement authoritative-first identity and closed admission decisions**

Resolution order is exact canonical ID → authoritative crosswalk → normalized exact alias within
validity → candidate-only fuzzy match. Admission validates ontology endpoints, SHACL shape,
availability, evidence spans, source lineage, contradiction search, author precision, independent
corroboration, freshness, and required human approval. Decisions append; they never edit Claims.

```python
from datetime import datetime
from decimal import Decimal
from typing import Protocol
from enum import StrEnum
from typing import Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict


class IdentityCandidate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    canonical_key: CanonicalIdentityKey
    method: str
    score: Decimal


class IdentityResolution(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    canonical_key: CanonicalIdentityKey | None
    method: str
    candidates: tuple[IdentityCandidate, ...]
    requires_human_review: bool


class IdentityInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    expected_kind: EntityKind
    supplied_canonical_key: CanonicalIdentityKey | None
    crosswalk_lookup: CrosswalkLookup | None
    normalized_alias: str
    venue_id: VenueId | None
    observed_at: datetime


class FuzzyCandidatePort(Protocol):
    def find(self, value: IdentityInput) -> tuple[IdentityCandidate, ...]: ...


class CanonicalIdentityPort(Protocol):
    def exists(self, key: CanonicalIdentityKey) -> bool: ...


class IdentityCrosswalkPort(Protocol):
    def resolve(self, lookup: CrosswalkLookup, *, at: datetime) -> tuple[CanonicalIdentityKey, ...]: ...


class AliasResolutionPort(Protocol):
    def resolve(
        self,
        *,
        kind: EntityKind,
        normalized_alias: str,
        venue_id: VenueId | None,
        at: datetime,
    ) -> tuple[TemporalAlias, ...]: ...


class IdentityResolver:
    def __init__(
        self,
        canonical: CanonicalIdentityPort,
        crosswalks: IdentityCrosswalkPort,
        aliases: AliasResolutionPort,
        fuzzy_candidates: FuzzyCandidatePort,
    ) -> None:
        self._canonical = canonical
        self._crosswalks = crosswalks
        self._aliases = aliases
        self._fuzzy_candidates = fuzzy_candidates

    def resolve(self, value: IdentityInput) -> IdentityResolution:
        supplied = value.supplied_canonical_key
        if supplied is not None and supplied.entity_kind is value.expected_kind and self._canonical.exists(supplied):
            return IdentityResolution(
                canonical_key=supplied,
                method="canonical_id",
                candidates=(),
                requires_human_review=False,
            )
        if value.crosswalk_lookup is not None:
            resolved = self._crosswalks.resolve(value.crosswalk_lookup, at=value.observed_at)
        else:
            resolved = ()
        if len(resolved) == 1 and resolved[0].entity_kind is value.expected_kind:
            return IdentityResolution(
                canonical_key=resolved[0],
                method="authoritative_crosswalk",
                candidates=(),
                requires_human_review=False,
            )
        aliases = self._aliases.resolve(
            kind=value.expected_kind,
            normalized_alias=value.normalized_alias,
            venue_id=value.venue_id,
            at=value.observed_at,
        )
        if len(aliases) == 1:
            return IdentityResolution(
                canonical_key=aliases[0].canonical_key,
                method="valid_exact_alias",
                candidates=(),
                requires_human_review=False,
            )
        candidates = tuple(
            IdentityCandidate(canonical_key=item.canonical_key, method="ambiguous_exact_alias", score=Decimal("1"))
            for item in aliases
        ) or self._fuzzy_candidates.find(value)
        return IdentityResolution(
            canonical_key=None,
            method="candidate_only",
            candidates=candidates,
            requires_human_review=bool(candidates),
        )


class ClaimProposal(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    claim: Claim
    decision_cutoff: datetime
    endpoint_types_valid: bool
    shape_conforms: bool
    contradiction_ids: tuple[UUID, ...]
    author_precision: Decimal
    minimum_author_precision: Decimal
    fresh_until: datetime | None
    requires_corroboration: bool
    requires_human: bool
    human_decision: bool | None


class AdmissionReason(StrEnum):
    ADMITTED = "admitted"
    MISSING_PROVENANCE = "missing_provenance"
    RECEIVED_AFTER_CUTOFF = "received_after_cutoff"
    INVALID_ENDPOINT = "invalid_endpoint"
    INVALID_SHAPE = "invalid_shape"
    CONTRADICTION_PRESENT = "contradiction_present"
    INSUFFICIENT_CORROBORATION = "insufficient_corroboration"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    HUMAN_REJECTED = "human_rejected"
    AUTHOR_PRECISION_BELOW_BAR = "author_precision_below_bar"
    STALE = "stale"


class AdmissionPolicy:
    def __init__(self, clock: ClockPort, reviewer_id: str, ledger: EvidenceLedgerPort) -> None:
        self._clock = clock
        self._reviewer_id = reviewer_id
        self._ledger = ledger

    def _reject(self, proposal: ClaimProposal, reason: AdmissionReason) -> AdmissionDecision:
        return AdmissionDecision.rejected(
            proposal.claim.claim_id,
            reason=reason.value,
            decided_by=self._reviewer_id,
            decided_at=self._clock.now(),
        )

    async def evaluate(self, proposal: ClaimProposal, *, cutoff: datetime) -> AdmissionDecision:
        if cutoff != proposal.decision_cutoff:
            raise ValueError("admission cutoff must match the sealed proposal cutoff")
        if proposal.claim.availability.received_at > cutoff:
            return self._reject(proposal, AdmissionReason.RECEIVED_AFTER_CUTOFF)
        if not proposal.claim.evidence_spans:
            return self._reject(proposal, AdmissionReason.MISSING_PROVENANCE)
        if not proposal.endpoint_types_valid:
            return self._reject(proposal, AdmissionReason.INVALID_ENDPOINT)
        if not proposal.shape_conforms:
            return self._reject(proposal, AdmissionReason.INVALID_SHAPE)
        if proposal.author_precision < proposal.minimum_author_precision:
            return self._reject(proposal, AdmissionReason.AUTHOR_PRECISION_BELOW_BAR)
        if proposal.fresh_until is not None and proposal.fresh_until < cutoff:
            return self._reject(proposal, AdmissionReason.STALE)
        origin_clusters = await self._ledger.origin_clusters_for_claim(proposal.claim.claim_id)
        independent = len(frozenset(origin_clusters))
        if proposal.requires_corroboration and independent < 2:
            return self._reject(proposal, AdmissionReason.INSUFFICIENT_CORROBORATION)
        if proposal.requires_human and proposal.human_decision is None:
            return self._reject(proposal, AdmissionReason.HUMAN_REVIEW_REQUIRED)
        if proposal.human_decision is False:
            return self._reject(proposal, AdmissionReason.HUMAN_REJECTED)
        if proposal.contradiction_ids:
            return AdmissionDecision(
                decision_id=uuid4(),
                claim_id=proposal.claim.claim_id,
                state=AdmissionState.CONTESTED,
                reason=AdmissionReason.CONTRADICTION_PRESENT.value,
                independent_source_count=independent,
                decided_by=self._reviewer_id,
                decided_at=self._clock.now(),
            )
        return AdmissionDecision(
            decision_id=uuid4(),
            claim_id=proposal.claim.claim_id,
            state=AdmissionState.ADMITTED,
            reason=AdmissionReason.ADMITTED.value,
            independent_source_count=independent,
            decided_by=self._reviewer_id,
            decided_at=self._clock.now(),
        )
```

- [ ] **Step 4: Verify safety cases and type checks**

Run: `uv run pytest tests/unit/semantic/test_identity_resolution.py tests/unit/semantic/test_claim_admission.py -v && uv run mypy src/trading_os/semantic/evidence`

Expected: all tests PASS and no fuzzy fixture produces a canonical merge.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/semantic/evidence config/semantic/admission.yaml tests/unit/semantic/test_identity_resolution.py tests/unit/semantic/test_claim_admission.py
git commit -m "feat: govern identity and claim admission"
```

### Task 9: Add reviewed query templates and typed execution

**Files:**
- Create: `src/trading_os/semantic/retrieval/query_registry.py`
- Create: `src/trading_os/semantic/retrieval/query_service.py`
- Create: `ontology/queries/decision/instrument-evidence.yaml`
- Create: `ontology/queries/decision/instrument-evidence.sparql`
- Create: `ontology/queries/decision/instrument-evidence.cypher`
- Create: `tests/unit/semantic/test_query_registry.py`
- Create: `tests/contract/semantic/test_query_equivalence.py`

**Interfaces:**
- Consumes: Task 7 `SemanticSnapshot` plus sealed `SemanticProjectionReceipt`, Task 1
  `QueryPackRelease`, and Task 4/5/6 retrieval adapters.
- Produces: `EvidenceQuery`, `QueryTemplateRegistry`, immutable `RetrievalReceipt`, closed semantic
  query errors, and `QueryService.execute(query) -> QueryExecutionResult`.

- [ ] **Step 1: Write unrestricted-query rejection and cutoff tests**

```python
# tests/unit/semantic/test_query_registry.py
import pytest

from trading_os.semantic.retrieval.query_registry import UnknownTemplate


def test_unknown_template_is_rejected(query_registry) -> None:
    with pytest.raises(UnknownTemplate):
        query_registry.bind("agent-authored-query", {})


def test_decision_query_requires_cutoff(query_registry) -> None:
    with pytest.raises(ValueError, match="decision_cutoff"):
        query_registry.bind("instrument-evidence-v1", {"instrument_id": "sec:1"})


def test_every_binding_participates_in_cache_identity(query_factory) -> None:
    original = query_factory()
    for field in (
        "validated_data_snapshot_id",
        "semantic_snapshot_id",
        "projection_receipt_id",
        "ontology_release_id",
        "query_pack_release_id",
        "decision_cutoff",
    ):
        assert original.cache_key != query_factory(**{field: DIFFERENT[field]}).cache_key
```

- [ ] **Step 2: Run and observe missing query registry**

Run: `uv run pytest tests/unit/semantic/test_query_registry.py -v`

Expected: FAIL on missing query registry/service.

- [ ] **Step 3: Implement manifest-hashed templates and typed parameter binding**

```python
import hashlib
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ProjectionKind(StrEnum):
    RDF = "rdf"
    NEO4J = "neo4j"
    RELATIONAL = "relational"


class QueryTemplateManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    template_id: str
    version: str
    max_depth: int
    text_by_projection: dict[ProjectionKind, str]
    sha256_by_projection: dict[ProjectionKind, str]


class UnknownTemplate(KeyError):
    pass


class EvidenceQuery(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    template_id: str
    template_version: str
    validated_data_snapshot_id: str
    semantic_snapshot_id: str
    projection_receipt_id: str
    ontology_release_id: str
    query_pack_release_id: str
    target_ids: tuple[str, ...]
    horizon: str
    domain_filters: tuple[str, ...]
    relation_allowlist: tuple[str, ...]
    max_depth: int
    minimum_admission_state: str
    maximum_age_days: int
    decision_cutoff: datetime

    @property
    def cache_key(self) -> str:
        return canonical_sha256(self.model_dump(mode="json"))


class RetrievalReceipt(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    receipt_id: str
    query_hash: str
    answer_hash: str
    query_binding: SemanticQueryBinding
    template_id: str
    template_version: str
    retrieval_path: ProjectionKind
    degraded_from: ProjectionKind | None = None
    created_at: datetime
```

The registry loads only release-manifest-listed templates, verifies their hashes, validates typed
parameters, caps depth at 3 for decision templates, and delegates to relational/RDF/Neo4j adapters.
Every `EvidenceAnswer` includes assertion IDs, contradiction IDs, missingness, provenance, template
version, projection, and degraded/fallback state.

```python
# src/trading_os/semantic/retrieval/query_registry.py
class QueryTemplateRegistry:
    def __init__(self, manifests: tuple[QueryTemplateManifest, ...]) -> None:
        for manifest in manifests:
            for projection, template_text in manifest.text_by_projection.items():
                digest = hashlib.sha256(template_text.encode()).hexdigest()
                if digest != manifest.sha256_by_projection[projection]:
                    raise ValueError(f"query template hash mismatch: {manifest.template_id}:{projection}")
        self._manifests = {item.template_id: item for item in manifests}

    def bind(self, template_id: str, parameters: dict[str, object]) -> EvidenceQuery:
        manifest = self._manifests.get(template_id)
        if manifest is None:
            raise UnknownTemplate(template_id)
        query = EvidenceQuery.model_validate(
            parameters | {"template_id": manifest.template_id, "template_version": manifest.version}
        )
        if query.max_depth > min(manifest.max_depth, 3):
            raise ValueError("decision query exceeds approved maximum depth")
        return query

    def template_text(self, query: EvidenceQuery, projection: ProjectionKind) -> str:
        manifest = self._manifests[query.template_id]
        if query.template_version != manifest.version:
            raise ValueError("query version is not in the active manifest")
        return manifest.text_by_projection[projection]
```

```python
# src/trading_os/semantic/retrieval/query_service.py
from typing import Protocol


class TemplateExecutionPort(Protocol):
    async def execute_template(
        self,
        *,
        template_text: str,
        parameters: dict[str, object],
    ) -> EvidenceAnswer: ...


class SemanticQueryError(RuntimeError):
    pass


class SemanticProjectionUnavailable(SemanticQueryError):
    pass


class SemanticProjectionInvalid(SemanticQueryError):
    pass


class SemanticProtocolError(SemanticQueryError):
    pass


class SemanticSnapshotMismatch(SemanticQueryError):
    pass


class QueryService:
    def __init__(
        self,
        registry: QueryTemplateRegistry,
        projection: ProjectionKind,
        adapter: TemplateExecutionPort,
    ) -> None:
        self._registry = registry
        self._projection = projection
        self._adapter = adapter

    async def execute(self, query: EvidenceQuery) -> QueryExecutionResult:
        await self._receipts.require_sealed(
            snapshot_id=query.semantic_snapshot_id,
            receipt_id=query.projection_receipt_id,
        )
        text = self._registry.template_text(query, self._projection)
        try:
            answer = await self._adapter.execute_template(
                template_text=text,
                parameters=query.model_dump(mode="json"),
            )
        except (TimeoutError, httpx.TimeoutException, httpx.TransportError) as exc:
            raise SemanticProjectionUnavailable("governed query timed out") from exc
        except (httpx.HTTPStatusError, ValueError, KeyError, ValidationError) as exc:
            raise SemanticProtocolError("projection response failed governed decoding") from exc
        bound_answer = answer.model_copy(
            update={
                "template_id": query.template_id,
                "template_version": query.template_version,
                "semantic_snapshot_id": query.semantic_snapshot_id,
                "decision_cutoff": query.decision_cutoff,
                "retrieval_path": self._projection.value,
                "degraded": False,
            }
        )
        if bound_answer.semantic_snapshot_id != query.semantic_snapshot_id:
            raise SemanticSnapshotMismatch("answer snapshot does not match the bound request")
        receipt = RetrievalReceipt.seal(query=query, answer=bound_answer, path=self._projection)
        return QueryExecutionResult(answer=bound_answer, receipt=receipt)
```

Fallback is explicit template-to-template policy, not a generic exception handler. Task 15 may
retry on the relational champion only when the active query-pack manifest declares an equivalent
relational template for the exact question and normalized error class. Integrity, binding, decode,
or missing-equivalent-template errors always fail closed.

- [ ] **Step 4: Verify registry and three-path query equivalence**

Run: `uv run pytest tests/unit/semantic/test_query_registry.py -v`

Run: `uv run pytest tests/contract/semantic/test_query_equivalence.py -v`

Expected: tests PASS for answered, contested, and unknown fixtures across equivalent templates.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/semantic/retrieval ontology/queries/decision tests/unit/semantic/test_query_registry.py tests/contract/semantic/test_query_equivalence.py
git commit -m "feat: execute governed semantic query templates"
```

### Task 10: Build technical and fundamental EvidencePackets

**Files:**
- Create: `src/trading_os/semantic/packets/models.py`
- Create: `src/trading_os/semantic/packets/technical.py`
- Create: `src/trading_os/semantic/packets/fundamental.py`
- Create: `tests/unit/semantic/test_technical_packet.py`
- Create: `tests/unit/semantic/test_fundamental_packet.py`

**Interfaces:**
- Consumes: exact `ValidatedDataSnapshotId`, Task 9 evidence answers, deterministic indicator/financial repositories.
- Produces: `EvidencePacket`, `TechnicalPacketBuilder.build(snapshot: TechnicalSnapshot, *, horizon: str) -> EvidencePacket`, and `FundamentalPacketBuilder.build(snapshot: FundamentalSnapshot, *, horizon: str) -> EvidencePacket`.

- [ ] **Step 1: Write adjustment, revision, and point-in-time tests**

```python
# tests/unit/semantic/test_technical_packet.py
def test_technical_packet_records_series_and_horizon(technical_builder, split_adjusted_snapshot) -> None:
    packet = technical_builder.build(split_adjusted_snapshot, horizon="1m")
    assert packet.domain == "technical"
    assert packet.lineage["price_series"] == "split_adjusted"
    assert packet.horizon == "1m"
```

```python
# tests/unit/semantic/test_fundamental_packet.py
def test_post_cutoff_restatement_is_excluded(fundamental_builder, snapshot_with_late_restatement) -> None:
    packet = fundamental_builder.build(snapshot_with_late_restatement, horizon="3m")
    assert "late-restatement" not in packet.supporting_observation_ids
```

- [ ] **Step 2: Run and observe missing packet modules**

Run: `uv run pytest tests/unit/semantic/test_technical_packet.py tests/unit/semantic/test_fundamental_packet.py -v`

Expected: FAIL on missing packets package.

- [ ] **Step 3: Implement common packet and deterministic builders**

```python
# src/trading_os/semantic/packets/models.py
import hashlib

import orjson
from pydantic import BaseModel, ConfigDict


class PacketContext(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    instrument_id: str
    validated_data_snapshot_id: str
    semantic_snapshot_id: str
    ontology_release_id: str
    query_pack_release_id: str
    retrieval_receipt_ids: tuple[str, ...]
    supporting_observation_ids: tuple[str, ...]
    refuting_observation_ids: tuple[str, ...]
    supporting_assertion_ids: tuple[str, ...]
    refuting_assertion_ids: tuple[str, ...]
    contradiction_ids: tuple[str, ...]
    freshness_band: str
    missingness: tuple[str, ...]
    applicable_regimes: tuple[str, ...]


class EvidencePacketContent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    domain: str
    instrument_id: str
    horizon: str
    validated_data_snapshot_id: str
    semantic_snapshot_id: str
    ontology_release_id: str
    query_pack_release_id: str
    retrieval_receipt_ids: tuple[str, ...]
    supporting_observation_ids: tuple[str, ...]
    refuting_observation_ids: tuple[str, ...]
    supporting_assertion_ids: tuple[str, ...]
    refuting_assertion_ids: tuple[str, ...]
    contradiction_ids: tuple[str, ...]
    freshness_band: str
    missingness: tuple[str, ...]
    applicable_regimes: tuple[str, ...]
    deterministic_features: dict[str, Decimal]
    lineage: dict[str, str]


class EvidencePacket(EvidencePacketContent):
    packet_id: str

    @classmethod
    def seal(cls, content: EvidencePacketContent) -> "EvidencePacket":
        canonical = orjson.dumps(content.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS)
        return cls(packet_id=hashlib.sha256(canonical).hexdigest(), **content.model_dump())


def packet_content(
    context: PacketContext,
    *,
    domain: str,
    horizon: str,
    supporting_observation_ids: tuple[str, ...],
    refuting_observation_ids: tuple[str, ...],
    deterministic_features: dict[str, Decimal],
    lineage: dict[str, str],
) -> EvidencePacketContent:
    return EvidencePacketContent(
        domain=domain,
        instrument_id=context.instrument_id,
        horizon=horizon,
        validated_data_snapshot_id=context.validated_data_snapshot_id,
        semantic_snapshot_id=context.semantic_snapshot_id,
        ontology_release_id=context.ontology_release_id,
        query_pack_release_id=context.query_pack_release_id,
        retrieval_receipt_ids=context.retrieval_receipt_ids,
        supporting_observation_ids=supporting_observation_ids,
        refuting_observation_ids=refuting_observation_ids,
        supporting_assertion_ids=context.supporting_assertion_ids,
        refuting_assertion_ids=context.refuting_assertion_ids,
        contradiction_ids=context.contradiction_ids,
        freshness_band=context.freshness_band,
        missingness=context.missingness,
        applicable_regimes=context.applicable_regimes,
        deterministic_features=deterministic_features,
        lineage=lineage,
    )
```

Technical features come only from versioned deterministic indicator functions and their declared
series/timeframe. Fundamental features retain filing, period, currency, accounting basis,
publication, receipt, and restatement lineage; conservative-lag policy is applied before values
enter the packet.

```python
from decimal import Decimal
from typing import Mapping, Protocol


class TechnicalFeatureEngine(Protocol):
    def compute(self, series: PriceSeries, manifest: FeatureManifest) -> Mapping[str, Decimal]: ...


class TechnicalPacketBuilder:
    def __init__(self, engine: TechnicalFeatureEngine) -> None:
        self._engine = engine

    def build(self, snapshot: TechnicalSnapshot, *, horizon: str) -> EvidencePacket:
        features = self._engine.compute(snapshot.series, snapshot.feature_manifest)
        content = packet_content(
            snapshot.context,
            domain="technical",
            horizon=horizon,
            supporting_observation_ids=snapshot.supporting_observation_ids,
            refuting_observation_ids=snapshot.refuting_observation_ids,
            deterministic_features={key: value for key, value in sorted(features.items())},
            lineage={
                "price_series": snapshot.series_kind,
                "feature_manifest": snapshot.feature_manifest.hash,
            },
        )
        return EvidencePacket.seal(content)


def latest_non_superseded_by_metric(
    observations: tuple[FundamentalObservation, ...],
) -> tuple[FundamentalObservation, ...]:
    superseded = frozenset(
        item.supersedes_observation_id
        for item in observations
        if item.supersedes_observation_id is not None
    )
    candidates = (item for item in observations if item.observation_id not in superseded)
    latest: dict[str, FundamentalObservation] = {}
    for item in sorted(candidates, key=lambda value: (value.period_end, value.received_at, str(value.observation_id))):
        latest[item.metric_id] = item
    return tuple(latest[key] for key in sorted(latest))


class FundamentalPacketBuilder:
    def build(self, snapshot: FundamentalSnapshot, *, horizon: str) -> EvidencePacket:
        eligible = tuple(item for item in snapshot.observations if item.received_at <= snapshot.decision_cutoff)
        latest = latest_non_superseded_by_metric(eligible)
        content = packet_content(
            snapshot.context,
            domain="fundamental",
            horizon=horizon,
            supporting_observation_ids=tuple(str(item.observation_id) for item in latest),
            refuting_observation_ids=(),
            deterministic_features={item.metric_id: item.numeric_value for item in latest},
            lineage={
                "filing_ids": ",".join(sorted({item.filing_id for item in latest})),
                "accounting_basis": snapshot.accounting_basis,
                "currency": snapshot.currency,
                "restatement_policy": snapshot.restatement_policy_id,
            },
        )
        return EvidencePacket.seal(content)
```

- [ ] **Step 4: Verify packet determinism and strict types**

Run: `uv run pytest tests/unit/semantic/test_technical_packet.py tests/unit/semantic/test_fundamental_packet.py -v && uv run mypy src/trading_os/semantic/packets`

Expected: all tests PASS and two builds serialize identically.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/semantic/packets tests/unit/semantic/test_technical_packet.py tests/unit/semantic/test_fundamental_packet.py
git commit -m "feat: build technical and fundamental evidence packets"
```

### Task 11: Build sentiment, macro, relationship, and portfolio EvidencePackets

**Files:**
- Create: `src/trading_os/semantic/packets/sentiment.py`
- Create: `src/trading_os/semantic/packets/macro.py`
- Create: `src/trading_os/semantic/packets/relationships.py`
- Create: `src/trading_os/semantic/packets/portfolio.py`
- Create: `tests/unit/semantic/test_sentiment_packet.py`
- Create: `tests/unit/semantic/test_macro_packet.py`
- Create: `tests/unit/semantic/test_relationship_packet.py`
- Create: `tests/unit/semantic/test_portfolio_packet.py`

**Interfaces:**
- Consumes: Task 9 evidence answers, validated news/event data, Task 6 bounded motifs, deterministic portfolio snapshot.
- Produces: `SentimentPacketBuilder.build(cluster: NarrativeCluster, *, horizon: str)`, `MacroPacketBuilder.build(release: MacroReleaseHistory, *, decision_cutoff: datetime)`, `RelationshipPacketBuilder.build(answer: EvidenceAnswer, *, horizon: str)`, and `PortfolioPacketBuilder.build(snapshot: PortfolioSnapshot, *, horizon: str)`, all returning `EvidencePacket`.

- [ ] **Step 1: Write syndication, vintage, causality, and namespace tests**

```python
# tests/unit/semantic/test_sentiment_packet.py
def test_syndicated_articles_are_one_evidence_family(sentiment_builder, syndicated_cluster) -> None:
    packet = sentiment_builder.build(syndicated_cluster, horizon="1m")
    assert packet.deterministic_features["independent_origin_count"] == Decimal("1")
```

```python
# tests/unit/semantic/test_macro_packet.py
def test_macro_surprise_uses_available_vintage(macro_builder, revised_macro_release) -> None:
    packet = macro_builder.build(revised_macro_release, decision_cutoff=revised_macro_release.initial_cutoff)
    assert packet.lineage["vintage"] == "initial"
```

```python
# tests/unit/semantic/test_relationship_packet.py
def test_unapproved_path_is_not_causal_evidence(relationship_builder, free_walk_answer) -> None:
    packet = relationship_builder.build(free_walk_answer, horizon="1m")
    assert packet.supporting_assertion_ids == ()
    assert "no_approved_motif" in packet.missingness
```

```python
# tests/unit/semantic/test_portfolio_packet.py
def test_portfolio_context_is_internal(portfolio_builder, portfolio_snapshot) -> None:
    packet = portfolio_builder.build(portfolio_snapshot, horizon="1m")
    assert packet.lineage["namespace"] == "internal-portfolio"
```

- [ ] **Step 2: Run and observe missing domain builders**

Run: `uv run pytest tests/unit/semantic/test_sentiment_packet.py tests/unit/semantic/test_macro_packet.py tests/unit/semantic/test_relationship_packet.py tests/unit/semantic/test_portfolio_packet.py -v`

Expected: FAIL on missing builder modules.

- [ ] **Step 3: Implement four bounded builders**

Sentiment deduplicates by origin cluster and records target, speaker, language, method/model, and
classification version. Macro records release vintage, consensus, realized value, deterministic
surprise, and closed shock taxonomy. Relationships accept only admitted, as-of, depth-capped motif
paths and keep causal/exposure weights code-owned. Portfolio context reads the immutable portfolio
snapshot and emits internal exposure/constraint fields without writing external-world assertions.

```python
# Each builder module imports its domain input type plus EvidencePacket, PacketContext, and packet_content.
from datetime import datetime
from typing import Protocol


class SentimentPacketBuilder:
    def build(self, cluster: NarrativeCluster, *, horizon: str) -> EvidencePacket:
        origins = frozenset(item.origin_cluster_id for item in cluster.documents)
        content = packet_content(
            cluster.context,
            domain="sentiment",
            horizon=horizon,
            supporting_observation_ids=tuple(
                sorted(str(item.observation_id) for item in cluster.documents)
            ),
            refuting_observation_ids=(),
            deterministic_features={
                "independent_origin_count": Decimal(len(origins)),
            },
            lineage={
                "target_id": cluster.target_id,
                "speaker_id": cluster.speaker_id,
                "language": cluster.language,
                "model_version": cluster.model_version,
                "classification": cluster.closed_classification.value,
            },
        )
        return EvidencePacket.seal(content)


class MacroPacketBuilder:
    def build(self, release: MacroReleaseHistory, *, decision_cutoff: datetime) -> EvidencePacket:
        eligible = tuple(item for item in release.vintages if item.received_at <= decision_cutoff)
        if not eligible:
            context = release.context.model_copy(
                update={"missingness": release.context.missingness + ("no_vintage_available_at_cutoff",)}
            )
            return EvidencePacket.seal(
                packet_content(
                    context,
                    domain="macro",
                    horizon=release.horizon,
                    supporting_observation_ids=(),
                    refuting_observation_ids=(),
                    deterministic_features={},
                    lineage={"release_id": release.release_id, "vintage": "missing"},
                )
            )
        vintage = max(eligible, key=lambda item: item.received_at)
        surprise = vintage.realized_value - vintage.consensus_value
        return EvidencePacket.seal(
            packet_content(
                release.context,
                domain="macro",
                horizon=release.horizon,
                supporting_observation_ids=(str(vintage.observation_id),),
                refuting_observation_ids=(),
                deterministic_features={
                    "surprise": surprise,
                },
                lineage={
                    "release_id": release.release_id,
                    "vintage": vintage.vintage_id,
                    "consensus_source": vintage.consensus_source_id,
                    "shock_class": vintage.closed_shock_class.value,
                },
            )
        )


class RelationshipContextResolver(Protocol):
    def for_answer(self, answer: EvidenceAnswer) -> PacketContext: ...


class RelationshipPacketBuilder:
    def __init__(
        self,
        contexts: RelationshipContextResolver,
        approved_motifs: frozenset[str],
    ) -> None:
        self._contexts = contexts
        self._approved_motifs = approved_motifs

    def build(self, answer: EvidenceAnswer, *, horizon: str) -> EvidencePacket:
        approved = tuple(
            path for path in answer.paths if path.motif_id in self._approved_motifs and path.depth <= 3
        )
        assertion_ids = tuple(sorted({item for path in approved for item in path.assertion_ids}))
        base = self._contexts.for_answer(answer)
        missingness = base.missingness if approved else base.missingness + ("no_approved_motif",)
        context = base.model_copy(
            update={"supporting_assertion_ids": assertion_ids, "missingness": missingness}
        )
        return EvidencePacket.seal(
            packet_content(
                context,
                domain="relationship",
                horizon=horizon,
                supporting_observation_ids=(),
                refuting_observation_ids=(),
                deterministic_features={"approved_path_count": Decimal(len(approved))},
                lineage={"motif_ids": ",".join(sorted({path.motif_id for path in approved}))},
            )
        )


class PortfolioPacketBuilder:
    def build(self, snapshot: PortfolioSnapshot, *, horizon: str) -> EvidencePacket:
        return EvidencePacket.seal(
            packet_content(
                snapshot.context,
                domain="portfolio",
                horizon=horizon,
                supporting_observation_ids=snapshot.supporting_observation_ids,
                refuting_observation_ids=snapshot.refuting_observation_ids,
                deterministic_features={
                    key: value for key, value in sorted(snapshot.deterministic_features.items())
                },
                lineage={
                    "namespace": "internal-portfolio",
                    "portfolio_snapshot_id": snapshot.portfolio_snapshot_id,
                    "constraint_policy_id": snapshot.constraint_policy_id,
                },
            )
        )
```

- [ ] **Step 4: Verify all domain packet suites**

Run: `uv run pytest tests/unit/semantic/test_*_packet.py -v && uv run mypy src/trading_os/semantic/packets`

Expected: all packet tests PASS and mypy exits 0.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/semantic/packets tests/unit/semantic/test_sentiment_packet.py tests/unit/semantic/test_macro_packet.py tests/unit/semantic/test_relationship_packet.py tests/unit/semantic/test_portfolio_packet.py
git commit -m "feat: build cross-domain evidence packets"
```

### Task 12: Build InstrumentBeliefState and the deterministic feature seam

**Files:**
- Create: `src/trading_os/semantic/models/belief.py`
- Create: `src/trading_os/semantic/reasoning/belief_builder.py`
- Create: `src/trading_os/semantic/reasoning/support_rules.py`
- Create: `src/trading_os/semantic/reasoning/decision_features.py`
- Create: `src/trading_os/semantic/reasoning/risk_overlays.py`
- Create: `src/trading_os/semantic/reasoning/deterministic_policy.py`
- Modify: `src/trading_os/research/seam.py`
- Modify: `src/trading_os/domain/candidates.py`
- Create: `tests/unit/semantic/test_belief_builder.py`
- Create: `tests/unit/semantic/test_decision_feature_seam.py`

**Interfaces:**
- Consumes: Tasks 10/11 packets, `HypothesisSupportRuleRelease`, `FeaturePolicyRelease`, and a
  versioned deterministic strategy policy.
- Produces: `InstrumentHypothesis`, observation-grounded `HypothesisAssessment`,
  `InstrumentBeliefState`, `DecisionFeatureSet`, tighten-only `RiskOverlaySet`,
  `DecisionFeatureProjector.project(state, strategy)`, and
  `DeterministicStrategyPolicy.evaluate(features) -> HotPathCandidate | None`.

- [ ] **Step 1: Write contradiction, no-fake-precision, and seam tests**

```python
# tests/unit/semantic/test_belief_builder.py
def test_conflicting_packets_produce_contested_hypothesis(belief_builder, supporting_packet, refuting_packet) -> None:
    state = belief_builder.build((supporting_packet, refuting_packet))
    assert state.assessments[0].status == "contested"


def test_belief_state_has_no_universal_confidence(valid_belief_state) -> None:
    assert "confidence" not in valid_belief_state.model_dump()
    assert "probability" not in valid_belief_state.model_dump()
```

```python
# tests/unit/semantic/test_decision_feature_seam.py
import pytest

from trading_os.semantic.reasoning.decision_features import ForbiddenDecisionFeature


def test_projector_rejects_raw_narrative(feature_projector, belief_with_narrative) -> None:
    with pytest.raises(ForbiddenDecisionFeature):
        feature_projector.project(belief_with_narrative, strategy="factor_tilt_v1")


def test_unknown_feature_is_dropped_not_auto_allowlisted(feature_projector, belief_with_unknown) -> None:
    projected = feature_projector.project(belief_with_unknown, strategy="factor_tilt_v1")
    assert "fundamental.unreviewed_metric" not in projected.numeric_features


def test_risk_overlay_can_only_tighten(valid_overlay) -> None:
    assert all(Decimal("0") <= value <= Decimal("1") for value in valid_overlay.multipliers.values())
```

- [ ] **Step 2: Run and observe missing belief/seam types**

Run: `uv run pytest tests/unit/semantic/test_belief_builder.py tests/unit/semantic/test_decision_feature_seam.py -v`

Expected: FAIL on missing belief and decision-feature modules.

- [ ] **Step 3: Implement categorical belief aggregation and allowlisted projection**

```python
# src/trading_os/semantic/models/belief.py
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class HypothesisStatus(StrEnum):
    SUPPORTED = "supported"
    CONTESTED = "contested"
    INSUFFICIENT = "insufficient"
    INAPPLICABLE = "inapplicable"


class InstrumentHypothesis(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    hypothesis_id: str
    instrument_id: str
    predicate_iri: str
    horizon: str
    required_domains: tuple[str, ...]
    applicable_regimes: tuple[str, ...]


class HypothesisAssessment(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    hypothesis_id: str
    status: HypothesisStatus
    supporting_assertion_ids: tuple[str, ...] = ()
    refuting_assertion_ids: tuple[str, ...] = ()
    supporting_observation_ids: tuple[str, ...] = ()
    refuting_observation_ids: tuple[str, ...] = ()
    evidence_packet_ids: tuple[str, ...] = ()
    support_rule_release_id: str
    reasons: tuple[str, ...] = ()

    @classmethod
    def insufficient(
        cls,
        hypothesis: InstrumentHypothesis,
        packets: tuple[EvidencePacket, ...],
        *,
        support_rule_release_id: str,
    ) -> "HypothesisAssessment":
        reasons = tuple(sorted({reason for packet in packets for reason in packet.missingness}))
        return cls(
            hypothesis_id=hypothesis.hypothesis_id,
            status=HypothesisStatus.INSUFFICIENT,
            support_rule_release_id=support_rule_release_id,
            evidence_packet_ids=tuple(packet.packet_id for packet in packets),
            reasons=reasons or ("no_supporting_assertion",),
        )


class InstrumentBeliefState(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    instrument_id: str
    semantic_snapshot_id: str
    validated_data_snapshot_id: str
    ontology_release_id: str
    query_pack_release_id: str
    reasoning_policy_release_id: str
    support_rule_release_id: str
    assessments: tuple[HypothesisAssessment, ...]
    evidence_packet_ids: tuple[str, ...]
    unresolved_identity_candidate_ids: tuple[str, ...]
    abstention_reasons: tuple[str, ...]
    generated_at: datetime


class DecisionFeatureSet(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    instrument_id: str
    snapshot_id: str
    strategy_id: str
    categorical_features: dict[str, str]
    numeric_features: dict[str, Decimal]
    lineage_ids: tuple[str, ...]


class RiskOverlaySet(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    instrument_id: str
    snapshot_id: str
    policy_release_id: str
    multipliers: dict[str, Decimal]
    veto_reasons: tuple[str, ...] = ()

    @field_validator("multipliers")
    @classmethod
    def tighten_only(cls, value: dict[str, Decimal]) -> dict[str, Decimal]:
        if any(multiplier < 0 or multiplier > 1 for multiplier in value.values()):
            raise ValueError("risk overlays must be within [0, 1]")
        return value
```

`BeliefStateBuilder` loads an exact `HypothesisSupportRuleRelease`. Each rule declares required
domains, qualifying observation predicates, support/refutation conditions, missing-data behavior,
and contradiction behavior. Packet presence alone never establishes support. The evaluator records
the exact supporting/refuting observation and assertion IDs used. `DecisionFeatureProjector` loads
a strategy-specific positive allowlist and silently excludes unknown producer keys while still
rejecting forbidden lineage. `RiskOverlayProjector` emits only multipliers in `[0, 1]` or vetoes.
The versioned deterministic strategy policy is the sole adapter from `DecisionFeatureSet` to
`HotPathCandidate`; neither beliefs nor graph paths enter sizing directly.

```python
# src/trading_os/semantic/reasoning/belief_builder.py
def assess(
    hypothesis: InstrumentHypothesis,
    packets: tuple[EvidencePacket, ...],
    *,
    support_rules: HypothesisSupportRuleEvaluator,
) -> HypothesisAssessment:
    applicable = tuple(
        packet
        for packet in packets
        if hypothesis.horizon == packet.horizon
        and (
            not hypothesis.applicable_regimes
            or set(hypothesis.applicable_regimes) & set(packet.applicable_regimes)
        )
    )
    if not applicable:
        return HypothesisAssessment(
            hypothesis_id=hypothesis.hypothesis_id,
            status=HypothesisStatus.INAPPLICABLE,
            support_rule_release_id=support_rules.release_id,
            reasons=("horizon_or_regime_mismatch",),
        )
    return support_rules.evaluate(hypothesis=hypothesis, packets=applicable)


class BeliefStateBuilder:
    def __init__(self, hypotheses, support_rules: HypothesisSupportRuleEvaluator, clock: ClockPort) -> None:
        self._hypotheses = hypotheses
        self._support_rules = support_rules
        self._clock = clock

    def build(
        self,
        packets: tuple[EvidencePacket, ...],
        *,
        unresolved_identity_candidate_ids: tuple[str, ...] = (),
        generated_at: datetime | None = None,
    ) -> InstrumentBeliefState:
        if not packets:
            raise ValueError("at least one snapshot-bound packet is required")
        bindings = {
            (
                packet.instrument_id,
                packet.validated_data_snapshot_id,
                packet.semantic_snapshot_id,
                packet.ontology_release_id,
                packet.query_pack_release_id,
            )
            for packet in packets
        }
        if len(bindings) != 1:
            raise ValueError("packets from different instruments or snapshots cannot be combined")
        (
            instrument_id,
            data_snapshot_id,
            semantic_snapshot_id,
            ontology_release_id,
            query_pack_release_id,
        ) = bindings.pop()
        hypotheses = tuple(item for item in self._hypotheses if item.instrument_id == instrument_id)
        assessments = tuple(
            assess(item, packets, support_rules=self._support_rules) for item in hypotheses
        )
        return InstrumentBeliefState(
            instrument_id=instrument_id,
            semantic_snapshot_id=semantic_snapshot_id,
            validated_data_snapshot_id=data_snapshot_id,
            ontology_release_id=ontology_release_id,
            query_pack_release_id=query_pack_release_id,
            reasoning_policy_release_id=self._support_rules.reasoning_policy_release_id,
            support_rule_release_id=self._support_rules.release_id,
            assessments=assessments,
            evidence_packet_ids=tuple(sorted(packet.packet_id for packet in packets)),
            unresolved_identity_candidate_ids=unresolved_identity_candidate_ids,
            abstention_reasons=tuple(
                sorted({reason for item in assessments for reason in item.reasons})
            ),
            generated_at=generated_at or self._clock.now(),
        )
```

```python
# src/trading_os/semantic/reasoning/decision_features.py
from collections.abc import Mapping
from decimal import Decimal
from typing import Protocol

from pydantic import BaseModel, ConfigDict


class ForbiddenDecisionFeature(ValueError):
    pass


class EvidencePacketRepository(Protocol):
    def load_exact(self, packet_ids: tuple[str, ...]) -> tuple[EvidencePacket, ...]: ...


class FeaturePolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    policy_id: str
    strategy_id: str
    numeric_allowlist: frozenset[str]
    categorical_hypothesis_allowlist: frozenset[str]
    forbidden_lineage_keys: frozenset[str]


class DecisionFeatureProjector:
    def __init__(self, policies: Mapping[str, FeaturePolicy], packets: EvidencePacketRepository) -> None:
        self._policies = policies
        self._packets = packets

    def project(self, state: InstrumentBeliefState, *, strategy: str) -> DecisionFeatureSet:
        policy = self._policies[strategy]
        packets = self._packets.load_exact(state.evidence_packet_ids)
        if tuple(sorted(packet.packet_id for packet in packets)) != tuple(
            sorted(state.evidence_packet_ids)
        ):
            raise ForbiddenDecisionFeature("packet repository did not return the exact sealed set")
        if any(
            packet.semantic_snapshot_id != state.semantic_snapshot_id
            or packet.validated_data_snapshot_id != state.validated_data_snapshot_id
            or packet.ontology_release_id != state.ontology_release_id
            for packet in packets
        ):
            raise ForbiddenDecisionFeature("packet snapshot binding does not match belief state")
        lineage_keys = {key for packet in packets for key in packet.lineage}
        if lineage_keys & policy.forbidden_lineage_keys:
            raise ForbiddenDecisionFeature("raw or non-deterministic lineage is not projectable")
        numeric: dict[str, Decimal] = {}
        for packet in packets:
            for name, value in packet.deterministic_features.items():
                qualified = f"{packet.domain}.{name}"
                if qualified in policy.numeric_allowlist:
                    numeric[qualified] = Decimal(value)
        categorical = {
            item.hypothesis_id: item.status.value
            for item in state.assessments
            if item.hypothesis_id in policy.categorical_hypothesis_allowlist
        }
        return DecisionFeatureSet(
            instrument_id=state.instrument_id,
            snapshot_id=state.semantic_snapshot_id,
            strategy_id=policy.strategy_id,
            categorical_features=categorical,
            numeric_features=numeric,
            lineage_ids=state.evidence_packet_ids + (policy.policy_id,),
        )


class DeterministicStrategyPolicy(Protocol):
    policy_release_id: str

    def evaluate(self, features: DecisionFeatureSet) -> HotPathCandidate | None: ...


class RiskOverlayProjector:
    def project(self, state: InstrumentBeliefState, *, policy: RiskOverlayPolicy) -> RiskOverlaySet:
        multipliers = policy.evaluate(state)
        return RiskOverlaySet(
            instrument_id=state.instrument_id,
            snapshot_id=state.semantic_snapshot_id,
            policy_release_id=policy.release_id,
            multipliers=multipliers,
            veto_reasons=policy.veto_reasons(state),
        )
```

Add a seam test that evaluates the same `DecisionFeatureSet` twice through the exact
`DeterministicStrategyPolicy` release and obtains byte-identical `HotPathCandidate`s. Add an import
test proving that the policy module can import only hot-path value objects—not RDF, Neo4j, Source
Records, LLM clients, or unrestricted query types.

- [ ] **Step 4: Verify containment and hot-path import boundary**

Run: `uv run pytest tests/unit/semantic/test_belief_builder.py tests/unit/semantic/test_decision_feature_seam.py tests/unit/research/test_hot_path_imports.py -v`

Expected: tests PASS; no hot-path package imports RDF, graph adapters, Source Records, or research models.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/semantic/models/belief.py src/trading_os/semantic/reasoning src/trading_os/research/seam.py src/trading_os/domain/candidates.py tests/unit/semantic tests/unit/research/test_hot_path_imports.py
git commit -m "feat: project evidence into deterministic decision features"
```

---

## Milestone 4 — Falsifiable Evaluation and Retrospective Improvement

### Task 13: Compare relational, RDF, and Neo4j reasoning paths

**Files:**
- Create: `src/trading_os/semantic/evaluation/metrics.py`
- Create: `src/trading_os/semantic/evaluation/differential.py`
- Create: `src/trading_os/semantic/evaluation/knowledge_contamination.py`
- Create: `config/semantic/reasoning_promotion.yaml`
- Create: `tests/unit/semantic/test_reasoning_metrics.py`
- Create: `tests/integration/semantic/test_differential_retrieval.py`

**Interfaces:**
- Consumes: frozen competency/adversarial cases and three Task 4/5/6 retrieval paths.
- Produces: `ReasoningMetrics`, `DifferentialEvaluation`, and `evaluate_challenger(manifest: EvaluationManifest, *, runner: FrozenCaseRunnerPort, gate: ReasoningPromotionGate) -> DifferentialEvaluation`.

- [ ] **Step 1: Write citation, abstention, and regression-gate tests**

```python
# tests/unit/semantic/test_reasoning_metrics.py
def test_correct_unknown_is_rewarded(metric_calculator, missing_knowledge_case) -> None:
    metrics = metric_calculator.score(missing_knowledge_case, answer_status="unknown")
    assert metrics.appropriate_abstention == 1


def test_challenger_with_identity_regression_cannot_promote(
    promotion_gate,
    valid_evaluation,
) -> None:
    degraded = valid_evaluation.model_copy(
        update={
            "challenger": valid_evaluation.challenger.model_copy(
                update={"catastrophic_false_merges": 1}
            )
        }
    )
    assert promotion_gate.evaluate(degraded).promotable is False


def test_prompt_injection_text_cannot_select_a_query_or_admit_a_claim(adversarial_runner) -> None:
    result = adversarial_runner.run("prompt-injection-source-v1")
    assert result.executed_template_ids == ("instrument-evidence-v1",)
    assert result.new_admission_decision_ids == ()


def test_contaminated_historical_llm_cell_is_not_promotable(promotion_gate, contaminated_evaluation) -> None:
    assert promotion_gate.evaluate(contaminated_evaluation).promotable is False


def test_uncorrected_multiple_comparison_cannot_promote(promotion_gate, uncorrected_evaluation) -> None:
    assert promotion_gate.evaluate(uncorrected_evaluation).reason == "multiplicity_gate_failed"
```

- [ ] **Step 2: Run and observe missing evaluation modules**

Run: `uv run pytest tests/unit/semantic/test_reasoning_metrics.py -v`

Expected: FAIL on missing semantic evaluation modules.

- [ ] **Step 3: Implement pre-registered champion/challenger scoring**

Score factual precision/recall, source entailment, citation correctness, contradiction detection,
appropriate abstention, missing-knowledge behavior, catastrophic false merges, future-fact leaks,
latency, and cost. `reasoning_promotion.yaml` declares primary metrics, zero-tolerance safety metrics,
one predeclared primary metric, minimum material effect, multiplicity correction, fixed retirement
horizon, and budgets. Run every frozen case against the relational champion, RDF, and Neo4j. For
historical cases involving an LLM role, run retrieval, no-retrieval, and masked-knowledge probes;
seal model identifier/provider knowledge-cutoff metadata and mark any contaminated cell
non-promotable. A challenger must meet effect-size and corrected-significance gates, every
safety/budget gate, and show no disallowed holdout regression.

```python
from decimal import Decimal
from typing import Protocol

from pydantic import BaseModel, ConfigDict


class ReasoningMetrics(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    factual_precision: float
    factual_recall: float
    source_entailment: float
    citation_correctness: float
    contradiction_detection: float
    appropriate_abstention: float
    missing_knowledge_score: float
    catastrophic_false_merges: int
    future_fact_leaks: int
    latency_ms: float
    cost: Decimal

    def metric(self, name: str) -> float:
        value = getattr(self, name)
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} is not a scalar score")
        return float(value)


class ReasoningPromotionPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    primary_metric: str
    protected_metrics: tuple[str, ...]
    minimum_material_effect: float
    allowed_regressions: dict[str, float]
    familywise_alpha: float
    multiplicity_method: Literal["holm"]
    fixed_retirement_horizon_runs: int
    minimum_case_count: int
    max_latency_ms: float
    max_cost: Decimal

    def allowed_regression(self, name: str) -> float:
        return self.allowed_regressions[name]


class PromotionResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    promotable: bool
    reason: str

    @classmethod
    def reject(cls, reason: str) -> "PromotionResult":
        return cls(promotable=False, reason=reason)


class EvaluationManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    manifest_hash: str
    frozen_case_set_hash: str
    retrieval_paths: tuple[Literal["relational", "rdf", "neo4j"], ...]
    primary_metric: str
    model_id: str | None
    model_provider: str | None
    declared_knowledge_cutoff: date | None
    knowledge_probe_modes: tuple[Literal["retrieval", "no_retrieval", "masked"], ...]
    multiplicity_family_id: str
    fixed_retirement_horizon_runs: int


class DifferentialEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    manifest_hash: str
    champion: ReasoningMetrics
    challenger: ReasoningMetrics
    promotion: PromotionResult | None = None
    corrected_p_value: float
    primary_effect: float
    contaminated_cell_ids: tuple[str, ...]
    knowledge_probe_receipt_ids: tuple[str, ...]


class FrozenCaseRunnerPort(Protocol):
    def score_all_paths_and_probes(self, manifest: EvaluationManifest) -> FrozenEvaluationCells: ...


class ReasoningPromotionGate:
    def __init__(self, policy: ReasoningPromotionPolicy) -> None:
        self._policy = policy

    def evaluate(self, evaluation: DifferentialEvaluation) -> PromotionResult:
        champion = evaluation.champion
        challenger = evaluation.challenger
        if evaluation.contaminated_cell_ids:
            return PromotionResult.reject("knowledge_contamination")
        if evaluation.corrected_p_value > self._policy.familywise_alpha:
            return PromotionResult.reject("multiplicity_gate_failed")
        if evaluation.primary_effect < self._policy.minimum_material_effect:
            return PromotionResult.reject("effect_size_gate_failed")
        if challenger.catastrophic_false_merges != 0 or challenger.future_fact_leaks != 0:
            return PromotionResult.reject("zero_tolerance_safety_failure")
        if challenger.latency_ms > self._policy.max_latency_ms or challenger.cost > self._policy.max_cost:
            return PromotionResult.reject("budget_exceeded")
        regressed = any(
            challenger.metric(name) < champion.metric(name) - self._policy.allowed_regression(name)
            for name in self._policy.protected_metrics
        )
        if regressed:
            return PromotionResult.reject("protected_metric_regression")
        return PromotionResult(promotable=True, reason="corrected_material_gain")


def evaluate_challenger(
    manifest: EvaluationManifest,
    *,
    runner: FrozenCaseRunnerPort,
    gate: ReasoningPromotionGate,
) -> DifferentialEvaluation:
    cells = runner.score_all_paths_and_probes(manifest)
    evaluation = DifferentialEvaluation.from_frozen_cells(manifest=manifest, cells=cells)
    return evaluation.model_copy(update={"promotion": gate.evaluate(evaluation)})
```

- [ ] **Step 4: Verify differential evaluation on frozen cases**

Run: `uv run pytest tests/unit/semantic/test_reasoning_metrics.py -v`

Run: `uv run pytest tests/integration/semantic/test_differential_retrieval.py -v -m integration`

Expected: tests PASS; planted future fact, false merge, and missing-provenance challengers are rejected.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/semantic/evaluation config/semantic/reasoning_promotion.yaml tests/unit/semantic/test_reasoning_metrics.py tests/integration/semantic/test_differential_retrieval.py
git commit -m "feat: evaluate semantic challengers against relational retrieval"
```

### Task 14: Implement the governed agentic improvement and promotion loop

**Files:**
- Create: `src/trading_os/semantic/improvement/models.py`
- Create: `src/trading_os/semantic/improvement/store.py`
- Create: `src/trading_os/semantic/improvement/roles.py`
- Create: `src/trading_os/semantic/improvement/promotion.py`
- Create: `src/trading_os/semantic/improvement/activation.py`
- Create: `src/trading_os/semantic/improvement/canary.py`
- Create: `alembic/versions/20260721_0004_semantic_improvement.py`
- Create: `tests/unit/semantic/test_improvement_loop.py`
- Create: `tests/unit/semantic/test_promotion_authority.py`
- Create: `tests/unit/semantic/test_decision_feature_activation.py`

**Interfaces:**
- Consumes: Task 13 evaluation, Task 1 release builder, human approval decisions, frozen experiment manifest.
- Produces: `FailureCase`, closed `RootCauseClass`, `Diagnosis`, `ChangeProposal`,
  `ExperimentManifest`, `ExperimentOutcome`, `ImprovementCoordinator.run(...)`, semantic-only
  `PromotionAuthority`, immutable `DecisionFeatureActivation`, `CanaryManifest`, `CanaryReceipt`,
  governed transition validation, and automatic rollback.

- [ ] **Step 1: Write self-promotion, holdout, and remediation-budget tests**

```python
# tests/unit/semantic/test_promotion_authority.py
def test_author_cannot_approve_own_change(promotion_authority, evaluated_proposal) -> None:
    decision = promotion_authority.decide(evaluated_proposal, approver_id=evaluated_proposal.author_id)
    assert decision.status == "rejected"
    assert decision.reason == "self_approval_forbidden"


def test_high_risk_change_always_requires_human(promotion_authority, causal_relation_proposal) -> None:
    decision = promotion_authority.decide(causal_relation_proposal, approver_id=None)
    assert decision.status == "awaiting_human"


def test_medium_risk_starts_human_gated(promotion_authority, medium_risk_proposal) -> None:
    decision = promotion_authority.decide(medium_risk_proposal, approver_id=None)
    assert decision.status == "awaiting_human"


def test_semantic_promotion_does_not_activate_features(promotion_publisher, approved_semantic_release) -> None:
    promotion_publisher.publish(**approved_semantic_release)
    assert promotion_publisher.feature_activation_store.active() is None


def test_activation_cannot_skip_paper_canary(activation_authority, shadow_activation) -> None:
    with pytest.raises(ValueError, match="PAPER_CANARY"):
        activation_authority.transition(shadow_activation, ActivationMode.PAPER_ACTIVE)


def test_canary_cap_breach_rolls_back(canary_monitor, live_canary_receipt) -> None:
    result = canary_monitor.observe(live_canary_receipt, capital_cap_breached=True)
    assert result.mode is ActivationMode.PAPER_ACTIVE
```

```python
# tests/unit/semantic/test_improvement_loop.py
def test_exhausted_budget_pauses_expansion(coordinator, exhausted_manifest) -> None:
    outcome = coordinator.run(exhausted_manifest.failure_case_id)
    assert outcome.status == "paused"
    assert outcome.baseline_remains_active is True


def test_unavailable_improvement_agent_freezes_release(unavailable_coordinator, failure_case) -> None:
    outcome = unavailable_coordinator.run(failure_case.failure_case_id)
    assert outcome.status == "paused"
    assert outcome.baseline_remains_active is True
```

- [ ] **Step 2: Run and observe missing improvement modules**

Run: `uv run pytest tests/unit/semantic/test_improvement_loop.py tests/unit/semantic/test_promotion_authority.py -v`

Expected: FAIL on missing improvement modules.

- [ ] **Step 3: Implement durable artifacts, role separation, shadow, and rollback**

```python
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ChangeRisk(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RootCauseClass(StrEnum):
    ONTOLOGY_GAP = "ontology_gap"
    IDENTITY_ERROR = "identity_error"
    QUERY_ERROR = "query_error"
    SUPPORT_RULE_ERROR = "support_rule_error"
    DATA_GAP = "data_gap"
    PROJECTION_ERROR = "projection_error"
    FEATURE_POLICY_ERROR = "feature_policy_error"
    CONTAMINATED_EVALUATION = "contaminated_evaluation"


class FailureCase(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    failure_case_id: UUID
    scope_id: str
    semantic_snapshot_id: str
    competency_question_id: str
    expected_status: str
    actual_status: str
    evidence_answer_hash: str


class Diagnosis(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    diagnosis_id: UUID
    failure_case_id: UUID
    analyst_id: str
    root_cause_class: RootCauseClass
    cited_artifact_ids: tuple[str, ...]


class ChangeProposal(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    proposal_id: UUID
    failure_case_id: UUID
    author_id: str
    risk: ChangeRisk
    patch_hash: str
    change_class: str
    affected_competency_questions: tuple[str, ...]


class ExperimentManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    experiment_id: UUID
    proposal_id: UUID
    champion_manifest_hash: str
    challenger_manifest_hash: str
    public_case_set_hash: str
    sealed_holdout_set_id: str
    maximum_attempts: int


class ExperimentOutcome(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    experiment_outcome_id: UUID
    experiment_id: UUID
    champion_metrics: ReasoningMetrics
    challenger_metrics: ReasoningMetrics
    artifact_hash: str


class RemediationBudget(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    maximum_attempts: int
    used_attempts: int
    maximum_elapsed_seconds: int
    used_elapsed_seconds: int
    maximum_compute_cost: Decimal
    used_compute_cost: Decimal
    maximum_reviewer_minutes: int
    used_reviewer_minutes: int
    maintenance_benefit_gate_failed: bool = False

    @property
    def can_attempt(self) -> bool:
        return (
            self.used_attempts < self.maximum_attempts
            and self.used_elapsed_seconds < self.maximum_elapsed_seconds
            and self.used_compute_cost < self.maximum_compute_cost
            and self.used_reviewer_minutes < self.maximum_reviewer_minutes
            and not self.maintenance_benefit_gate_failed
        )


class AutoPromotionPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    policy_id: str
    human_approved_by: str
    automatically_allowed_change_classes: frozenset[str]

    def auto_allows(self, change_class: str) -> bool:
        return change_class in self.automatically_allowed_change_classes


class EvaluatedProposal(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    proposal_id: UUID
    author_id: str
    risk: ChangeRisk
    change_class: str
    evaluation: PromotionResult
    policy: AutoPromotionPolicy


class PromotionStatus(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
    AWAITING_HUMAN = "awaiting_human"


class PromotionDecision(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    status: PromotionStatus
    reason: str
    approved_by: str | None = None

    @classmethod
    def rejected(cls, reason: str) -> "PromotionDecision":
        return cls(status=PromotionStatus.REJECTED, reason=reason)

    @classmethod
    def awaiting_human(cls) -> "PromotionDecision":
        return cls(status=PromotionStatus.AWAITING_HUMAN, reason="human_approval_required")

    @classmethod
    def approved(cls, approved_by: str) -> "PromotionDecision":
        return cls(status=PromotionStatus.APPROVED, reason="approved", approved_by=approved_by)


class ImprovementRunResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    status: str
    baseline_remains_active: bool
    diagnosis_id: UUID | None = None
    proposal_id: UUID | None = None
    experiment_outcome_id: UUID | None = None
    evaluated_proposal_id: UUID | None = None


class ActivationMode(StrEnum):
    DISABLED = "disabled"
    SHADOW = "shadow"
    PAPER_CANARY = "paper_canary"
    PAPER_ACTIVE = "paper_active"
    LIVE_CANARY = "live_canary"
    LIVE_ACTIVE = "live_active"


class DecisionFeatureActivation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    activation_id: str
    mode: ActivationMode
    ontology_release_id: str
    query_pack_release_id: str
    reasoning_policy_release_id: str
    support_rule_release_id: str
    feature_policy_release_id: str
    deterministic_strategy_policy_release_id: str
    risk_overlay_policy_release_id: str
    scope: tuple[str, ...]
    capital_cap: Decimal
    risk_cap: Decimal
    horizon_started_at: datetime
    horizon_ends_at: datetime
    rollback_activation_id: str | None
    approved_by: str


class CanaryReceipt(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    receipt_id: str
    activation_id: str
    mode: ActivationMode
    observed_scope: tuple[str, ...]
    capital_used: Decimal
    risk_used: Decimal
    success_gate_ids: tuple[str, ...]
    rollback_trigger_ids: tuple[str, ...]
    passed: bool
```

Persist FailureCase, Diagnosis, ChangeProposal, ExperimentManifest, and ExperimentOutcome in
insert-only tables. Evaluator, root-cause analyst, ontology steward, data steward, query steward,
and red-team roles emit typed artifacts; none can publish directly. Holdout answers are exposed only
to the evaluator. HIGH is always human-approved; MEDIUM begins human-approved; LOW becomes eligible
for automatic promotion only when a separately human-approved policy version permits the exact
change class. Shadow regressions atomically restore the prior active release pointer and append a
rollback event. This authority changes semantic release pointers only; it cannot create or modify a
`DecisionFeatureActivation`. Economic authority is a separate append-only transition log with the
only forward transitions `DISABLED → SHADOW → PAPER_CANARY → PAPER_ACTIVE → LIVE_CANARY →
LIVE_ACTIVE`. Any state may transition to `DISABLED` or its declared prior safe activation.
Canary scope, capital/risk caps, fixed horizon, success gates, rollback triggers, exact artifact
bindings, and approver are content-hashed before execution. A cap breach, safety trigger, or failed
horizon atomically restores the rollback activation and appends a rollback receipt.

```python
from typing import Protocol


class ImprovementStorePort(Protocol):
    def get_failure(self, failure_id: UUID) -> FailureCase: ...
    def remediation_budget(self, scope_id: str) -> RemediationBudget: ...
    def append_diagnosis(self, diagnosis: Diagnosis) -> None: ...
    def append_proposal(self, proposal: ChangeProposal) -> None: ...
    def append_manifest(self, manifest: ExperimentManifest) -> None: ...
    def append_outcome(self, outcome: ExperimentOutcome, evaluation: PromotionResult) -> None: ...
    def append_evaluated_proposal(self, proposal: EvaluatedProposal) -> None: ...
    def append_result(self, result: ImprovementRunResult) -> None: ...


class RootCauseAnalystPort(Protocol):
    def diagnose(self, failure: FailureCase) -> Diagnosis: ...


class ChangeStewardPort(Protocol):
    def propose(self, diagnosis: Diagnosis) -> ChangeProposal: ...


class ExperimentRunnerPort(Protocol):
    def freeze_manifest(self, proposal: ChangeProposal) -> ExperimentManifest: ...
    def run(self, manifest: ExperimentManifest) -> ExperimentOutcome: ...


class DifferentialEvaluatorPort(Protocol):
    def compare(self, outcome: ExperimentOutcome) -> PromotionResult: ...


class ImprovementAgentUnavailable(RuntimeError):
    pass


class ImprovementCoordinator:
    def __init__(
        self,
        store: ImprovementStorePort,
        analyst: RootCauseAnalystPort,
        steward: ChangeStewardPort,
        experiments: ExperimentRunnerPort,
        evaluator: DifferentialEvaluatorPort,
        promotion_policy: AutoPromotionPolicy,
    ) -> None:
        self._store = store
        self._analyst = analyst
        self._steward = steward
        self._experiments = experiments
        self._evaluator = evaluator
        self._promotion_policy = promotion_policy

    def run(self, failure_id: UUID) -> ImprovementRunResult:
        failure = self._store.get_failure(failure_id)
        if not self._store.remediation_budget(failure.scope_id).can_attempt:
            result = ImprovementRunResult(status="paused", baseline_remains_active=True)
            self._store.append_result(result)
            return result
        try:
            diagnosis = self._analyst.diagnose(failure)
            self._store.append_diagnosis(diagnosis)
            proposal = self._steward.propose(diagnosis)
            self._store.append_proposal(proposal)
            manifest = self._experiments.freeze_manifest(proposal)
            self._store.append_manifest(manifest)
            outcome = self._experiments.run(manifest)
            evaluation = self._evaluator.compare(outcome)
            self._store.append_outcome(outcome, evaluation)
            evaluated = EvaluatedProposal(
                proposal_id=proposal.proposal_id,
                author_id=proposal.author_id,
                risk=proposal.risk,
                change_class=proposal.change_class,
                evaluation=evaluation,
                policy=self._promotion_policy,
            )
            self._store.append_evaluated_proposal(evaluated)
        except ImprovementAgentUnavailable:
            result = ImprovementRunResult(status="paused", baseline_remains_active=True)
            self._store.append_result(result)
            return result
        return ImprovementRunResult(
            status="awaiting_promotion_decision",
            baseline_remains_active=True,
            diagnosis_id=diagnosis.diagnosis_id,
            proposal_id=proposal.proposal_id,
            experiment_outcome_id=outcome.experiment_outcome_id,
            evaluated_proposal_id=evaluated.proposal_id,
        )


class PromotionAuthority:
    def decide(self, proposal: EvaluatedProposal, *, approver_id: str | None) -> PromotionDecision:
        if approver_id == proposal.author_id:
            return PromotionDecision.rejected("self_approval_forbidden")
        if proposal.risk in {ChangeRisk.HIGH, ChangeRisk.MEDIUM} and approver_id is None:
            return PromotionDecision.awaiting_human()
        if approver_id is None and proposal.policy.human_approved_by == proposal.author_id:
            return PromotionDecision.awaiting_human()
        if approver_id is None and not proposal.policy.auto_allows(proposal.change_class):
            return PromotionDecision.awaiting_human()
        if not proposal.evaluation.promotable:
            return PromotionDecision.rejected("evaluation_gate_failed")
        return PromotionDecision.approved(approved_by=approver_id or proposal.policy.policy_id)


class SemanticReleasePointerPort(Protocol):
    def promote_and_append_event(
        self,
        release_id: str,
        *,
        approved_by: str,
        expected_active_release_id: str,
    ) -> UUID: ...
    def rollback_and_append_event(self, promotion_id: UUID, *, reason: str) -> str: ...


class PromotionPublisher:
    def __init__(self, releases: SemanticReleasePointerPort) -> None:
        self._releases = releases

    def publish(
        self,
        release_id: str,
        *,
        prior_release_id: str,
        decision: PromotionDecision,
    ) -> UUID:
        if decision.status is not PromotionStatus.APPROVED or decision.approved_by is None:
            raise PermissionError("only an approved promotion decision can activate a release")
        return self._releases.promote_and_append_event(
            release_id,
            approved_by=decision.approved_by,
            expected_active_release_id=prior_release_id,
        )


class ShadowMonitor:
    def __init__(self, releases: SemanticReleasePointerPort) -> None:
        self._releases = releases

    def observe(self, promotion_id: UUID, *, safety_regression: bool) -> str | None:
        if not safety_regression:
            return None
        return self._releases.rollback_and_append_event(
            promotion_id,
            reason="shadow_safety_regression",
        )
```

`20260721_0004_semantic_improvement.py` declares `revision = "20260721_0004"` and
`down_revision = "20260721_0003"`. In addition to the improvement artifacts, it creates insert-only
semantic-promotion, decision-feature-activation, canary-manifest, canary-receipt, and rollback tables
with UPDATE/DELETE rejection triggers.

- [ ] **Step 4: Verify authority, offline-only behavior, and rollback**

Run: `uv run pytest tests/unit/semantic/test_improvement_loop.py tests/unit/semantic/test_promotion_authority.py tests/unit/semantic/test_decision_feature_activation.py -v && uv run mypy src/trading_os/semantic/improvement`

Expected: tests PASS; no agent role has a graph-write or decision-feature-activation mutation port.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/semantic/improvement alembic/versions/20260721_0004_semantic_improvement.py tests/unit/semantic/test_improvement_loop.py tests/unit/semantic/test_promotion_authority.py tests/unit/semantic/test_decision_feature_activation.py
git commit -m "feat: govern semantic diagnosis promotion and rollback"
```

### Task 15: Compose the reasoning cycle and prove end-to-end fallback

**Files:**
- Create: `src/trading_os/semantic/cycle.py`
- Create: `src/trading_os/semantic/bootstrap.py`
- Create: `src/trading_os/semantic/handoff.py`
- Create: `config/semantic/runtime.yaml`
- Modify: `docs/superpowers/plans/2026-07-21-trading-os-v1-implementation.md`
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Test: `tests/integration/semantic/test_reasoning_cycle.py`
- Test: `tests/unit/semantic/test_semantic_bootstrap.py`
- Test: `tests/integration/semantic/test_semantic_fallback.py`
- Test: `tests/integration/semantic/test_baseline_failure.py`
- Test: `tests/integration/semantic/test_semantic_crash_recovery.py`

**Interfaces:**
- Consumes: Tasks 1–14 and the existing EOD orchestration boundary.
- Produces: `ReasoningCycle.run(request) -> InstrumentBeliefState`,
  `SemanticDecisionHandoff.prepare(...) -> ActivatedDecisionInputs`, explicitly governed relational
  fallback, sealed retrieval/audit receipts, semantic promotion evidence, and the exact Trading OS
  integration contract.

- [ ] **Step 1: Write complete-cycle, fallback, and restart tests**

```python
# tests/integration/semantic/test_reasoning_cycle.py
async def test_cycle_returns_snapshot_bound_belief(reasoning_cycle, cycle_request) -> None:
    state = await reasoning_cycle.run(cycle_request)
    assert state.semantic_snapshot_id == cycle_request.semantic_snapshot_id
    assert state.validated_data_snapshot_id == cycle_request.validated_data_snapshot_id
    assert state.assessments


async def test_shadow_activation_has_no_economic_inputs(handoff, shadow_request) -> None:
    result = await handoff.prepare(shadow_request, strategy_id="factor_tilt_v1")
    assert result.decision_features is None
    assert result.risk_overlays is None
    assert result.hot_path_candidate is None


async def test_active_handoff_binds_exact_activation(handoff, paper_canary_request) -> None:
    result = await handoff.prepare(paper_canary_request, strategy_id="factor_tilt_v1")
    assert result.activation_id == paper_canary_request.activation_id
    assert all(value <= 1 for value in result.risk_overlays.multipliers.values())
```

```python
# tests/unit/semantic/test_semantic_bootstrap.py
import pytest

from trading_os.semantic.bootstrap import UnsupportedOntologyRelease


def test_runtime_rejects_unsupported_major_release(semantic_bootstrap, ontology_release_v2) -> None:
    with pytest.raises(UnsupportedOntologyRelease):
        semantic_bootstrap.assert_supported(ontology_release_v2)
```

```python
# tests/integration/semantic/test_semantic_fallback.py
async def test_projection_failure_uses_relational_champion(degraded_cycle, cycle_request) -> None:
    state = await degraded_cycle.run(cycle_request)
    assert "semantic_projection_unavailable" in state.abstention_reasons
    assert degraded_cycle.audit.retrieval_path == "relational"
```

```python
# tests/integration/semantic/test_semantic_crash_recovery.py
async def test_restart_reuses_sealed_snapshot(restarted_cycle, sealed_request) -> None:
    first = await restarted_cycle.run(sealed_request)
    second = await restarted_cycle.run(sealed_request)
    assert first.model_dump_json() == second.model_dump_json()
```

```python
# tests/integration/semantic/test_baseline_failure.py
import pytest

from trading_os.semantic.cycle import RelationalChampionUnavailable


async def test_projection_and_baseline_failure_aborts_decisioning(failed_cycle, cycle_request) -> None:
    with pytest.raises(RelationalChampionUnavailable):
        await failed_cycle.run(cycle_request)
    assert await failed_cycle.results.get(cycle_request.cycle_id) is None
```

- [ ] **Step 2: Run and observe missing reasoning composition**

Run: `uv run pytest tests/integration/semantic/test_reasoning_cycle.py tests/integration/semantic/test_semantic_fallback.py tests/integration/semantic/test_baseline_failure.py tests/integration/semantic/test_semantic_crash_recovery.py -v -m integration`

Expected: FAIL on missing semantic cycle/bootstrap modules.

- [ ] **Step 3: Implement idempotent composition and update Trading OS integration**

`ReasoningCycle` loads exact data/semantic snapshots, runs approved queries, builds all six packets,
constructs the belief state, seals an audit event, and returns it. A normalized availability error
may invoke a query-pack-declared equivalent relational template and marks degraded state; integrity,
binding, decode, or missing-equivalence errors fail closed. Baseline failure aborts decisioning. The
EOD cycle passes the belief state through `DecisionFeatureProjector`, the exact activated
`DeterministicStrategyPolicy`, and the tighten-only risk projector.
`semantic/handoff.py` exposes this typed boundary without importing control or evaluation packages
that do not exist yet. Update the Trading OS plan: this plan augments Tasks 12–13, replaces Tasks
15–17, and preserves Task 14; Task 18 consumes only an activated `HotPathCandidate`; Task 19 consumes
`RiskOverlaySet`; Task 32 calls `ReasoningCycle` and `SemanticDecisionHandoff`; Task 34 evaluates
semantic promotion without activation; Task 35 replays sealed relationship packets and policy
releases; Task 36 enforces the paper/live canary state machine.

```python
# src/trading_os/semantic/bootstrap.py
from packaging.specifiers import SpecifierSet


class UnsupportedOntologyRelease(RuntimeError):
    pass


class SemanticBootstrap:
    def __init__(self, supported_releases: str) -> None:
        self._supported_releases = SpecifierSet(supported_releases)

    def assert_supported(self, release: OntologyRelease) -> None:
        if release.semantic_version not in self._supported_releases:
            raise UnsupportedOntologyRelease(release.semantic_version)
```

Set `config/semantic/runtime.yaml` to
`supported_ontology_releases: ">=1.0.0,<2.0.0"`; bootstrap resolves every historical request by
its exact release ID through `OntologyReleaseRegistry.get_exact()` before applying this range.

```python
# src/trading_os/semantic/handoff.py
class ActivatedDecisionInputs(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    activation_id: str
    activation_mode: ActivationMode
    belief_state_id: str
    decision_features: DecisionFeatureSet | None
    risk_overlays: RiskOverlaySet | None
    hot_path_candidate: HotPathCandidate | None
    audit_receipt_id: str


class SemanticDecisionHandoff:
    def __init__(
        self,
        reasoning: ReasoningCycle,
        projector: DecisionFeatureProjector,
        risk_projector: RiskOverlayProjector,
        activations: DecisionFeatureActivationPort,
        strategy_policies: DeterministicStrategyPolicyRegistry,
    ) -> None:
        self._reasoning = reasoning
        self._projector = projector

    async def prepare(
        self,
        request: ReasoningCycleRequest,
        *,
        strategy_id: str,
    ) -> ActivatedDecisionInputs:
        belief = await self._reasoning.run(request)
        activation = await self._activations.get_exact(request.activation_id)
        activation.assert_exact_artifact_bindings(request.decision_binding)
        if activation.mode in {ActivationMode.DISABLED, ActivationMode.SHADOW}:
            return ActivatedDecisionInputs.shadow(belief=belief, activation=activation)
        features = self._projector.project(belief, strategy=strategy_id)
        overlays = self._risk_projector.project(belief, policy=activation.risk_overlay_policy)
        candidate = self._strategy_policies.get_exact(
            activation.deterministic_strategy_policy_release_id
        ).evaluate(features)
        return ActivatedDecisionInputs.seal(
            belief=belief,
            activation=activation,
            decision_features=features,
            risk_overlays=overlays,
            hot_path_candidate=candidate,
        )
```

```python
# src/trading_os/semantic/cycle.py
import hashlib
from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict, model_validator

from trading_os.semantic.retrieval.query_service import SemanticProjectionUnavailable

class RelationalChampionUnavailable(RuntimeError):
    pass


class DecisionRuntimeBinding(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    semantic_query: SemanticQueryBinding
    reasoning_policy_release_id: str
    support_rule_release_id: str
    feature_policy_release_id: str
    activation_id: str


class ReasoningCycleRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    cycle_id: str
    reasoning_time: datetime
    decision_cutoff: datetime
    validated_data_snapshot_id: str
    semantic_snapshot_id: str
    projection_receipt_id: str
    ontology_release_id: str
    query_pack_release_id: str
    reasoning_policy_release_id: str
    support_rule_release_id: str
    feature_policy_release_id: str
    activation_id: str
    approved_queries: tuple[EvidenceQuery, ...]
    portfolio_snapshot: PortfolioSnapshot

    @model_validator(mode="after")
    def cutoff_precedes_reasoning(self) -> "ReasoningCycleRequest":
        if self.decision_cutoff > self.reasoning_time:
            raise ValueError("decision cutoff cannot follow reasoning time")
        return self

    @property
    def semantic_binding(self) -> SemanticQueryBinding:
        return SemanticQueryBinding(
            data_snapshot_id=self.validated_data_snapshot_id,
            semantic_snapshot_id=self.semantic_snapshot_id,
            projection_receipt_id=self.projection_receipt_id,
            ontology_release_id=self.ontology_release_id,
            query_pack_release_id=self.query_pack_release_id,
            decision_cutoff=self.decision_cutoff,
        )

    @property
    def decision_binding(self) -> DecisionRuntimeBinding:
        return DecisionRuntimeBinding(
            semantic_query=self.semantic_binding,
            reasoning_policy_release_id=self.reasoning_policy_release_id,
            support_rule_release_id=self.support_rule_release_id,
            feature_policy_release_id=self.feature_policy_release_id,
            activation_id=self.activation_id,
        )


class ReasoningResultStorePort(Protocol):
    async def get(self, cycle_id: str, *, binding_hash: str) -> InstrumentBeliefState | None: ...
    async def put_if_absent(
        self,
        cycle_id: str,
        state: InstrumentBeliefState,
        *,
        binding_hash: str,
    ) -> InstrumentBeliefState: ...


class SnapshotBundlePort(Protocol):
    async def load_exact(
        self,
        validated_data_snapshot_id: str,
        semantic_snapshot_id: str,
        projection_receipt_id: str,
    ) -> SnapshotBundle: ...


class QueryBatchPort(Protocol):
    async def execute_all(
        self,
        queries: tuple[EvidenceQuery, ...],
    ) -> tuple[QueryExecutionResult, ...]: ...


class PacketBuilderSet(Protocol):
    async def build_all(
        self,
        snapshots: SnapshotBundle,
        answers: tuple[EvidenceAnswer, ...],
        portfolio_snapshot: PortfolioSnapshot,
    ) -> tuple[EvidencePacket, ...]: ...


class ReasoningCycleCompleted(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    event_id: str
    cycle_id: str
    semantic_snapshot_id: str
    state_hash: str
    retrieval_path: str

    @classmethod
    def from_state(
        cls,
        state: InstrumentBeliefState,
        *,
        cycle_id: str,
        retrieval_path: str,
    ) -> "ReasoningCycleCompleted":
        state_hash = hashlib.sha256(state.model_dump_json().encode()).hexdigest()
        event_id = hashlib.sha256(f"{cycle_id}:{state_hash}:{retrieval_path}".encode()).hexdigest()
        return cls(
            event_id=event_id,
            cycle_id=cycle_id,
            semantic_snapshot_id=state.semantic_snapshot_id,
            state_hash=state_hash,
            retrieval_path=retrieval_path,
        )


class AuditPort(Protocol):
    async def append_once(self, event: ReasoningCycleCompleted, *, idempotency_key: str) -> None: ...


class ReasoningCycle:
    def __init__(
        self,
        snapshots: SnapshotBundlePort,
        queries: QueryBatchPort,
        relational: QueryBatchPort,
        packet_builders: PacketBuilderSet,
        beliefs: BeliefStateBuilder,
        audit: AuditPort,
        results: ReasoningResultStorePort,
    ) -> None:
        self._snapshots = snapshots
        self._queries = queries
        self._relational = relational
        self._packet_builders = packet_builders
        self._beliefs = beliefs
        self._audit = audit
        self._results = results

    async def run(self, request: ReasoningCycleRequest) -> InstrumentBeliefState:
        snapshots = await self._snapshots.load_exact(
            request.validated_data_snapshot_id,
            request.semantic_snapshot_id,
            request.projection_receipt_id,
        )
        if any(
            (
                query.validated_data_snapshot_id,
                query.semantic_snapshot_id,
                query.projection_receipt_id,
                query.ontology_release_id,
                query.query_pack_release_id,
                query.decision_cutoff,
            )
            != (
                request.validated_data_snapshot_id,
                request.semantic_snapshot_id,
                request.projection_receipt_id,
                request.ontology_release_id,
                request.query_pack_release_id,
                request.decision_cutoff,
            )
            for query in request.approved_queries
        ):
            raise ValueError("every query must bind the requested snapshots, release, and cutoff")
        cache_binding = canonical_sha256(request.decision_binding.model_dump(mode="json"))
        existing = await self._results.get(request.cycle_id, binding_hash=cache_binding)
        if existing is not None:
            return existing
        try:
            query_results = await self._queries.execute_all(request.approved_queries)
            retrieval_path = "semantic"
        except SemanticProjectionUnavailable as error:
            fallback_queries = self._query_pack.equivalent_relational_queries(
                request.approved_queries,
                normalized_error=error,
            )
            if fallback_queries is None:
                raise
            query_results = await self._relational.execute_all(fallback_queries)
            retrieval_path = "relational"
        answers = tuple(result.answer for result in query_results)
        packets = await self._packet_builders.build_all(
            snapshots,
            answers,
            request.portfolio_snapshot,
        )
        state = self._beliefs.build(packets, generated_at=request.reasoning_time)
        if retrieval_path == "relational":
            state = state.model_copy(
                update={
                    "abstention_reasons": state.abstention_reasons
                    + ("semantic_projection_unavailable",)
                }
            )
        event = ReasoningCycleCompleted.from_state(
            state,
            cycle_id=request.cycle_id,
            retrieval_path=retrieval_path,
        )
        await self._audit.append_once(event, idempotency_key=request.cycle_id)
        return await self._results.put_if_absent(
            request.cycle_id,
            state,
            binding_hash=cache_binding,
        )
```

Add this exact operational note to `README.md`:

```markdown
## Semantic reasoning

Ontology source and SHACL constraints live under `ontology/` and are canonical. Postgres stores
append-only evidence; Fuseki and Neo4j are rebuildable projections sealed by a separate
`SemanticProjectionReceipt`. Decisioning always binds an exact data snapshot, semantic snapshot,
projection receipt, ontology release, query-pack release, reasoning/feature policies, and cutoff.
If a semantic projection is unavailable, reasoning degrades explicitly to the permanent relational
champion; if that champion is unavailable, decisioning fails closed.
```

Add this exact repository rule to `CLAUDE.md`:

```markdown
- Never write directly to Fuseki or Neo4j from runtime code. Change Git-owned ontology source or
  append evidence, compute a new SemanticSnapshot, rebuild both projections with its final ID, and
  seal a SemanticProjectionReceipt. The deterministic trading path may consume only an activated
  DecisionFeatureSet and tighten-only RiskOverlaySet, never raw narrative or graph handles.
```

- [ ] **Step 4: Run the full semantic and boundary verification suite**

Run: `uv run pytest tests/unit/semantic tests/contract/semantic -v`

Run: `uv run pytest tests/integration/semantic -v -m integration`

Run: `uv run mypy src/trading_os/ontology src/trading_os/semantic && uv run ruff check src/trading_os/ontology src/trading_os/semantic tests/unit/semantic tests/contract/semantic tests/integration/semantic`

Expected: all tests PASS, mypy exits 0, ruff exits 0, and the end-to-end fallback trace identifies the relational path.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/semantic/cycle.py src/trading_os/semantic/bootstrap.py src/trading_os/semantic/handoff.py config/semantic/runtime.yaml docs/superpowers/plans/2026-07-21-trading-os-v1-implementation.md tests/unit/semantic/test_semantic_bootstrap.py tests/integration/semantic README.md CLAUDE.md
git commit -m "feat: compose auditable semantic reasoning cycle"
```

---

## Final Acceptance Checklist

- [ ] Ontology, query-pack, reasoning/support-rule, and feature-policy release hashes are independently reproducible; every meaning-changing artifact participates in compatibility checks.
- [ ] Released IRIs remain stable and no runtime store can mutate ontology source.
- [ ] Source, observation, claim, admission, identity, and improvement tables reject UPDATE/DELETE.
- [ ] Typed identity/crosswalk/alias records prevent cross-type, cross-venue, and ticker-reuse collisions; false fuzzy matches never auto-merge.
- [ ] Availability state, not event date alone, excludes planted future/unknown/inconsistent facts.
- [ ] Relational retrieval runs with Fuseki, Neo4j, and LLM services unavailable.
- [ ] Final `SemanticSnapshotId` is computed before projection; RDF and Neo4j carry it and a separate sealed receipt proves assertion and approved-entailment equivalence.
- [ ] Decision queries bind the full snapshot/release/receipt/cutoff context and emit sealed retrieval receipts.
- [ ] Transport/protocol/integrity errors normalize consistently; only declared equivalent templates may fall back.
- [ ] All six evidence domains emit deterministic, snapshot-bound packets with provenance and missingness.
- [ ] Versioned support rules ground every assessment in supporting/refuting observations; conflicts produce CONTESTED and missing requirements produce INSUFFICIENT/unknown.
- [ ] `InstrumentBeliefState` contains no trade parameter or universal confidence/probability.
- [ ] Hot-path modules cannot import RDF, Neo4j, Source Record, LLM, narrative, or unrestricted query types.
- [ ] Every challenger is compared with the permanent relational champion on holdout/adversarial cases.
- [ ] Promotion requires predeclared primary metric, minimum effect, multiplicity correction, and fixed retirement horizon; contaminated historical LLM cells are excluded.
- [ ] High-impact changes cannot promote without a different human approver.
- [ ] Exhausted remediation budget pauses ontology expansion while the baseline remains active.
- [ ] Semantic promotion alone has no economic authority; immutable activation cannot skip paper/live canaries.
- [ ] Canary cap/safety regression restores the prior safe activation and appends a rollback receipt.
- [ ] `RiskOverlaySet` can only tighten or veto, and no legacy `ExposureVector` reaches resumed Trading OS tasks.
- [ ] Semantic projection failure degrades explicitly to relational retrieval; baseline failure aborts decisioning.
