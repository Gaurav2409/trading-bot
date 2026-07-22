# MoA verifier V2 — FX / multi-asset capability and compliance integrity

**Reviewed:** `chunk-2.out.md` against `source-brief.md`, the approved Trading OS design, the
approved Trading World Ontology amendment, and the live-domain opportunity audit.

**Decision rule:** ambiguity in a safety, legal/compliance, identity, activation, accounting, or
migration contract is a failure. This review assesses architectural integrity, not legal advice.
The supplied RBI/NSE statements are treated as design inputs that must be reverified by a qualified
human before activation.

## Executive result

**FAIL. Keep every FX execution capability disabled. Do not adopt the proposed generic seams as
written, because some of them would also regress the approved India/US cash-equity V1.**

The extension correctly recognizes that currency futures require pair, contract, session, expiry,
margin, settlement, and multi-currency semantics, and it strongly states per-account household
isolation. Those strengths do not cure the blocking faults below: unsafe deactivation ordering,
an authority collision with `DecisionFeatureActivation`, incomplete derivative accounting and
reconciliation, identity/time incompatibility with the approved ontology, unsupported legal
overclaims, and a migration sequence with contradictory prerequisites.

## Required-lens scorecard

| Required check | Result | Basis |
|---|---|---|
| 1. Stable cross-asset kernel vs asset-specific semantics | **FAIL** | The control-plane/plugin direction is useful, but the boundary is neither executable nor compatible with the existing two-market V1. It says settlement currency is “trivially INR” and defaults account capability to NSE/BSE/IN even though V1 also contains USD-denominated Alpaca/US cash equities. It excludes all price/quantity/P&L semantics from the kernel without defining the typed envelopes and plugin ports that `OrderIntent`, ledger, risk, and reconciliation require. |
| 2. FX pair/contract/session/expiry/margin/P&L/reconciliation | **FAIL** | The delta table is broad but not safe enough to implement. Contract identity, quotation scale, daily MTM cash flows, margin/collateral state, expiry settlement, session/value-date calendars, and broker/clearing reconciliation remain ambiguous or incorrect for some pairs. |
| 3. India jurisdiction/venue gating without legal overclaim | **FAIL** | The verified principle—authorised person, permitted purpose, authorised ETP or recognised exchange, and no LRS remittance for overseas forex margin—is present. But the document turns this into unsupported blanket claims about all OTC spot FX, “illegal” cross-account analytics, and owner-only authority. |
| 4. Capability activation/deactivation safety | **FAIL** | Activation artifacts, precedence, and atomicity are underdefined. Deactivation can wait on a human override before the stop is applied, has no `REDUCE_ONLY`/position-management state, and can collide with the ontology’s separately approved feature-activation state machine. |
| 5. Household + multi-asset isolation | **FAIL** | Per-account custody and authority separation is mostly sound, but analytics netting contradicts aggregate exposure reporting; owner-only authority contradicts discretionary mandates; membership/visibility/mandate temporal changes are absent; and rollback proposes dropping governance tables. |
| 6. Ontology identity/time changes | **FAIL** | `OntologyVersion` and an `ontology_version_id` do not satisfy the approved release/snapshot/query/reasoning/feature contracts. The proposed derivative and spot identities conflate stable identity with mutable contract terms or transaction facts and omit the approved bitemporal evidence spine. |
| 7. Migration ordering | **FAIL** | Canonical identity/time foundations are not installed before new instrument schemas; FX research is unnecessarily coupled to family execution; Phase 2 contradicts Phase 1 on when the household view is populated; Phase 4 skips semantic/economic activation canaries; invented session-count gates do not resolve the controlling go-live conflict. |
| 8. Contradictions/hidden couplings | **FAIL** | There are contradictions within the extension and against both approved designs, including six “three” amendments, immutable releases that are later “frozen,” a deactivation described as fast despite a blocking acknowledgment, and a version-namespacing recommendation inconsistent with stable term IRIs. |

## Blocking findings

### FX-V2-01 — Deactivation ordering is unsafe

