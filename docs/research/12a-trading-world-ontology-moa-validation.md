# Validated Synthesis — Trading World Ontology MOA Review

> **Controlling advisory:** This synthesis supersedes the raw MOA findings wherever they conflict. The joint `NO-GO` applies to accepting the raw review as authoritative, not to the bounded ontology capability itself.
>
> **Raw report under test:** [12-trading-world-ontology-moa-review.md](/Users/I321170/Documents/Projects/trading-bot/docs/research/12-trading-world-ontology-moa-review.md:1)

## Joint Verdict: NO-GO

## Summary

The mechanical joint-verdict rule yields **NO-GO**: V1, V2, and V3 are each NO-GO, and any one NO-GO is sufficient. Across the three lenses there are **11 blocking FAILs and 4 non-blocking WARNs**.

This verdict applies to accepting `12-trading-world-ontology-moa-review.md` as an authoritative review, implementation-readiness gate, defect inventory, severity ranking, or promotion specification. It does **not** by itself reverse the underlying capability proposition. Collectively, the reports continue to support a bounded ontology as a semantic/evidence/provenance/retrieval/audit layer, with a permanent relational champion and no causal or autonomous-alpha claim. They also support **NO-GO for executing the implementation plan unchanged** and **NO-GO for live economic influence now**. Shadow evaluation remains no more than **REVIEW**, and only after the validated blockers and evaluation/governance gaps below are corrected.

The principal reason the generated review is non-authoritative is not merely severity disagreement. Several of its P1 mechanisms are reversed, already guarded, non-executable at the proposed task position, or based on conflated ID/type domains. At the same time, the reports validate a narrower set of real implementation blockers and two additional governance/evaluation gaps: LLM knowledge-time contamination and the absence of a mandatory canary before live activation.

## Lens Verdicts

| Lens | Verdict | FAIL | WARN | Synthesis |
|---|---:|---:|---:|---|
| V1 — semantic-temporal correctness | NO-GO | 2 | 2 | Invalid universal temporal ordering and materially unfaithful findings prevent semantic acceptance. |
| V2 — executable plan/types/operations | NO-GO | 7 | 1 | Multiple P1 diagnoses reverse actual control flow/types or propose non-executable remedies, despite identifying several genuine blockers. |
| V3 — usefulness/evaluation/governance | NO-GO | 2 | 1 | Historical LLM contamination is uncontrolled and the promotion flow lacks a mandatory canary; success attribution is also too permissive. |
| **Joint** | **NO-GO** | **11** | **4** | Joint rule: any lens NO-GO makes the synthesis NO-GO. |

## All FAILs (blocking)

1. **V1 / C4 — Temporal and provenance correctness.** The lens quotes artifact line 369 as alleging **“`occurred_at` not `<= published_at`”** and directing **“Add ordering.”** It finds this materially false because an advance merger announcement, scheduled policy event, future-period guidance, or future delisting can be published before occurrence/effect. The lens states that enforcing the ordering would **“reject valid point-in-time evidence and collapse announcement time into event-effective time.”** The correct hard rule is availability at the decision cutoff; there is no universal occurrence/publication order.

2. **V1 / C8 — Findings fidelity.** The lens identifies multiple mechanisms that cannot coexist with the approved design as reported. For §1 F1, the artifact says a feature **“absent from every `numeric_allowlist`”** reaches `DecisionFeatureSet`, but the lens reports that the positive allowlist rejects it. For §1 F4, the claimed choice between every snapshot failing and entailments **“silently escap[ing] equivalence”** is described as a **“materially invented dichotomy.”** It also reports that the P2 F-14 demand for evaluator/promoter/red-team **“distinct model IDs”** contradicts the rule that roles may share models while identities/authority remain separated, and that F-19's time order is contradicted. These reversals make the findings set unsafe as an authoritative defect inventory even though many other semantic boundaries are faithful.

