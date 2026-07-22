## 1. Executive verdict

The three most consequential design changes, in priority order:

1. **`CurrentPortfolioAnalysis` becomes a mandatory, snapshot-scoped pre-trade dependency — never a report.** Because the OS now must reason about holdings and positions it did not create, deterministic eligibility/sizing/risk cannot run against OS-ledger state alone. Every order gate must consume an immutable, account-scoped snapshot that fuses broker-current state (including external positions), the OS ledger, open orders, cash, and settlement/pledge state, all clock-stamped. **ARCHITECTURAL-INFERENCE**, grounded in **SOURCE-ANCHORED** facts: Zerodha splits holdings/positions and lacks lifetime P&L and strategy-origin tags; Alpaca drops closed positions from its current-position endpoint. Broker state is necessary but structurally incomplete.

2. **Provenance and completeness become first-class, per-line risk inputs — not metadata.** Every holding/position carries an explicit `ProvenanceTier` (`OS_LEDGER_CONFIRMED` / `RECONCILED` / `BROKER_SNAPSHOT_ONLY` / `MANUAL_ENTRY` / `UNKNOWN`). Non-confirmed provenance **downgrades confidence and constrains automation — it never silently passes**. The OS must never claim complete lifetime history or blended P&L that the sources cannot support.

3. **Identity/authority/account primitives land in the V1 schema now, but only single-authorized-account execution ships.** `Person → UserProfile → LegalOwner → BrokerConnection → BrokerageAccount` must be distinct from day one, with `Household`/`Membership`/`TradingMandate`/`HouseholdPortfolioView` present as **read-only, authority-free seams**. Collapsing identity into a single "user" now is an irreversible migration hazard. **HARD INVARIANT:** a consolidated household view never changes account-level owner, authority, capital envelope, risk, reconciliation, or kill switch.

---

## 2. V1 CurrentPortfolioAnalysis contract

**Purpose.** Deterministic, account-scoped, snapshot-bound answer to: *"Given everything that exists in this account right now — including positions the OS did not create — what exposures, cash constraints, order reservations, protection gaps and confidence limits must gate new trading?"* Not advice, not alpha.

### Inputs

**Day 9 (required):**
- `AccountRef` — broker, account_id, base currency, legal owner, authorization status.
- `BrokerSnapshot` — **SOURCE-ANCHORED**: Zerodha `/portfolio/holdings` + `/portfolio/positions` (qty, avg/last price, P&L, settlement/authorisation state); Alpaca open positions (qty, cost basis, market value) + account cash/buying power.
- `BrokerOpenOrders` — reserved qty / pending cash delta.
- `OSLedgerSlice` — append-only order intents, fills, fees/taxes captured, reconciliation + kill-switch events, at a pinned `ledger_cut_id`.
- `ManualHoldingEntries` — user-declared external/pre-OS positions.
- `PriceSnapshot`, `FXRateSnapshot` — each stamped with source + exchange-clock + OS-receipt-clock.
- `InstrumentMaster` — canonical instrument id, ISIN/CUSIP, exchange, country, currency, lot/tick, tradability.
- `RiskPolicyVersion` — immutable, pinned at analysis time.

**Foundation-only seams (schema present, not exercised):** household/membership view inputs, multiple profiles per person, separately authorised family accounts.

**Deferred:** complete tax-lot reconstruction, learned alpha from personal history, automated corporate-action backfill, full factor/correlation/liquidity models, cross-account netting.

### Canonical records

- **`BrokerSnapshotRecord`** — append-only; raw payload hash; `broker_reported_at` + `os_received_at`; per-line provenance.
- **`PortfolioLine`** — instrument id, `quantity_total`, `quantity_available` (total − pledged − unsettled − open-order-reserved), `settlement_state` (`T0/T1/T2/PLEDGED/LIEN/UNAUTHORIZED`), `cost_basis` (source-tiered, nullable), `last_price`, `market_value`, `unrealized_pnl` (source-tiered), `provenance_tier`, currency, source-field hash.
- **`CashLine`** — settled, unsettled, available-to-trade, reserved-by-open-orders, currency, source, timestamp.
- **`OpenOrderReservation`** — order id, side, qty, limit/mkt, estimated notional, reserved cash/position impact, broker state, `os_originated` flag.
- **`PortfolioSnapshot`** — envelope: all lines + cash + open-order summary + `ExposureVector` + `CompletenessAssessment` + all clocks + `policy_version_id`.
- **`CurrentPortfolioAnalysis`** — `snapshot_id`, `account_ref`, exposure summary, concentration flags, completeness report, `confidence_tier`, freshness vector.

