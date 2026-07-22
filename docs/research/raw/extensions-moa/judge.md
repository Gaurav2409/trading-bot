# Extensions MoA — Joint Judge Report

Date: 2026-07-22

## Decision

| Lens | Verifier verdict | Judge disposition |
|---|---|---|
| Portfolio / account / identity | FAIL | FAIL remains after removing the superseded paper-first objection. The authority, normalization, completeness, authorization, protective-action, snapshot/CAS, and sizing-before-risk defects are still blocking. |
| FX / multi-asset / compliance | FAIL | FAIL remains. FX is future-only, but the proposed seams would regress the two-market cash-equity V1 and are not safe foundations for later FX. |
| Structure / scope / nine-day realism | REVIEW | Useful evidence, but the raw self-audits are unreliable and their proposals require the corrections below. |

By rule, any verifier FAIL yields a joint NO-GO. This rejects the two raw proposals **as specifications**, not the extension direction itself.

## Controlling decisions

The following newer decisions supersede conflicting language in the approved base specs and are settled, not unresolved:

- V1 is long-only cash equity through **both Zerodha and Alpaca**, with direct-live Tier 0 for each after bounded static, replay, contract, and protocol-readiness checks. There is no fixed 90-day paper campaign.
- Promotion thresholds, evidence windows, capital limits, and expansion gates are immutable, content-addressed, configurable releases; fixed five-day, ten-session, or other calendar counts are not architecture.
- Current portfolio analysis is mandatory in V1.
- Family operation and FX execution are future capabilities. V1 installs only their stable schema and isolation seams.
- Day 9 means a complete, shallow first live vertical slice, not mature alpha, mature ontology promotion, family execution, or FX execution.

## (a) Raw MoA proposals rejected

- Reject `chunk-1`'s fused broker/ledger truth, scalar settlement state, overlapping confidence rules, stale-data haircut option for opening risk, fresh-pull-dependent kill path, underspecified owner/credential/mandate model, `(broker_id, account_number)` identity, risk-before-sizing flow, legacy `ExposureVector`, ad-hoc `OntologySnapshot`, and one-account Day-9 acceptance.
- Reject `chunk-2`'s permission-bearing India default, one capability FK per account, INR-only assumptions, account-bound reusable capability release, human-gated deactivation, mutable/frozen rollback language, incomplete generic kernel, unstable FX identities, incomplete MTM/margin/settlement/reconciliation model, blanket OTC/owner-only legal claims, destructive household rollback, and family-to-FX migration coupling.
- Reject both chunks' PASS self-audits. Their size claims are false, and section/item counts do not establish architectural correctness.

## (b) High-confidence ideas accepted

- Make current, account-scoped portfolio state a hard dependency for every exposure-increasing decision, including broker holdings/positions, cash, open orders, settlement restrictions, external/manual positions, and OS provenance.
- Preserve raw broker custody observations separately from append-only OS intention/history. Carry per-line provenance and separately labelled broker-reported, OS-ledger, and unknown/partial P&L; never claim complete lifetime history from current broker endpoints.
- Keep every account's owner, credentials, authority, capital envelope, orders, positions, reconciliation, compliance state, and kill switch isolated. A household is a consent-scoped derived view, never custody or execution authority.
- Use immutable releases, typed asset/product capability seams, separate broker and venue identities, source/entitlement lineage, and asset-aware clocks. FX requires pair, contract, tick, session, expiry/roll, margin, settlement, and multi-currency semantics.
- Keep research non-executable, the relational path authoritative for deterministic decisioning, and semantic projections versioned and rebuildable.

## (c) Exact corrective architecture

