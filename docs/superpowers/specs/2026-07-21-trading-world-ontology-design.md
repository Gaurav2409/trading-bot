# Trading World Ontology — Design Amendment

> **Further amended on 2026-07-22:**
> `docs/superpowers/specs/2026-07-22-live-v1-architecture-amendment.md` controls live-product,
> portfolio, account/family and multi-asset boundaries. This document remains controlling for
> ontology releases, semantic snapshots, projection receipts, evaluation, and independent
> `DecisionFeatureActivation` before semantic features gain economic influence.

**Status:** Approved on 2026-07-21; validated post-review amendment approved on 2026-07-21

**Amends:** `2026-07-20-trading-os-design.md`, especially D13, D14/D14a, D28, and D30
**Research basis:** `docs/research/11-trading-world-ontology.md`
**Review basis:** `docs/research/12a-trading-world-ontology-moa-validation.md`

This revision incorporates only source-verified review findings. The validated synthesis supersedes
the raw MOA review wherever they conflict. The long-term hybrid decision is unchanged; the
amendments make its identity, projection, plan-splice, evaluation, and activation contracts
executable.

## 1. Decision

Build a full hybrid semantic-reasoning layer that covers technical, fundamental, sentiment,
macro/event, economic-relationship, and portfolio-context evidence.

The layer produces a snapshot-bound `InstrumentBeliefState`. It does not produce a target price,
position size, order, or execution instruction. A separate deterministic policy projects admitted
belief fields into strategy features and later generates trades.

The target architecture has:

1. a version-controlled OWL/SHACL ontology as the canonical semantic definition;
2. an append-only evidence ledger and content-addressed source store as factual history;
3. an RDF semantic projection for standards-native queries and validation;
4. a Neo4j operational projection for bounded relationship traversal;
5. ordinary snapshot-scoped relational retrieval as a permanent champion baseline; and
6. an offline, governed agentic improvement loop that diagnoses failures and proposes challengers;
7. separately versioned query, reasoning-policy, and feature-policy releases; and
8. a separately approved decision-feature activation state machine from shadow through bounded
   canary to broader paper or live influence.

This is a long-term architecture decision. Coding agents lower implementation cost, but the design
does not assume they remove data-quality, semantic-governance, operational, or evaluation risk.

## 2. Why the current plan is only partially sufficient

The approved Trading OS already contains much of the operational substrate:

- Neo4j causal-KG storage and deterministic, bounded traversal;
- provenance-gated edge admission and human review;
- valid-time fields, snapshot cutoffs, and future-edge rejection;
- a content-addressed `ValidatedDataSnapshotId`;
- strict containment of LLM outputs;
- historical event replay; and
- permanent rule-based trading baselines.

It does not yet define:

- Legal Entity → Issuer → Security → Listing → Ticker identity boundaries;
- ontology modules, stable term identifiers, releases, deprecation, or migration policy;
- the distinction between Source Record, Observation, Claim, Evidence Span, and Admitted Assertion;
- complete bitemporal and availability-time semantics;
- contradiction, missingness, refutation, and inapplicability states;
- a standards-native RDF projection;
- multi-domain evidence contracts;
- governed query templates and competency questions;
- an `InstrumentBeliefState` boundary; or
- a champion/challenger retrospective improvement loop for reasoning quality.

The existing causal KG becomes one governed projection and reasoning subdomain. It is not discarded.

## 3. Goals and non-goals

### Goals

- Give agents and deterministic policies a consistent, point-in-time view of the trading world.
- Prevent issuer, security, listing, and ticker identity errors.
- Preserve source evidence, derivation, revisions, contradictions, and uncertainty.
- Support bounded cross-domain reasoning without flattening every input into a generic signal.
- Make historical reasoning byte-reproducible from an explicit cutoff and release set.
- Compare semantic retrieval continuously against a simpler relational champion.
- Learn from failures through a governed, auditable agentic loop.
- Remain interoperable with financial and semantic standards without becoming dependent on one store.

### Non-goals

- Claim that an ontology creates investment alpha.
- Import all of FIBO or enable unrestricted OWL inference.
- Treat graph proximity or an asserted dependency as identified causality.
- Let an LLM directly admit facts, merge identities, change the ontology, or write the active graph.
- Permit unrestricted natural-language-to-SPARQL/Cypher in decisioning.
- Produce live trades from the reasoning layer.
- Modify the active ontology or policy during a decision cycle.
- Replace the append-only operational event log with a knowledge graph.

## 4. Core invariants

1. **Semantics, evidence, projection, and decision policy are separate layers.**
2. **The ontology source and append-only factual history are canonical; RDF and Neo4j are rebuildable.**
3. **Every decision-consumable answer binds an ontology version, semantic snapshot, and cutoff.**
4. **Every admitted assertion has provenance; absence of evidence is not evidence of absence.**
5. **LLMs propose and explain; governed code validates, admits, queries, and aggregates.**
6. **No universal truth/confidence scalar exists without outcome-specific forward calibration.**
7. **The relational retrieval baseline remains available even after ontology challengers win.**
8. **No agent can promote its own change.**
9. **High-impact semantic changes always require human approval.**
10. **The deterministic trading path consumes a strict projection, never raw narrative or graph walks.**
11. **Semantic release promotion never grants economic authority; decision-feature activation is a
    separate immutable, independently approved artifact.**