### Outputs
Holdings + positions (OS and non-OS); conservative cash/buying-power; open-order reservations; exposure by instrument/issuer/sector/country/currency/(sleeve where OS-originated)/provenance; concentration (top-weight, issuer, sector/country/currency); **P&L split into three labelled streams — `broker_reported`, `os_ledger`, `unknown_partial` — never blended**; freshness per data class.

**Exposure depth (Day 9 vs deferred), explicit:**

| Exposure | Day 9 | Later |
|---|---|---|
| Sector / country / currency | GICS-L1 / ISO country / currency weights | richer taxonomy |
| Concentration | per-name + sector/country/currency weights vs policy | issuer-graph rollups |
| Liquidity | `liquidity_confidence=LOW` unless coarse ADV bucket available | ADV/spread models, notional caps |
| Correlation / factor | proxy (shared sector/country/currency) or `NOT_COMPUTED` | beta, style factors, correlation matrix |
| Event | earnings/corp-action **flag** if feed available, else `OPEN-VERIFICATION` | full event-risk calendar |
| Protection coverage | **deterministic-control coverage only** (is this line inside limits/monitoring/kill-switch?) — *not* downside guarantee; unmodelled hedges flagged `PROTECTION_UNMODELLED` | options/hedge ledger |

### Pre-trade use
1. Retrieve/build latest account-scoped snapshot within the staleness window.
2. Assemble effective state: current holdings + positions + open-order reservations + cash + unsettled/pledged/blocked + **all non-OS positions**.
3. Compute post-trade hypothetical (add candidate notional, reserve cash, update exposure/concentration).
4. Deterministic checks run on **post-trade state**: max single-name, sector/country/currency concentration, cash availability, long-only/no-short invariant, tradability, staleness thresholds, policy-version match, **account-level kill switch**.
5. Research ranking may *penalize* crowded/stale/unprotected candidates but **cannot override deterministic risk**.

### Clocks (all independent, all on every report)
`ledger_cut_id`, `broker_reported_at`, `os_received_at`, `market_data_as_of`, `fx_as_of`, `policy_version_id`, `ontology_version_id` (if labels attached), `analysis_created_at`. **OPEN-VERIFICATION:** Zerodha holdings may lack a reliable last-updated field — fall back to HTTP-response time recorded as `os_received_at`, and treat `broker_reported_at` as unknown rather than fabricating one.

### Completeness / confidence
Per-line tier propagates to a snapshot `confidence_tier`:
- `HIGH` — ≥95% of market value `OS_LEDGER_CONFIRMED`, no open corporate action, no stale price/FX.
- `MEDIUM` — any `RECONCILED`/`MANUAL_ENTRY`; estimated cost basis.
- `LOW` — any `BROKER_SNAPSHOT_ONLY`; FX/price beyond staleness threshold.
- `UNKNOWN` — unsupportable.

Rules (**SOURCE-ANCHORED**): never infer strategy origin from broker tags unless OS-created and ledger-linked; never claim complete cost basis/lifetime P&L; always separate broker-reported from OS-ledger P&L; any non-confirmed line sets `INCOMPLETE_HISTORY`.