`chunk-2.out.md:112` says deactivation blocks new orders immediately, then requires
`hasOpenPositions(...)` and a human-acknowledged `ForceDeactivationOverride` *before proceeding*.
Lines 179–180 repeat that sequencing. This is contradictory and introduces a race and an
availability hazard: a compliance/data/venue failure must be able to revoke new-exposure authority
atomically even when the position query or human is unavailable.

Required correction:

1. Append and enforce `ENTRY_DISABLED` (or equivalent) first, atomically and with highest-precedence
   fencing for the affected scope.
2. Independently derive `NO_POSITION`, `REDUCE_ONLY`, or `MANAGEMENT_ONLY` from reconciled custody
   state. Open positions keep the plugin, broker transport, market/reference data, margin monitor,
   expiry manager, and reconciliation alive.
3. Require human override only for an exceptional action that would abandon or force-close an open
   position—not for disabling new exposure.
4. Specify conflict precedence, overlapping-scope intersection, unique active release selection,
   effective-time handling, stale-worker fencing, and revalidation for submit/amend/cancel/replace.
5. Never “freeze” or mutate a release (`line 145`); append a superseding revocation/activation event.

### FX-V2-02 — `AssetClassCapabilityRelease` can collapse independent authorities

The proposed release binds ontology, research schema, data, risk, execution, valuation,
reconciliation, compliance, and live mode in one artifact (`lines 77–95`). The approved ontology
instead requires a separately approved `DecisionFeatureActivation` binding Ontology,
QueryPack, ReasoningPolicy, support rules, FeaturePolicy, deterministic strategy, evaluation, and
canary receipts. Semantic promotion must never grant economic authority. The extension neither
binds that artifact nor says the two releases are an AND gate. Its `PAPER_ONLY → LIVE_ALLOWED`
sequence also omits `SHADOW`, paper canary, paper active, live canary, and rollback receipts.

Required correction: define capability as an independent execution ceiling. A decision may affect
orders only when the account/product capability, `DecisionFeatureActivation`, current compliance
profile, data entitlement, broker readiness, reconciled account state, and kill-switch generation
all match the decision and are simultaneously effective. None may imply or supersede another.

### FX-V2-03 — The proposed capability cardinality and defaults regress V1

`line 32` puts one `capability_gate_id` FK on every account and defaults it to NSE/BSE/IN;
`lines 80–92` scope a release to one asset class and one account. An account can have multiple
research/paper/live product scopes, and V1 already spans India and US cash equities. One account FK
cannot model that safely. “Settlement currency is trivially INR” (`line 30`) is false for the
approved USD Alpaca sleeve and conflicts with the existing two-currency accounting contract.

Required correction: use a many-record, deny-by-default account-capability association keyed by
account + jurisdiction/residency context + asset/product + venue/segment + broker account, with no
permission-bearing default. Preserve native, settlement, functional/reporting, and conversion-rate
currencies as distinct typed roles. Do not mark `CashEquityPlugin` simply `LIVE`; live authority is
per account, market, product, and release.

### FX-V2-04 — The stable kernel/plugin boundary is incomplete

A kernel need not know equity or futures formulas, but it still needs asset-neutral typed contracts
for money, signed economic direction, quantity descriptors, price observations, order lifecycle,
cash flows, position identity, valuations, and reconciliation differences. Otherwise the claimed
generic `OrderIntent → ExecutionRecord`, append-only ledger, and reconciliation report cannot be
validated without untyped plugin payloads. The proposal also does not relocate existing
equity-specific couplings: INR-numeraire risk, fixed-fractional share sizing, resting-stop
assumptions, corporate-action protection, session readiness, and the global portfolio snapshot.

Required correction: specify narrow versioned plugin ports and common envelopes while leaving
quotation, unit, margin, settlement, expiry, and session rules in product modules. `SessionClock`
must be selected by venue + segment + product + operation and use trading and settlement calendars;
`isOpen(ts, account)` alone is insufficient.

### FX-V2-05 — Currency-future identity and time do not conform to the approved ontology

`pair + venue + expiry month + specVersion` (`lines 44, 65, 73`) makes mutable terms part of
identity and lacks an exchange-assigned series/listing identifier, segment, exact expiry/last-trade
dates, and temporal alias. A later correction or parameter change can therefore create a new
instrument identity for the same listed contract. Conversely, YearMonth can collide where series
or expiry rules differ. `SpotFX {pair, valueDate,counterparty}` conflates product/pair identity with
deal facts; value date and counterparty belong to a quote/deal/position contract, not the stable
currency-pair identifier.

