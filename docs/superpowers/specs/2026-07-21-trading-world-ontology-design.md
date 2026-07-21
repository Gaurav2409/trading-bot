# Trading World Ontology — Design Amendment

**Status:** Design approved; written amendment awaiting file review

**Amends:** `2026-07-20-trading-os-design.md`, especially D13, D14/D14a, D28, and D30
**Research basis:** `docs/research/11-trading-world-ontology.md`

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
6. an offline, governed agentic improvement loop that diagnoses failures and proposes challengers.

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
the semantic version, content hash, module hashes, mapping versions, inference ruleset, SHACL
report, compatibility report, migration reference, author/reviewer identities, and approval.

Term IRIs remain stable and do not contain the release number; each immutable ontology document
uses a release-specific `owl:versionIRI`. Released IRIs are never reused with a new meaning.
Deprecated terms remain resolvable, identify their replacements where one exists, and ship with a
machine-readable migration. Release numbering follows this policy:

- **MAJOR:** incompatible meaning, domain/range, identity, cardinality, or inference change;
- **MINOR:** backward-compatible classes, properties, shapes, mappings, or query templates; and
- **PATCH:** labels, descriptions, examples, and other non-logical metadata only.

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

### 5.5 SemanticSnapshot

`SemanticSnapshot` is the reproducibility boundary:

```text
SemanticSnapshot {
  snapshot_id
  ontology_release_id
  evidence_cutoff
  admitted_assertion_set_hash
  source_manifest_hash
  inference_ruleset_id
  rdf_projection_hash
  neo4j_projection_hash
  projection_builder_version
  validation_report_hash
  created_at
}
```

Both projections are rebuilt from the same manifest. Cross-store equivalence tests compare
canonical assertion IDs, endpoint types, validity, and approved entailments. Any mismatch rejects
the snapshot; neither partial projection becomes active.

## 6. Ontology modules and shared semantics

### 6.1 Identity and tradability

The required chain is:

```text
LegalEntity ─issues→ Security ─admittedAs→ Listing ─tradedAt→ Venue
                                          └─hasAlias→ Ticker(valid interval)
```

`Issuer`, `Security`, `Listing`, and `Ticker` are never interchangeable. Legal entities use LEI
where available; securities and listings retain ISIN and venue identifiers; venues use MIC.
Vendor IDs and names are temporal aliases, not canonical identity.

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
regime, observations, supporting/refuting assertion IDs, data quality, freshness, missingness, and
deterministic derived fields.

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
  semantic_snapshot_id
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

Responses return facts plus assertion IDs, evidence paths, validity, provenance, contradictions,
missingness, query-template version, projection used, and fallback/degraded status.

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
or arbitrary fields from the belief state. A `DecisionFeatureProjector` allowlists deterministic
numeric observations and closed categorical assessments, verifies their lineage, and emits a
strategy-specific `DecisionFeatureSet`. A versioned deterministic policy then produces a
`HotPathCandidate`; sizing, risk, compliance, and execution remain unchanged.

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
  → human/automatic policy gate
  → promote, reject, or roll back
  → record Outcome