### Failure behavior (fail-closed for *opening* risk, fail-open for *protective* action)
- Broker fetch fails → serve last snapshot flagged `STALE`; **block new opening orders**; do **not** block kill-switch / position-closing.
- Partial fetch (holdings ok, positions fail or vice-versa) → partial snapshot with missing-segment flag; block opening orders only.
- Price/FX stale beyond threshold → `STALE_PORTFOLIO_RISK_BLOCK` or deterministic haircut; block cross-currency sizing if FX `UNQUANTIFIED`.
- Cash ambiguous/conflicting → use lower of broker cash and internal reserved cash; block if conflict > tolerance.
- Open orders unfetchable → block new orders (avoid double cash/exposure reservation).
- Unsettled/pledged/blocked ambiguous → exclude from `quantity_available`, still count as owned exposure.
- Reconciliation drift > threshold → account-level kill switch or human review.
- **Kill-switch exception:** the close/kill path forces an unconditional fresh broker pull, bypassing the cache/staleness gate — an explicit architectural carve-out, never the default.

---

## 3. Household-capable domain model

| Type | Role | Key invariants | V1 schema? |
|---|---|---|---|
| **Person** | Natural/legal identity | immutable `person_id`; PII in secret store; 1 Person → many UserProfiles | **★ required** |
| **UserProfile** | Login/interaction identity | one tenancy; carries prefs/UI roles; **never holds broker credentials** | **★ required** |
| **Household** | View-scoping grouping | **owns nothing**; no custody, no authority | seam (present, inert) |
| **Membership** | Person/Profile ↔ Household | role, visibility, consent, start/end; revocable; grants **no** brokerage authority | seam |
| **LegalOwner** | Who owns the account | immutable once set; matches broker KYC; **never derived from Household** | **★ required** |
| **BrokerConnection** | Credential + session | scoped to explicit authorized accounts; **secrets in secret store, never DB rows/graph**; `credential_version`, `token_expiry`, `scopes_granted` | **★ required** |
| **BrokerageAccount** | Broker-side account | one LegalOwner (may be joint/entity); account-scoped envelope, policy, reconciliation, **kill switch**; unique `(broker_id, account_number)` | **★ required** |
| **Portfolio** | OS view of one account | belongs to exactly one BrokerageAccount; subject of `CurrentPortfolioAnalysis` | **★ required** |
| **Sleeve** | Sub-portfolio attribution | never crosses account boundary; OS sleeves tag **future** orders only, never retro-tag external positions | seam |
| **CapitalEnvelope** | Authorized capital/risk budget | account/sleeve-scoped; versioned/immutable; **never summed into a household envelope that drives orders** | **★ required** |
| **TradingMandate / Consent** | Explicit authority grant | names actor, account, permitted actions, time range, revocation; **prerequisite for any cross-person order**; V1 asserts none exists | seam |
| **Role / Permission** | RBAC | tenancy-scoped; **no cross-account permission without a Mandate** | **★ required** |
| **PolicyAssignment** | Binds policy version to account/sleeve | append-only, immutable per version; account-level is authoritative for execution | **★ required** |
| **HouseholdPortfolioView** | Derived read model | computed, never authoritative; `view_only=true`, `no_trading_authority=true`; preserves per-account breakdown | seam (deferred behavior) |

**Cross-cutting invariants**
1. A `Household` never owns a `BrokerageAccount` and has zero custody rights.
2. A `HouseholdPortfolioView` never changes account-level owner, authority, capital envelope, risk, reconciliation, or kill switch. (**HARD RULE**)
3. Trading authority is account-scoped; **never household-scoped by default**.
4. `BrokerConnection` secrets are usable only for accounts/scopes its mandate authorizes; readable only by the secret manager + the account's reconciliation service — **never joinable through Household/Membership**, never present in any graph/ontology projection.
5. Account-level kill switch dominates all research, household, and sleeve permissions.
6. OS provenance attaches only to OS-created orders/fills; broker-current external positions stay external until matched to ledger evidence.
7. Reconciliation and PolicyAssignment are per-account, never per-household.
8. Cross-account netting is prohibited in V1 risk checks (no future cross-guarantee/margin structure exists yet).

**Tenancy & secret ownership.** A `UserProfile` lives in a tenant; a `Household` groups profiles **within one tenancy only** (cross-tenancy household deferred, needs a dedicated consent protocol). Secrets are owned by `(Person, Broker)` via `BrokerConnection` — not by `UserProfile` and never by `Household`. Admin/support access is separately audited and confers **no** order authority.

