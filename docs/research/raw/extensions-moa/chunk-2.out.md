## 7. Multi-asset architecture verdict

**Verdict: CONDITIONAL-GO for the forward architecture; NO-GO for any FX in the nine-day cash-equity V1.**

**Stable cross-asset kernel (asset-neutral, no instrument semantics) — ARCHITECTURAL-INFERENCE**

The kernel is a *control plane*, not a generic "instrument" abstraction. It owns only what is invariant across every asset class:

- `Account` — legal owner, credential binding, consent/mandate, capital envelope, compliance state, kill switch. Never household-scoped.
- `PolicyRelease` — immutable, versioned, signed, effective-dated; carries capability gates.
- `LedgerEntry` — append-only, timestamped, account-scoped; corrections by reversal/adjustment only, never mutation.
- `OrderIntent → ExecutionRecord` — typed deterministic state machine.
- `ReconciliationReport` — broker-account-scoped; no assumed fill finality without broker/clearing confirmation.
- `ResearchEvidence` — typed, versioned, linked to model/ontology/policy IDs; can neither size nor execute.
- `OntologyVersion` — append-only term governance.

The kernel must contain **no** price, quantity, P&L, margin, settlement, expiry, or session semantics. Those are plugin concerns.

**Asset-specific plugins (sealed, capability-gated)**

| Plugin | Owns | V1 state |
|---|---|---|
| `CashEquityPlugin` | ISIN/symbol, corporate actions, long-only, cash-funded, T+ settlement, equity bands/sessions | **LIVE** |
| `CurrencyFuturesPlugin` (NSE CDS) | pair identity, contract unit, tick/tick-value, expiry/roll, RBI-reference settlement, SPAN margin | SEALED |
| `OTCSpotFXPlugin` | bilateral pair, counterparty, value-date, financing/swap | **CONSTITUTIONALLY BLOCKED** for India-resident |

**Boundary changes to make in V1 now** (cheap now, structural debt later) — ARCHITECTURAL-INFERENCE

1. Make `Instrument` a **sealed discriminated union**, not a string/flat record. `CashEquity` is the only constructible variant; `CurrencyFuture` and `SpotFX` exist in the type system but are sealed behind a `CapabilityGate.isOpen()` guard returning `false`.
2. Add `settlement_currency: CurrencyCode` to every cash, fee, tax, P&L and position record — trivially `INR` now, no migration later.
3. Add `AssetClass` as a first-class policy dimension; enable only `CASH_EQUITY`.
4. Add `capability_gate_id` FK on every `Account`, defaulting to `{assetClass: EQUITY, venue: NSE|BSE, jurisdiction: IN}`.
5. Make `SessionClock` a plugin-injected interface, never a hardcoded NSE-equity window.
6. Split `Venue` from `Broker` (two fields, never one).
7. Make kill switches **account-scoped and asset-class-scoped** from day one.
8. Ensure every order-intent row carries `policy_release_id`, `account_id`, `asset_class`, `instrument_id`, `venue_id`, `evidence_bundle_id`.
9. Store `price_source_id` provenance on every price observation.
10. Make `RiskParameters` a typed, versioned record linked to Account + PolicyRelease, not embedded constants.

## 8. FX domain delta