```

### Durable artifacts

- `FailureCase`: question, expected answer, actual answer, trace, snapshot, severity, reporter.
- `Diagnosis`: root-cause class, evidence, affected components, confidence band, reviewer.
- `ChangeProposal`: exact patch, risk class, rationale, affected competency questions.
- `ExperimentManifest`: frozen datasets, cases, metrics, thresholds, cost/latency budgets, seeds,
  model IDs, ontology/builder/query versions, and remediation budget.
- `ExperimentOutcome`: metric deltas, regressions, reviewer findings, promotion decision, rollback.

### Agent roles

- Evaluator: detects and reproduces reasoning failures.
- Root-cause analyst: classifies identity, coverage, temporal, extraction, ontology, query,
  inference, aggregation, or explanation faults.
- Ontology steward: proposes vocabulary, constraint, mapping, or migration patches.
- Data steward: proposes source, identity, lineage, or quality-rule corrections.
- Query steward: proposes bounded query-template changes.
- Red-team reviewer: searches for leakage, overfitting, unsupported inference, and hidden regressions.

Roles may share infrastructure or models, but an authoring agent cannot serve as the sole evaluator
or promoter of its own change.

### Promotion authority

**Always human-approved:** term meaning, class/property semantics, identity merges, causal or
economic relationships, source-trust policy, admission rules, belief aggregation, and changes that
alter decision features.

**Initially human-approved:** SHACL constraints, external-standard mappings, and query templates.
These may earn automatic promotion only after a separately approved policy demonstrates that the
change class is low risk and consistently passes holdout, shadow, rollback, and equivalence gates.

**Potentially automatable later:** additive aliases backed by authoritative identifiers, metadata
corrections that do not change identity/meaning, and query rewrites proven semantically equivalent.

No agent can edit active releases or active evidence. Promotion publishes a new immutable release.

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

An ontology challenger is promotable only when it clears all safety metrics, meets frozen
cost/latency budgets, shows a pre-registered material improvement on at least one primary reasoning
metric, and causes no disallowed regression on the untouched holdout and adversarial suites.

### Exposure and later economic value

Reasoning quality is the v1 required gate. Exposure/risk evaluation is secondary: compare against
sector lookup, direct-link relationships, static ownership, and no-ontology baselines using
historical point-in-time replays.

Net-of-cost return improvement becomes a required gate only after a deterministic trade policy is
added. The existing rule-null, buy-and-hold comparison, DSR/CPCV, and forward-paper gates remain.

### Remediation and pause policy

Each evaluation pilot freezes its maximum candidate cycles, elapsed time, compute/reviewer budget,
and material-improvement thresholds before the first challenger is built. Failures enter the
improvement loop until this budget is exhausted.

Pause ontology expansion—not baseline operation—when the frozen remediation budget is exhausted
without a promotable challenger, maintenance cost exceeds its frozen benefit threshold, or safety
failures persist. The relational champion continues operating and evidence is retained for future
diagnosis.

## 14. Error handling and degraded operation

| Failure | Behavior |
|---|---|
| Invalid Ontology Release | Reject publication; active release remains unchanged. |
| RDF/Neo4j/ledger mismatch | Reject SemanticSnapshot; no partial activation. |
| Semantic projection unavailable | Use relational baseline; mark reasoning degraded. |
| Missing/ambiguous identity | Do not merge; abstain for affected instrument. |
| Missing provenance or availability time | Exclude assertion from decisioning. |
| Query timeout or depth breach | Abort semantic query; use bounded baseline where equivalent. |
| Unsupported inference | Return explicit insufficient/unknown state. |
| Improvement agents unavailable | Freeze active release; normal reasoning continues. |
| Shadow regression | Automatically remove challenger and restore prior active release. |
| Baseline unavailable | Fail closed for decisioning; do not let ontology become the sole path. |

Fallbacks are explicit in the `InstrumentBeliefState` and audit trail. A degraded answer never
silently masquerades as a normal ontology answer.

## 15. Security, integrity, and licensing

- Treat every external document as untrusted data, not instructions.
- Store raw content separately from prompts, templates, and ontology source.
- Allowlist extraction schemas, query templates, relation types, and endpoints.
- Sign/hash Ontology Releases, SemanticSnapshots, query templates, and experiment manifests.
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
- Test stable IRIs, deprecation, semantic-version compatibility, and migrations.

### Temporal and identity

- Plant future sources, late arrivals, corrections, ticker reuse, mergers, spin-offs, ADRs,
  delistings, and ambiguous names.
- Assert that historical snapshots reconstruct only what was actually available.
- Treat a false merge as a dedicated safety failure, not an ordinary accuracy miss.

### Projection contracts

- Rebuild RDF and Neo4j from the same manifest.
- Compare assertion ID sets, endpoints, types, validity, and query results.
- Verify projection stores reject independent writes at the application boundary.

### Query and belief contracts

- Execute every competency template against relational, RDF, and applicable Neo4j paths.
- Test depth, relation, admission, freshness, and cutoff constraints.
- Delete required knowledge and assert correct abstention.
- Ensure `DecisionFeatureProjector` cannot represent rationale, raw LLM JSON, unrestricted graph
  handles, or non-allowlisted fields.

### Improvement-loop controls

- An author cannot approve its own proposal.
- No proposal can edit an active release.
- Holdout cases remain unavailable to proposing agents.
- Failed shadow releases roll back reproducibly.
- Promotion is impossible without the required human decision for its risk class.

## 17. Changes required in the existing plan

Before implementing the current 37-task plan, revise it as follows:

1. **Foundation:** add canonical identity, time, evidence, ontology-release, and semantic-snapshot
   types immediately after the core value objects.
2. **Ports:** add `OntologyRegistryPort`, `EvidenceLedgerPort`, `SourceBlobPort`,
   `SemanticGraphPort`, and projection-builder contracts/fakes.
3. **D13:** add the content-addressed source store and Jena Fuseki/TDB2 semantic projection.
4. **D14/D14a:** broaden the causal KG into the economic-relationship subdomain; keep all six
   admission gates and deterministic traversal safeguards.
5. **D28:** bind `ValidatedDataSnapshotId` to a validated `SemanticSnapshotId` rather than a bare
   KG edge-set version.
6. **Slow research:** make analyst and LLM outputs proposed Claims/Observations with evidence spans,
   not decision facts.
7. **Reasoning:** add domain EvidencePacket builders, governed queries, `BeliefStateBuilder`, and
   `DecisionFeatureProjector`.
8. **D30:** move the hard seam to `DecisionFeatureSet → deterministic policy → HotPathCandidate`;
   keep all raw narrative and graph access structurally unreachable.
9. **Evaluation:** add the relational reasoning champion, competency suite, differential retrieval
   harness, agentic retrospective loop, shadow releases, and rollback.
10. **Acceptance:** require reasoning-quality promotion before the deterministic trading policy may
    consume ontology-derived features.

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
8. Permit deterministic policy integration only after semantic promotion.
9. Evaluate exposure/risk utility, then later net-of-cost trading utility under existing gates.