3. **V2 / C2 — API and type fidelity.** Four reported artifact claims conflict with the anchor contracts: (a) artifact lines 43/81 say an unlisted key reaches output, while the lens quotes the actual guard as **“`if qualified in policy.numeric_allowlist`”**; (b) line 82 alleges policy-mediated same-author approval although `PromotionAuthority.decide` already returns `awaiting_human` for that equality; (c) lines 55/88 compare `semantic_snapshot_id` with `ValidatedDataSnapshotId` even though the types carry distinct semantic and validated-data IDs; and (d) line 261 invents a DB-backed async requirement where both the repository port and projector are explicitly synchronous. The lens concludes that these are material direction, ID-domain, and contract errors.

4. **V2 / C3 — Suspected Chunk-A claims.** The lens rejects all four sampled Chunk-A hypotheses as written: F1/H2 reverses the positive allowlist; F2 duplicates an existing same-author guard; F3 says the champion/cases sit behind infrastructure even though **“Task 4 creates the cases before Task 5”** and asks E2 to pass before its RDF/Neo4j arms exist; and F8/H8 finds a real cache problem but proposes a check that **“cannot detect a stale `validated_data_snapshot_id`.”** The failure is both evidentiary and positional: suspected defects were promoted to blockers without tracing the full control flow, task prerequisites, and ID bindings.

5. **V2 / C4 — Persistence, transactions, and migrations.** The artifact turns permitted mechanisms or unknowns into proven blockers. The lens says artifact lines 115/183 incorrectly call a mutable active-release pointer an append-only violation even though the design deliberately uses a **“CAS-managed operational pointer plus an appended audit event.”** It also says lines 229/344 infer **“Multiple heads / migration failure”** without the `revision`/`down_revision` values needed to prove that consequence. Finally, line 247 bundles sample-import issues with an unsupported requirement that a generic in-memory fake implement a registry-specific transactional port. These findings must be split and conditioned on inspected contracts.

6. **V2 / C5 — Services, projections, rebuilds, and idempotency.** The reported N-Triples blocker is false for the stated one-graph-per-build API: the lens reports that the graph IRI is passed out-of-band to Graph Store and included in the hash, so the claim that graph membership is always lost and equivalence always fails is **“directionally wrong.”** The claimed absence of Neo4j snapshot stamping/filtering is also largely already implemented. The same check preserves real findings—provisional-versus-sealed snapshot-ID inconsistency, RDF/SHACL vocabulary mismatch, and lack of credential/network write-denial tests—but their validity does not rescue the false P1 mechanisms bundled into this section.

7. **V2 / C6 — Test order and executable contracts.** The artifact alleges blockers contradicted by the named task sequence and tests. The lens again states that Task 4 creates the frozen competency fixture before Task 5; reports that the `DecisionFeatureSet → HotPathCandidate` seam is explicitly required, though its signature/test is underspecified; rejects a bundled compile/fixture inference; and notes that **“Pydantic `ValidationError` is a `ValueError`,”** so the cited `pytest.raises(ValueError, match="decision_cutoff")` test is not necessarily broken. The genuine missing `ExposureVector`/replay replacement remains a blocker, but the section as a whole is not a reliable executable-contract judgment.

8. **V2 / C7 — Deterministic trading boundary.** Artifact F1's remediation would weaken the boundary it aims to protect. The lens says requiring every producer feature key to appear in **some** allowlist **“converts an exclusion policy into a coverage target.”** The approved invariant is strategy-specific positive admission, and the testable rule is that unknown/unapproved keys are absent from every applicable strategy output—not that all producer keys acquire a policy home. The artifact also overstates the seam as wholly absent; the missing work is a concrete adapter/test and legacy-consumer reconciliation.

9. **V2 / C8 — Finding quality.** Too many P1 findings have unsupported consequences, wrong severity, already-present remedies, or non-executable remediation. The lens specifically says several false P1s drive the artifact's line-384 **“nine P1 implementation blockers”** conclusion and top-five amendment list, so **“this is not a severity-only disagreement.”** Its exhaustive sample validates a narrower blocker set while reversing or downgrading A-F1/F2/F3/F4, B-F-01a/F-02/F-02b/F-04/F-05/F-06, C-F-02/F-04/F-06/F-07/F-08/F-09/F-12/F-17, and several P2/P3 claims. P1 status therefore needs proof of an exact path, consequence, failing test, and executable remedy.