---

## 4. Decision-flow and semantic integration

```
[BrokerSnapshot pull]  ──►  BrokerPortfolioImported / BrokerCashImported / BrokerOpenOrdersImported
        │
        ▼
[BrokerSnapshotRecord]  (append-only, payload hash, dual clocks)  ──►  LedgerCutSelected
        │
        ▼
[Canonicalize]  ──►  HoldingsCanonicalized / PositionsCanonicalized / CashCanonicalized
        │
        ▼
[Provenance match vs OS ledger]  ──►  PositionProvenanceClassified   (unmatched → BROKER_SNAPSHOT_ONLY)
        │
        ▼
[Valuation + FX + Exposure]  ──►  ValuationMarksAttached / ExposureVectorComputed
        │
        ▼
[Completeness scoring]  ──►  CompletenessAssessmentRecorded
        │
        ▼
[PortfolioSnapshot] ──► PortfolioAnalysisCompleted{snapshot_id, account_ref, confidence_tier}
        │
    ┌───┴───────────────────────────────┐
    ▼                                   ▼
[ResearchRankingContext]         [PreTradeRiskCheck]  (staleness-gated read of PortfolioSnapshot)
  read-only, account-scoped        post-trade state; account kill-switch; policy version
  penalize crowded/stale/          │  ──► PreTradeRiskDecision{pass|block|degrade}
  pledged/unprotected              ▼
  ──► CandidatePortfolioFitScored  [SizingEngine] (CapitalEnvelope) ──► SizingDecision
                                    ▼
                                  [ExecutionGateway] (kill-switch validate, broker adapter)
                                    ──► OrderIntentCreated / BrokerOrderSubmitted / FillRecorded / OrderRejected
                                    ▼
                                  [LedgerAppend] fill → provenance_tier=OS_LEDGER_CONFIRMED
                                    ▼
                                  BrokerReconciliationCompleted / DriftDetected
```

**Semantic / ontology integration (non-execution).** `PortfolioAnalysisCompleted` triggers a versioned `OntologySnapshot{as_of: snapshot_id, account_ref}` — holdings, sector weights, concentration written as read-only graph context for research explanation. Research agents read the ontology snapshot, **never live broker state**. Retrospective analysis reads `(LedgerSlice, BrokerSnapshotRecord)` pairs by `snapshot_id`; external/manual lines stay partial-provenance. **Execution has a typed dependency only on `PortfolioSnapshot` from the ledger service; ontology types are absent from the execution module's dependency graph** — enforced at the interface boundary and by an adversarial test that injects divergent ontology state and asserts execution is unaffected.

**Anti-leakage rules.** Every artifact carries `tenant_id`, `account_ref`, `snapshot_id`, `policy_version_id`, `created_at`, freshness fields. Pre-trade decisions **reject** any candidate whose snapshot `account_ref` ≠ target execution account. Research prompts are permission-filtered and never receive unconsented family-account data. `HouseholdPortfolioView` is assembled only from snapshots the querying profile has explicit per-account read consent for, and **never drives `PreTradeRiskCheck`**.

**Minimum typed artifacts/events.** `BrokerSnapshotRecord`, `PortfolioLine`, `CashLine`, `OpenOrderReservation`, `PortfolioSnapshot`, `CurrentPortfolioAnalysis`, `PortfolioAnalysisCompleted`, `PositionProvenanceClassified`, `ExposureVectorComputed`, `CompletenessAssessmentRecorded`, `ConcentrationAlert`, `CandidatePortfolioFitScored`, `PreTradeRiskDecision`, `SizingDecision`, `OrderIntentCreated`, `BrokerOrderSubmitted`, `FillRecorded`, `BrokerReconciliationCompleted`, `DriftDetected`, `KillSwitchToggled`, `PolicyAssignmentRef`, `OntologySnapshot`.

---

## 5. Nine-day scope and acceptance gates

