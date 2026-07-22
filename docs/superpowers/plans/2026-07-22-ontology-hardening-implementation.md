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

> **Revised after Hermes MoA improvement review** (2026-07-22, `deep-research`, 3/3 refs LIVE;
> `docs/research/raw/ontology-hardening/17-p1p2-hermes-moa-review.md`). Key changes: added a
> dependency-manifest task H0; **reordered to H6 → H7 → H9 → H8 → H11 → H10** so a module never
> references terms it doesn't import; split identity from tradability and time from provenance; and
> made temporal/cutoff safety, correction lineage, false-merge, and projection leakage first-class.

- **Task H0 [P1] Module dependency manifest (build BEFORE H6):** machine-readable `owl:imports` DAG
  plus a per-module ontology IRI and `owl:versionIRI` recorded in the `SemanticReleaseManifest`. The
  build fails if any module references a term outside its import closure. This is what keeps manifest
  hashing (H4) and projection parity (H13) honest as modules multiply.
- **Task H6a [P1] Identity canonicalization:** `LegalEntity`, time-scoped `IssuerRole` (ADR-0005),
  `Security`/`Instrument`, `Listing`, `Venue`, identifier, ticker alias, `BrokerInstrument`, validity
  interval, and a governed `IdentityAssertion` (status `candidate|asserted|confirmed|disputed|
  rejected|superseded`, confidence, validity, provenance). Identity/broker-instrument links use a
  typed, revocable `tw:mapsToInstrument` with a validity interval — **never `owl:sameAs` or functional
  properties** (open-world `sameAs` propagates merges transitively and irreversibly). SHACL rejects
  two distinct Securities asserted equivalent without a governed `IdentityAssertion`; a SPARQL
  constraint rejects one broker instrument mapped to two Securities in overlapping intervals.
- **Task H6b [P1] Tradability / capability:** `VenueSegment`, `ListingStatus`, `BrokerInstrument`
  orderability, `Restriction`, `CircuitBand`, settlement, `DataEntitlement`, `AccountCapabilityAssignment`,
  `TradabilityRiskPacket` — each account/snapshot/policy-scoped and deny-by-default. Keeps the broad
  discovery universe and the account tradable allowlist provably distinct (spec §4, §8).
- **Task H7a [P1] Time module:** `owl:imports <http://www.w3.org/2006/time>`; declare
  `tw:occurredAt`, `tw:effectiveAt`, `tw:publishedAt`, `tw:receivedAt`, `tw:decisionCutoffAt`,
  `tw:snapshotId`, each with explicit domain and `sh:maxCount 1`; bind `SemanticSnapshot` to a cutoff.
  Intervals map to `time:Interval`/`hasBeginning`/`hasEnd` with a **documented half-open convention**
  and an explicit open-interval sentinel (never null-defaults-to-now). Instance validation rejects any
  admitted fact with `receivedAt > decisionCutoffAt`. **No universal `occurred-before-published` or
  `published ≤ received` axiom** — guidance is future-effective and backfilled/embargoed data is real;
  gate on **receipt-vs-cutoff only**.
- **Task H7b [P1] Provenance module:** `owl:imports <http://www.w3.org/ns/prov>`; `SourceRecord`/
  `Claim`/`EvidenceSpan`/`SemanticSnapshot` as `prov:Entity`; `ExtractionActivity`/`AdmissionActivity`/
  `ProjectionBuildActivity` as `prov:Activity`; extractor/model/human/policy as `prov:Agent`; use
  `prov:used`/`wasGeneratedBy`/`wasDerivedFrom`/`wasAttributedTo`/`wasRevisionOf`/`generatedAtTime`/
  `invalidatedAtTime`. Model correction/supersession as a `CorrectionActivity` with mandatory
  `prov:used` → superseded record and `prov:wasRevisionOf` on the new record; SHACL rejects a
  correction lacking a superseded target and rejects in-place mutation of the superseded fact. A
  separate `tw:ForwardGuidanceRecord` shape explicitly **allows** `effectiveAt > receivedAt`.
  Provenance proves lineage, not correctness — admission status stays orthogonal.
- **Task H9 [P1] Events/relationships module:** typed corporate + macro events; issuer/security/
  sector/commodity/FX exposure paths. A `tw:RelationshipAssertion` superclass carries a mandatory
  `tw:relationshipType` enum (`OBSERVED|CONTRACTUAL|CAUSAL_HYPOTHESIS|INFERRED`), confidence, subject/
  object roles, provenance and validity interval; SHACL rejects a `RelationshipAssertion` lacking
  `relationshipType`; causal/inferred relationships are risk-only unless corroborated and activated.