10. **V3 / C5 — Point-in-time and leakage.** Data-time and holdout controls do not control knowledge already memorized by the evaluated LLM. The lens says that fixing a model version **“does not establish what post-event facts that model already memorized during pretraining or later fine-tuning”** and that historical 2020/2022 replay can therefore look point-in-time clean while being answered from model memory. It reports no model/fine-tune knowledge-cutoff metadata, post-cutoff stratification, masked entity/outcome variants, no-retrieval probes, or contamination sensitivity analysis. Contaminated cells must be excluded from promotion metrics.

11. **V3 / C7 — Agentic loop and governance.** The artifact's mandatory state machine moves from `SHADOW_PASSED` through promotion directly to `ACTIVE`. The lens finds that neither the state machine nor final exit gates require **“a bounded canary with explicit exposure limits, observation window, stop conditions, and automatic rollback.”** A generic reference to other live blockers is not an auditable canary condition. Mandatory `CANARY_APPROVED → CANARY_RUNNING → CANARY_PASSED` states and immutable receipts are required before broader live activation.

## All WARNs (non-blocking)

1. **V1 / C2 — Canonical authority and projections.** The artifact correctly calls RDF rebuildable and **“not truth authority,”** but labels the row **“RDF canonical/standards representation.”** The lens also reports that the factual-authority summary omits TimescaleDB and the operational event log. Correct the label and complete the authority inventory; this is imprecision, not a material reversal.

2. **V1 / C3 — Ontology release, version, and migration.** The release model is substantially accurate, but the artifact proposes a **“governed executable registry”** and says **“Record `git_commit_sha` and reject a dirty tree.”** The lens classifies these as optional hardening beyond the approved requirements for content-addressed releases and machine-readable migration. They must be labeled proposals, not existing P1 invariants.

3. **V2 / C1 — Task splice and prerequisites.** The main splice and Task 6 skipped-file dependency are correct, but artifact lines 221/227 overstate later modification of base Task 13 as a **“Central ambiguous splice.”** The lens reports that Task 7 already names the later modification and exact semantic snapshot binding. Historical-manifest compatibility is underspecified, but re-running Task 13 is not required.

4. **V3 / C8 — Usefulness decisions.** The artifact allows promotion when a challenger **“improves ≥1 pre-registered reasoning metric”** and retires only after an unspecified `N` generations. Without a minimum effect size, mandatory primary metric, multiplicity rule, and fixed `N`, an immaterial or selectively convenient gain can be called success. Tighten attribution criteria before shadow promotion or retirement decisions.

## Corrected Advisory Bottom Line

| Decision object | Corrected disposition | Reason supported by the lenses |
|---|---|---|
| Generated MOA review as authoritative | **NO-GO** | Eleven blocking lens failures include reversed mechanisms, conflated types, non-executable remediation, uncontrolled LLM knowledge-time leakage, and a missing canary. |
| Bounded ontology capability | **Retain the conceptual GO, narrowly scoped** | V1 validates layer separation, identity, evidence/belief/causal discipline, and fail-closed fallback; V3 validates the bounded value proposition, permanent relational champion, falsifiability, controlled comparisons, and causal/calibration discipline. This is not an alpha claim. |
| Execute the implementation plan unchanged | **NO-GO** | The reports validate concrete snapshot, compatibility, identity, assessment, fallback, splice, vocabulary, IRI, legacy-consumer, and activation-barrier defects. |
| Non-economic shadow evaluation | **REVIEW after amendments** | Shadow may proceed only after the validated implementation blockers, model-contamination protocol, and material-attribution gates are made executable; it must have no order/risk effect. |
| Live economic influence | **NO-GO now** | A shadow-to-live canary is absent, economic activation is not separately governed, and evaluation cells may be contaminated. |

The corrected plan should retain the ontology as a challenger behind the permanent snapshot-scoped relational champion. Semantic projection failure should fall back only where an equivalent baseline exists; baseline failure should close. No result from this synthesis supports graph-path causality, direct sizing, autonomous promotion, or autonomous alpha.

## Validated High-Confidence Findings

### Real implementation blockers to retain