1. **Portfolio truth:** store immutable source observations and publish a field-level authority/conflict matrix. Broker data is authoritative for broker-reported custody, order, cash, and settlement observations; the OS log is authoritative for its own intents, fills, reservations, and strategy provenance; derived availability uses both, and conflicts remain explicit reconciliation facts. Canonicalization must define Zerodha holdings/positions overlap, manual-line deduplication, and non-overlapping quantity/cash buckets.
2. **Portfolio gate:** seal account and owner/global cuts with broker segments, open orders, ledger cut, `ValidatedDataSnapshotId`, policy releases, clocks, and CAS version. Aggregate orthogonal completeness dimensions by deterministic worst state. Missing/stale custody, cash, open orders, identity, corporate-action, price, or FX inputs block new exposure for the affected scope.
3. **Hot path:** `DecisionFeatureSet` plus a sealed portfolio snapshot -> deterministic provisional sizing -> post-trade risk/compliance with `PortfolioRiskOverlaySet`/`RiskOverlaySet` (tighten or veto only) -> CAS reservation -> immediate revalidation -> submit. Bind any semantic input to `SemanticSnapshotId`, sealed projection receipt, and independent `DecisionFeatureActivation`; graph state is never custody truth.
4. **Protection:** an emergency stop atomically fences new exposure first. Use `ENTRY_DISABLED`/`DRAINING` with reconciled `NO_POSITION`, `REDUCE_ONLY`, or `MANAGEMENT_ONLY`; keep broker-native protection, valuation, data, expiry management, and reconciliation alive. If custody refresh fails, do not infer a close quantity: preserve protection, alert, and reconcile until broker authority returns.
5. **Identity and family seam:** model `LegalParty`, `Person`, `UserProfile`, ownership relation, `BrokerConnection`, `BrokerageAccount`, account-access grant, read consent, trading mandate, policy assignment, `Household`, membership, and derived view separately. Grants are scoped, append-only, effective-dated, revocable, and runtime-checked. Household analytics may show gross/net information and, with consent plus policy, tighten an account; they may never loosen limits or net cash, collateral, margin, loss budgets, or orders.
6. **Capability seam:** the stable kernel owns typed `Money`, `CurrencyCode`, quantity descriptors, clocks, event identity, policy references, and common order/ledger/reconciliation envelopes. Product plugins own quotation, unit, session, margin, settlement, and expiry rules. A reusable `AssetClassCapabilityRelease` is separate from the many-record `AccountCapabilityAssignment` and from semantic feature activation. Execution authority is the intersection of capability, account assignment/mandate, compliance, entitlement, broker readiness, reconciled state, and kill-switch generation.
7. **FX future:** keep transport incapable of live FX execution in V1. Model `CurrencyPair`, derivative product/series, listed contract, venue segment/listing, and temporal alias separately; version contract terms, quotation scale, calendars, margin, settlement references, and source lineage. Before any later activation, specify side-aware MTM cash events, collateral/margin, fees/taxes, expiry/final settlement, roll, corrections, and deterministic reconciliation fail directions. Reverify India product-purpose-person-venue legality; block unsupported offshore leveraged FX/CFD routes without claiming all OTC spot activity is unlawful.

## (d) Unresolved items

- Freeze executable schemas and tests for the portfolio authority matrix, broker/manual merge rules, quantity/cash buckets, completeness lattice, snapshot/CAS cut, and protective-action state machine.
- Freeze tenant-safe account identifiers and the ownership/access/consent/mandate event model, including joint/entity ownership and authorised representatives.
- Reconcile the approved specs to the controlling direct-live, two-broker, configurable-release, mandatory-portfolio, and `RiskOverlaySet` decisions before implementation planning.
- Confirm external Day-9 readiness: funded/legal accounts, Zerodha API/static IP and required tagging, Alpaca live credentials/account flags/data entitlement, and required infrastructure. These can block operation even when code is ready.
- Defer exact FX broker/product selection and obtain current human legal/compliance verification before any FX activation; the future domain/accounting contracts above still need an independent re-review.

## Suggested Spec Patch

- Replace the fixed 90-day paper-first baseline and one-account language with bounded preflight plus direct-live Tier 0 for both broker-scoped cash-equity sleeves; keep later expansion evidence in immutable `PromotionPolicyRelease`s. This baseline decision does not waive the independent activation evidence required before ontology-derived features gain economic influence.
- Add the corrected current-portfolio authority, normalization, completeness, CAS, and protection contracts as V1 gates.
- Replace every remaining `ExposureVector` consumer with the approved `DecisionFeatureSet` and tighten-only `RiskOverlaySet` seam, including a typed portfolio overlay.
- Add the LegalParty/account authority schema and future-only family seams; prohibit family execution in V1.
- Add the common typed multi-asset envelopes, independent capability/account-assignment/feature-activation authorities, and future FX identities without enabling FX execution.
- Update the nine-day acceptance table to require both Zerodha and Alpaca, current portfolio analysis, independent envelopes/kill switches, immutable policy releases, and bounded readiness evidence.
- Update the stale EOD-only discovery and "Kite has no sandbox" text to the approved multi-clock discovery model and brief Kite sandbox/protocol-smoke-test use; neither change creates an unrestricted intraday mandate or a calendar paper campaign.

JOINT VERDICT: NO-GO