12. **`SemanticSnapshotId` is derived before projection from canonical semantic content; only a
    sealed projection receipt makes that snapshot queryable.**
13. **Event occurrence/effect time and publication/availability time remain distinct; there is no
    universal `occurred_at <= published_at` rule.**
14. **LLM knowledge-time contamination is measured separately from source-data point-in-time
    correctness and contaminated evaluation cells cannot support promotion.**

## 5. Storage and source-of-truth architecture

### 5.1 Canonical semantic source

The ontology lives in Git as modular Turtle/OWL and SHACL artifacts:

```text
ontology/
  modules/
    core.ttl
    identity.ttl
    time.ttl
    provenance.ttl
    evidence.ttl
    events.ttl
    reasoning.ttl
    technical.ttl
    fundamental.ttl
    sentiment.ttl
    macro.ttl
    relationships.ttl
    portfolio-context.ttl
  shapes/
    core.shacl.ttl
    identity.shacl.ttl
    evidence.shacl.ttl
    domains.shacl.ttl
    belief-state.shacl.ttl
  mappings/
    fibo.ttl
    prov-o.ttl
    owl-time.ttl
    identifiers.ttl
  queries/
    competency/
    decision/
  releases/
    <semantic-version>.json
```

Git history is authoring history. An `OntologyRelease` is an immutable build artifact containing
the semantic version, content hash, module hashes, mapping hashes, inference-ruleset hash,
canonical-IRI-scheme ID, SHACL report, compatibility report, migration reference,
author/reviewer identities, and approval. Its semantic-contract hash covers every meaning-bearing
artifact: OWL modules, SHACL shapes, external mappings, approved inference rules, and canonical IRI
encoding rules. Labels, examples, and other non-logical metadata are recorded separately so they
cannot hide a logical change.

Decision query templates form an immutable `QueryPackRelease`; approved causal/exposure motifs and
fitted structural weights plus domain `HypothesisSupportRuleRelease`s form an immutable
`ReasoningPolicyRelease`; strategy-specific feature allowlists form an immutable
`FeaturePolicyRelease`. These artifacts are versioned separately from the ontology because they
have different compatibility and promotion lifecycles. Every query, belief, evaluation, and
activation receipt binds their exact release IDs where applicable.

Term IRIs remain stable and do not contain the release number; each immutable ontology document
uses a release-specific `owl:versionIRI`. Released IRIs are never reused with a new meaning.
Deprecated terms remain resolvable, identify their replacements where one exists, and ship with a
machine-readable migration. Release numbering follows this policy:

- **MAJOR:** incompatible meaning, domain/range, identity, cardinality, or inference change;
- **MINOR:** backward-compatible classes, properties, shapes, mappings, or approved inference
  additions; and
- **PATCH:** labels, descriptions, examples, and other non-logical metadata only.

Compatibility checks compare the complete semantic contract, not only removed term IRIs or a
small set of SHACL predicates. A mapping, inference, canonical-IRI, domain/range, identity,
cardinality, or other meaning-changing difference requires the declared compatible migration and
the appropriate MAJOR release. `QueryPackRelease`, `ReasoningPolicyRelease`, and
`FeaturePolicyRelease` have equivalent compatibility reports and never inherit compatibility from
an unchanged ontology release.

Runtime consumers declare a supported release range. Historical SemanticSnapshots permanently
retain their original Ontology Release and migration chain. Release manifests are registered in
Postgres and publication is appended to the operational event log; Git tags alone are not runtime
authority.

### 5.2 Canonical factual history

- Postgres holds append-only Source Record metadata, observations, claims, identity candidates,
  admission/review decisions, supersessions, and provenance activities.
- TimescaleDB remains authoritative for time-series observations and their revisions.
- A content-addressed `SourceBlobPort` stores raw filings, releases, transcripts, news/vendor
  payloads, and evidence spans. Local development may use a filesystem implementation; deployed
  environments use an object-store implementation behind the same port.
- The existing Postgres operational event log remains authoritative for Trading OS state changes.

Corrections append a new record and supersession link. No source, observation, claim, identity,
or admission record is updated in place.

### 5.3 RDF semantic projection

Apache Jena Fuseki with TDB2 is the reference RDF projection. It supplies SPARQL access, named
graphs, transactional RDF storage, SHACL integration, backups, and bounded inference facilities.
The design uses SHACL Core plus explicitly approved SPARQL constraints and an application-owned,
bounded RDFS/OWL 2 RL-style entailment ruleset. Every allowed entailment has positive and negative
fixtures. Jena's own documentation warns that excessive inference can harm performance, so its
full OWL reasoner and unrestricted inference are prohibited in operational snapshots.

