# Ontology Hardening Implementation Plan

**Date:** 2026-07-22
**Trigger:** `docs/research/16-core-ttl-schema-audit.md` (core.ttl schema audit)
**Controlling spec:** `docs/superpowers/specs/2026-07-22-live-v1-architecture-amendment.md` (§7 relational
champion; RDF/Neo4j are rebuildable projections)
**ADRs:** `docs/adr/0004-split-ontology-schema-from-instance-validation.md`,
`docs/adr/0005-model-issuer-as-time-scoped-role.md`

## Context

The nine-day V1 delivered an ontology **kernel** (Task 11): stable names for 11 concepts, 3 object
properties, 4 timestamp/hash fields, plus a content-addressed release and a relational champion. The
audit accepts this as milestone scaffolding but identifies two foundation defects to repair before any
agent depends on the graph, and stages a governed expansion. This plan turns the audit's P0/P1/P2
recommendations into tasks.

Non-negotiable invariants (unchanged): relational snapshot-scoped retrieval is the permanent decision
champion; Fuseki and Neo4j are rebuildable projections that never own truth; ontology-derived features
influence economics only through an effective `DecisionFeatureActivation`; graph size / inferred-triple
count / fluent explanations are never success metrics.

## Status legend

- **[P0]** — implemented in this plan's PR (repair the build contract before reliance).
- **[P1] / [P2]** — planned and specified here; **not executed** in this PR. Each is a future task.

---

## P0 — repair the semantic build contract (implemented now)

### Task H1 [P0]: Split ontology-schema validation from instance-snapshot validation

**Files:** `src/trading_os/ontology/releases.py`, `src/trading_os/ontology/instance_validation.py`,
`tests/unit/ontology/test_release.py`, `tests/unit/ontology/test_instance_validation.py`

- The release builder must validate the **ontology document** (parse, require an ontology IRI +
  `owl:versionIRI`, lint) and must NOT apply instance-targeted SHACL to the vocabulary.
- A separate `validate_instance_snapshot(facts, shapes)` applies SHACL to actual canonical facts and
  returns a report (conforms + violations) plus the rejected facts.
- Red test: the current "empty vocabulary conforms" behavior is replaced — schema validation checks
  document conventions; instance validation is exercised against real focus nodes.

### Task H2 [P0]: Model EvidencePacket links; remove the no-op shape

**Files:** `ontology/core.ttl`, `ontology/shapes/core.shacl.ttl`,
`tests/unit/ontology/test_instance_validation.py`

- Remove the `sh:minCount 0` EvidencePacket constraint (always-satisfied no-op per SHACL spec).
- Add explicit `tw:containsClaim` / `tw:isDerivedFrom` relationships so a packet references claims and
  evidence rather than being mis-inferred as a `Claim` via `supportedBy`'s domain.
- `Claim tw:supportedBy SourceRecord` stays a separate relationship.

### Task H3 [P0]: Field rules — timezone, cardinality, payload-hash, name alignment

**Files:** `ontology/shapes/core.shacl.ttl`, `ontology/core.ttl`,
`tests/unit/ontology/test_instance_validation.py`

- SourceRecord: exactly one `payload_hash` with a declared algorithm/format pattern; `publishedAt`,
  `receivedAt` are timezone-qualified `xsd:dateTime` (naive datetimes fail).
- Align the RDF field name with the Python model: rename `sourceRecordHash` → `payload_hash`.
- Negative fixtures: duplicate hashes, zone-less timestamps, and missing required provenance fail.

### Task H4 [P0]: Ontology/version metadata in Turtle + release manifest

**Files:** `ontology/core.ttl`, `src/trading_os/ontology/releases.py`,
`src/trading_os/ontology/manifest.py`, `tests/unit/ontology/test_release.py`

- Declare the ontology IRI and `owl:versionIRI` (plus prior-version/imports where relevant) inside
  `core.ttl`; schema validation fails if version metadata is absent.