| Raw finding(s) | Corrected high-confidence finding |
|---|---|
| B-F-01 / C-F-05 | Task 7 can bind/query projections with a proposed snapshot ID and derive a different sealed ID. Make one immutable final `SemanticSnapshotId` bind both projections and every answer, or make the build identifier/final identifier transition explicit and unqueryable until sealing. |
| B-F-03 | Compatibility checking is too narrow if it omits mappings, inference rules, and other meaning-bearing artifacts. Expand the compatibility contract and tests beyond limited syntax/predicate inspection. |
| B-F-06id | Flat untyped IDs/aliases can collapse issuer, security, listing, ticker, and venue/time scope. Introduce typed point-in-time identity keys and crosswalks. |
| B-F-13 | Observation-only evidence packets can fall into `insufficient` because assessment recognizes supporting assertion IDs but not declared observation semantics. Define and test observation support explicitly. |
| B-F-14 | Projection failures other than `TimeoutError` are not consistently normalized to the semantic-unavailable path, so intended baseline fallback/fail-closed behavior is incomplete. |
| C-F-01 | Ontology Task 6 modifies `src/trading_os/kg/neo4j_store.py`, but the explicit splice skips the base task that creates it. Create/own that module in the ontology sequence or change the dependency. |
| C-F-03 | Resumed base consumers still expect `ExposureVector` and KG replay/weight artifacts whose producers were skipped. Supply replacement types/APIs and integration tests before resuming. |
| C-F-10 | Emitted RDF vocabulary (`urn:trading:*`) does not match the ontology/SHACL vocabulary (`urn:trading-os:ontology#*`). Use one governed vocabulary and prove SHACL applies to emitted data. |
| C-F-11 | Canonical identity strings are passed to `URIRef` without a guarantee that they are absolute IRIs. Define canonical IRI construction/validation and reject invalid identities before projection. |
| C-F-16 | Semantic/reasoning release promotion is not the same as permission for economic activation. Add an independently approved, snapshot-bound decision-feature activation artifact and keep semantic promotion unable to change orders or risk by itself. |

### Additional high-confidence controls

- Add the V3 C5 model-knowledge contamination protocol: persist available model/fine-tune cutoff metadata, stratify before/after cutoff, add masked-entity/outcome and no-retrieval probes, label evidence-free correctness as contamination, and exclude contaminated cells from promotion metrics.
- Add the V3 C7 mandatory canary states between shadow and broad activation, with caps, a minimum observation horizon, protected-metric alarms, automatic rollback, independent approval, and immutable receipts.
- Preserve the canonical boundaries validated by V1: Git/release registry for ontology authority; append-only factual/provenance history; RDF and Neo4j as rebuildable projections; typed temporal identity; evidence/assertion/belief separation; deterministic decision features; and fail-closed/fallback behavior.
- Retain supported P2 hardening: ledger-verified syndication origin clusters (A-F5), registry-level author/approver recheck (A-F6), physical claim/assertion separation (F-08a), a closed diagnosis enum (C-F-13), activation proof tied to shadow/canary evidence (the supported portion of C-F-14), and credential/network write-denial tests (C-F-15).
- Correct the stale-cache issue by validating or keying the complete request binding—both semantic and validated-data snapshot IDs, plus represented release/cutoff—not by comparing unlike ID domains.
- Tighten promotion usefulness: pre-register a primary metric, minimum material effect, multiplicity rule, protected metrics, and fixed retirement horizon `N`.

## Retracted or Downgraded Raw Findings

### Retract or reverse

| Raw finding | Corrected disposition |
|---|---|
| A-F1 / §1 F1 / H2 | **Retract and reverse.** Unknown/unlisted numeric keys are excluded by the active positive allowlist. Replace the proposed all-key coverage test with per-strategy rejection tests. |
| A-F2 / §1 F2 exact bypass | **Retract the alleged current bypass.** The same-author policy condition is already checked. Retain author/approver separation as an invariant and optionally recheck it at publication as defense in depth. |
| A-F3 / F3 | **Retract.** Task 4 creates the relational champion and frozen cases before Task 5; graph ablation E2 cannot pass before Tasks 5–6 create its challenger arms. |
| B-F-01a / §2 F-01a | **Retract as a P1 invariant.** A CAS-managed active pointer plus append-only activation events is allowed; immutable releases and audit events remain required. |
| C-F-04 | **Retract.** N-Triples does not lose named-graph identity in the stated single-graph API because graph IRI is carried out-of-band and hashed. Do not mandate N-Quads for this reason. |
| C-F-12 | **Retract.** The repository and projector contracts are deliberately synchronous; no DB-backed async deadlock path was shown. |
| A-F9 | **Retract the default-inference allegation.** No default reasoner wrapper was identified. A no-unapproved-entailment contract test may remain as hardening. |
| C-F-22 | **Retract.** Pydantic `ValidationError` subclasses `ValueError`, and the missing-field message can name `decision_cutoff`. |
| P2 F-19 | **Retract and prohibit.** There is no universal `occurred_at <= published_at` invariant. Validate availability against cutoff without collapsing event and publication time. |
| P2 F-14 distinct-model requirement | **Retract as a requirement.** Role/identity and authority separation are mandatory; evaluator/promoter/red-team model IDs need not be distinct unless adopted as an explicit policy experiment. |