Official references: [Jena overview](https://jena.apache.org/documentation/index.html),
[TDB2](https://jena.apache.org/documentation/tdb2/index.html),
[SHACL](https://jena.apache.org/documentation/shacl/), and
[Fuseki inference configuration](https://jena.apache.org/documentation/fuseki2/fuseki-configuration.html).

Named graphs distinguish ontology releases, admitted assertion batches, provenance, approved
entailments, and internal portfolio context. A logical snapshot selects immutable graph sets; the
physical store may compact them without changing their hashes or meaning.

### 5.4 Neo4j operational projection

Neo4j remains the serving projection for:

- rule-admissible causal/exposure motifs;
- bounded relationship queries;
- anti-hub scoring and depth caps;
- graph algorithms approved for a specific policy; and
- human exploration of returned evidence paths.

Neo4j is never written independently. Projection builders consume only admitted ledger records
and a published Ontology Release. Every node and relationship carries canonical IDs, assertion
IDs, validity, provenance references, ontology version, and semantic snapshot ID.

### 5.5 SemanticSnapshot and projection seal

Semantic identity and physical projection receipts are separate to avoid a circular identifier.
`SemanticSnapshotId` is computed before either projection from the canonical semantic-content
manifest:

```text
SemanticContentManifest {
  validated_data_snapshot_id
  ontology_release_id
  evidence_cutoff
  admitted_assertion_set_hash
  source_manifest_hash
  inference_ruleset_hash
  canonical_iri_scheme_id
}

SemanticSnapshot {
  snapshot_id = SHA256(canonical(SemanticContentManifest))
  content_manifest
  created_at
}
```

RDF and Neo4j builders receive this final `snapshot_id`; there is no provisional ID visible to a
runtime query. After both builds finish, the equivalence gate emits:

```text
SemanticProjectionReceipt {
  receipt_id
  semantic_snapshot_id
  rdf_projection_hash
  neo4j_projection_hash
  projection_builder_version
  validation_report_hash
  equivalence_report_hash
  sealed_at
  status: SEALED
}
```

Both projections are rebuilt from the same content manifest. Cross-store equivalence tests compare
canonical assertion IDs, typed endpoint IRIs, validity, and the results of approved entailment
fixtures under the bound ruleset. Physical representation hashes may differ by store; the receipt
proves that their decision-visible semantics are equivalent. Any mismatch rejects the receipt.
Unsealed or rejected snapshots are never queryable, cached, activated, or used as fallback inputs.

## 6. Ontology modules and shared semantics

### 6.1 Identity and tradability

The required chain is:

```text
LegalEntity ─playsRole→ IssuerRole ─issues→ Security ─admittedAs→ Listing ─tradedAt→ Venue
                                                             └─hasAlias→ TickerAlias(valid interval, venue)
```

`LegalEntity`, `IssuerRole`, `Security`, `Listing`, `Venue`, and `TickerAlias` are never
interchangeable. Every canonical key is typed as `(entity_kind, canonical_id)`. Legal entities use
LEI where available; securities retain ISIN; venues use MIC; listings use a venue-scoped listing
identifier. A single string set is never used as a cross-type identity registry.

Identity crosswalks explicitly type their source and target kinds, source authority, evidence,
validity interval, and review state. Aliases are many-to-many temporal records keyed by alias kind,
normalized value, venue where applicable, and validity interval; ticker reuse or simultaneous
cross-venue/share-class aliases cannot overwrite one another. A governed `CanonicalIriEncoder`
turns typed canonical keys into absolute IRIs for RDF and the same canonical strings used by Neo4j
and relational fingerprints.

Fuzzy matches produce `IdentityCandidate` records with method, evidence, match class, and review
state. They never silently merge nodes. Mergers, spin-offs, ADR relationships, share-class
changes, ticker changes, and delistings are explicit events and relationships.

### 6.2 Time

Every applicable record distinguishes:

- `occurred_at`: when the world event happened;
- `published_at`: when a source made it public;
- `received_at`: when the vendor/system could access it;
- `valid_from` / `valid_to`: when a relationship or state held in the world;
- `recorded_at`: when the system recorded it;
- `superseded_at`: when a newer system record replaced it; and
- `decision_cutoff`: the latest admissible information for a reasoning run.

Historical evaluation filters by actual availability, not merely event date. Unknown or
inconsistent availability time makes the item ineligible for decisioning.

No universal ordering exists between `occurred_at` and `published_at`. Advance announcements may be
published before a future-effective event, while late reports may be published after occurrence.
Any additional ordering rule is scoped to a named event type. An explicit availability state
records `KNOWN`, `UNKNOWN`, or `INCONSISTENT`; only `KNOWN` items whose required availability fields
are at or before the decision cutoff are eligible.

### 6.3 Evidence and epistemic state

The evidence chain is:

```text
SourceRecord → EvidenceSpan → Claim → ReviewDecision → AdmittedAssertion
                         ↘ ExtractionActivity ↙
```

PROV-O concepts guide Entity/Activity/Agent derivation without importing the entire model into
every runtime object. Claims and observations can be `PROPOSED`, `ADMITTED`, `CONTESTED`,
`REFUTED`, `DEPRECATED`, or `REJECTED`.

Reasoning distinguishes:

- supported;
- contradicted/contested;
- insufficient evidence;
- missing data;
- stale data;
- inapplicable evidence; and
- explicit negative evidence.

These states never collapse into a single nullable field or generic confidence number.

## 7. Bounded evidence domains

All domains use the shared identity, time, provenance, and epistemic spine, but retain distinct
contracts.

### Technical

Price/volume observations, adjustment basis, timeframe, deterministic indicator definition,
lookback, data snapshot, and market-regime applicability. An indicator value is an observation,
not a bullish/bearish fact.

### Fundamental

Metric definition, issuer/security target, fiscal period, filing, accounting basis, currency,
publication/availability, restatement lineage, conservative lag, and peer/universe context.

### Sentiment and narrative

Document cluster, target, speaker, audience, language, source lineage, extraction/classification
method, model version, label, intensity band, and time. Syndicated copies share an origin cluster
and cannot count as independent corroboration.

### Macro and market events

Release/event identity, vintage, observation period, consensus, realized value, deterministic
surprise calculation, and the closed supply/demand/uncertainty plus threat/act/escalation shock
taxonomy from D14.

### Economic relationships

Supply, customer, ownership, competition, substitution, geography, product, regulation, and
jurisdiction assertions with validity and provenance. Causal/exposure use requires separately
approved motifs and structural weights; an asserted relationship alone is not causality.

### Portfolio context

Holdings, cash, factor/sector/currency exposure, liquidity, concentration, constraints, and risk
state. This is internal state in a separate graph namespace and is never represented as an
external-world fact.

Each domain evaluator produces a typed `EvidencePacket` with target, horizon, snapshot, applicable
regime, observations, supporting/refuting assertion IDs, supporting/refuting observation IDs, data
quality, freshness, missingness, deterministic numeric fields, and their evaluator/policy lineage.
An immutable `HypothesisSupportRuleRelease` declares how observations in each domain support,
refute, or remain neutral toward a hypothesis. Technical or fundamental observations therefore do
not become assertions, but they also cannot be accidentally treated as insufficient merely because
they lack an assertion ID.

## 8. Trust and admission pipeline

1. Capture the immutable source and all availability timestamps.
2. Resolve authoritative identifiers; retain ambiguous matches as candidates.
3. Produce a domain-specific Observation or proposed Claim.
4. Run OWL consistency/entailment checks and SHACL type/shape validation.
5. Check timestamp order, duplication/syndication, source independence, contradictions, author
   precision, and domain-specific admission rules.
6. Require human approval for high-impact identity, relationship, source-trust, and semantic
   changes.
7. Append the admission result and reason.
8. Build a SemanticSnapshot only from admitted inputs.

LLMs may extract typed claims and evidence spans, classify closed event/sentiment types, nominate
identity candidates, select an approved query template, and summarize returned evidence.

LLMs may not write admitted assertions, merge identities, create numeric causal strengths, execute
unrestricted graph queries for decisioning, change the active ontology, promote a release, or emit
trade parameters.

## 9. Query contract

Decision-consumable queries use reviewed templates with typed parameters:

```text
EvidenceQuery {
  template_id
  template_version
  query_pack_release_id
  semantic_snapshot_id
  semantic_projection_receipt_id
  target_ids[]
  horizon
  domain_filters[]
  relation_allowlist[]
  max_depth
  minimum_admission_state
  maximum_age
  decision_cutoff
}
```

Responses are sealed `RetrievalReceipt`s. They return facts plus assertion/observation IDs, evidence
paths, validity, provenance, contradictions, missingness, query-pack/template versions, snapshot and
projection-receipt IDs, projection used, and fallback/degraded status. Packet builders reject a
receipt whose hash or complete request binding does not match.

Unrestricted SPARQL/Cypher remains research-only. An agent can map natural language to an approved
template and typed parameters, but decisioning never executes agent-authored graph text.

Initial competency questions include:

- Which tradable listings represented securities issued by entities exposed to supplier X at
  cutoff T?
- Which admitted assertions supporting the answer were available before T?
- Which relationships were stale, contradicted, inferred, or missing?
- Which technical, fundamental, sentiment, macro, relationship, and portfolio evidence supports
  or refutes hypothesis H at horizon Z?
- What changed between semantic snapshots S1 and S2, and why did the answer change?
- Does the RDF answer equal the Neo4j answer for every shared decision template?

## 10. InstrumentBeliefState and deterministic trade boundary

An `InstrumentHypothesis` is a falsifiable proposition with target, direction, horizon, regime
assumptions, and invalidation conditions.

```text
HypothesisAssessment {
  hypothesis_id
  status: SUPPORTED | CONTESTED | INSUFFICIENT | INAPPLICABLE
  evidence_quality_band
  freshness_band
  supporting_assertion_ids[]
  refuting_assertion_ids[]
  supporting_observation_ids[]
  refuting_observation_ids[]
  contradiction_ids[]
  missingness[]
  applicable_regimes[]
}

InstrumentBeliefState {
  instrument_id
  semantic_snapshot_id
  validated_data_snapshot_id
  ontology_release_id
  assessments[]
  evidence_packet_ids[]
  unresolved_identity_candidates[]
  abstention_reasons[]
  generated_at
}
```

`BeliefStateBuilder` is deterministic and versioned. It preserves competing hypotheses and does
not force all domains into one score.

The deterministic trading layer does not consume raw RDF, Neo4j paths, Source Records, narrative,
or arbitrary fields from the belief state. A `DecisionFeatureProjector` uses a strategy-specific
positive allowlist: unknown or unapproved keys are absent, and no policy is required to allowlist
every producer key. It verifies deterministic lineage and emits two closed outputs:

```text
DecisionFeatureSet → DeterministicStrategyPolicy → HotPathCandidate
RiskOverlaySet → RiskEngine (tighten or veto only)
```

`DecisionFeatureSet` contains only approved deterministic numeric observations and closed
categorical assessments. `RiskOverlaySet` replaces the legacy KG `ExposureVector`; it contains
versioned relationship/portfolio constraints and multipliers bounded to `(0, 1]`, so it cannot
increase position size, risk limits, or leverage. Sizing, compliance, and execution never accept
beliefs, graph paths, or agent-authored fields.

Producing those objects does not authorize their economic use. A separate immutable
`DecisionFeatureActivation` binds the exact ontology, query-pack, reasoning-policy, support-rule,
feature-policy, deterministic-strategy, evaluation-manifest, and approved scope. Its mode is one of
`DISABLED`, `SHADOW`, `PAPER_CANARY`, `PAPER_ACTIVE`, `LIVE_CANARY`, or `LIVE_ACTIVE`. Every runtime
decision binds its actual validated-data snapshot, semantic snapshot, sealed projection receipt,
and activation ID. A semantic release can be active for research while all feature activations
remain `DISABLED` or `SHADOW`.

LLM-originated values can cross only as closed classifications through code-owned mappings and
only where the existing tighten-only or gate/rank rules permit them. Numeric technical,
fundamental, macro, and portfolio values may cross only when produced by deterministic evaluators
from a validated data snapshot.

## 11. Relational retrieval baseline

Ordinary snapshot-scoped relational retrieval is a permanent champion, not temporary scaffolding.
It answers the same competency questions from typed Postgres/Timescale records and bounded joins,
without RDF entailment or Neo4j traversal.

Every evaluation runs at least:

1. relational retrieval champion;
2. ontology/RDF challenger; and
3. ontology/Neo4j challenger for shared relationship questions.

Raw-document retrieval may be retained as a diagnostic comparison but is not the safety baseline.
The champion remains operational after semantic promotion to detect drift and provide fallback.

## 12. Agentic retrospective improvement loop

The loop is offline and event-driven:

```text
Observe failure
  → create FailureCase
  → classify root cause
  → create ChangeProposal
  → build challenger release
  → replay training/regression cases
  → evaluate untouched holdout + adversarial cases
  → shadow deploy
  → semantic promotion decision
  → create separately governed DecisionFeatureActivation candidate
  → bounded paper canary
  → paper active, reject, or roll back
  → later live canary after every base live blocker clears
  → live active or roll back
  → record Outcome
```

### Durable artifacts

- `FailureCase`: question, externally grounded expected answer, actual answer, trace, complete
  snapshot/release binding, severity, reporter, and label provenance.
- `Diagnosis`: closed root-cause class (`identity`, `coverage`, `temporal`, `extraction`, `ontology`,
  `query`, `inference`, `aggregation`, `explanation`, `data`, `retrieval`, `evidence`, `model`,
  `policy`, or `execution`), evidence, affected components, confidence band, and reviewer.
- `ChangeProposal`: exact patch, risk class, rationale, affected competency questions.
- `ExperimentManifest`: frozen datasets, cases, metrics, thresholds, cost/latency budgets, seeds,
  model IDs and available knowledge cutoffs, ontology/builder/query/reasoning/feature versions,
  pre-registered primary metric, minimum material effect, multiplicity rule, protected metrics,
  fixed retirement horizon, and remediation budget.
- `ExperimentOutcome`: metric deltas, regressions, reviewer findings, promotion decision, rollback.
- `DecisionFeatureActivation`: immutable economic-authority candidate, exact artifact bindings,
  scope, mode, independent approval, prior activation, and rollback target.
- `CanaryManifest` / `CanaryReceipt`: capped symbols/notional/exposure, minimum observation horizon,
  protected-metric alarms, stop conditions, observed outcomes, and automatic rollback evidence.

### Agent roles

- Evaluator: detects and reproduces reasoning failures.
- Root-cause analyst: classifies identity, coverage, temporal, extraction, ontology, query,
  inference, aggregation, or explanation faults.
- Ontology steward: proposes vocabulary, constraint, mapping, or migration patches.
- Data steward: proposes source, identity, lineage, or quality-rule corrections.
- Query steward: proposes bounded query-template changes.
- Red-team reviewer: searches for leakage, overfitting, unsupported inference, and hidden regressions.

Roles may share infrastructure or models, but an authoring agent cannot serve as the sole evaluator
or promoter of its own change. Authority separation is based on durable role and principal
identities; distinct model IDs are not mandatory unless an experiment explicitly studies model
diversity.

### Promotion authority

**Always human-approved:** term meaning, class/property semantics, identity merges, causal or
economic relationships, source-trust policy, admission rules, belief aggregation, and changes that
alter decision features.

**Initially human-approved:** SHACL constraints, external-standard mappings, and query templates.
These may earn automatic promotion only after a separately approved policy demonstrates that the
change class is low risk and consistently passes holdout, shadow, rollback, and equivalence gates.

**Potentially automatable later:** additive aliases backed by authoritative identifiers, metadata
corrections that do not change identity/meaning, and query rewrites proven semantically equivalent.

No agent can edit active releases or active evidence. Semantic promotion publishes a new immutable
semantic release; it does not activate decision features. Feature activation always requires its
own approved artifact and a successful prior state:

```text
DISABLED → SHADOW → PAPER_CANARY → PAPER_ACTIVE
PAPER_ACTIVE + all base live blockers → LIVE_CANARY → LIVE_ACTIVE
```

No transition may skip shadow or its applicable canary. Canary failure automatically restores the
prior activation, appends the rollback event, and leaves the semantic release available for
research/audit if it remains semantically valid.

## 13. Evaluation and falsifiability

### Semantic/data quality

- Entity-resolution precision/recall by entity type, with catastrophic false merges reported
  separately.
- Claim/relationship precision, evidence coverage, contradiction rate, staleness, and deprecation
  latency.
- Zero admitted future facts in planted-leakage tests.
- Complete decision-consumable provenance.
- Byte-reproducible answers for identical snapshots and templates.
- Exact cross-projection equivalence for shared query contracts.

### Agent reasoning

Compare champion and challengers on factual precision, completeness, source entailment, citation
correctness, contradiction detection, appropriate abstention, missing-knowledge behavior, latency,
and cost. Cases include false premises, deleted required facts, ambiguous identities, stale facts,
syndicated sentiment, corrections, and regime changes.

Historical LLM evaluations also run a pre-registered knowledge-time contamination protocol. Record
model and fine-tune knowledge cutoffs where available; stratify cases before and after those
cutoffs; run retrieval, no-retrieval, masked-entity, and masked-outcome variants; and mark a correct
answer unsupported by admissible evidence as contaminated rather than a retrieval success. If
cutoff metadata is unavailable, masking and no-retrieval probes must bound contamination or the
cell is non-promotable. Contaminated cells never contribute to a primary promotion statistic.

An ontology challenger is promotable only when it clears all safety metrics, meets frozen
cost/latency budgets, shows a pre-registered material improvement on at least one primary reasoning
metric, clears its minimum effect size and multiplicity rule, and causes no disallowed regression
on the untouched holdout and adversarial suites. A convenient improvement on any one of many
metrics is not sufficient.

### Exposure and later economic value

Reasoning quality is the v1 required gate. Exposure/risk evaluation is secondary: compare against
sector lookup, direct-link relationships, static ownership, and no-ontology baselines using
historical point-in-time replays.

Net-of-cost return improvement becomes a required gate only after a deterministic trade policy is
added. Semantic/reasoning promotion cannot satisfy that economic gate or change activation mode.
The existing rule-null, buy-and-hold comparison, DSR/CPCV, and forward-paper gates remain, followed
by bounded canary evidence before broader economic influence.

### Remediation and pause policy

Each evaluation pilot freezes its maximum candidate cycles, elapsed time, compute/reviewer budget,
and material-improvement thresholds before the first challenger is built. Failures enter the
improvement loop until this budget is exhausted.

Pause ontology expansion—not baseline operation—when the frozen remediation budget is exhausted
without a promotable challenger, maintenance cost exceeds its frozen benefit threshold, or safety
failures persist. The fixed retirement horizon states how many independently evaluated challenger
generations may run before this decision; it is never an unspecified `N`. The relational champion
continues operating and evidence is retained for future diagnosis.

## 14. Error handling and degraded operation

| Failure | Behavior |
|---|---|
| Invalid Ontology Release | Reject publication; active release remains unchanged. |
| RDF/Neo4j/ledger mismatch | Reject projection receipt; snapshot remains unsealed and unqueryable. |
| Semantic transport/service timeout or outage | Use relational baseline only for an equivalent reviewed template; mark reasoning degraded. |
| Malformed, corrupt, or semantically mismatched projection answer | Reject the answer; use an equivalent reviewed baseline where one exists, otherwise fail closed. |
| Missing/ambiguous identity | Do not merge; abstain for affected instrument. |
| Missing provenance or availability time | Exclude assertion from decisioning. |
| Query timeout or depth breach | Abort semantic query; use bounded baseline where equivalent. |
| Unsupported inference | Return explicit insufficient/unknown state. |
| Improvement agents unavailable | Freeze active release; normal reasoning continues. |
| Stale cached reasoning result | Reject unless semantic snapshot, validated-data snapshot, ontology/query/policy releases, and cutoff all match the request. |
| Shadow or canary regression | Automatically remove challenger/activation and restore the prior activation. |
| Missing or mismatched activation/canary receipt | Keep feature influence disabled; no economic transition. |
| Baseline unavailable | Fail closed for decisioning; do not let ontology become the sole path. |

Fallbacks are explicit in the `InstrumentBeliefState` and audit trail. A degraded answer never
silently masquerades as a normal ontology answer.

## 15. Security, integrity, and licensing

- Treat every external document as untrusted data, not instructions.
- Store raw content separately from prompts, templates, and ontology source.
- Allowlist extraction schemas, query templates, relation types, and endpoints.
- Sign/hash Ontology Releases, SemanticSnapshots, projection receipts, query/reasoning/feature
  releases, experiment manifests, feature activations, and canary receipts.
- Enforce least privilege: extractors cannot admit; authors cannot promote; runtime readers cannot
  write source or ontology stores.
- Record source licences, permitted transformations, retention, and redistribution constraints.
- Redact secrets and personal data from graph projections and experiment traces.
- Include prompt-injection and evidence-spoofing cases in the adversarial suite.

## 16. Testing strategy

### Ontology and constraints

- Parse every module and mapping.
- Run SHACL positive/negative fixtures.
- Test approved entailments and prohibited entailments.
- Test stable IRIs, deprecation, semantic-version compatibility, mappings, inference-rule changes,
  canonical-IRI rules, and migrations.

### Temporal and identity

- Plant future sources, late arrivals, corrections, ticker reuse, mergers, spin-offs, ADRs,
  delistings, and ambiguous names.
- Assert that historical snapshots reconstruct only what was actually available.
- Treat a false merge as a dedicated safety failure, not an ordinary accuracy miss.
- Verify advance announcements where `published_at < occurred_at`, late reports where the reverse
  holds, and unknown availability without imposing a universal ordering.
- Verify typed crosswalks, venue-scoped temporal aliases, and absolute canonical IRIs.

### Projection contracts

- Rebuild RDF and Neo4j from the same manifest.
- Compare assertion ID sets, endpoints, types, validity, and query results.
- Verify projection stores reject independent writes at the application boundary.
- Prove the precomputed `SemanticSnapshotId` keys both projections and only a matching sealed
  `SemanticProjectionReceipt` makes them queryable.
- Prove emitted RDF uses the ontology/SHACL vocabulary and credential-level runtime writes fail.

### Query and belief contracts

- Execute every competency template against relational, RDF, and applicable Neo4j paths.
- Test depth, relation, admission, freshness, and cutoff constraints.
- Delete required knowledge and assert correct abstention.
- Ensure `DecisionFeatureProjector` cannot represent rationale, raw LLM JSON, unrestricted graph
  handles, or non-allowlisted fields.
- Test observation-only support/refutation rules separately from assertion support.
- Inject unknown producer keys and prove every strategy-specific positive allowlist excludes them.
- Normalize timeout, transport, protocol, decoding, and equivalence failures into explicit fallback
  or fail-closed outcomes.

### Improvement-loop controls

- An author cannot approve its own proposal.
- No proposal can edit an active release.
- Holdout cases remain unavailable to proposing agents.
- Failed shadow releases roll back reproducibly.
- Promotion is impossible without the required human decision for its risk class.
- Run retrieval/no-retrieval/masked evaluation variants and exclude contaminated cells.
- Reject semantic-promotion-to-economic-activation shortcuts.
- Reject every state transition that skips paper/live canary evidence; test caps, horizons, alarms,
  immutable receipts, and automatic rollback.

## 17. Changes required in the existing plan

Before implementing the current 37-task plan, revise it as follows:

1. **Foundation:** add canonical identity, time, evidence, ontology-release, and semantic-snapshot
   types immediately after the core value objects. Identity registries and aliases are typed and
   point-in-time; the canonical IRI encoder is shared by every projection.
2. **Ports:** add `OntologyRegistryPort`, `EvidenceLedgerPort`, `SourceBlobPort`,
   `SemanticGraphPort`, projection-builder contracts/fakes, `QueryPackRegistryPort`, and
   `DecisionFeatureActivationPort`.
3. **D13:** add the content-addressed source store and Jena Fuseki/TDB2 semantic projection.
4. **D14/D14a:** broaden the causal KG into the economic-relationship subdomain; keep all six
   admission gates and deterministic traversal safeguards. The ontology sequence owns its Neo4j
   projection instead of modifying a file created only by skipped base tasks.
5. **D28:** precompute a final `SemanticSnapshotId`, build both projections under it, and require a
   sealed `SemanticProjectionReceipt` rather than a bare KG edge-set version.
6. **Slow research:** make analyst and LLM outputs proposed Claims/Observations with evidence spans,
   not decision facts.
7. **Reasoning:** add domain EvidencePacket builders, governed queries, `BeliefStateBuilder`, and
   `DecisionFeatureProjector`; make observation support/refutation an explicit, versioned contract.
8. **D30:** move the hard seam to `DecisionFeatureSet → deterministic policy → HotPathCandidate`;
   replace the skipped `ExposureVector` contract with a tighten-only `RiskOverlaySet`; keep all raw
   narrative and graph access structurally unreachable.
9. **Evaluation:** add the relational reasoning champion, competency suite, differential retrieval
   harness, LLM knowledge-time contamination protocol, agentic retrospective loop, shadow
   releases, material-effect gates, and rollback.
10. **Activation:** separate semantic promotion from feature activation; require immutable
    `DecisionFeatureActivation` plus bounded paper/live canary states and receipts.
11. **Plan splice:** provide concrete replacements for every resumed consumer of skipped base
    `ExposureVector`, traversal, weight, and KG replay artifacts before resuming at Task 18.
12. **Acceptance:** require semantic promotion, separately approved feature activation, applicable
    canary evidence, and all existing economic/live gates before ontology-derived features can
    affect orders or risk.

Risk/execution/compliance implementation may proceed independently where its interfaces do not
depend on belief-state semantics. Ontology-dependent slow-research and causal-KG tasks must use the
revised contracts.

## 18. Adversarial verdict

The ontology is justified as a semantic correctness, evidence, retrieval, exposure, and audit
layer. It is not justified as an autonomous market-understanding or alpha engine.

The most dangerous failure is not a query error; it is a coherent but false answer created from a
bad identity merge, stale assertion, duplicated source, future fact, unsupported causal path, or
LLM-authored guess. The design therefore makes provenance, temporal reconstruction, contradiction,
abstention, baseline comparison, and independent promotion authority load-bearing.

Option A is worthwhile if it improves reasoning under these constraints. If repeated governed
challengers cannot beat ordinary relational retrieval within a pre-registered remediation budget,
the semantic system remains available for research/audit where useful, but its expansion and
decision-policy integration pause.

## 19. Delivery sequence

1. Publish the glossary and ontology-kernel release process.
2. Implement identity, time, provenance, evidence, and Source Record foundations.
3. Implement the relational champion and competency suite before semantic projections.
4. Build RDF and Neo4j projections plus cross-store equivalence tests.
5. Add all six bounded domain contracts and evidence-packet builders.
6. Build governed queries and `InstrumentBeliefState`.
7. Run semantic champion/challenger evaluation and the retrospective loop in paper/research mode.
8. Create a `SHADOW` feature activation only after semantic promotion; it has no order/risk effect.
9. Run a bounded `PAPER_CANARY`, then allow `PAPER_ACTIVE` only with a valid canary receipt.
10. Evaluate exposure/risk and net-of-cost trading utility under the existing gates.
11. After every base live blocker clears, require a separate `LIVE_CANARY` before `LIVE_ACTIVE`.

## 20. Validated review resolution

The following findings from `12a-trading-world-ontology-moa-validation.md` are controlling:

| Validated finding | Design resolution | Implementation-plan owner |
|---|---|---|
| Proposed and sealed snapshot IDs can diverge | Precompute `SemanticSnapshotId`; seal projections with a separate receipt | Ontology Tasks 5–7 |
| Compatibility ignores meaning-bearing artifacts | Hash and diff modules, shapes, mappings, inference, and IRI rules; version query/reasoning/feature packs separately | Ontology Task 1 |
| Flat identity maps collapse types/time | Typed canonical keys, typed crosswalks, temporal venue-scoped aliases, canonical IRI encoder | Ontology Tasks 2 and 8 |
| Observation-only packets become insufficient | Versioned per-domain observation support/refutation rules and IDs | Ontology Tasks 10–12 |
| Semantic errors do not all reach fallback/closed behavior | Normalize transport, protocol, decoding, and mismatch outcomes by equivalence policy | Ontology Tasks 9 and 15 |
| Ontology Task 6 modifies a skipped-task file | Ontology sequence creates and owns the Neo4j semantic projection | Ontology Task 6 |
| Resumed tasks consume skipped KG artifacts | Replace them with `DecisionFeatureSet`, `RiskOverlaySet`, and semantic replay contracts | Ontology Task 15; base Tasks 18, 19, 32, 34, 35 |
| RDF projection vocabulary and IDs evade SHACL/IRI guarantees | One ontology vocabulary plus a validated canonical IRI encoder | Ontology Tasks 2 and 5 |
| Semantic promotion can leak into economic authority | Separate immutable `DecisionFeatureActivation` | Ontology Tasks 14–15; base Tasks 32, 34, 36 |
| Historical LLM memory can contaminate point-in-time tests | No-retrieval/masked probes and non-promotable contaminated cells | Ontology Task 13; base Tasks 34–35 |
| Shadow can jump to broad activation | Mandatory paper/live canary states, receipts, caps, alarms, and rollback | Ontology Task 14; base Tasks 34 and 36 |

The following raw-review claims are explicitly rejected and must not reappear in the plan:

- unlisted numeric keys pass the positive feature allowlist;
- every producer feature must appear in some allowlist;
- same-author policy approval lacks an existing guard;
- the relational champion or competency fixtures must move ahead of their prerequisites;
- `occurred_at <= published_at` is a universal temporal invariant;
- N-Triples loses named-graph identity in the specified single-graph Graph Store API;
- the synchronous feature projector is inherently an async deadlock;
- Alembic filenames alone prove multiple heads; or
- role independence requires distinct model IDs.
