# Independent MOA Adversarial Review — Trading World Ontology

> **Validation status: `NO-GO` for treating this raw synthesis as authoritative.** Three independent lenses found reversed mechanisms, overstated severities, and missing evaluation/governance controls. Use the controlling [validated synthesis](/Users/I321170/Documents/Projects/trading-bot/docs/research/12a-trading-world-ontology-moa-validation.md:1), which preserves the high-confidence findings and explicitly retracts or downgrades the unsound ones below.
>
> **Status:** Advisory review of the approved research, design, and coordinated implementation plans. It does not modify those source documents.
>
> **Method:** Three sequential Hermes `deep-research` Mixture-of-Agents passes over the same four-file, 383,582-byte corpus, followed by structural stitching and three independent adversarial verifier lenses. Source anchors use filenames plus exact headings, task names, APIs, types, tests, or quoted phrases.
>
> **Decision vocabulary:** `GO` means usable as written for the stated stage; `REVIEW` means useful but amendments are required before that stage; `NO-GO` means the proposed capability should not proceed at that stage. Proposed thresholds are hypotheses until pre-registered and measured.

## 1. Executive verdict, usefulness, and falsifiability

### 1.1 Verdict in one page

**(a) Conceptual usefulness: GO.** The approved design cleanly separates ontology, evidence ledger, projections, belief state, deterministic decision features, risk sizing, and broker execution (`2026-07-21-trading-world-ontology-design.md` §4 "Core invariants"), so a bounded semantic-evidence layer fills a genuine gap the relational plan leaves open — issuer/security/listing/ticker conflation, no assertion-vs-world-fact distinction, and unspecified cross-domain integration.

**(b) Safety architecture: GO with mandatory review of two load-bearing seams.** The invariants (LLMs propose / governed code admits; projections rebuildable; relational baseline permanent; author ≠ approver) are correct and enforceable, but the `DecisionFeatureProjector` allowlist and the policy-mediated auto-promotion path each admit a runtime bypass that no current test catches (§1.5 F1, F2).

**(c) Implementation readiness: REVIEW.** Task interfaces follow disciplined red-green-refactor, but the relational champion and competency suite sit behind three infrastructure milestones, so a fundamental RDF/Neo4j projection defect would be discovered only after high sunk cost (§1.5 F3), and the snapshot-equivalence fingerprint semantics for approved entailments are undecided (§1.5 F4).

**Unique contribution beyond snapshot-scoped relational retrieval:** versioned identity resolution across legal-entity/issuer/security/listing/ticker with merge lineage; typed epistemic states (ADMITTED/CONTESTED/REFUTED/DEPRECATED) without per-domain schema duplication; cross-domain contradiction detection through a shared assertion spine; standards-aligned PROV-O/OWL-Time provenance for external audit; deterministic ontology-version diffing between `SemanticSnapshot` pairs; and SHACL-enforced structural prohibition of `targetPrice`/`orderQuantity` in belief state (design §5–§10).

**What it cannot contribute:** source truth from missing/late data, causality from a graph path, or investment alpha. It is credited with alpha only after the plan's own net-of-cost, post-cutoff, forward-paper gates (design §13).

**Recommendation: proceed only after amendments.** Do not stop the program and do not begin full semantic-projection integration until the four P1 findings are remediated and the relational champion is built first as the permanent comparison and fallback.

### 1.2 Strongest steelman

**Benefit 1 — Identity-integrity prevents contamination cascades.** *Mechanism:* design §6.1 makes `LegalEntity → Security → Listing → Ticker` distinct and routes fuzzy matches to `IdentityCandidate` human review; mergers/ADRs/ticker-reuse are explicit events. *Workflow:* every competency answer, exposure vector, and calibration cell keyed on `instrument_id` is protected from wrong-entity binding. *Falsifiable measure:* on ≥50 planted corporate-event cases (design §16 identity class), the ontology arm achieves entity-link precision **[P]** ≥ 0.95 with zero catastrophic false merges versus the ticker-keyed relational champion.

**Benefit 2 — Point-in-time discipline makes historical evaluation honest.** *Mechanism:* §6.2 separates `occurred_at`/`published_at`/`received_at`/`recorded_at`/`superseded_at`/`decision_cutoff`; `SemanticSnapshotBuilder` rejects cross-store mismatch (§5.5). *Workflow:* Task 35 KG replay and Task 34 promotion consume only evidence admissible at event as-of. *Falsifiable measure:* zero admitted future facts in planted look-ahead suites; `test_projection_equivalence` rejects every snapshot carrying a post-cutoff assertion.

**Benefit 3 — Contradiction/missingness enable honest abstention.** *Mechanism:* `HypothesisAssessment.status` distinguishes SUPPORTED/CONTESTED/INSUFFICIENT/INAPPLICABLE and `EvidenceAnswer` carries `missingness`/`contradiction_ids`; a NULL relational row conflates all of these. *Workflow:* HITL and audit can separate "no evidence" from "contradicted" from "inapplicable." *Falsifiable measure:* on ≥30 adversarial cases with planted contradictions and deletions (Task 13), `appropriate_abstention` ≥ champion and no ANSWERED status when required claims are deleted.

**Benefit 4 — Cross-domain integration with shared provenance.** *Mechanism:* all six `EvidencePacket` builders share one `PacketContext` spine, letting `BeliefStateBuilder` mark a hypothesis CONTESTED when a relationship packet refutes a technical packet on the same entity (design §7, §10). *Workflow:* `DecisionFeatureProjector` can refuse to project features from a CONTESTED belief — a structural guard flat signal tables lack. *Falsifiable measure:* `test_belief_builder` confirms a refuting packet yields CONTESTED and the projector raises `ForbiddenDecisionFeature` when the strategy allowlist excludes it.

**Benefit 5 — Projection auditability via rebuildable equivalence.** *Mechanism:* §5.5 requires RDF and Neo4j to rebuild from one manifest with exact assertion/fingerprint equality or the snapshot is rejected. *Workflow:* proves operational Neo4j traversal and standards-native RDF represent the identical admitted ledger. *Falsifiable measure:* byte-reproducible answer hashes and exact cross-projection fingerprint equivalence for every shared decision template.

**Benefit 6 — Governed improvement instead of self-modification.** *Mechanism:* §12 forbids an author from being sole evaluator/promoter and requires durable `FailureCase`/`Diagnosis`/`ChangeProposal`/`ExperimentManifest`/`ExperimentOutcome`; `ShadowMonitor` atomically rolls back on safety regression; `RemediationBudget` caps expansion. *Workflow:* the ontology is repaired without live-cycle mutation and failed challengers are diagnosed, not silently abandoned. *Falsifiable measure:* every promoted challenger improves ≥1 pre-registered reasoning metric versus `relational_champion` with no safety regression on the untouched holdout.

### 1.3 Strongest adversarial case

**H1 — Semantic overhead delays the deterministic v1 baseline.** *Anchor:* implementation plan "Global Constraints … Execute Trading OS Tasks 1–14 first"; design §19 step 3. *Symptom:* Fuseki, TDB2, and the Turtle toolchain go live before any paper trade; the relational champion (Task 4) is exercised only after four milestones. *Consequence:* unstable ontology infra blocks Trading OS Task 18 and the 90-day paper clock never starts. *Kill/rollback:* if ontology Tasks 1–4 are not completable within one sprint, defer to a parallel research branch and unblock Task 18 from the relational baseline alone (design §11).

**H2 — `DecisionFeatureProjector` allowlist bypassed by a new domain.** *Anchor:* Task 12 `DecisionFeatureProjector` docstring; design §10. *Symptom:* a seventh domain adds a `deterministic_features` key that passes `forbidden_lineage_keys` but is absent from every `numeric_allowlist`, and no test enumerates domain keys against policies. *Consequence:* non-deterministic/LLM-origin numbers reach `DecisionFeatureSet`, violating D4/D30 at runtime with green tests. *Kill/rollback:* block release until a test proves every domain feature key is accounted for in at least one policy (F1).

**H3 — Projection drift via approved entailments silently changes answers.** *Anchor:* Task 7 `SemanticSnapshotBuilder`; design §5.5. *Symptom:* an OWL 2 RL rule adds a derived triple with no ledger fingerprint, so either every entailment-bearing snapshot fails to seal or entailments are silently excluded from equivalence. *Consequence:* semantic reasoning is blocked, or inferred facts escape the audit check. *Kill/rollback:* formally decide entailment fingerprint semantics before writing projection code; reject snapshots until the equivalence rule is deterministic (F4).

**H4 — Authoritative-crosswalk merge propagates non-locally.** *Anchor:* research §6.2 objection 3; design §6.1. *Symptom:* GLEIF ISIN→LEI maps a subsidiary ISIN to a same-named parent via an authoritative (non-fuzzy) method that bypasses human review. *Consequence:* every path touching the parent is contaminated; calibration accrues to the wrong entity; replays invalidate. *Kill/rollback:* planted authoritative-crosswalk error must register as a catastrophic false merge with nonzero count blocking promotion (design §13).

**H5 — Point-in-time leakage via unknown availability time.** *Anchor:* design §6.2; implementation plan Global Constraint "Unknown or inconsistent availability time makes the item ineligible for decisioning." *Symptom:* a replay answer includes a source with `received_at` after cutoff, unknown receipt, or a post-cutoff correction. *Consequence:* historical performance and reasoning quality are invalid. *Kill/rollback:* any future-fact leak is a zero-tolerance safety failure — reject snapshot and challenger (design §13 protected metrics).

**H6 — Syndication dedup fails, inflating corroboration.** *Anchor:* design §7 sentiment; Task 8 `AdmissionPolicy`; Task 11 `test_syndicated_articles_are_one_evidence_family`. *Symptom:* `origin_cluster_ids` are supplied by the caller; an extractor assigns distinct IDs to the same wire story, so `independent_source_count` reports 2. *Consequence:* a contested sentiment claim is ADMITTED instead of PROPOSED on fabricated corroboration. *Kill/rollback:* cluster IDs must be resolved from the ledger by a governed clustering service, not accepted from the proposal (F5).