The approved ontology requires typed canonical keys, typed temporal crosswalks, venue-scoped
aliases, stable IRIs without release numbers, release-specific version IRIs, and separate event,
publication, receipt, validity, recording, supersession, and cutoff time. The extension supplies
none of those for contract specs, margin parameters, settlement references, or calendars. Its
red-team suggestion to avoid collision by “namespacing” equity-v1/futures-v2 terms (`line 167`) can
encourage versioned term IRIs, contrary to the approved stable-IRI rule.

Required correction: model `CurrencyPair`, derivative product/series, listed contract, venue
segment/listing, and temporal exchange aliases as separate typed identities. Treat contract terms,
margin parameters, calendars, and settlement references as immutable, effective-dated,
source-provenanced observations/assertions with publication/receipt/cutoff lineage. Bind the full
OntologyRelease, SemanticSnapshot, sealed projection receipt, QueryPack, ReasoningPolicy,
FeaturePolicy, and activation IDs where they influence a decision.

### FX-V2-06 — P&L, margin, and reconciliation are not implementation-safe

The formula `(exit-entry) × contract-unit × lots, converted to INR` (`line 57`) omits side/sign,
quotation unit/scale (material for pairs quoted per multiple units), contract multiplier version,
fees/taxes, daily settlement/variation-margin cash flows, and the distinction among trade price,
daily settlement price, final settlement reference, broker valuation, and reporting conversion.
For INR-quoted contracts, unconditional “converted to INR” is at best ambiguous. `native_currency`
plus `reporting_currency` is also insufficient to identify quote, settlement, collateral, fee, and
functional currencies.

The migration mentions only a generic margin snapshot, futures MTM record, margin call, and “MTM
reconciliation.” It does not define reconciliation of contract master/spec version; orders,
amends/cancels and fills; long/short lots and net position; daily settlement cash; initial/ongoing
margin and broker add-ons; collateral and available funds; fees/taxes; expiry/final settlement;
roll legs; corrections; or broker/clearing cutoffs. A plugin cannot go live without all of these
having deterministic discrepancy classes and fail directions.

Required correction: define quotation and monetary dimensions explicitly; ledger daily MTM and
settlement as cash events; retain immutable broker and exchange observations; and reconcile every
listed state above per broker account and contract. Session handling must include venue breaks,
pair-currency holidays, expiry/last-trade cutoffs, settlement publication availability, and
timezone rules—not generic “24×5” or a single session clock.

### FX-V2-07 — India compliance language exceeds the sources

The source brief supports transactions with authorised persons for permitted purposes, electronic
transactions through authorised ETPs or recognised Indian exchanges, and the prohibition on LRS
remittances for overseas online forex margin. It does **not** support the blanket statement that
all `OTCSpotFXPlugin` activity is constitutionally blocked for every India resident (`line 25`):
authorised-person spot conversions for permitted purposes are not the same product as offshore
leveraged retail FX/CFDs. “Authorised principal = legal account owner only” (`line 131`) also
conflicts with the document's own signed/discretionary mandate model. Calling a cross-account risk
dependency “illegal” (`line 129`) is an unsupported legal conclusion; it is already defensible as
a constitutional custody/risk invariant without that claim.

Required correction: constitutionally block unsupported/offshore leveraged retail FX/CFD routes
and any unverified product-purpose-account-venue combination. Do not assert that every OTC spot
transaction is prohibited. Represent owner, authorised representative, mandate grantor/grantee,
scope, evidence, validity, and revocation separately. Make legal/compliance policy
effective-dated and source-backed with `verified_at`, reviewer, applicability, expiry/review date,
and fail-closed freshness, as required by the live-domain audit. Label NSE-CDS-only execution as a
conservative product policy, not a complete statement of Indian law.

### FX-V2-08 — Household isolation contains internal contradictions