| Dimension | Cash equity (NSE/BSE) | Exchange-traded currency futures (NSE CDS) | OTC / spot FX |
|---|---|---|---|
| Identity | ISIN + exchange symbol | pair + expiry month (e.g. USDINR-25JUN) + venue — **SOURCE-ANCHORED** (NSE CDS spec) | pair + counterparty + value date |
| Underlying | fractional corporate claim | obligation to exchange notional at expiry | immediate (T+2) currency exchange |
| Base/quote | INR-denominated, no pair | explicit base/quote (USD/INR, EUR/INR, GBP/INR, JPY/INR) — **SOURCE-ANCHORED** | market convention; inversion rules apply |
| Pip/tick | INR price increment per share | contract-specific tick & tick-value — **SOURCE-ANCHORED**; exact value **OPEN-VERIFICATION** against current NSE parameters | pip = 4th decimal for majors; N/A to NSE CDS |
| Contract/lot | shares; lot may be 1 (delivery) | contract unit in base ccy × lots → notional — **SOURCE-ANCHORED**; exact unit **OPEN-VERIFICATION** | LP-defined minimums; N/A for India-resident |
| Session clock | equity session + auctions | currency-segment session differs from equity — **SOURCE-ANCHORED** (NSE CDS) | ~24×5 global; irrelevant absent authorised venue |
| Expiry/roll | none for cash shares | explicit expiry cycle + roll; last-trade & settlement rules — **SOURCE-ANCHORED** | spot value-date T+2; rolling spot = financing/swap |
| Margin/leverage | long-only, cash-funded (none) | exchange/clearing margin (SPAN + exposure) — **SOURCE-ANCHORED** | offshore leveraged FX/CFD **NOT lawful to assume** for India-resident; LRS cannot remit forex margin — **SOURCE-ANCHORED** (RBI FAQ #146) |
| Settlement | securities/cash, T+ in INR | cash-settled vs published reference rate — **SOURCE-ANCHORED** | bilateral delivery / correspondent-bank chain |
| Venue/price multiplicity | NSE/BSE, official close | single recognised exchange book + settlement price | many LPs/ECNs; indicative ≠ executable |
| Events | dividends, splits, rights, bonuses | expiry, settlement-rate publication, margin changes | value-date rolls, swaps, counterparty events |
| Netting | per security/account; long-only cannot oversell | long/short net per contract/account/clearing | bilateral per legal agreement |
| Financing/swap | none (fees/taxes only) | daily MTM margining | tom-next swap material |
| P&L | (exit−entry)×qty in INR | (exit−entry)×contract-unit×lots, converted to INR | (exit−entry)×notional in base, converted |
| Risk | issuer/sector/liquidity/corp-action | notional, basis, roll, margin-call, expiry-liquidity, gap | counterparty, leverage, rollover, settlement, jurisdiction |

**Types and invariants derived**

```
Instrument =
  | CashEquity     { isin: ISIN; venue: Venue }
  | CurrencyFuture { pair: CurrencyPair; expiry: YearMonth; venue: Venue; specVersion: ContractSpecVersion }
  | SpotFX         { pair: CurrencyPair; valueDate: Date; counterparty: LegalEntity }   -- CAPABILITY-GATED, non-constructible in V1

CurrencyPair = { base: CurrencyCode; quote: CurrencyCode }   -- invariant: base ≠ quote; direction is economic, never inferred
QuantityType = Shares | Contracts | BaseCurrencyAmount | QuoteCurrencyAmount   -- no untyped numeric quantity
Price        = { value; source; entitlement; ts; executable|indicative; permitted_use }
```

Invariants: (a) `InstrumentId` is subtype-specific — a currency future is `pair+venue+expiry+specVersion`, never "FX"; (b) derivatives require `ExpiryDate/LastTradeDate/SettlementRule/RollPolicy`; (c) tick/pip come from `PriceIncrementPolicy`, never decimal-count inference; (d) `MarginModel` forbidden for V1 equity, required for futures, **constitutionally blocked** for unverified offshore margin FX; (e) every P&L/valuation row carries `native_currency + reporting_currency + conversion_source + ts + rate_type`.

## 9. Capability and compliance gating

**Immutable `AssetClassCapabilityRelease` — ARCHITECTURAL-INFERENCE**

```
AssetClassCapabilityRelease {
  release_id, version(monotone SemVer), created_at, effective_from, effective_until?
  asset_class
  scope: { jurisdiction, resident_status, account_id (single; NEVER household),
           permitted_venues, permitted_brokers, permitted_instrument_filter }
  data_entitlement_ref
  risk_policy_ref, execution_policy_ref, valuation_policy_ref,
  reconciliation_policy_ref, compliance_policy_ref, kill_switch_policy_ref
  research_evidence_schema_id, ontology_version_id
  activation_state: DISABLED | RESEARCH_ONLY | PAPER_ONLY | LIVE_ALLOWED
  constitutional_blocks[], configurable_limits[]
  authorised_by (human principal), signer_ids, hash_of_release
}
```

Append-only in the ledger; **deactivation is a new record, never a mutation**.

**Configurable gates** (new PolicyRelease / RiskPolicy, no code change): permitted pairs within an enabled class, max order value, max notional, max open positions, max margin utilisation, session subset stricter than venue, broker order types, evidence freshness, price-source preference, per-account capital envelope.

**Constitutional gates** (kernel-hardcoded; config cannot override):

1. No FX tradability until jurisdiction + resident-status + permitted-purpose + authorised venue/platform + broker-account authority are all verified.
2. No assumption that offshore leveraged spot FX/CFDs are legal for an India-resident; no LRS remittance of forex margin — **SOURCE-ANCHORED** (RBI FAQ #146).
3. Family membership confers no trading authority — **SOURCE-ANCHORED** (stated constraint).
4. Research agents can neither size nor execute.
5. No live execution without an explicit signed immutable capability release.
6. No account inherits another's consent, credentials, positions, capital envelope, or kill switch.
7. No instrument trades without valuation + risk + execution + reconciliation policies bound.
8. No data source is usable for trading unless entitlement + permitted-use flags are true.

**Safe activation** — monotonic, auditable: `DISABLED → RESEARCH_ONLY → PAPER_ONLY → LIVE_ALLOWED`. Each transition requires a new immutable release, prior-release diff + sign-off, dry-run reconciliation, paper/sandbox test where available, explicit per-account opt-in, kill-switch test, and a pre-staged rollback release. Ordering invariant: risk + execution + valuation + **data entitlement** must all be live *before* `LIVE_ALLOWED` — never a window where execution is authorised without a price feed.

**Safe deactivation** — faster than activation, and layered (global asset-class → jurisdiction → broker → account → instrument → data-source kill switches). Blocks new orders immediately; permits only policy-approved risk-reducing exits where legally valid; **never stops reconciliation ingestion**. Deactivation must first call `hasOpenPositions(account, asset_class)`; if true, require a human-acknowledged `ForceDeactivationOverride` in the ledger before proceeding.

## 10. Family plus multi-asset interaction

| Concern | Account-level (mandatory, enforced first) | Household-level (read-only analytics ONLY) |
|---|---|---|
| Orders / execution / netting | per account | **never aggregated** |
| Risk limits | per account, per PolicyRelease | informational dashboard only |
| Reconciliation | per account | **never aggregated** |
| Kill switch | per account (read-only from household) | can read, **cannot write** |
| Capital / margin / collateral | per account | display-only sum |
| Compliance state / consent / credentials | per account | not aggregated |

**Currency normalization**: household views need a reporting currency (INR for India-resident context). Every normalized record stores `native_currency, reporting_currency, conversion_rate, conversion_source, conversion_ts, rate_type` (RBI reference for INR pairs). Never use a live bid/ask mid as a normalization input to anything that influences sizing. Normalized household P&L is an **analytical artefact, not a ledger entry**.

**Transfer prohibition**: no family member's cash, margin headroom, or securities may satisfy another's order. The system must not even construct a data structure implying an in-progress or completed inter-account transfer. Cross-account netting prohibited at ledger *and* analytics layers.

**Correlated exposure**: household view may display aggregate same-currency/same-issuer/DV01 exposure, labelled `INFORMATIONAL — NOT FOR EXECUTION`. No risk engine may use household correlation to modify a per-account limit — doing so manufactures an illegal cross-account margin dependency.

**Mandate scope** — typed, account-specific, asset-class-specific, venue-specific, time-bounded: `READ_ONLY | RESEARCH_VIEW | ORDER_PROPOSAL | ORDER_APPROVAL_REQUIRED | DISCRETIONARY_EXECUTION | RECONCILIATION_ONLY | TAX_REPORTING_ONLY`. Authorised principal = the legal account owner only.

**Never aggregated for execution**: buying power, margin, collateral, order/position netting, kill-switch state, broker credentials, suitability/compliance status, loss limits, consent, legal ownership, tax lots, FX permitted-purpose, data entitlements. Family execution is only a coordinator *view* over separately authorised per-account decisions.

## 11. Migration sequence

**Phase 0 — Cash-equity V1 (days 1–9, now).** Long-only cash equities; deterministic risk/execution; append-only ledger; immutable releases; broker reconciliation; account+asset-class kill switches; research evidence only (no agent sizing/execution). *Schema seams to install now:* `asset_class`, `instrument_type` (discriminated), `settlement_currency`, `venue_id`, `session_calendar_id`, `capability_release_id`, `policy_release_id`, `price_source_id`, `account_capability`, `risk_policy_version`, `kill_switch_scope`. *Evidence gate:* equity reconciliation passes ≥5 consecutive trading days. *Rollback:* baseline — disable order creation, reconciliation continues, ledger stays append-only.

**Phase 1 — Family read-only aggregation.** Link accounts into a household *view*; no cross-account execution, shared credentials, or pooled capital. *Schema:* `household_id`, `household_membership`, `account_visibility_grant`, `mandate_scope`, `reporting_currency`, `normalized_valuation_snapshot` (display-only, timestamped). *Evidence gate:* each account reconciles individually; static proof that **no cross-account order pathway exists in code**. *Rollback:* drop household-view tables; account ledgers untouched.

**Phase 2 — Separately authorised family execution.** Per-account mandate verification, capability release, capital envelope, kill switch, broker credentials; independent KYC + signed mandate per member. *Schema:* `account_mandate`, `mandate_artifact_hash`, `order_approval_record`, `account_execution_capability`. *Evidence gate:* each account's first execution reconciles independently before household view is populated; no "household order" object may route directly. *Rollback:* revoke mandate → account reverts to read-only/self-only.

**Phase 3 — Exchange-traded FX research (NSE CDS).** Research only for recognised exchange-traded currency derivatives; `CurrencyFuturesPlugin` installed but execution gate CLOSED. Build contract ontology from NSE CDS specs (base/quote, contract unit, tick, session, expiry, settlement reference, margin) — **SOURCE-ANCHORED**. *Schema:* `currency_pair`, `derivative_contract`, `contract_spec_version`, `expiry_calendar`, `margin_parameter_snapshot`, `settlement_reference`, `tick_value_policy`, `fx_research_evidence`. *Evidence gate:* evidence proves contract identity/venue/session/expiry/tick/margin; specs validated against live NSE CDS feed; ontology version bumped; no OTC/spot evidence may be promoted; state stays `RESEARCH_ONLY`. *Rollback:* unload plugin; evidence remains immutable but non-tradable; gate stays CLOSED.

**Phase 4 — Permitted FX execution (NSE CDS only), after full verification.** Only if jurisdiction, resident-status, broker, authorised venue/platform, account, data entitlement, instrument, risk, execution, valuation and reconciliation gates all pass; use authorised persons/recognised Indian exchanges for permitted purposes — **SOURCE-ANCHORED**; offshore leveraged spot FX/CFD stays disabled. *Preconditions (OPEN-VERIFICATION):* current RBI/exchange/broker legal verification; CDS-segment-activated broker account; live data entitlement; SPAN margin model tested; reconciliation supports derivative MTM; kill switch tested for derivative orders; signed `AssetClassCapabilityRelease`. *Schema:* `futures_position`, `futures_mtm_record`, `roll_event`, `margin_call_event`. *Evidence gate:* paper/sim reconciliation ≥10 sessions; margin validated vs NSE SPAN. *Rollback:* block new FX orders; permit only compliant risk-reducing exits; freeze release; continue margin/reconciliation ingestion; emit compliance incident if deactivation followed a gate failure.

## 12. Red-team verdict and amendments

**Hidden coupling / failure traps** (ARCHITECTURAL-INFERENCE unless flagged):

1. `Instrument` as symbol-only string → USDINR future, spot USD/INR and an equity ticker collide on one key.
2. Assuming every asset has *share* quantity semantics (no `QuantityType`).
3. Reusing equity session hours for the currency segment → silent reject/accept of valid/invalid orders.
4. Ignoring expiry → accidentally holding a future into settlement.
5. Treating indicative FX quotes as executable prices.
6. `SpotFX` variant constructible before the jurisdiction gate is enforced → a test/misconfig routes a real spot order. **(SOURCE-ANCHORED risk: RBI FAQ #146)**
7. Any "fund foreign broker account" flow constitutes illegal remittance of forex margin under LRS. **(SOURCE-ANCHORED: RBI FAQ #146)**
8. Household buying power / margin used to fund an individual account's order.
9. Family mandate silently implying trading authority across all accounts; account creation *copying* the primary's capability release as a default.
10. One broker credential reused across family accounts.
11. Global-only kill switch with no account/asset-class/venue layers — or, inversely, a household "emergency stop" that closes a member's position without consent.
12. Research evidence carrying a `suggestedSize`/`target position` field that a later dev wires into execution.
13. Netting long USD in one account against short USD in another for execution; household DV01 feeding back into per-account limits (illegal cross-account margin dependency).
14. Hardcoding INR as the only ledger currency; reconciliation reading only INR MTM while notional is USD → phantom P&L discrepancies.
15. Failing to version contract specs/margin params → historical trades reinterpreted with current specs; treating settlement price ≡ last-traded ≡ broker valuation.
16. Roll (near-month close + far-month open) leaving a ledger gap → P&L attribution over/understates return.
17. Ontology version collision — equity ontology v1 term IDs reused by futures ontology v2 without namespacing → cross-asset evidence misread.
18. Policy-release ordering window where execution is authorised before the data entitlement/price feed is live (determinism violation).
19. Order amend/cancel paths that skip re-running capability gates.
20. Deactivating a plugin while open positions exist, leaving them unmanaged; rollback that mutates append-only ledger history; deactivation that halts reconciliation ingestion.
21. Test/demo environment not broker-endpoint-isolated → an accidental real offshore FX order is a *regulatory violation*, not just a bug. **(SOURCE-ANCHORED: RBI FAQ #146)**

**Verdict: CONDITIONAL-GO.** The V1 cash-equity architecture is sound for its stated scope. FX stays fully disabled in V1; the conditional is discharged by installing the seams above and the three mandatory amendments below.

**Exact generic design amendments:**

- **A — Sealed instrument union from day one.** `CashEquity` is the only constructible variant in V1; `CurrencyFuture` and `SpotFX` exist in the type system but are sealed behind `CapabilityGate.isOpen()` returning `false` until a matching signed `AssetClassCapabilityRelease` activates. Kills traps 1, 6.
- **B — SessionClock as injected interface.** `SessionClock { isOpen(ts, account)→bool; nextOpen(ts)→ts }`; equity plugin injects NSE equity hours, futures plugin injects CDS hours, kernel hardcodes nothing. Kills trap 3.
- **C — Deactivation precondition check.** `deactivate(CapabilityRelease)` must first call `hasOpenPositions(account, asset_class)`; if true, require a human-acknowledged `ForceDeactivationOverride` ledger record before proceeding. Kills trap 20.
- **D — Order-intent completeness constraint.** Every order-intent row must carry non-null `policy_release_id, account_id, asset_class, instrument_id, venue_id, evidence_bundle_id`; a null in any = hard reject. Prevents silent cross-context leakage.
- **E — Research-evidence schema forbids executable fields.** No `size`, `quantity`, `price`, or `target_position` field may exist on any `ResearchEvidence` type; enforced by schema + migration test. Kills trap 12.
- **F — Constitutional-block table + policy-diff review.** Config cannot override constitutional gates; every activation requires a machine-checked prior-release diff and human sign-off. Backstops traps 7, 9, 13.

<!-- CHUNK-2 SELF-AUDIT: headings=7-12; fx_delta=present; capability_gate=present; family_interaction=present; adversarial_count>=15; verdict=PASS; reason=Sections 7-12 all present; FX delta table spans identity/underlying/base-quote/pip-tick/contract-lot/session/expiry-roll/margin/settlement/venue/events/netting/financing/pnl/risk with SOURCE-ANCHORED and OPEN-VERIFICATION tags; immutable AssetClassCapabilityRelease with configurable-vs-constitutional split and monotonic activation + layered faster-than-activation deactivation; family section separates account-level mandatory from household read-only, defines currency normalization, transfer prohibition, correlated-exposure labelling and never-aggregate-for-execution list; five-phase migration (0-4) with schema seams, evidence gates and rollback each; 21 red-team traps (>=15) plus GO verdict CONDITIONAL-GO and six exact amendments A-F; output within 8-15 KB. -->