**H7 — Improvement loop contaminates the holdout.** *Anchor:* Task 14 `ExperimentManifest.sealed_holdout_set_id`; design §12 "Holdout cases remain unavailable to proposing agents." *Symptom:* live `FailureCase`s from the same distribution are folded into training while the holdout is not re-sealed, so repeated cycles align challengers to the holdout. *Consequence:* promotions rest on metrics that no longer measure out-of-distribution generalization. *Kill/rollback:* freeze the holdout at v1; any expanded holdout is a new experiment with a new manifest hash (F-note in §1.4 E9).

**H8 — Both paths down yields stale-snapshot decisioning.** *Anchor:* design §14 "Baseline unavailable → Fail closed"; Task 15 `RelationalChampionUnavailable`, `ReasoningResultStorePort.get()`. *Symptom:* a cache hit returns a prior-cycle `InstrumentBeliefState` whose `semantic_snapshot_id` differs from the current `ValidatedDataSnapshotId`. *Consequence:* decisioning proceeds against stale evidence while appearing current, violating exact-snapshot binding. *Kill/rollback:* `SemanticDecisionHandoff.prepare()` must assert `DecisionFeatureSet.snapshot_id == request.semantic_snapshot_id` and raise otherwise (F-adjacent to F8).

**H9 — Evaluation gaming converts semantic gains into alpha claims.** *Anchor:* design §13 "Exposure and later economic value"; research §5. *Symptom:* improved citation/abstention scores are cited to justify decision-policy integration before exposure/risk or net-of-cost gates clear. *Consequence:* ontology features enter policy prematurely. *Kill/rollback:* ontology-derived decision features remain disabled until semantic promotion clears AND the separate DSR/CPCV/cost/replay/forward-paper gates pass.

### 1.4 Falsification and value-of-information plan

All experiments hold fixed: `ValidatedDataSnapshotId`, `SemanticSnapshotId`, ontology release, `decision_cutoff`, prompt/model versions, strategy, sizing/risk/execution config, and a pre-registered frozen corpus. Every experiment compares `relational_champion` with ≥1 graph arm (`rdf_challenger`, `neo4j_challenger`, or both). Thresholds marked **[P]** are proposals requiring empirical calibration, not validated facts.

| Exp | Question | Arms | Primary metrics | Corpus | Research vs trading |
|---|---|---|---|---|---|
| E1 | Entity-link accuracy | champion (ticker key) vs `ontology_identity` (LEI/ISIN + temporal alias) | precision, recall, catastrophic false merges on ≥50 planted corporate events | held-out entity-event fixtures | research only |
| E2 | Answer quality + abstention | champion vs `rdf_challenger` vs `neo4j_challenger` | factual precision/recall, source entailment, citation correctness, appropriate abstention, missing-knowledge score; incl. 20 false-premise + 20 deleted-fact | `competency_cases.json` frozen at Task 4 | research only |
| E3 | Point-in-time correctness | all arms | future-fact leaks (zero-tolerance), publication/receipt cutoff fidelity on planted late arrivals | temporal fixture set (Task 7) | data integrity |
| E4 | Causal-claim precision | `ontology_relationship` vs `direct_sector_lookup` vs `no_relationship` | fraction of asserted links with an identified public mechanism; label hypothesis vs identified effect | ≥30 labeled supply/customer links from filings public before a fixed date | knowledge quality |
| E5 | Latency/cost | all arms on E2 corpus | p50/p95 latency, per-query LLM cost, DB time, degraded-fallback rate | E2 corpus | operational |
| E6 | Reproducibility | all arms | byte-identical answers and `packet_id` for identical snapshot+query across two runs; cross-projection fingerprint equality | E2 subset | integrity |
| E7 | Trading-policy containment | `ontology_challenger` vs champion | zero non-allowlisted `DecisionFeatureSet` fields; zero trade parameters in belief state; `test_hot_path_imports` passes; sizing insensitive to belief rationale | structural, no market data | safety gate |
| E8 | Exposure/risk ranking | `ontology_relationship` vs sector-lookup vs direct-link-only vs no-ontology | Spearman ρ vs realized cross-sectional returns; top-minus-bottom spread net of costs; turnover | COVID-2020 & Russia/Ukraine-2022 point-in-time replays (Task 35) | risk utility (separated from alpha) |
| E9 | Promotion-gate validity | `reasoning_promotion.yaml` | zero promotions when catastrophic_false_merges>0 or future_fact_leaks>0; requires ≥1 primary-metric gain; no protected-metric regression; holdout re-seal enforced | adversarial metric suite | governance |

**Proposed thresholds [P] (not validated):** E1 precision ≥ 0.95, zero catastrophic merges; E2 abstention ≥ champion, factual precision not worse by > 5 pp; E4 ≥ 70% of links mechanism-backed; E8 Spearman ρ ≥ 0.10 (matching the existing manifest field). **Financial outcome is a separate, later gate:** net-of-cost return improvement is required only after a deterministic trade policy exists (design §13), never inferred from research metrics.

### 1.5 Material findings from this lens

| ID | Severity | Source anchor | Finding | Consequence | Remediation | Validation test |
|---|---|---|---|---|---|---|
| F1 | P1 | Task 12 `DecisionFeatureProjector`; design §10 | `test_hot_path_imports.py` checks module imports, not runtime data flow; no test asserts every domain `deterministic_features` key is present in some `FeaturePolicy.numeric_allowlist`. | A new domain can route non-deterministic/LLM-origin numerics into `DecisionFeatureSet` with green CI, violating D4/D30. | Enumerate all `EvidencePacketContent` subclasses' feature keys and assert each appears in ≥1 frozen allowlist; fail CI otherwise. | Add `test_all_domain_feature_keys_are_accounted_in_some_policy` to `test_decision_feature_seam.py`. |
| F2 | P1 | Task 14 `PromotionAuthority.decide()`; design §12 | Self-approval check is `approver_id == author_id`; a LOW-risk change auto-promotes via an `AutoPromotionPolicy` whose `human_approved_by` may equal the proposal author, giving policy-mediated self-approval. | An agent authors both a policy and a matching proposal and auto-promotes without human review. | If `proposal.author_id == proposal.policy.human_approved_by`, force MEDIUM (human-gated) regardless of declared risk. | Add `test_policy_approved_by_same_author_requires_human` to `test_promotion_authority.py`. |
| F3 | P1 | Global Constraints; design §19 step 3 | Relational champion (Task 4) + competency suite (Task 13) sit behind three infrastructure milestones and 12 tasks. | A projection defect surfaces only after high sunk cost, forcing re-architecture of Tasks 5–7. | Promote Task 4 to run immediately after Trading OS Task 14; gate Task 5 (Fuseki) on E2 passing against the relational baseline. | Require `competency_cases.json` + `test_relational_champion.py` to pass before any projection task starts. |
| F4 | P1 | Task 7 `SemanticSnapshotBuilder`; `fingerprint.py`; design §5.5 | Design does not specify whether approved OWL 2 RL entailments belong in the assertion-set/fingerprint. Entailed triples have no ledger fingerprint, so either every entailment-bearing snapshot fails to seal or entailments silently escape equivalence. | Semantic reasoning is blocked, or inferred facts bypass the audit check. | Decide and document entailment fingerprint semantics; if included, add `entailment_set_hash` to `SemanticSnapshotBuildRequest` and the fingerprint. | Integration test with ≥1 approved entailment asserting deterministic seal-or-exclude behavior. |
| F5 | P2 | Task 8 `AdmissionPolicy.evaluate()`; design §8 | `origin_cluster_ids` is caller-supplied; the policy counts distinct IDs without verifying they came from the governed dedup pipeline. | Agent-fabricated cluster IDs create false corroboration; a contested claim is ADMITTED with `independent_source_count=2`. | Carry `source_record_ids` on `ClaimProposal`; resolve clusters from the ledger via a governed `SourceClusteringService` before counting. | `test_syndicated_sources_count_as_one_origin` must verify cluster IDs come from ledger lookup, not the proposal. |
| F6 | P2 | Task 1 `build_release()` vs `OntologyReleaseRegistry.publish()`; design §12 | `authored_by != approved_by` is enforced only in `build_release`; `publish()` accepts any `OntologyRelease` without re-checking. | A release object built outside `build_release` could be published self-approved. | Re-assert `authored_by != approved_by` in `publish()` as defense-in-depth. | Add `test_publish_rejects_self_approved_release` to `test_ontology_registry.py`. |
| F7 | P2 | Task 8 `minimum_author_precision`; research §2.3 (COLING 2020, 78% precision) | Threshold is externally supplied with no specified calibration protocol; a fixed value admits low-quality claims or blocks good ones. | Systematic, invisible admission bias upstream of the economic gate. | Bootstrap-calibrate on ≥200 labeled claims by entity/relation type; record value + date in `admission.yaml`; re-measure after model/prompt changes. | `test_admission_precision_calibration.py` asserts config value ≥ latest measured lower bound. |
| F8 | P2 | Task 15 `ReasoningResultStorePort.get()`; design §14 | A cache hit can return a prior-cycle belief state whose `semantic_snapshot_id` differs from the current `ValidatedDataSnapshotId`; handoff does not re-verify binding. | Decisioning proceeds on stale evidence while appearing current, breaking exact-snapshot binding. | `SemanticDecisionHandoff.prepare()` asserts `DecisionFeatureSet.snapshot_id == request.semantic_snapshot_id` and raises otherwise. | Plant a stale result in the store; assert handoff raises rather than returns it. |
| F9 | P3 | Task 5 `infra/fuseki/config.ttl`; design §5.3 | Read-only Fuseki config specifies no inference stanza and relies on Jena defaults; default RDFS entailment could inject derived triples into query results. | Query equivalence (E2/E6) fails silently on class-hierarchy questions. | Pin an explicit empty reasoner on the read-only endpoint; apply entailments only in the build profile and record `inference_ruleset_id` in the manifest. | Contract test queries an uploaded subclass assertion and confirms no RDFS-derived triples appear at the read-only endpoint. |