### Downgrade, split, or rewrite

| Raw finding | Corrected disposition |
|---|---|
| A-F4 / §1 F4 | **Downgrade to reproducibility hardening.** The claimed fail-or-escape dichotomy is false; specify and test derived-answer reproducibility. A separate `entailment_set_hash` is optional if existing ruleset/projection hashes suffice. |
| B-F-02 / §2 F-02 | **Downgrade.** Snapshot stamping, snapshot-qualified keys, filtered reads, and seal rejection already exist. Atomic whole-graph replacement may be operational hardening, but the stated missing controls are mostly present. |
| B-F-02b / §2 F-02b | **Downgrade.** Binding motif/weight/model IDs is plausible once the actual runtime artifact replacing skipped Task 16 is defined; it is not yet a current P1 contract. |
| B-F-04 / §2 F-04 | **Rewrite.** Exact historical release retention is semantically required, but bypassing the supported range is not established. Separate exact-replay preservation from any compatibility/cutoff policy defect. |
| B-F-05 / §2 F-05 | **Downgrade.** Unknown availability is already ineligible. A first-class unavailable state and retrieval/parser activity timestamps improve auditability but are not proven P1 admission defects. |
| B-F-06 | **Downgrade as speculative.** Holdout self-ground-truth through `value_text` lacks a demonstrated prompt consumer. Retain expected-answer independence and add taint tests only where an executable render path exists. |
| C-F-02 / §3 F-02 | **Downgrade to WARN/P2.** The feature-to-candidate seam is required and named, but its exact adapter signature and test are underspecified. |
| C-F-06 | **Downgrade and narrow.** Temporal normalization is a real risk for semantically equivalent offsets, but failure of every valid snapshot was not established. Add canonical-time fixtures. |
| C-F-07 | **Downgrade to P2.** Small local synchronous file I/O may block an event loop but does not prove hangs or nondeterminism; define an async object-store port for production if needed. |
| C-F-08 | **Split.** Literal missing imports may be compile defects; event-union registration depends on the base union; a generic in-memory fake is not required by the named Postgres registry fixture. |
| C-F-09 | **Downgrade to P2 specification gap.** Require explicit `revision`/`down_revision` ordering, but do not claim multiple heads until the chain proves it. |
| C-F-17 / §3 F-17 | **Downgrade the stated direct leak to governance risk.** The holdout is sealed; distribution overfitting remains plausible. Treat V3 C5's model-knowledge contamination as the distinct blocking issue. |
| A-F8 / F8 / H8 | **Rewrite, not discard.** The early cache return is a real risk, but the artifact compares unlike ID domains. Key or validate both snapshot IDs and the rest of the request binding. |
| F-12 migration registry / clean-Git rule | **Downgrade to optional hardening.** Machine-readable migrations and content-addressed immutable releases are required; a separate executable registry and dirty-tree rejection are proposed mechanisms. |
| F-14 shadow proof | **Split.** Requiring activation evidence is supported; requiring different model IDs is not. Extend the supported state proof through mandatory canary receipts. |
| F-18 monotone safety | **Narrow.** Direct narrative/graph output must not set size, and LLM-originated closed classifications are tighten-only/gate-rank. Do not impose a universal rule that every deterministic allowlisted ontology feature can only decrease output. |
| Task 12–13 “central ambiguous splice” | **Downgrade to compatibility documentation.** The later modification is already named; specify historical-manifest compatibility without requiring Task 13 to be rerun. |