The per-account custody, credentials, capital, compliance, reconciliation, and kill-switch rules
are sound. However, `line 127` prohibits cross-account netting even in analytics while `line 129`
permits aggregate same-currency/DV01 exposure; signed aggregate currency exposure is analytical
netting. The correct prohibition is on execution, collateral, margin, buying-power, loss-budget,
or limit offsets. Analytics may show both gross and net informational exposure with lineage and no
feedback into per-account decisions.

`line 131` says only the legal owner can be the authorised principal while also defining
discretionary execution, and Phase 2 relies on signed mandates. Membership, visibility grants,
mandates, ownership/representative changes, and revocations lack bitemporal append-only contracts.
Dropping household tables as rollback (`line 139`) destroys governance/audit history.

Required correction: make household membership and every visibility/mandate grant immutable,
effective-dated, revocable events; distinguish owner from authorised representative; require
per-account runtime authorization; retain revoked history; and make household projections
rebuildable. Explicitly test that no household aggregate type is accepted by sizing, risk-limit,
order, margin, settlement, or reconciliation ports.

### FX-V2-09 — Migration order is contradictory and skips controlling gates

The approved ontology requires canonical identity/time/evidence/release foundations before new
domain schemas. Phase 0 does not install them. FX research does not depend on family execution, so
placing it only after Phase 2 creates a hidden, unnecessary coupling. Phase 1 populates a household
view, while Phase 2 says an account's first execution must reconcile before that view is populated.
Phase 4 jumps from research to execution without the ontology's semantic promotion,
`DecisionFeatureActivation` shadow, paper canary/active, live canary, and receipt sequence.

The extension also invents five-day and ten-session evidence thresholds without an approved
manifest or source. More importantly, it does not resolve the controlling-document conflict: the
approved OS still says 90-day paper-first, while the later live-domain audit says direct-live Tier
0 with no 90-day wait. An FX migration cannot inherit two incompatible promotion rules.

Required order:

1. Resolve and publish the controlling cash-equity live-promotion rule.
2. Install common typed money/quantity/time/identity envelopes and ontology foundation without
   enabling any new product.
3. Complete per-account cash-equity portfolio/reconciliation and immutable capability controls for
   both India and US V1.
4. Build household read-only projections and independently test isolation. Family execution is a
   separate optional track; it does not gate FX research.
5. Build currency-futures identity/spec/calendar/price/margin/settlement/reconciliation in
   `RESEARCH_ONLY`, with transport incapable of reaching a live endpoint.
6. Complete semantic release/evaluation and an independent `DecisionFeatureActivation` through
   shadow and paper canary, while product execution remains disabled.
7. After current legal, venue, broker, entitlement, account, risk, margin, execution, valuation,
   reconciliation, and kill-switch evidence is approved, run product-level paper acceptance.
8. Permit a separately capped live canary only under the intersection of all effective releases;
   expand or roll back from immutable receipts.

## False self-audit claims

The self-audit on `line 184` is **not reliable**:

- It reports `verdict=PASS` based primarily on section presence and item counts despite the
  blocking contradictions above.
- It calls `CONDITIONAL-GO` a “GO verdict,” weakening the actual condition.
- The body says “the three mandatory amendments below” (`line 173`) but lists six (A–F).
- It claims the output is within 8–15 KB; the file is 21,229 bytes.
- It calls deactivation layered and faster than activation even though its own human-override
  precondition can prevent immediate deactivation.
- It claims migration gates and rollback are present but does not detect “drop tables,” “freeze
  release,” or the Phase 1/Phase 2 population contradiction.

## Minimum re-review acceptance conditions

A successor draft is eligible for re-review only if it:

1. replaces the deactivation protocol with immediate entry fencing plus durable open-position
   management;
2. defines capability and `DecisionFeatureActivation` as independent, intersecting authorities;
3. supplies stable derivative/pair/listing/deal identities and full approved temporal lineage;
4. provides pair-aware quotation, MTM, margin, settlement, expiry/roll, and reconciliation
   invariants with deterministic fail directions;
5. narrows India statements to the supplied sources and current human verification;
6. makes household grants append-only and resolves analytics-vs-execution netting;
7. removes permission-bearing defaults and supports both India and US V1 accounts; and
8. republishes a dependency-correct migration with one controlling promotion policy and mandatory
   semantic/product canary receipts.

VERDICT: FAIL