<!-- CHUNK-A SELF-AUDIT: 1/1 top-level sections emitted; three explicit verdicts (GO / GO-with-review / REVIEW); 6 benefits; 9 failure hypotheses; champion-controlled experiment matrix (E1–E9, every arm vs relational_champion, snapshot/prompts/strategy/risk/execution/corpus held fixed); every material finding has severity+anchor+consequence+remediation+validation test; research-quality separated from trading outcomes; proposed thresholds marked [P], no invented alpha; no truncation -->

## 2. Architecture and semantic correctness review

### 2.1 Layer and authority map

| Layer/artifact | Authority | Mutability | Version key | Rebuild source | Allowed writers / readers | Failure direction | May affect economic state? |
|---|---|---|---|---|---|---|---|
| Ontology source + releases | Git-owned OWL/Turtle/SHACL + runtime `OntologyReleaseRegistry` (Git tags are not runtime authority) | Source mutable pre-release; `OntologyRelease` immutable post-publication | `OntologyReleaseId` (SHA-256), semver, module/mapping/shape hashes, `owl:versionIRI` | Git modules/shapes/mappings via `build_release` | Writers: ontology steward + distinct human approver; readers: snapshot builders, validators, query registry, bootstrap | Reject invalid release; prior active release unchanged | Indirectly — only by changing admitted query/feature semantics |
| Append-only factual/evidence ledger | `PostgresEvidenceLedger` + content-addressed `SourceBlobPort` | Insert-only; corrections supersede, never update | `claim_id`/source/observation/admission IDs, content hashes, `recorded_at`, supersession links | Raw blobs + source metadata + extraction/review/admission records | Writers: capture/extract/`AdmissionPolicy`; high-impact identity/relation human-approved; LLMs may not write; readers: relational/RDF/Neo4j builders, champion | Fail closed; missing provenance rejects claim | No directly — affects belief only after feature projection |
| Validated data + `SemanticSnapshot` manifests | `SemanticSnapshotBuilder` (reproducibility boundary) | Immutable once sealed | `ValidatedDataSnapshotId`, `SemanticSnapshotId`, `ontology_release_id`, assertion/source/projection hashes | Canonical data/evidence ledgers + release + projection builders | Writers: correctness layer + snapshot builder after equivalence gate; readers: all decision/replay paths | Reject partial/mismatched snapshot; no partial activation | Yes — every decision-consumable answer must bind these |
| RDF canonical/standards representation (Fuseki/TDB2) | Standards-native projection + validation; **not** truth authority | Rebuildable named graphs; build-profile writes only | Named graph IRI, `rdf_projection_hash`, release graph | Admitted ledger records + release + ruleset | Writers: isolated build profile; readers: reviewed SPARQL templates (read-only, no `update`) | Unavailable → relational fallback; mismatch → reject snapshot; never fail-open | Indirectly only if sealed + template-bound |
| Neo4j operational projection | Serving/read projection; rebuildable | Rebuildable; no application-level runtime writes | `neo4j_projection_hash`, `semantic_snapshot_id`, assertion IDs | Same admitted-assertion manifest + release | Writers: privileged `Neo4jProjectionBuilder` (build profile); readers: approved depth-capped motifs | Unavailable → relational fallback; cross-store mismatch → reject snapshot | Indirectly; must never be sole economic authority |
| Retrieval answers / receipts | Query service over pinned snapshot + template | **Modeled as transient `EvidenceAnswer` DTO** — no receipt hash/signature | Template ID/version, snapshot IDs, projection path, cutoff | Relational/RDF/Neo4j query over sealed snapshot | Writers: deterministic `QueryService`; readers: packet/belief builders, audit | Unknown/abstain on missing facts; timeout → degraded | Yes — packets + belief state consume them |
| Evidence packets + `InstrumentBeliefState` | Deterministic builders (Tasks 10–12) | Immutable sealed (`packet_id`); belief immutable, cached by `cycle_id` | `packet_id`, `semantic_snapshot_id`, `validated_data_snapshot_id`, `ontology_release_id`, builder/policy versions | Query answers + domain observations + portfolio snapshot | Writers: deterministic packet/belief builders; readers: `DecisionFeatureProjector`, audit | Missing/contested → INSUFFICIENT/CONTESTED/abstain | Indirectly via `DecisionFeatureProjector` only |
| Fitted causal weights / motif policy | Versioned offline `EdgeWeightFitter` artifact + approved motif registry | Immutable post-approval; new artifact per training run | Weight artifact ID, motif-policy ID, training cutoff/dataset hash, code version | Historical labeled shock data | Writers: offline fitter + steward/reviewer; readers: `Traversal`, relationship packet, risk | Unsupported/unknown → no causal/exposure support | Yes for exposure/risk; must be tighten-only unless separately promoted |
| Policy/risk/sizing/compliance | Deterministic code + frozen config + sealed promotion manifest | Frozen per campaign/release; new campaign for changes | Config hash, strategy ID, feature-policy ID, promotion manifest hash | `DecisionFeatureSet`, portfolio/account/broker state, risk configs | Writers: deterministic code/config governance; readers: EOD/execution | Fail closed / reduce-only on stale/unknown | Yes — directly |
| Broker execution / custody | External broker = actual economic state; internal append-only event log = observed intents/fills | Broker state mutable externally; internal observations append-only | `IntentId`, broker order IDs, stream versions, reconciliation event IDs | Broker APIs/fixtures + event-log replay | Writers: `ExecutionCoordinator`/`Reconciler`; readers: protection/risk/accounting | Reconcile before retry; unknown → reduce/halt/block symbol | Yes — directly |

**Dual-authority and canonical-blur flags:**

1. **Snapshot ID vs. projection ID (P1).** `2026-07-21-trading-world-ontology-implementation.md Task 7` seals `snapshot_id` **after** projections are already built and queried under `proposed_snapshot_id`. Projections physically carry a non-sealed ID, so a lookup by the final sealed ID is incomplete, and the proposed ID becomes de facto canonical during the build window. See F-01.
2. **Two source-record authorities (P2).** `Task 3` (semantic source records) and `2026-07-21-trading-os-v1-implementation.md Task 29` (market-data source records) both persist immutable source records with independent hash/licence contracts. Unless unified, one vendor document acquires two provenance identities. See F-07.
3. **Fuseki validation ≠ admission authority.** `design §5.3` correctly frames RDF as projection, but the heavy SHACL role must never let a Fuseki validation report *admit* a fact — it may only reject a build. Flagged; the code respects this today.
4. **Active-release pointer as mutable row (P1).** `PromotionPublisher`/`ShadowMonitor.rollback_and_append_event` imply a mutable "active release" pointer alongside the insert-only `ontology_release` table. If rollback is an in-place UPDATE, it violates the append-only invariant and can be corrupted by a promotion/rollback race. See F-01a.

### 2.2 Ontology releases, compatibility, and migrations

The foundation is sound: stable term IRIs (`urn:trading-os:ontology#LegalEntity`) separated from release-specific `owl:versionIRI` (`urn:trading-os:ontology:1.0.0`); immutable `OntologyRelease` manifests; MAJOR/MINOR/PATCH policy; deprecation without IRI reuse; runtime registry over Git tags; historical snapshots pinned to their original release via `get_exact()`. This satisfies the long-term hybrid premise without being over-complex.

Adversarial findings:

1. **Compatibility check is narrower than the advertised contract (P1).** `Task 1 check_compatibility` compares removed OWL terms and a fixed set of schema/SHACL constraint predicates via symmetric difference. It does **not** compare mappings (`fibo.ttl`/`prov-o.ttl`/`owl-time.ttl`), the inference ruleset, query-template assumptions, endpoint-type policy, or term definitions with semantic force. `design §5.1` says MAJOR includes "incompatible meaning, domain/range, identity, cardinality, **or inference** change" — the code detects only part of that. A semantically breaking mapping or inference change can ship as MINOR/PATCH. See F-03.
2. **Symmetric-difference is simultaneously too strict and too loose (P2).** It flags additive SHACL shapes on **new** classes as breaking (forcing needless MAJOR bumps, contradicting the plan's "MINOR covers backward-compatible shapes"), while missing mapping/inference drift entirely. Classify a constraint change as MAJOR only when it references a **pre-existing** term IRI. See F-10.
3. **Inference ruleset is a hardcoded string, not content (P2).** `inference_ruleset_hash=_hash(b"rdfs+approved-owl-rl-v1")` never changes when the actual Jena entailment config changes. Historical snapshots claim the same ruleset while receiving different inferences. Hash the ruleset **file** and give every permitted/prohibited entailment positive/negative fixtures. See F-11.
4. **Migration is a reference, not a governed executable registry (P2).** `build_release` accepts `migration_ref: str | None` plus a compatibility hash, but no tested migration-artifact registry proves an old fact is interpretable under its old release and *optionally* transformable under the new one **without reinterpreting old bytes**. See F-12.
5. **Historical replay may be coupled to the active runtime range (P1).** `Task 15` sets `supported_ontology_releases: ">=1.0.0,<2.0.0"` and `SemanticBootstrap.assert_supported` rejects unsupported majors. Correct for active decisioning, but replay of a v1 snapshot after v2 activation must **bypass the range check** and use `get_exact()` on the original release; otherwise a v1 factual snapshot becomes operationally unreplayable. See F-04.
6. **`owl:imports` resolution unverified (P2 latent).** Modules `owl:imports <urn:trading-os:ontology>` (a non-dereferenceable URN). The validator loads all modules into one graph, which works, but nothing asserts imports are treated as a dependency declaration rather than a silently-ignored live fetch. Document and test that cross-module constraints (e.g., `tos:Claim rdfs:subClassOf tos:Assertion` from `core.ttl`) are enforced at validation. See F-11.
7. **Release provenance not bound to a clean Git commit (P2).** `build_release(root: Path)` hashes the working tree, not a committed ref. A build from uncommitted edits yields a hash reproducible from no Git ref. Record `git_commit_sha` and reject a dirty tree. See F-09.

**Adversarial replay test (required):** seal a v1 snapshot (source record + claim + admitted assertion + identity alias + query template + belief state). Publish v2 with a renamed/deprecated relation, changed `skos:closeMatch` mapping, and stricter SHACL. Required: v1 replay loads the v1 release and returns byte-equivalent v1 answers; optional migration to v2 creates **new** migrated assertion IDs / explicit migration provenance; no in-place reinterpretation of v1 bytes; no hash change without a meaning-preserving guarantee.

### 2.3 Temporal and provenance model

The seven-dimension model (`design §6.2`) — `occurred_at`, `published_at`, `received_at`, `valid_from/valid_to`, `recorded_at`, `superseded_at`, `decision_cutoff` — is the correct decision-time PIT invariant, and `AvailabilityWindow` enforces `published_at ≤ received_at ≤ recorded_at` with non-empty half-open validity. The chain document → `SourceRecord` → `EvidenceSpan` → `Claim`/`Observation` → `AdmissionDecision` → `SemanticSnapshot` → `EvidenceQuery`/`EvidenceAnswer` → `InstrumentBeliefState`/`DecisionFeatureSet` propagates snapshot IDs end-to-end. Corrections resolve through `admitted_claims_as_of`, which filters `received_at ≤ cutoff AND recorded_at ≤ cutoff` and drops superseded claims — correct, **provided every consumer routes through it**.

Leakage routes and gaps:

1. **No distinct retrieval/ingestion/parser-activity time (P1).** `design §6.2` defines `received_at` as "vendor/system **could** access it," but there is no first-class `retrieved_at`/`ingested_at`, nor a persisted `ExtractionActivity` recording extractor/parser **model version, prompt/schema hash, extraction time, and agent identity**. This blocks auditing late collection and parser reruns, and weakens replay of any LLM/parser-derived claim. See F-05, F-13.
2. **No explicit unknown/unavailable availability state (P1).** `design §6.2` says unknown availability makes an item ineligible, but `AvailabilityWindow` **requires** `published_at`/`received_at`/`recorded_at`, pressuring callers to fabricate timestamps rather than mark "unknown." Add an availability-state enum; unknown ⇒ ineligible, never coerced to cutoff. See F-05.
3. **Fundamental restatement filter depends on an unspecified boundary (P1).** `Task 10 FundamentalPacketBuilder` filters `received_at ≤ decision_cutoff` **before** `latest_non_superseded_by_metric`, which is correct **only if** its inputs are already cutoff-gated (i.e., sourced from `admitted_claims_as_of`, not a raw snapshot). The repository↔builder boundary is unspecified. See F-04.
4. **`abstention_reasons` is free-text, not a closed enum (P2).** `InstrumentBeliefState.abstention_reasons: tuple[str, ...]` and `ReasoningCycle` appends bare `"semantic_projection_unavailable"`. Downstream degraded-state detection pattern-matches strings; an undocumented code silently bypasses gates. Make it `tuple[AbstentionReason, ...]`. See F-08.
5. **Cutoff binding is a convention, not a structural guarantee (P2 governance).** Only `admitted_claims_as_of` enforces the dual `received_at`/`recorded_at` filter; a future template bypassing it loses PIT binding. Elevate to a MUST: every evidence-table query includes both filters.

**Tests to plant:** future publication; late vendor receipt; late system ingestion; parser rerun after cutoff; filing restatement; backdated valid interval with late publication; unknown publication time; supersession received after cutoff. Expected: only facts public + received + recorded + admitted + not-superseded as of cutoff enter a decision snapshot.

### 2.4 Identity and entity resolution

The chain `LegalEntity –issues→ Security –admittedAs→ Listing –tradedAt→ Venue` with `hasAlias→ Ticker(valid interval)` (`design §6.1`) is directionally correct; `ListingIdentity` enforces a non-empty half-open interval; `IdentityResolver` uses the right priority order (canonical ID → authoritative crosswalk → valid exact alias → fuzzy candidate-only) and never auto-merges fuzzy matches (`requires_human_review=True`, `canonical_id=None`).

Material gaps:

1. **Type-specific identity incomplete (P1).** `Task 2` defines `LegalEntityId`/`SecurityId`/`ListingId`/`ListingIdentity` but no explicit `IssuerId`, `InstrumentId`, `ShareClassId`, ADR/underlying relation, parent/subsidiary relation, or typed crosswalk object. `Task 8` accepts a supplied canonical ID from a **flat** `canonical_ids` set without proving the expected entity **type**, and stores `valid_aliases: dict[str, tuple[str, datetime, datetime|None]]` keyed only by normalized alias — unsafe for ticker reuse or simultaneous cross-venue/share-class aliases (a second entry overwrites the first). Key on `(alias, venue_mic)` at minimum. See F-06.
2. **Corporate-action identity events are not ontology terms (P2).** `identity.ttl` lacks `tos:MergerEvent`/`tos:SpinOffEvent`/`tos:DelistingEvent` with `effectiveDate`/`predecessor`/`successor`. Lineage must be inferred from `valid_to` + human-authored relationship claims rather than queried semantically; exposure analysis may traverse stale edges to a successor. See F-05a.
3. **No fuzzy similarity floor (P2).** `FuzzyCandidatePort.find` returns candidates with no minimum score, flooding the human-review queue and raising approve-under-pressure merge risk. Add a `score_floor` (e.g., 0.80) in `admission.yaml`; below-floor ⇒ no candidate, no review, unknown entity. See F-07a.
4. **Sector/geography/macro-region identity drift (P2).** The resolver focuses on security aliases; organization/sector/geography taxonomies must be release-pinned mappings or exposure replay drifts.

**Replay test:** two companies sharing a ticker at different times; one ADR + one underlying ordinary; one spin-off; one issuer with multiple listed share classes. Query exposure before/after each event. Required: no alias resolves outside its validity interval; no fuzzy auto-merge; ADR/underlying propagation only via approved relation templates; byte-equivalent replay after later corporate actions.

### 2.5 Evidence, belief, and causal discipline

The separation is strong and Pydantic-`extra="forbid"`-enforced: `SourceRecord → EvidenceSpan → Claim → ReviewDecision → AdmittedAssertion`; PROV-O-aligned derivation; `EvidencePacket` keeps `supporting_assertion_ids` vs `refuting_assertion_ids` distinct; `HypothesisAssessment` uses a closed status enum with **no numeric probability**; `BeliefStateShape` structurally forbids `targetPrice`/`orderQuantity` via `sh:maxCount 0`. Causal discipline holds: `RelationshipPacketBuilder` rejects non-approved-motif paths (`"no_approved_motif"`) and LLM ordinals are tighten-only via `min(Decimal("1"), multiplier)`.

**Where SHACL/OWL validates shape but not truth:** SHACL confirms type, cardinality, closed shapes, and approved entailments; it cannot establish source truth, independent corroboration, freshness, absence, an identified causal effect, or calibration. The system correctly keeps admission policy, corroboration, and causal identification **outside** ontology validation — but this must be stated plainly: **the graph can be semantically valid and empirically wrong simultaneously, and SHACL will not detect the latter.** The only empirical gate is champion/challenger vs relational retrieval; there is no runtime calibration proving admitted claims are predictive.

Hardening needed:

1. **Claim vs AdmittedAssertion not physically distinct (P2).** `Claim.state` is copied and projected as `AdmittedAssertion` triples, risking a proposed/rejected claim being read as admitted truth or laundering a rejected proposal. Derive a distinct `AdmittedAssertion` ledger row (own ID + admission provenance) from claim + `ReviewDecision`; projections consume only assertion rows. See F-08a.
2. **Observation- vs assertion-support asymmetry (P1).** `assess()` reasons primarily over `supporting/refuting_assertion_ids`; pure technical/fundamental **observation-only** packets can collapse to INSUFFICIENT despite valid deterministic observations. Define per-domain observation→assessment contracts. See F-13.
3. **Causal-model version not pinned in the snapshot (P1).** `SemanticSnapshot` binds `inference_ruleset_id` but **not** `motif_policy_id`, `fitted_weight_artifact_id`, or causal-model version. Relationship/risk overlays are then irreproducible if weights/motifs change without a snapshot-key change. See F-02b.
4. **Self-confirming improvement loop (P1).** `FailureCase.expected_answer` origin is unspecified; if expected answers derive from prior ontology outputs, a systematic error self-validates and the loop optimizes toward it. Label expected-answer provenance (human/held-out/external) and prohibit ontology-derived ground truth; keep holdout invisible to proposers. See F-06.
5. **Contamination via `Observation.value_text` (P1).** The projection test excludes `span_hash`/raw text from quads, but `value_text` is carried into `EvidencePacket.deterministic_features`; if any LLM explanation step renders those features into a prompt, injection re-enters. Exclude `value_text` from every prompt-rendering path and taint-track it. See F-06.
6. **Motif-registry governance gap (P2).** The `approved_motifs` frozenset is injected without a specified approval process or version-bump policy; a misconfigured set admits unapproved causal paths. Bind motif additions to human-approved release changes. See F-11a.
7. **Corroboration lineage transient (P2).** `origin_cluster_ids` exist only on `ClaimProposal`; independent-source counts can't be re-audited after restart. Persist syndication/origin-cluster lineage. See F-09a.

**Agent/contamination tests:** inject prompt-injection text into a source blob; delete required graph facts; inject a false premise; have an agent propose an identity merge; let one model author diagnosis+proposal+evaluation. Expected: no admitted edge, no self-promotion, abstention on missing knowledge, and a trace proving source text never became query text, ontology source, graph-property prose, or a decision feature.

### 2.6 Failure-mode matrix and findings

| ID | Sev | Exact source anchor | Invariant violated | Consequence | Remediation | Validation / chaos test |
|---|---|---|---|---|---|---|
| F-01 | P1 | `trading-world-ontology-implementation.md Task 7: Seal SemanticSnapshots` | Sealed snapshot ID must be the ID all projections carry | Neo4j/RDF rows written under `proposed_snapshot_id`; queries by final sealed ID incomplete; proposed ID de facto canonical | Precompute deterministic snapshot ID before projection, or build under a provisional ID then rebuild/rewrite under the final sealed ID before activation | Build identical inputs twice; assert all ledger/RDF/Neo4j rows carry final `SemanticSnapshot.snapshot_id`, never a proposed ID |
| F-01a | P1 | `Task 14 ... PromotionPublisher`/`ShadowMonitor.rollback_and_append_event` | Active-release pointer must be append-only; rollback is an append | In-place UPDATE breaks insert-only; promotion/rollback race corrupts the pointer | Model active release as an event stream (`ReleaseActivated`/`ReleaseRolledBack`); latest terminal event wins; optimistic stream-version check | Inject two simultaneous rollbacks; assert exactly one append and a deterministic active release |
| F-02 | P1 | `Task 6 Neo4jProjectionBuilder.build` (`MERGE` semantics) | Neo4j must be atomically replaced per manifest; partial state not queryable | Mid-build crash leaves mixed-snapshot nodes; stale graph queryable if runtime doesn't gate by `semantic_snapshot_id` | Stamp `semantic_snapshot_id` on every node/rel; delete-for-snapshot or transactional bulk load; runtime always filters by snapshot | Kill build mid-`MERGE`; assert identical rebuild fingerprint and no stale mismatched-snapshot nodes queryable |
| F-02b | P1 | `design §7 Bounded evidence domains` + `§5.5 SemanticSnapshot` | Causal/exposure model versioned separately from ontology+facts | Relationship packets/risk overlays irreproducible if weights/motifs change without snapshot-key change | Add `motif_policy_id`, `fitted_weight_artifact_id`, causal-model version to `SemanticSnapshot`, `EvidenceQuery`, relationship packets | Replay same snapshot under changed weight artifact; require binding/hash mismatch, not silent answer drift |
| F-03 | P1 | `Task 1 check_compatibility` | Compatibility must cover meaning, mappings, inference, identity, query contracts | Semantically breaking mapping/inference/query change ships as MINOR/PATCH | Extend compatibility to modules, mappings, SHACL, inference rules, query templates, definitions, endpoint policy, migration fixtures | Mutate mapping/inference/query under same major; expect `BreakingReleaseVersion` unless migration + MAJOR present |
| F-04 | P1 | `Task 15 SemanticBootstrap.assert_supported` + `design §5.1` | Historical replay loads original release, independent of active range | v1 snapshots unreplayable after v2 if bootstrap rejects old majors; also raw-input fundamental filter (`Task 10`) may leak post-cutoff restatements | Separate active-decision range from a historical replay registry using `get_exact()`; ensure fundamental builder consumes only cutoff-gated (`admitted_claims_as_of`) inputs | Activate v2, replay v1 snapshot → byte-equivalent v1 answer; plant post-cutoff restatement superseding a pre-cutoff obs → pre-cutoff obs remains |
| F-05 | P1 | `design §6.2 Time` + `Task 2` | Unknown/unavailable availability must not be fabricated or treated as false; retrieval/parse activity must be recorded | Callers guess timestamps to satisfy required fields; late collection/parser reruns unauditable | Add availability-state enum, `retrieved_at`/`ingested_at`, `ExtractionActivity` (model version, prompt/schema hash, agent id); unknown ⇒ ineligible | Plant unknown/late-receipt/parser-rerun facts; assert admission rejects or marks ineligible, never coerces to cutoff |
| F-06 | P1 | `Task 14 FailureCase` (expected answer) + `Task 8 LicensedSourceReader` / `Observation.value_text` | Improvement ground truth must not derive from prior ontology output; raw text must not reach prompts | Systematic ontology error self-validates; `value_text` injection re-enters via downstream LLM | Label expected-answer provenance (human/held-out/external), ban ontology-derived truth; exclude `value_text` from all prompt-rendering paths; taint-track | One agent authors proposal+evaluation and sees holdout; planted injection in `value_text` → assert rejection, no self-promotion, no LLM receives the string |
| F-06id | P1 | `design §6.1` + `Task 8` (`valid_aliases`, flat `canonical_ids`) | Canonical identity type-specific + point-in-time | Flat sets merge issuer/security/listing/ticker or mishandle ticker reuse | Model `IssuerId`/instrument/share-class IDs, typed crosswalks, `(alias, venue_mic)` many-to-many temporal aliases, identity-event lineage | Ticker-reuse + ADR + spin-off fixture → no cross-type merge, correct date-scoped resolution |
| F-07 | P2 | `Task 3` + `trading-os-v1-implementation.md Task 29` | Source provenance has one canonical namespace | Market-data and semantic source records diverge; citation/licence audit weakened | Unify `SourceRecordId`/content-hash/licence policy across ledgers or define a single-authority crosswalk | Same vendor doc used for OHLCV/news/claim → one source identity + licence policy across both repositories |
| F-07a | P2 | `Task 8 FuzzyCandidatePort.find` | Candidates need a minimum evidence-quality floor | Low-score candidates flood review; approve-under-pressure merge risk | Add `score_floor` (e.g., 0.80) to `admission.yaml`/port; below-floor ⇒ no candidate, no review, unknown | Best fuzzy score 0.55 → empty candidates, `requires_human_review=False` |
| F-08 | P2 | `Task 12 InstrumentBeliefState.abstention_reasons: tuple[str,...]` | Abstention reasons closed + queryable | String pattern-matching fragile; new code silently bypasses gates | Define `AbstentionReason(StrEnum)`; use `tuple[AbstentionReason,...]`; emit typed reasons | Add a bare-string reason → `mypy` type error at assignment |
| F-08a | P2 | `design §6.3` + `Task 5 rdf_mapping` | Claim, ReviewDecision, AdmittedAssertion physically distinct | Copied `Claim.state` read as admitted truth; rejected proposal laundered | Distinct `AdmittedAssertion` row from claim+decision; projections consume only assertion rows | Append rejected+proposed claims → absent from RDF/Neo4j and relational champion |
| F-09 | P2 | `Task 1 build_release(root: Path)` | Release manifest ↔ reproducible committed Git state | Build from uncommitted edits → hash reproducible from no ref | Add `git_commit_sha`; verify clean `git status --porcelain` and record HEAD | Build with uncommitted module edit → `UncommittedOntologySource` |
| F-10 | P2 | `Task 1 check_compatibility` (symmetric diff) | MINOR permits additive new-class shapes; MAJOR only tightens existing terms | Needless MAJOR bumps slow iteration; mapping/inference drift missed | Flag MAJOR only when a changed constraint references a pre-existing term IRI; add mapping/inference to the diff | Add new class + shape in MINOR → no `BreakingReleaseVersion`; tighten existing → raises |
| F-11 | P2 | `Task 1 inference_ruleset_hash=_hash(b"rdfs+approved-owl-rl-v1")` + `approved_motifs` frozenset | Inference ruleset + motif registry versioned, documented, governed | String hash unchanged when Jena config changes; misconfigured motifs admit unapproved causal paths | Hash a ruleset **file**; positive/negative entailment fixtures; bind motif additions to human-approved releases | Change Fuseki inference → fingerprints diverge and snapshot rejected; add unapproved motif → path excluded |
| F-12 | P2 | `design §5.1` + `Task 1` (`migration_ref: str | None`) | Migration is a governed, executable, tested registry | Old facts may be reinterpreted without a meaning-preserving migration | Machine-readable migration artifacts in the registry; historical snapshots retain the migration chain | Deprecate a relation in v2 with migration → v1 replay byte-equivalent; migrated assertions get new IDs/provenance |
| F-13 | P1 | `Task 12 belief_builder assess()` | Observations, assertions, hypotheses separately consumable | Observation-only technical/fundamental packets falsely INSUFFICIENT | Per-domain observation→assessment contracts; keep assertion support separate from observation support | Technical-only hypothesis with valid deterministic observations → SUPPORTED/INSUFFICIENT per declared rule, not accidental missing-assertion |
| F-14 | P1 | `design §14` + `Task 9 QueryService.execute` (only `TimeoutError` → `SemanticProjectionUnavailable`) | Projection failure degrades to relational; baseline failure fails closed | HTTP/protocol/malformed-JSON projection errors bypass intended fallback | Normalize all Fuseki/Neo4j unavailable/corrupt/timeout/mismatch errors into explicit degraded fallback where equivalent; non-equivalent → closed abort | Kill Fuseki; return malformed SPARQL JSON; corrupt Neo4j response → relational fallback or closed abort per policy |
| F-15 | P2 | `design §9` + `Task 9` (`EvidenceAnswer` DTO) | Decision-consumable retrieval is an immutable bound receipt | `EvidenceAnswer` tamperable between query and packet/belief construction | Add `RetrievalReceipt` hash/signature over template, params, snapshot IDs, projection, assertion IDs, missingness, body | Flip an assertion ID / retrieval path post-query → packet builder rejects receipt-hash mismatch |

**Implied chaos matrix:** stale release; incompatible release; missing migration; old-snapshot replay after major change; partial RDF rebuild; partial Neo4j rebuild; direct runtime graph write; semantic mapping drift; future-publication leak; late-receipt/ingestion leak; parser-rerun revision leak; false identity merge; missing provenance; duplicated syndicated facts; malformed inference rule; unsupported causal edge; corrupted retrieval receipt; semantic-projection timeout; malformed projection response; relational-baseline outage.

<!-- CHUNK-B SELF-AUDIT: 1/1 top-level sections emitted; authority map complete; ontology release+migration replay tested; temporal/provenance+identity+evidence/causal layers separated; >=12 failure modes; every material finding has severity+anchor+consequence+remediation; no truncation -->

## 3. Implementation executability, improvement loop, and prioritized decision

### 3.1 Cross-plan splice and dependency audit

**Splice map.** Execute Trading OS (TOS) Tasks 1–14; then execute the full ontology plan (ONT 1–15); ONT augments TOS 12–13, replaces the semantic/KG/research content of TOS 15–17, preserves the independent rule-null of TOS 14; then resume TOS at Task 18 consuming `DecisionFeatureSet`.

| Segment | Produces (contract) | Consumed by | Splice hazard |
|---|---|---|---|
| TOS 1–2 | `Settings`, package, IDs/enums/`Money`/`Quantity`, SHA-256 conventions | ONT 1 (release IDs/hashes), ONT 2 (UUID VO) | None if run first. |
| TOS 3 | `ResearchTradeThesis`, `HotPathCandidate`, `ConvictionBand`, `SeamProjector`, hot-path import test | ONT 12 **modifies** `research/seam.py` + `domain/candidates.py` | TOS 3's seam tests still assert the old seam; ONT 12 rewrites it. Old tests will conflict unless amended. **P1.** |
| TOS 4–5 | orders/portfolio; 13 ports incl. `GraphStorePort`, `SecurityMasterPort`, `EventStorePort`, fakes | ONT 6 (`ports/graph.py`), ONT 8 (SecurityMaster) | ONT 6 **also modifies `kg/neo4j_store.py`**, created only by TOS 15 (replaced). Missing-file break. **P1.** |
| TOS 6–8 | `EventEnvelope`, `EventType`, memory+Postgres stores, Valkey | ONT 1 extends `EventType` + `PostgresEventStore` with `append_in_transaction` | In-memory fake lacks `append_in_transaction`; integration fixture wiring unspecified. **P1.** |
| TOS 9–11 | kill switch, reservations, readiness | ONT 15 cycle, resumed TOS | None. |
| TOS 12 | `RawBar`, `CorporateAction`, `UniverseMembership`, `BrokerCashEvent` | ONT 3 adds evidence ledger *alongside* | "Augment" is additive, not re-run. Needs explicit note. |
| TOS 13 | `ValidatedDataSnapshotId`, manifest, `CorrectnessLayer` | ONT 7 patches manifest to bind `SemanticSnapshotId` | Central ambiguous splice — must be *additive compatibility migration*, not reopening TOS 13. |
| TOS 14 | factors, `GateRank`, permanent `RuleNullJob` | preserved; must stay import-independent | Correct. Must run with RDF/Neo4j/LLM absent. |
| TOS 15–17 | (replaced) originally `Traversal`, `ExposureVector`, weight artifacts, LLM research | **still consumed by resumed TOS 19 (`ExposureVector`) and TOS 35 (KG replay/weights)** | Replacement removes producers of artifacts resumed tasks still import. **P1.** |
| ONT 1–15 | releases, evidence, projections, packets, belief, `DecisionFeatureSet`, `ReasoningCycle` | resumed TOS 18+ | ONT 15 must concretely amend TOS 18/19/32/34/35/37, not merely add a header note. **P1.** |
| Resume TOS 18+ | sizing/risk/compliance/execution/eval | — | TOS 18 consumes "admitted symbol/direction"; no explicit `DecisionFeatureSet → candidate` adapter exists. **P1.** |

**"Augment Tasks 12–13" — decision.** Yes, it requires revisiting their *interfaces* after TOS 14, but **not** re-running or invalidating completed base work. The disambiguating amendment: *"After ONT 7, apply an additive manifest-compatibility migration — historical `ValidatedDataSnapshotManifest` with bare KG edge-set remain readable; new decision-consumable manifests must bind exact `SemanticSnapshotId` + `OntologyReleaseId` + cutoff. TOS 14 remains import-independent and operates on data-only snapshots; any semantic-derived feature uses the enriched manifest."* This removes the "augment after they already ran" ambiguity by fixing "augment" = additive patch, not re-execution.

**Migration-order hazard.** ONT `0002/0003/0004` sequential names collide conceptually with TOS `20260721_0002/0003/0004` timestamped names. Alembic orders by revision ID + `down_revision`, not filename, so filenames alone are ambiguous. **P1** — one linear head required.

---

### 3.2 API, type, persistence, and service contract audit

Concrete contradictions with anchors (sample code is contract):

1. **ONT 6 modifies nonexistent files** — `Task 6 → Files: Modify: src/trading_os/kg/neo4j_store.py`. Created only by replaced TOS 15. **Break.** Amendment: ONT 6 must **Create** all Neo4j projection/runtime under `semantic/projections/neo4j.py` and only touch `ports/graph.py` (add a port-only stub in the TOS 14 commit).

2. **RDF serialization drops named graph** — ONT 5 `rdf.py`: `graph.serialize(format="nt")` emits N-Triples (3-part); named-graph IRI is lost, so the projection hash never captures graph membership. `claim_to_quads` builds 4-tuples but `RdfProjectionBuilder.build` adds only `(s,p,o)` to a default `Graph()`. Cross-store fingerprint equality (ONT 7) then fails deterministically. **P1.** Use `format="nquads"` or hash `graph_iri + sorted(nt)` per named graph (the builder already prepends `graph_iri` to the returned hash but not to the serialized bytes — insufficient).

3. **Snapshot-ID identity mismatch** — ONT 7 `SemanticSnapshotBuilder.build` queries Neo4j/RDF by `request.proposed_snapshot_id` but `seal_semantic_manifest` returns a *recomputed* `snapshot_id` (hash of manifest sans `proposed_snapshot_id`). Projections are keyed by the proposed ID; decision queries later bind the sealed ID; they can differ. **P1.** Use one deterministic ID end-to-end: precompute final ID → build projections under it → verify → activate.

4. **Cross-store datetime fingerprint drift** — `projection_fingerprint` (ONT 5 `fingerprint.py`) calls `received_at.isoformat()`. Postgres returns aware UTC; Neo4j returns `neo4j.time.DateTime`; RDF returns xsd:dateTime lexical (`Z` vs `+00:00`). Three different strings → three different SHA-256 → `ProjectionMismatch` on every valid snapshot. **P1.** Add a single `normalize_utc(dt)->str` (`astimezone(UTC)`, fixed microsecond+`+00:00` form) applied identically in all three fingerprint paths.

5. **Async blob store blocks the loop** — ONT 3 `blob_store.py` declares `async def put/get` but calls synchronous `Path.read_bytes()/write_bytes()`. Under asyncio integration tests this blocks. **P1.** Wrap in `asyncio.to_thread`/`anyio.Path`, or mark filesystem store test-only with an async object-store production adapter.

6. **`append_in_transaction` contract holes** — ONT 1 `registry.py`: `TransactionalEventWriterPort` + `PostgresEventStore.append_in_transaction` use `text(...)`, `func`, `EventEnvelope`, `EventType`, `OntologyReleasePublished`, `StreamConflict`, `EventLogRow` **without imports shown**, and `EventEnvelope.new` sets `stream_version=-1`. The in-memory fake (TOS 6) has no `append_in_transaction`. Sample-as-contract fails `mypy`/collection. **P1.** Add imports; register `OntologyReleasePublished` in the discriminated payload union + deserializer; add `append_in_transaction` to the in-memory store or force Postgres in the integration fixture.

7. **`model_copy(update=...)` bypasses validation** — ONT 3 `admitted_claims_as_of`: `claim.model_copy(update={"state": states[...]})` on a frozen model injects a DB-sourced value without re-validation. **P2.** Use `Claim.model_validate({**claim.model_dump(), "state": state.value})`.

8. **Neo4j temporal read assumption** — ONT 6 `projection_fingerprints`: `row["received_at"].to_native()` fails if stored/returned as ISO string. **P2.** Guard: `v.to_native() if hasattr(v,"to_native") else datetime.fromisoformat(v)`.

9. **Fuseki `fromisoformat` fragility** — ONT 5 `select_projection_fingerprints` parses SPARQL literals with `datetime.fromisoformat`; lexical variants break it. **P2.** Use a robust isoparse and normalize before hashing (couples to #4).

10. **RDF vocabulary ≠ ontology IRIs** — modules define `urn:trading-os:ontology#…`; `rdf_mapping.py` emits `urn:trading:assertionId/subject/receivedAt…`. SHACL shapes target `tos:` classes, so projected quads are never shape-validated. **P1 (before shadow).** Map projection predicates to ontology IRIs (or add SHACL over the projection vocabulary with fixtures).

11. **Non-IRI canonical IDs** — `claim_to_quads` does `URIRef(claim.subject_id)`; if IDs are UUIDs/vendor strings, serialization is invalid/inconsistent. **P1 (before shadow).** Canonical encoder `urn:trading-os:id:<type>:<escaped>` used in RDF + Neo4j fingerprints.

12. **Direct-write denial is shape-only** — ONT 5/6 assert `not hasattr(...,"update"/"execute_write")`. This proves nothing about credentials/network. **P2.** Read-only Fuseki/Neo4j credentials + network profile tests: runtime `PUT graph`/write-Cypher must raise permission errors.

13. **Sync projector inside async handoff** — ONT 12 `DecisionFeatureProjector.project` is sync but `load_exact` may be DB-backed; called from async `SemanticDecisionHandoff.prepare`. **P1.** Make `project` async, or contractually require a preloaded in-memory packet cache.

14. **Fuseki service naming** — ONT 1 defines build vs runtime datasets; contract test says `docker compose up -d fuseki`. Ambiguous if both profiles share the name. **P2.** Distinct services `fuseki-runtime`/`fuseki-build`.

15. **Neo4j version pin conflict** — ONT tech stack `Neo4j Community 2026.06.0` vs TOS `neo4j:5-community` + `neo4j>=5.24,<6`. **P3.** Pin one server image + driver range.

Underspecified but not contradictory: `EvidenceSpan.span_hash` never re-verified (P3, document as advisory); `_admission_states_as_of` intentionally drops REFUTED/DEPRECATED (P3, add docstring).

---

### 3.3 Deterministic trading boundary

**End-to-end trace.**

```
ValidatedDataSnapshotId + SemanticSnapshotId + OntologyReleaseId + decision_cutoff
 → ReasoningCycle.run(request)
     → SnapshotBundlePort.load_exact(...)                 [read-only; fail-closed if absent]
     → QueryBatchPort.execute_all(approved EvidenceQuery)  [frozen template_id, depth≤3, allowlist]
         · SemanticProjectionUnavailable → RelationalRetrieval fallback (degraded)
         · relational failure → RelationalChampionUnavailable → ABORT
     → PacketBuilderSet.build_all(...)  [6 deterministic packets; numeric only from det. evaluators]
     → BeliefStateBuilder.build(packets) [categorical rule table; no floats/price/qty]
     → InstrumentBeliefState             [SHACL: targetPrice/orderQuantity maxCount 0]
 → DecisionFeatureProjector.project(state, strategy)
     [numeric_allowlist + closed categorical only; forbidden_lineage_keys blocks raw narrative/LLM JSON]
     → DecisionFeatureSet
 → [MISSING] Deterministic strategy adapter: DecisionFeatureSet → AdmittedCandidate/HotPathCandidate
 → GateRank.rank()   [conviction reorders/vetoes only; no quantity]
 → Sizer.size()      [signature excludes conviction/thesis/model/calibration]
 → RiskEngine.evaluate() [overlay multiplier min(1,·); shrink/veto only]
 → ComplianceGate.evaluate() [versioned rules, collect-all]
 → HITL [entry: default-deny on timeout; exit: default-proceed]
 → ExecutionCoordinator.submit() [revalidate hash/snapshot; append IntentId BEFORE broker]
 → BrokerAdapter.submit() [kill-generation checked; ack-loss → reconcile_intent once]
 → append fill/ack events; release reservation; ProtectionSupervisor
```

**Permitted agent mutations:** propose Claims/Observations/EvidenceSpans; nominate identity candidates; classify closed event/sentiment enums; select approved query templates + typed params; summarize returned evidence; propose *offline* ontology/query/data changes.
**Forbidden:** admit facts; merge identities; write RDF/Neo4j/ledger; emit numeric causal strength or any sizing/risk input; change active ontology/release/policy; run unrestricted SPARQL/Cypher for decisioning; optimize against live P&L; self-promote; emit price/qty/stop/risk-budget/order.

**Fail-closed points:** correctness fault → no snapshot; provenance/availability missing → assertion excluded; received-after-cutoff → rejected; fuzzy-only identity → abstain per instrument; projection mismatch → snapshot rejected; semantic down → relational fallback (degraded flagged); relational down → abort; unsupported release → reject; query timeout/depth breach → abort/bounded baseline; missing knowledge → unknown/abstain; stale approval/kill-generation → block; `OUTCOME_UNKNOWN` → reduce + block + alert.

**Bypass proof holds *only* if F-02 (the `DecisionFeatureSet → strategy candidate` adapter) is added** and TOS 18/19/32/35 are amended to consume it rather than legacy `ExposureVector`/thesis objects. Structural guarantees present: `InstrumentBeliefState` SHACL forbids trade fields; `DecisionFeatureProjector` forbidden-lineage check; hot-path import tests forbid `research.models`/RDF/Neo4j/SourceRecord; Sizer signature property test. **Gap:** no test yet asserts that a *semantic feature cannot increase* Sizer/Risk output (overlay is min(1,·) in risk but the new numeric features entering via `DecisionFeatureSet` have no monotone-safety test). Add one.

---

### 3.4 Retrospective agentic improvement loop

Structure (ONT 14) matches the required pattern: FailureCase → Diagnosis → ChangeProposal → ExperimentManifest(frozen datasets/seeds/holdout) → ExperimentOutcome → differential eval vs **permanent relational champion on identical frozen snapshots** → shadow → human/policy gate → promote/rollback → immutable Outcome. Conformant on: identical-snapshot comparison (`frozen_case_set_hash`), versioned patches (`patch_hash`), offline replay, rollback (`ShadowMonitor`), insert-only trace, author≠approver.

**Gaps vs required behavior:**
- **Diagnosis buckets are a free string** (`root_cause_class: str`) and omit **data/retrieval/evidence/model/policy/execution**. Ungoverned routing. **P2.** Closed `RootCauseClass` StrEnum: `identity, coverage, temporal, extraction, ontology, query, inference, aggregation, explanation, data, retrieval, evidence, model, policy, execution`.
- **Shadow not a mandatory pre-activation state.** `PromotionPublisher.publish` can activate without a required prior successful shadow. **P2.** Require `SHADOW_RUNNING → SHADOW_PASSED` before decision-feature-affecting activation.
- **Independence is instance-only.** author≠approver checked, but evaluator/red-team may share model with the steward. **P2.** Record distinct `evaluator_id`, `red_team_reviewer_id`, `promoter_id`; require distinct model IDs.

**Risks & mitigations:**
- *Goodhart / multiple testing* — repeated challengers against visible public cases inflate wins. Log active-challenger count in `ExperimentManifest`; pre-register; keep holdout sealed from proposers; apply a multiplicity correction to reasoning-metric thresholds (analogous to base DSR, no numeric value invented).
- *Leakage / feedback contamination* — growing public `FailureCase` set teaches the distribution; a reporter that is the erring agent under-reports. Add `public_case_freeze_timestamp` (challenger trains only on cases predating freeze); FailureCases created by the **evaluator** role, not the reasoning agent; every challenger's suite plants future facts + late arrivals.
- *Self-confirming ontology* — steward proposes vocabulary then benefits from it; evaluate against externally-labeled factual cases and the relational champion, never ontology-derived labels alone.
- *Regime drift* — frozen cases miss new regimes; scheduled human-reviewed holdout rotation.
- *Live-P&L optimization / promotion bias* — **no economic/P&L metric may be a primary reasoning-promotion gate.** Add `forbids_economic_primary_gate: Literal[True]` on `ExperimentManifest`, enforced by the gate; policy-approver must not have authored any change in the auto-promotable class.

**Minimum governance state machine:**
`REPORTED → DIAGNOSED(closed bucket) → PROPOSED(risk,patch_hash) → CHALLENGER_BUILT → OFFLINE_REPLAYED → HOLDOUT_EVALUATED → SHADOW_RUNNING → SHADOW_PASSED → PROMOTION_RECOMMENDED → DECIDED(HIGH/MED→human≠author≠evaluator; LOW→approved policy) → ACTIVE | REJECTED | ROLLED_BACK`.
**Contracts:** promotion = new immutable release → `activate_and_append_event(expected_active_release_id=…)` (CAS); rollback = `rollback_and_append_event` restoring prior pointer atomically + event + HITL notice; neither edits in place.

---

### 3.5 Prioritized findings and exact amendments

**Blocking before implementation**

| ID | Sev | Anchor | Finding | Consequence | Amendment | Owner | Validating test |
|---|---|---|---|---|---|---|---|
| F-01 | P1 | ONT Task 6 "Modify: `kg/neo4j_store.py`, `ports/graph.py`" | Modifies files created only by replaced TOS 15–16 | Collection/import break after splice | Ont 6 **Create**s Neo4j projection under `semantic/projections/neo4j.py`; add port-only `GraphStorePort` stub in TOS 14 | ONT 6 (+TOS 14) | `test_ont6_builds_without_kg_store` on fresh repo post-TOS14 |
| F-02 | P1 | TOS 18 "Consumes admitted symbol/direction" vs ONT 12 `DecisionFeatureSet` | No `DecisionFeatureSet→candidate` adapter | Resumed TOS 18+ not executable / seam ambiguity | Add deterministic `feature policy → AdmittedCandidate`; amend TOS 18 to consume it | ONT 15 + TOS 18 | `test_task18_consumes_decision_feature_set_only`; hot-path import test |
| F-03 | P1 | ONT plan "replaces 15–17"; TOS 19 `ExposureVector`, TOS 35 KG replay/weights | Producers of `ExposureVector`/replay artifacts removed | TOS 19/35 cannot compile or silently revive KG | Produce compatibility exposure/replay artifacts from relationship packets, or amend TOS 19/35 to consume semantic motifs via projector | ONT 15 + TOS 19/35 | `test_no_resumed_task_imports_skipped_kg`; `test_replay_uses_semantic_or_declared_vector` |
| F-04 | P1 | ONT 5 `rdf.py` `serialize(format="nt")` | N-Triples drops named-graph IRI from hashed bytes | Cross-store equivalence always fails | Use `format="nquads"` (verify `rdflib` pin) or hash per-graph with IRI prefixed to bytes | ONT 5 | `test_rdf_serialization_contains_graph_iri`; equivalence passes |
| F-05 | P1 | ONT 7 `SemanticSnapshotBuilder.build` / `seal_semantic_manifest` | Projections keyed by `proposed_snapshot_id`; sealed ID recomputed differently | Sealed snapshot fails later retrieval/audit | One deterministic ID end-to-end (precompute→build→verify→activate) | ONT 7 | `test_sealed_id_matches_projection_and_query_binding` |
| F-06 | P1 | ONT 5 `fingerprint.py` `received_at.isoformat()` across 3 stores | Datetime lexical drift → mismatched SHA-256 | `ProjectionMismatch` on every valid snapshot | `normalize_utc(dt)` (astimezone UTC, fixed form) used in all fingerprint paths | ONT 5/6/7 | `test_projection_equivalence` with planted claim |
| F-07 | P1 | ONT 3 `blob_store.py` `async def` + sync `Path.*` | Blocks event loop | Async tests hang / nondeterministic | Wrap in `asyncio.to_thread`/`anyio.Path`; mark FS store test-only | ONT 3 | async timing/no-block test |
| F-08 | P1 | ONT 1 `registry.py` | Missing imports; payload union unregistered; in-memory fake lacks `append_in_transaction` | `mypy`/collection + integration failure | Add imports; register `OntologyReleasePublished` in union+deserializer; add method to in-memory store or force Postgres fixture | ONT 1 | `mypy`; event round-trip; `test_ontology_registry` |
| F-09 | P1 | ONT 1 `0002…` vs TOS `20260721_0002…` | Ambiguous Alembic head chain | Multiple heads / migration failure | Explicit `revision`/`down_revision` linear chain: `0001_event_log → ONT release/evidence → improvement → market/accounting/calibration` | ONT 1/3/14 + TOS 29–31 | `alembic heads`==1; `upgrade head` from empty |

**Blocking before shadow**

| ID | Sev | Anchor | Finding | Consequence | Amendment | Owner | Test |
|---|---|---|---|---|---|---|---|
| F-10 | P1 | ONT modules vs ONT 5 `rdf_mapping.py` predicates | Projection vocab `urn:trading:*` ≠ ontology `tos:` | SHACL never validates decision projection | Map predicates to ontology IRIs or add SHACL+fixtures over projection vocab | ONT 5 | `test_projected_claim_conforms_to_shapes` |
| F-11 | P1 | ONT 5 `claim_to_quads` `URIRef(subject_id)` | Non-IRI canonical IDs | Invalid/inconsistent RDF | Canonical IRI encoder `urn:trading-os:id:<type>:<id>` in RDF+Neo4j fingerprints | ONT 5/6 | `test_ids_encoded_as_absolute_iris` |
| F-12 | P1 | ONT 12 sync `project` + DB-backed `load_exact` | Sync call blocks in async handoff | Hidden deadlock in EOD | Make `project` async or require preloaded packet cache | ONT 12 | async boundary test |
| F-13 | P2 | ONT 14 `Diagnosis.root_cause_class: str` | Free-string, missing data/retrieval/evidence/model/policy/execution | Ungoverned routing | Closed `RootCauseClass` StrEnum | ONT 14 | reject unknown class |
| F-14 | P2 | ONT 14 `PromotionAuthority`/`ShadowMonitor` | Activation possible without required prior shadow; evaluator/promoter not distinct-model | Untested activation / non-independent promotion | Require `SHADOW_PASSED` before feature-affecting activation; record distinct `evaluator_id`/`promoter_id`/`red_team_id` with distinct model IDs | ONT 14 | `test_promotion_requires_shadow_and_role_independence` |
| F-15 | P2 | ONT 5/6 direct-write tests | Only assert method absence | No credential/network write protection | Read-only creds/network profile tests | ONT 5/6/15 | runtime write raises permission error |

**Blocking before economic use**

| ID | Sev | Anchor | Finding | Consequence | Amendment | Owner | Test |
|---|---|---|---|---|---|---|---|
| F-16 | P1 | ONT 13 "exposure/risk secondary"; TOS 34/35 | No barrier stopping reasoning wins from altering size/risk pre-economic gate | Reasoning quality mistaken for alpha | `ExperimentManifest.forbids_economic_primary_gate: Literal[True]` enforced by gate; ontology features enter size/risk only after TOS 34 economic gate | ONT 13/14 + TOS 34/35 | `test_semantic_promotion_alone_cannot_enable_orders_or_size` |
| F-17 | P1 | ONT 14 growing public `FailureCase` | Distribution leakage to proposer | Goodhart overfit | `public_case_freeze_timestamp`; challenger trains only on pre-freeze cases; FailureCase authored by evaluator | ONT 14 | `test_challenger_excludes_post_freeze_cases` |
| F-18 | P2 | §3.3 gap | No monotone-safety test on new numeric `DecisionFeatureSet` inputs to Sizer/Risk | Semantic feature could inflate size | Property test: ontology features can only tighten (never raise) sizing/risk output | TOS 18/19 | `test_semantic_features_never_increase_size_or_risk` |

**Non-blocking**

| ID | Sev | Anchor | Finding | Amendment |
|---|---|---|---|---|
| F-19 | P2 | ONT 2 `AvailabilityWindow` | `occurred_at` not `≤ published_at`; naive datetimes accepted | Add ordering + reject naive/non-UTC |
| F-20 | P2 | ONT 3 `admitted_claims_as_of` `model_copy` | Validator bypass on `state` | `model_validate({**dump,"state":state.value})` |
| F-21 | P2 | ONT 6 `to_native()` | Fails on ISO-string temporal | `hasattr` guard |
| F-22 | P2 | ONT 9 `pytest.raises(ValueError, match="decision_cutoff")` | Pydantic raises `ValidationError`; message won't match | `raises(ValidationError)` + substring check |
| F-23 | P3 | ONT 1 migration naming; Neo4j pin `2026.06.0` vs `5-community` | Style/pin inconsistency | Standardize naming; pin one Neo4j image+driver |
| F-24 | P3 | ONT 3 `EvidenceSpan.span_hash`; `_admission_states_as_of` | Advisory hash / silent state filter | Document both |

Prefer these small amendments over redesign; the architecture is sound.

---

### 3.6 Final decision

**(a) Build the ontology capability — GO.** The narrowed semantic-evidence/provenance/retrieval/audit layer is justified; invariants (permanent relational champion, snapshot-bound provenance-returning queries, deterministic policy consumes only `DecisionFeatureSet`, no autonomous-alpha claim) are correctly structured.

**(b) Execute the current ontology plan unchanged — NO-GO.** Nine P1 implementation blockers (F-01…F-09) are compile/collection/equivalence failures that break the first integration run. Apply the top-five amendments first.

**(c) Graph/agent output into shadow decisions — REVIEW (conditional GO).** Permitted only after all P1 impl + before-shadow findings close (esp. F-10 SHACL-over-projection, F-11 canonical IRIs, F-12 async projector, F-13 closed buckets, F-14 mandatory shadow+role independence, F-15 credential write-denial), and a challenger beats the relational champion on the frozen suite on ≥1 pre-registered reasoning metric with zero safety regressions. No order placement or risk change in shadow.

**(d) Economic/live influence — NO-GO (current state).** Requires: semantic promotion cleared; F-16 (economic-gate isolation) + F-17 (leakage freeze) + F-18 (monotone-safety) resolved; base TOS 34 90-day paper manifest satisfied (CPCV/DSR, rule-null + buy-and-hold beat, required replays, forward paper); all TOS 36 live blockers attested. Reasoning quality alone is insufficient.

**Top five amendments (priority order) with gates.**
1. **F-01** Ont 6 creates its own Neo4j projection; add port stub to TOS 14. *Entry gate M2.*
2. **F-04 + F-06** N-Quads + uniform `normalize_utc`; unblocks all cross-store equivalence. *Entry gate M2.*
3. **F-05** Single deterministic `SemanticSnapshotId` binding ledger/RDF/Neo4j/queries/audit. *Entry gate M2.*
4. **F-02 (+F-18)** Deterministic `DecisionFeatureSet → candidate` adapter with monotone-safety proof; amend TOS 18/19/32/35. *Exit gate before resuming TOS 18.*
5. **F-16 + F-08 + F-09** `forbids_economic_primary_gate=True`, executable event registration, single Alembic head. *Safety/build gate before any loop run.*

**Entry/exit gates.**
- *Enter ONT M1:* TOS 1–14 pass incl. independent rule-null; F-01…F-09 resolved; single Alembic head from empty DB; semantic packages type-check without skipped KG files.
- *Exit → shadow:* relational/RDF/Neo4j equivalence on frozen snapshots; rule-null + relational champion operate with Fuseki/Neo4j/LLM/reasoner **down**; templates reject unrestricted graph text; closed diagnosis buckets + independent promotion identities; write-denial proven by credentials/network.
- *Exit → economic:* challenger beats champion on pre-registered reasoning metrics with no protected-metric regression; feature adapter passes hot-path import + no-risk-increase; TOS 34 gate + required replays + forward paper pass; compliance/protection/reconciliation/accounting/live-blockers satisfied.

**Retirement conditions (retire semantic expansion; keep permanent relational champion + evidence ledger for audit).** After the frozen remediation budget is exhausted, retire/pause if any persist: entity false-merge or future-fact leak above pre-registered safety threshold; no material reasoning-metric improvement over relational retrieval across N independently evaluated challenger generations; cross-store equivalence/rebuild reproducibility cannot be stabilized; maintenance cost exceeds frozen benefit threshold; repeated missing-knowledge/false-premise abstention failures; any promotion achieved by optimizing economic/live P&L (F-16 violation); or ontology work delays/weakens the deterministic paper-trading foundation. On retirement: freeze active release, serve relational champion, retain ledger, do not expand graph-derived features into the hot path.

<!-- CHUNK-C SELF-AUDIT: 1/1 top-level sections emitted; cross-plan splice audited; API/type/persistence/services checked; end-to-end deterministic boundary traced; retrospective loop+governance assessed; four explicit final decisions; every material finding has severity+anchor+consequence+remediation+owner+test; no truncation -->

<!-- STITCH SELF-AUDIT: chunks A+B+C stitched in order; §§1-3 present; all three chunk self-audits present; source plans unchanged -->