## Suggested Prompt Patch

Copy the following into the generator prompt. Each patch is keyed to one blocking lens FAIL, names its insertion point, and includes an acceptance test.

```text
[PATCH V1-C4 — Chunk B, Temporal/Provenance hard rules; insert immediately after the PIT time-dimension definitions]
Never infer or require a universal ordering between occurred_at/effective_at and published_at. Advance announcements and future-effective events may have published_at < occurred_at. Eligibility at a decision cutoff is governed by actual availability/provenance (including required received_at and recorded_at checks and supersession), not by occurrence-before-publication. Any additional temporal ordering must be scoped to a named event type and cited to an explicit contract.
TEST: Include (1) an advance announcement with published_at < occurred_at that remains valid if available by cutoff, (2) a late report with occurred_at < published_at that is excluded before receipt/recording, and (3) unknown availability that is ineligible. Reject any finding that proposes occurred_at <= published_at globally.

[PATCH V1-C8 — Chunk C, Findings Fidelity hard rules; insert before the severity/final-findings table]
For every finding, record: exact artifact claim; exact anchor/code mechanism; control-flow/type trace; whether the item is a contradiction, missing requirement, underspecification, or optional hardening; and the smallest executable remediation. If an existing guard negates the alleged path, retract the finding. Do not turn an optional mechanism into an approved invariant, and do not require model separation where only role/authority separation is required.
TEST: Mandatory sentinel audit must correctly reject these four claims unless new evidence proves them: absent allowlist keys reach output; entailments necessarily fail or escape without a new hash; distinct model IDs are mandatory; occurred_at must precede published_at.

[PATCH V2-C2 — Chunk A, API/Type Fidelity hard rules; insert before generating suspected defects]
Build a typed contract ledger for every referenced API: input/output types, sync/async status, guards, ID domains, and caller/callee flow. Never compare SemanticSnapshotId with ValidatedDataSnapshotId, infer async from storage speculation, or allege bypass without tracing the existing guard. Quote the exact branch that admits or rejects the value.
TEST: The generated review must show that unknown numeric keys are dropped by the positive allowlist, same-author policy approval reaches awaiting_human, semantic and validated-data IDs remain distinct, and a synchronous port is not called a deadlock without a blocking implementation path.

[PATCH V2-C3 — Chunk A, Suspected-Claim adjudication; insert after the hypothesis list and before any P1 promotion]
Treat every Chunk-A suspicion as a hypothesis. Attempt to falsify it by tracing the complete branch, cache-hit path, task dependency graph, and named tests. A task cannot be moved before its prerequisites, and a cross-arm experiment cannot gate creation of the arms it compares. Cache checks must cover the complete request binding, not a same-named or different-domain ID.
TEST: Produce a dependency DAG proving Task 4 follows Tasks 1–3 and precedes Task 5, while E2 follows creation of RDF and Neo4j arms. For stale-cache findings, demonstrate a failing case that changes only ValidatedDataSnapshotId and verify the proposed fix catches it.

[PATCH V2-C4 — Chunk B, Persistence/Migrations section; insert after the authority-and-mutability table]
Enumerate immutable ledger rows, mutable CAS-managed operational pointers, and append-only audit events separately. Do not label a CAS pointer an append-only violation unless the governing contract requires event-derived state. Do not claim Alembic multiple heads without inspecting revision and down_revision. Do not require a generic fake to implement a port unless a named test/fixture uses that fake.
TEST: Show one successful CAS activation with an appended event and no mutation of immutable releases; validate the explicit migration chain from ontology migrations into resumed base migrations; map each required fake method to a named test fixture.

[PATCH V2-C5 — Chunk B, Services/Projections section; insert before projection-blocker findings]
Analyze serialization together with its transport API. If graph identity is supplied out-of-band and included in the hash, do not claim N-Triples loses the named graph. Before alleging partial-query exposure, inspect snapshot stamps, snapshot-qualified keys, read filters, sealing, and activation. Distinguish method-surface restrictions from credential/network denial.
TEST: Round-trip one named graph through the exact Graph Store API and verify graph IRI/hash membership; attempt to query an unsealed/mismatched snapshot and require rejection; run credential-level direct-write denial tests; separately reproduce final-ID/projection-ID mismatch and vocabulary mismatch.

[PATCH V2-C6 — Chunk C, Task Order and Executable Contracts; insert before the implementation verdict]
Create a producer/consumer/file-ownership matrix across skipped, ontology, and resumed tasks. A compile/test P1 requires an exact unresolved symbol, missing file, incompatible signature, or failing named test. Underspecified signatures are WARN/P2 unless a consumer cannot be implemented. Split bundled findings when their evidence or fixture requirements differ.
TEST: The matrix must identify the real missing neo4j_store.py producer and missing ExposureVector/replay replacements, while recognizing the named DecisionFeatureSet-to-HotPathCandidate seam. Run/type-check the cited exception contract before claiming ValueError/ValidationError incompatibility.

[PATCH V2-C7 — Chunk C, Deterministic Boundary hard rules; insert immediately before seam acceptance criteria]
Preserve strategy-specific positive admission: only keys in the active policy numeric_allowlist may enter DecisionFeatureSet. Never use “every producer key appears in some allowlist” as a safety target. Raw narrative, RDF/graph paths, and agent outputs cannot set sizing/risk; deterministic allowlisted observations cross only through the projector and deterministic strategy seam.
TEST: For every strategy policy, inject unknown, known-but-unapproved, narrative, and wrong-lineage fields and assert all are absent/rejected; assert only explicitly approved fields appear; then verify the resulting DecisionFeatureSet is the sole semantic input to HotPathCandidate construction.

[PATCH V2-C8 — Chunk C, Finding Quality and Severity; insert before counting P0/P1 blockers]
A P1 must include: exact source location, reachable mechanism, concrete consequence, minimal reproducer or failing contract test, executable remediation at the stated task position, and confidence. Mark duplicates, split bundles, and downgrade unsupported consequence claims. Do not count a P1 or use it in remediation ordering until all fields pass adversarial review.
TEST: Re-score every P1 against the sentinel set A-F1/F2/F3, B-F-01a/F-02, C-F-04/F-12/F-22. The final blocker count and top amendments must be recomputed after retractions/downgrades, with duplicate B-F-01/C-F-05 counted once operationally.

[PATCH V3-C5 — Chunk A, Evaluation/Leakage hard rules; insert immediately after the frozen experiment contract]
Pre-register an LLM knowledge-time contamination protocol. Persist model and fine-tune knowledge-cutoff metadata where available; stratify cases before/after that cutoff; add masked entity/outcome variants and no-retrieval probes; classify evidence-free correct answers as contamination; report sensitivity by stratum; and exclude contaminated cells from promotion metrics. If cutoff metadata is unavailable, mark the affected historical cell non-promotable unless masking/probes bound contamination.
TEST: For each historical case, run retrieval, no-retrieval, and masked variants; flag answers correct without admissible evidence; prove no flagged cell contributes to the primary promotion statistic.

[PATCH V3-C7 — Chunk C, Governance State Machine; insert between SHADOW_PASSED and ACTIVE]
Replace the direct transition with CANARY_APPROVED -> CANARY_RUNNING -> CANARY_PASSED -> ACTIVE. Canary approval must be independent and bind the exact release, snapshots, policy, model/prompt, symbols, notional/exposure cap, minimum observation horizon, protected metrics, stop conditions, and rollback target. Missing or mismatched canary evidence prohibits activation. Persist immutable canary receipts and trigger automatic rollback on any stop condition.
TEST: State-machine tests must reject SHADOW_PASSED -> ACTIVE, reject missing/expired/mismatched receipts, enforce caps and horizon, trigger rollback on each protected-metric alarm, and allow ACTIVE only from CANARY_PASSED with independent approval.
```

## Individual Lens Reports

The detailed lens reports are run artifacts retained for this session under `/private/tmp/trading-ontology-moa-review-20260721/verify/`:

- `verify-V1-semantic-temporal.md`
- `verify-V2-executability.md`
- `verify-V3-usefulness-governance.md`

The durable conclusions, evidence excerpts, counts, retractions, and prompt patches from all three reports are incorporated above.