- **Task H8 [P1] Evidence/reasoning module (imports H9):** `Observation`, `Claim`, `AdmittedAssertion`,
  `Contradiction` (must name an opposing target — reject self-/target-less contradiction),
  `EvidencePacket`, `InstrumentHypothesis` (with horizon), plus `SourceFamily`, `EvidenceSpan`,
  `ExtractionModelVersion`, `AdmissionPolicyRelease`, `AssertionStatus`. Every `AdmittedAssertion`
  links to an admission activity + policy + source record/span. Syndicated/same-`SourceFamily` copies
  cannot count as independent corroboration.
- **Task H8b [P1] Belief-state projection (imports H9, H10):** `InstrumentBeliefState`,
  `SemanticSnapshot` binding, and the categorical-only `DecisionFeatureSet` projection — emitted only
  through an effective `DecisionFeatureActivation`. Split out of H8 because it depends on events (H9)
  and markers (H10).
- **Task H11 [P1] Portfolio-projection context:** an explicit **projection allowlist** — projectable =
  concentration *band* / exposure *category* / completeness-dimension enum / mandate metadata / policy
  release IDs / partition metadata; relational-only = cash buckets, buying power, order quantities,
  fill prices, cost basis. A `tw:PortfolioProjectionShape` with `sh:closed true` fails on any raw
  quantity/cash/price/fill literal; a separate shape forbids household pooling of buying power/cash/
  orders across accounts (spec §5).
- **Task H10 [P1] Technical/fundamental/sentiment markers (imports H8/H9):** typed marker definitions
  with unit, window, sampling frequency, horizon, calculation version, direction, freshness, and a
  corroboration policy.
- **Task H11b [P1] Governance/release module:** first-class `SemanticRelease`/`ShapeRelease`/
  `MappingRelease`/`QueryPackRelease`/`InferencePolicyRelease`/`PolicyAssignment` with effective
  interval, supersession and approval evidence, so every answer is reproducible from exact releases.

---

## P2 — prove usefulness rather than merely grow (planned; not executed here)

- **Task H12 [P2] Competency-query pack:** ≥3 queries per module, with mandatory coverage of
  identity-disambiguation, cutoff-leakage, correction/supersession, contradiction, and
  portfolio-completeness. Every query ships ≥1 positive golden + ≥1 expected-empty counterexample +
  ≥1 cutoff-exclusion case, each with its SPARQL text, expected rows, a poisoned graph, and a p95
  latency budget; CI fails otherwise. Extends the relational baseline beyond today's
  `evidence_for(instrument_id, data_snapshot_id)`.
- **Task H13 [P2] Projection parity + challenger evaluation:** relational, RDF and Neo4j answers must
  agree on the exact snapshot; disagreement degrades to the relational champion and is recorded.
  Define `relational_champion_score` (precision / recall / p95 latency on the H12 pack) as the null
  hypothesis. A challenger is eligible only if `recall ≥ champion` AND `precision ≥ champion − ε`
  (ε ≤ 0.05) AND **zero new** cutoff-leakage AND **zero new** false-merge positives AND ≥1
  pre-specified metric improves by a meaningful out-of-sample effect size on a frozen evaluation
  manifest. "Incremental decision value" = change in a sealed, out-of-sample retrospective outcome
  metric attributable to the feature — never in-sample query counts.
- **Task H14 [P2] Governed promotion and demotion:** a semantic feature is promoted only when H13
  passes, gated by `DecisionFeatureActivation`, with the frozen evaluation manifest stored as
  provenance **before** activation and a cooldown via `PromotionPolicyRelease`. Add a
  `DecisionFeatureDeactivation` (immutable release mirroring activation) and **automatic
  demotion-to-research-only on any protected-safety-metric regression** — turning a feature off is a
  policy release, never a code change.

## Acceptance for this PR (P0 only)

- Ontology-schema and instance-snapshot validation are separate code paths (ADR-0004).
- No no-op SHACL constraints remain; EvidencePacket links are modeled.
- Timezone/cardinality/hash/name-alignment rules enforced with negative fixtures.
- `core.ttl` carries `owl:versionIRI`; release identity is a manifest hash over meaning-bearing
  artifacts.
- Negative safety tests fail for malformed/leaky/false-merge/stale/unsupported-entailment cases.
- `make verify` green; relational champion remains the production baseline.