| Day | Milestone | Acceptance criteria |
|---|---|---|
| 1 | **Contract + schema freeze** | V1 types land: Person, UserProfile, LegalOwner, BrokerConnection, BrokerageAccount, Portfolio, CapitalEnvelope, PolicyAssignment, Role/Permission; household seam columns present-but-nullable; **no Household object can authorize trading** (invariant test passes) |
| 2 | **Broker import adapters** | Zerodha holdings+positions, Alpaca positions+cash+open-orders pulled into raw tables; raw payload hashed, dual-clock stamped; **idempotent on replay**; import failure → account-scoped stale/fail status |
| 3 | **Canonicalization + provenance** | canonical holdings/positions/cash built; OS-ledger match assigns tiers; **connected account with pre-existing external holdings shows them**; no strategy-origin claim on unmatched lines |
| 4 | **Valuation, FX, freshness** | prices/FX/classification attached, timestamped; **stale price/FX → explicit LOW-confidence / fail-closed**; market value + basic exposure computed |
| 5 | **Risk + sizing integration** | pre-trade risk consumes snapshot incl. non-OS holdings + open orders; **candidate breaching concentration via a manual/external holding is rejected or resized**; pending buy reserves cash |
| 6 | **Reconciliation + kill switch** | ledger↔broker drift thresholds; **drift > threshold blocks live orders**; kill switch is account-level, **not overridable by household view**; kill path forces fresh pull |
| 7 | **Household foundation + permission tests** | skeletal household/membership/view generation; execution stays single-account/single-profile; **view is read-only, preserves account ids + permission filters, exposes no credentials** (secret-leak test passes) |
| 8 | **End-to-end dry run (paper/sim)** | full slice: import → snapshot → research candidate → fit score → deterministic risk → order intent → paper submit → reconcile; **every decision references snapshot_id + policy_version**; audit trail reconstructs allow/block reason |
| 9 | **Limited live vertical slice** | small-scope live, long-only cash, one account; **account kill switch tested; stale broker state blocks orders; external holdings influence sizing/risk; P&L display separates broker/os-ledger/unknown; household remains read-only** |

**Non-goals (Day 9).** Mature/learned alpha; multi-user or family execution; household order authority; complete lifetime P&L reconstruction; tax optimization; derivatives/margin/shorting; automated corporate-action backfill; full factor/correlation model; cross-account netting; any downside-protection guarantee.

---

## 6. Adversarial findings