- `SemanticReleaseManifest` hashes every meaning-bearing artifact (ontology modules, shapes, and
  named policies), bound to a clean Git commit; the manifest hash — not raw two-file bytes — is the
  release identity. Whitespace/comment-only changes must not change the manifest hash of unchanged
  meaning.

### Task H5 [P0]: Negative safety tests

**Files:** `tests/unit/ontology/test_negative_safety.py`

Prove these fail (never silently conform):
- malformed source record (missing required provenance),
- future-data leakage (a fact whose receipt time is after the decision cutoff),
- false identity merge (two distinct securities asserted identical without a governed identity
  assertion),
- stale snapshot (a semantic snapshot older than its freshness policy),
- unsupported entailment (a `supportedBy` misuse that would infer the wrong type).

---

## P1 — minimum useful reasoning ontology (planned; not executed here)

Build small reviewed modules, not one giant `core.ttl`. Each is a future task with its own tests.

- **Task H6 [P1] Identity/tradability module:** `LegalEntity`, time-scoped `IssuerRole` (per ADR-0005),
  `Security`/`Instrument`, `Listing`, `Venue`, identifier, ticker alias, broker instrument, validity
  interval, identity-assertion status/confidence.
- **Task H7 [P1] Time/provenance module:** occurrence/effective/publication/receipt/cutoff times;
  `SourceRecord`, `EvidenceSpan`, extraction + admission activities (PROV-O aligned), source family,
  correction/supersession lineage.
- **Task H8 [P1] Evidence/reasoning module:** `Observation`, `Claim`, `AdmittedAssertion`,
  `Contradiction`, `EvidencePacket`, `InstrumentHypothesis` (with horizon), `InstrumentBeliefState`,
  `SemanticSnapshot`.
- **Task H9 [P1] Events/relationships module:** typed corporate + macro events; issuer/security/
  sector/commodity/FX exposure paths; distinguish observed vs contractual relationship vs causal
  hypothesis.
- **Task H10 [P1] Technical/fundamental/sentiment markers:** typed marker definitions with unit,
  window, sampling frequency, horizon, calculation version, direction, freshness, corroboration policy.
- **Task H11 [P1] Portfolio-context module:** account/mandate/beneficial-owner, holding, reservation,
  exposure, concentration, currency, completeness state. Broker balances/execution stay in the
  operational relational ledger; project only governed facts.

---

## P2 — prove usefulness rather than merely grow (planned; not executed here)

- **Task H12 [P2] Competency-query pack:** a versioned pack derived from concrete agent questions
  (candidate evidence, contradictions, freshness, tradability, portfolio context), each with golden
  answers, counterexamples, cutoff-leakage and identity-trap cases. Extends the relational baseline
  beyond today's `evidence_for(instrument_id, data_snapshot_id)`.
- **Task H13 [P2] Projection parity + challenger evaluation:** relational, RDF and Neo4j answers must
  agree on the exact snapshot; disagreement degrades to the relational champion and is recorded.
  Evaluate the challenger on answer correctness, provenance completeness, cutoff safety, false merges,
  latency, degradation, and incremental decision value.
- **Task H14 [P2] Governed promotion:** a semantic feature is promoted only when it improves a sealed
  downstream evaluation without harming protected safety metrics, gated by `DecisionFeatureActivation`.

## Acceptance for this PR (P0 only)

- Ontology-schema and instance-snapshot validation are separate code paths (ADR-0004).
- No no-op SHACL constraints remain; EvidencePacket links are modeled.
- Timezone/cardinality/hash/name-alignment rules enforced with negative fixtures.
- `core.ttl` carries `owl:versionIRI`; release identity is a manifest hash over meaning-bearing
  artifacts.
- Negative safety tests fail for malformed/leaky/false-merge/stale/unsupported-entailment cases.
- `make verify` green; relational champion remains the production baseline.