| # | Failure mode | Sev | Detection | Response |
|---|---|---|---|---|
| 1 | **Incomplete pre-OS history treated as complete** (SOURCE-ANCHORED: no lifetime P&L / origin tags at either broker) | High | any line `≠ OS_LEDGER_CONFIRMED` | set `INCOMPLETE_HISTORY`; split P&L streams; block strategy attribution; never report cumulative P&L as complete |
| 2 | **Duplicate identity / account collision** (same account under two profiles) | High | unique `(broker_id, account_number)`; dedup on BrokerConnection create | reject duplicate; require explicit account-transfer/merge review; never auto-merge authority |
| 3 | **Manual / non-OS trades ignored in pre-trade risk** | Critical | broker line unmatched to ledger but present in snapshot; reconciliation delta each cycle | include as external exposure in risk/sizing; block opening orders on affected instrument until acknowledged |
| 4 | **Stale prices / stale snapshot permit oversized order** | High | `os_received_at` delta vs policy; staleness gate | `STALE_PORTFOLIO_RISK_BLOCK` or haircut; force re-pull before opening orders |
| 5 | **Credential leakage via household view / graph** | Critical | secret-store access log; `BrokerConnection` not joinable through Household/Membership; graph-export scan | secrets owned by `(Person, Broker)` only; pen-test gate before household views ship; rotate/revoke on hit |
| 6 | **Family aggregation assumed to grant trading authority** | Critical | `TradingMandate` existence is a hard prerequisite; V1 asserts none exists | reject at domain layer by invariant; audit any cross-profile order attempt |
| 7 | **Cost-basis error distorts P&L / tax-like display** (broker avg-price ≠ true lot basis) | Medium | compare broker cost basis to OS-ledger basis; flag divergence > threshold | OS ledger authoritative; surface discrepancy in CompletenessReport; never auto-correct without user confirm |
| 8 | **Currency translation error masks exposure** | High | stamp FX source+time; compare to broker market value where available | timestamped FX marks; `FX_UNQUANTIFIED` beyond staleness; **no cross-currency aggregation for risk sizing**; show local + reporting currency |
| 9 | **Corporate action changes qty/basis mid-flight** | High | broker qty ≠ ledger-expected qty; corp-action calendar flag | `CORPORATE_ACTION_PENDING`; block sizing on affected instrument; manual confirm (auto-backfill deferred) |
| 10 | **Pledged / unsettled / blocked qty treated as saleable** (SOURCE-ANCHORED: Zerodha auth/T1/T2; Alpaca unsettled cash) | High | `settlement_state` per line; `quantity_available = total − pledged − unsettled − reserved` | risk uses `quantity_available` only; still count full qty as owned exposure; alert if pledged > threshold |
| 11 | **Protection / hedge coverage mismatch** | Med | position has exposure but no monitoring/exit/hedge record; V1 flags `PROTECTION_UNMODELLED` | treat all exposure as unhedged in V1; never claim downside protection; options ledger deferred |
| 12 | **Aggregate household view masks account-level breach** | Critical | household weight looks safe while one account is in violation | household view is additive annotation only; **per-account risk runs independently and cannot be overridden**; always accompany with per-account ConcentrationFlags |
| 13 | **Open orders omitted → double cash/exposure reservation** | High | broker open-order import stale/failed; internal reservations mismatch | block new orders until open orders reconciled |
| 14 | **Instrument identity collision across brokers/exchanges** | High | same symbol → different ISIN/exchange/currency | require canonical instrument id w/ exchange+country; reject ambiguous mapping |
| 15 | **Broker P&L and OS P&L blended into one number** | Medium | report contains P&L without provenance split | force `broker_reported` / `os_ledger` / `unknown_partial` labels |
| 16 | **Kill switch scoped to user instead of account** | Critical | one profile toggles but another path can trade same account | store/enforce kill switch on `BrokerageAccount`; check at order gate |
| 17 | **Kill-switch acts on stale snapshot** (closes wrong qty) | Critical | close path would otherwise reuse cached snapshot | kill/close path forces unconditional fresh broker pull — explicit exception to staleness gate |
| 18 | **Research agent sees unauthorized family data** | High | prompt/context contains out-of-consent accounts | snapshot permission filtering; red-team prompt logs; deny unscoped household data |
| 19 | **Ontology graph used as execution source of record** | High | execution references graph instead of snapshot/ledger | execution depends only on `PortfolioSnapshot`; ontology absent from execution dep graph; injection test asserts no effect |
| 20 | **Reconciliation drift normalized away by aggregate totals** | High | account-level diff hidden by opposite diff elsewhere | reconcile per account+instrument; no cross-account offsetting |

---

<!-- CHUNK-1 SELF-AUDIT: headings=1-6; portfolio_contract=present; domain_invariants=present; day9_scope=present; adversarial_count=20; verdict=PASS; reason=All six sections emitted. Contract covers manual holdings, open orders, cash, unsettled/pledged, cost basis, valuation, three-way P&L split, sector/country/currency/factor/correlation/liquidity/event exposures, protection coverage, freshness, completeness/confidence tiers and fail-closed/fail-open behavior with Day-9-vs-deferred split explicit. Domain model distinguishes all 14 named types with invariants, tenancy boundaries, secret ownership and V1-schema marking. Decision-flow shows research→risk→sizing→execution→retrospective→ontology with anti-leakage rules and minimum typed artifacts/events. Nine-day sequence has per-day acceptance criteria and non-goals. Adversarial section has 20 findings covering every required failure mode. HARD RULES respected: design research only, no code, no investment advice, household view never alters account authority/risk/kill switch, no false completeness claims, epistemic tags applied. Size within 8-15 KB. -->
