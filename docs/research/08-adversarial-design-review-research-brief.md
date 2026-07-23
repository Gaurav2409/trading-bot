# Trading OS — Adversarial Design Review and Research Brief

> **Status:** Research brief; no implementation authorized.
> **Date:** 2026-07-20.
> **Spec under review:** `docs/superpowers/specs/2026-07-20-trading-os-design.md`
> **Authoritative decisions:** `docs/research/RESEARCH-STATE.md` (D1–D24 and amendments).

## Purpose

This document records an adversarial review of the Trading OS design and provides a
ready-to-use prompt for a coding/research agent to validate the findings against primary
sources. It is a critique and research agenda, not an implementation plan.

The non-negotiable invariant remains D4:

> LLMs propose; deterministic code disposes. No LLM-derived number may set or alter size,
> price, exit thresholds, risk limits, or compliance outcomes. The hot-path seam carries
> only the permitted thesis classification and the exposure vector produced by deterministic
> causal-KG traversal.

## Executive conclusion

The design is not ready for approval. Its high-level plane separation is sound, and the
Phase-A correctness gate is in the right conceptual position, but the boundary is not yet
enforceable. Eight blocker-class findings permit covert LLM sizing, duplicate or unprotected
exposure, or legal non-compliance. Eleven further major findings cover data correctness,
accounting, recovery, cross-sleeve risk, missing lifecycle flows, and testability.

## Findings and proposed design edits

### F01 — Blocker: conviction-keyed Kelly is a D4 seam leak

- **Touches:** spec §9 lines 253–256 and §10 lines 265–268; D4, D5, D9b.
- **Failure:** Two identical candidates receive different LLM conviction buckets. Mature
  per-bucket statistics select different 1/4-Kelly ceilings, so the LLM bucket changes
  permitted quantity despite the claim that conviction never moves a number.
- **Proposed edit:** Make `CalibrationStore` evaluation-only in v1. `Sizer`, `RiskEngine`,
  `ExitManager`, and `ComplianceGate` must not read any statistic keyed by model, prompt,
  conviction bucket, thesis identity, or another LLM output. Remove the executable
  conviction-keyed Kelly ceiling. Any future Kelly ceiling must use deterministic variables,
  be identical for LLM and null candidates, and require a new design decision.
- **Decision-log impact:** D5 and D9b must be amended; editing the narrative spec alone is
  insufficient.

### F02 — Blocker: LLM-authored KG magnitude/confidence can alter exposure numerically

- **Touches:** spec §3 lines 71–82 and §5 lines 136–145; D4, D14, D14a.
- **Failure:** The LLM emits a different event-confidence or magnitude value, or proposes an
  edge with higher confidence. Deterministic traversal multiplies that value into the exposure
  vector, which changes the risk tilt or allowed position. Deterministic arithmetic does not
  remove the value's LLM provenance.
- **Proposed edit:** `MacroEventLabel` may contain closed categorical taxonomy fields only:
  `driver`, `source`, `phase`, and `direction`. No LLM-emitted scalar or ordinal
  magnitude/confidence may be consumed by traversal. `EdgeProposal` contains endpoints,
  relation, and citations only—no weight or confidence. Deterministic policy assigns evidence
  confidence from source type, corroboration count, age, and admission state;
  `EdgeWeightFitter` remains the only source of numeric weights.
- **Decision-log impact:** D14/D14a require amendment if their magnitude/confidence fields are
  intended to be LLM-supplied numeric or ordinal inputs.

### F03 — Blocker: the absolute broker-side protection guarantee is false

- **Touches:** spec §5 lines 153–163 and §6 lines 177–195; D6, D12, D18, D22.
- **Failure:** Kite accepts an entry but its acknowledgement is lost. The order fills while
  the broker is disconnected or the host is down. `ExitManager` never sees the fill and no GTT
  exists. A later partial fill can likewise increase position quantity above protected quantity.
- **Proposed edit:** Replace the absolute guarantee with a broker-confirmed protection-coverage
  state machine. Suggested states: `SUBMITTED_UNCONFIRMED`,
  `PARTIALLY_FILLED_UNPROTECTED`, `PROTECTION_PENDING`, and `PROTECTED`. A position is
  protected only when active broker-confirmed exit quantity covers broker-reconciled position
  quantity. Any deficit blocks further exposure. Ambiguous entry outcomes reconcile before
  retry. Failure to establish protection by a configured deadline triggers controlled
  liquidation or `HALTED_UNVERIFIED` plus urgent manual intervention.
- **Required honesty:** Kite cannot guarantee a zero-duration atomic fill-to-GTT transition;
  the spec must state the residual window rather than claim it does not exist.

### F04 — Blocker: GTT cancellation and fired-but-unfilled have the wrong fail direction

- **Touches:** spec §6 lines 179–180 and §5 lines 159–161; D12, D18, D20.
- **Failure:** A gap-through fires a DAY-limit GTT that remains unfilled. The design continues
  until EOD, potentially carrying an unprotected position overnight. A CA cancellation can
  also occur before the ex-date while repair is deferred to a later EOD cycle.
- **Proposed edit:** Any protective-coverage deficit is fail-closed for exposure increases and
  puts the affected symbol in `REDUCING`. A deterministic `ProtectionSupervisor` on the risk
  clock must detect GTT cancellation, rejection, expiry, unfilled trigger orders, and partial-fill
  growth immediately. It repairs or executes the configured controlled-liquidation policy.
  EOD reconciliation is a backstop only. `HALTED` must never cancel a protective order except
  during a confirmed replace operation.

### F05 — Blocker: the 180-day idle-FX watchdog does not prevent a FEMA breach

- **Touches:** spec §7 lines 208–215; D19; stream 07 §§1f and 5.
- **Failure:** Sale proceeds remain idle. The system warns at day 150 and blocks investment at
  day 175, but does not repatriate the money. Day 180 arrives with the legal state unchanged.
  Blocking investment also removes one possible cure without executing the other.
- **Proposed edit:** Create an `IdleFxLot` for every remittance remainder, sale receipt,
  dividend, refund, and other realized-FX credit. Record origin, value date, amount, remaining
  amount, allocation rule, and legal deadline. Reinvestment and repatriation consume lots under
  a fixed, legally reviewed method. Every lot must have broker/bank-confirmed disposition by the
  operational deadline. If automated repatriation is not explicitly authorized and tested,
  require verified manual repatriation; without either capability, the US sleeve cannot go live.
- **Live blocker:** Obtain a written FEMA opinion defining the clock start, allocation method,
  active-trading cash treatment, and whether any Alpaca cash sweep counts as reinvestment.

### F06 — Blocker: a local ledger cannot enforce the PAN-wide LRS cap

- **Touches:** spec §7 lines 208–212 and §8 lines 238–241; D19, D21.
- **Failure:** The user has remitted USD 200k through another bank or for another purpose. The
  OS knows only about USD 20k sent to Alpaca and approves another USD 50k, breaching the
  PAN-wide USD 250k FY limit.
- **Proposed edit:** Split `PreRemittanceGate` from `PreTradeGate`. Pre-remittance checks require
  a current PAN-wide opening balance and all FY remittances across every bank and purpose,
  supported by AD-bank records or an explicit signed attestation. Unknown or stale external
  state fails closed. Repatriation never reduces the cumulative meter. Purchases using already
  remitted settled cash do not themselves consume the LRS cap.

### F07 — Blocker: HITL ordering and timeout behavior are unsafe

- **Touches:** spec §5 lines 153–157 and §9 lines 257–259; D17, D18, D22.
- **Failure:** The numbered flow submits in step 11 and seeks review in step 12. Separately, a
  time-stop or regime exit can be suppressed by default-no-trade when the reviewer is absent,
  retaining risk instead of reducing it.
- **Proposed edit:** Move HITL before submission. Bind approval to an immutable order-set hash,
  portfolio/data snapshot version, and expiry. After approval, rerun cash, risk, compliance,
  protection, and kill-switch checks immediately before submission. Default-no-trade applies to
  exposure-increasing orders. Broker-side protective stops never require approval. Planned
  risk-reducing exits are visible during a review window but proceed at expiry unless the final
  D17/D18 policy explicitly and safely defines otherwise.
- **Decision-log impact:** D17 and D18 need a human decision on whether exit review is approval,
  veto, or notification.

### F08 — Blocker: append-only events do not make broker effects idempotent

- **Touches:** spec §5 lines 126–127, §6 lines 189–191, and §10 lines 269–270; D6, D15,
  D16, D18.
- **Failure:** An order-intent event is written, the broker accepts the order, acknowledgement is
  lost, and the process crashes. Replay blindly submits again and doubles exposure. GTT create,
  replace, modify, and cancel have analogous races.
- **Proposed edit:** Every broker effect starts with a unique durable `IntentId`. Replay reconciles
  that intent against broker orders and trades before any retry. Use native client IDs/tags where
  available. If the broker cannot prove idempotency, an unknown outcome enters
  `OUTCOME_UNKNOWN`, blocks related exposure, and reconciles; it is never blindly retried.
  Contract tests should assert no duplicate economic effect under acknowledgement loss. Add a
  durable kill-switch generation/fencing token so stale workers cannot submit after HALT.

### F09 — Major: all-LLM-down behavior conflicts with D12 and null independence is unproven

- **Touches:** spec §3 lines 87–90 and §6 lines 175–176; D11 versus D12.
- **Failure:** One implementation follows D12 and halts the market when all providers fail;
  another follows §6 and continues the null. The null may also consume LLM tables, graph output,
  calibration state, or an LLM-derived universe, making the advertised rules-only fallback false.
- **Proposed edit:** After resolving D12, define `RuleNullJob` to consume only a sealed validated
  market snapshot, deterministic signal config, and deterministic portfolio state. It must not
  read theses, reports, KG output, calibration data, prompt/model state, or LLM health. LLM failure
  suspends the LLM strategy only; data, broker, reconciliation, compliance, and portfolio-state
  failures still halt both. Define deterministic provider-diversity quorum and distinguish loss of
  an optional analyst from loss of the required synthesizer.

### F10 — Major: the seam guarantee is not encoded by the interfaces

- **Touches:** spec §3 lines 66–85 and §5 lines 143–149; D4.
- **Failure:** Plane 1 stores `TradeThesis{conviction,direction,rationale}`, while the hot path is
  described as receiving a thesis. A permissive schema accepts fields such as `target_vol` or
  `stop_hint`, or later code parses rationale. Merely omitting a `size` field is inadequate.
- **Proposed edit:** Keep `ResearchTradeThesis` entirely in Plane 1. A deterministic projector
  emits `HotPathCandidate{thesis_id, conviction_band, direction}` with closed enums and
  `additionalProperties=false`. `Sizer` accepts neither thesis type; it accepts an admitted
  symbol/direction plus deterministic market, portfolio, and risk inputs. Rationale and raw LLM
  JSON must be structurally inaccessible downstream. Reject extra fields, non-finite numbers,
  nested free-form extensions, and provider-specific additions at the boundary.

### F11 — Major: the correctness gate lacks an immutable, typed snapshot boundary

- **Touches:** spec §5 lines 129–145 and §8 lines 228–235; D20.
- **Failure:** Correctness passes, then a late CA revision mutates a queried table. Signals read
  `latest` rather than the rows that passed validation. The US sleeve can also pass without an
  independent split, dividend, delisting, and universe-history ledger because Phase A specifies
  India checks only.
- **Proposed edit:** `CorrectnessLayer` emits a content-addressed
  `ValidatedDataSnapshotId` containing exact OHLCV, CA-ledger, universe-membership, calendar,
  news-cutoff, and enabled-signal versions. Every signal, traversal, simulation, and evaluation
  interface requires the token and cannot query an unsealed latest view. Missing, stale,
  future-dated, or revised required data invalidates it. Add an independent US CA/delisting and
  membership-history source. Bind every factor to raw, split-adjusted, or total-return series.
  The active-signal manifest must show quality disabled until PIT fundamentals clear D20.

### F12 — Major: the compliance rule set is incomplete and mixes lifecycle stages

- **Touches:** spec §7 lines 200–222; D19; streams 06 and 07.
- **Failure:** An Indian-issuer ADR passes the common-stock whitelist; a synthetic or commodity
  ETF passes `plain ETF`; an India order leaves through an unregistered egress IP; a dividend
  lacks Form 67 data; or tagging uses the wrong generic/unique algo-ID rule.
- **Proposed edit:** Organize D19 by stage:
  - **India pre-order:** own/immediate-family account allowlist, observed egress IP matched to the
    broker whitelist, conservative OPS throttle, current broker-required algo tag, cadence gate,
    DDPI capability, and long-delivery-only checks.
  - **US pre-order:** US-listed, long, fully paid, cash-account and settled-cash flags; reject
    Indian-issuer ADRs, derivatives, commodities, FX, crypto, leveraged/inverse, and synthetic
    exposures.
  - **Pre-remittance:** PAN-wide meter, designated AD bank, approved purpose code, external-state
    freshness, and idle-FX disposition ability.
  - **Post-event/reporting:** gross dividends, withholding, Form 67 deadline, Schedule FA account,
    peak/closing balance, income/sale proceeds, and ITR-2/FSI/TR/OS/CG outputs.
  - Add the primary SEBI/NSE circular and broker SOP to the verify-before-live blockers.

### F13 — Major: two-currency accounting is not deterministic or replay-safe

- **Touches:** spec §8 lines 238–241; D21.
- **Failure:** A fractional US fill settles the next day; the live FX observation is corrected;
  the SBI prior-month date falls on a holiday; or fees, withholding, and CA cash-in-lieu are
  omitted. Updating a fill violates append-only history, while recomputation can produce a
  different replay. Equity and realized-FX gains can be double-counted.
- **Proposed edit:** Use fixed-point decimal quantities and money. Store trade timestamp,
  exchange trade date, settlement/value date, and tax-recognition date separately. Native fills
  are immutable; `TaxFxRateAssigned`, `LiveFxMarkObserved`, and corrections are separate events
  referring to immutable rate records. Define rate source, direction, timestamp, holiday fallback,
  rounding, and stale-rate behavior. Cover fees, taxes, dividends, withholding, remittances,
  repatriations, and cash-in-lieu. Define an approved FX-lot method. Round quantities to venue and
  broker precision, then rerun risk/compliance. Use AD-bank certificates for gross LRS amounts;
  record spreads, fees, and TCS separately.

### F14 — Major: local exit/recovery state is not reconstructable

- **Touches:** spec §5 line 155 and §6 lines 189–191; D15, D18.
- **Failure:** ATR-trail state, entry regime, time-stop deadline, stop broker ID, approval expiry,
  or order reservation exists only in process memory or Valkey. A restart recovers quantity but
  silently loses the exit policy.
- **Proposed edit:** Enumerate durable events for position episodes, fill allocation, stop
  intent/acknowledgement, coverage, trail ratchets, time-stop deadlines, entry regime, approval
  decisions, order reservations, and strategy attribution. Valkey is projection-only.
  Calibration is keyed by unique `position_episode_id` and written once after the episode reaches
  zero, including multi-day partial exits. State that the event log is audit/intention truth while
  the broker is authoritative for current custody; missing external activity is appended as an
  observed reconciliation event after resolution, never rewritten into history.

### F15 — Major: independent sleeve cycles can overspend global risk

- **Touches:** spec §5 line 126 and §8 lines 238–241; D5, D15, D16, D21.
- **Failure:** India and US jobs read the same portfolio snapshot. Each consumes most of the
  remaining cluster or currency-risk budget, and the combined committed exposure breaches the
  cap. Pending orders, unsettled cash, and FX movement make the result worse.
- **Proposed edit:** Use a versioned global portfolio snapshot containing both sleeves, open and
  pending orders, unsettled cash, protection deficits, and live FX marks. Before submission, an
  order set obtains a durable cash/risk reservation through compare-and-swap against the snapshot
  version. Stale reservations are rejected and recomputed. Research can run concurrently; risk
  commits cannot use the same stale version.

### F16 — Major: rule-null and LLM execution attribution is undefined

- **Touches:** spec §3 lines 87–90 and §1 lines 29–37; D10, D10a, D11.
- **Failure:** Both paths buy the same stock, or one exits while the other retains it. The broker
  has one net position and stop, so P&L, costs, exit behavior, and calibration cannot be attributed;
  the three-way scoreboard becomes invalid.
- **Proposed edit:** Define separate immutable `StrategyBook`s and capital/risk budgets. If broker
  execution is netted, specify deterministic fill allocation, virtual tax lots, cost allocation,
  conflicting-exit resolution, and physical stop coverage. Otherwise require separate supported
  accounts/subaccounts. Aggregate risk across all books regardless of execution separation.

### F17 — Major: dividends, credentials, and calendar/session lifecycle flows are missing

- **Touches:** spec §3 lines 62–64 and §5 lines 124–163; D16, D19, D21, D22.
- **Failure:** A Kite token expires while a CA has cancelled protection; local state remains visible
  but cannot be verified or repaired. A US dividend creates idle USD and withholding obligations
  without an idle-FX lot. DST, Muhurat trading, or an unscheduled closure causes EOD work to run
  before the true session close.
- **Proposed edit:** Add `SessionReadiness` using a versioned authoritative calendar and observed
  close; unknown sessions fail closed. Add `CredentialReadiness` before every order/protection job;
  Kite `TokenException` is not automatically retried and requires re-authentication plus
  reconciliation before new exposure. Add `BrokerCashEventIngestor` for dividends, withholding,
  interest/sweep income, fees, reversals, repatriations, and cash-in-lieu, feeding accounting,
  idle-FX, Schedule FA, and Form 67 state.

### F18 — Major: mandatory D14a graph-admission controls disappeared from the spec

- **Touches:** spec §3 lines 71–80, §4 lines 101–107, and §11 lines 287–291; D14a.
- **Failure:** A one-source edge is human-approved, receives high confidence, and enters traversal
  before the LLM authoring process meets the required precision bar. The edge then remains
  indefinitely because only additions, not deprecations, are modeled.
- **Proposed edit:** Restore every locked D14a gate: no provenance means traversal-ineligible;
  a second independent source is required above confidence 0.5; the approximate 0.85 precision
  bar on about 200 expert-labelled claims precedes Layer-1 admission; `valid_from`,
  `last_confirmed`, and source-publication date are mandatory; unconfirmed edges decay about 30%
  annually; authoring must deprecate as well as add. These controls apply to v1 human-gated edges;
  auto-add remains v2.

### F19 — Major: promotion thresholds are undefined and KG validation is omitted

- **Touches:** spec §1 lines 27–37 and §10 lines 271–276; D9b, D10a, D14.
- **Failure:** Tracking-error, slippage, drawdown, maturity, or decision-count thresholds are chosen
  after paper results are visible. Three quiet paper months contain no meaningful macro shock, so
  KG quality is never tested.
- **Proposed edit:** Freeze and hash a promotion manifest before paper day 1 containing all numeric
  bounds, trial registry, cost assumptions, minimum decision windows, cross-sectional sample
  definition, and per-sleeve benchmarks. Restore D14's net-of-cost cross-sectional rank-correlation
  metric and mandatory historical 2020 COVID and 2022 Russia–Ukraine replays. State how dependent
  cross-sectional observations affect effective sample size.

### F20 — Major: independent testability is asserted but not designed

- **Touches:** spec §4 lines 94–120 and §10 lines 263–281; D3, D6, D10, D15.
- **Failure:** Testing `CorporateActionMonitor` requires live Kite, `GraphStore` requires Neo4j,
  calendar tests use the real clock, or the Kite contract suite risks live orders because Kite has
  no sandbox. Provider schema failures and prompt-injected extra fields are not exercised.
- **Proposed edit:** Give every external boundary a typed port and offline fake: clock/calendar,
  market data/CA, FX rates, security master, graph store, event store, broker transport, and LLM
  role. Separate pure contract/mapping tests with recorded fixtures from credentialed smoke tests.
  Add deterministic tests for acknowledgement loss, duplicate scheduler fires, partial fills,
  GTT failure, CA replacement, token expiry, stale FX, DST/holiday edges, extra LLM fields, and
  stale-worker fencing.

## Ranked priorities

1. Remove conviction-keyed Kelly and every calibration-to-sizing path.
2. Remove LLM-supplied KG magnitude/confidence/edge numbers and enforce the seam with strict
   projected types.
3. Replace the false always-protected guarantee with continuously reconciled protection coverage
   and an ambiguous-fill state machine.
4. Make the 180-day idle-FX rule and PAN-wide LRS cap operationally enforceable.
5. Make every broker side effect crash-safe under acknowledgement loss, with reconciliation before
   retry and durable watchdog fencing.

## Human decisions required before editing the authoritative design

1. **D4 versus D5/D9b:** conviction-bucket calibration feeds Kelly sizing.
2. **D4 versus D14/D14a:** LLM-classified magnitude/confidence and edge confidence may feed
   numeric traversal.
3. **D4/D5 versus D24:** D24 says web-augmented theses may eventually be allowed to move size.
4. **D11 versus D12:** the null must continue independently, but all-provider failure is also a
   kill-switch trigger.
5. **D17 versus D18:** default-no-trade is safe for entries but may suppress risk-reducing exits.
6. **D9a versus D16/event triggers:** slowest-signal cadence conflicts with trade-capable daily or
   event-triggered LLM work.
7. **D11 versus D20:** the null includes quality while quality is disabled until PIT data exists.
8. **D9b threshold:** the decision log requires a maturity threshold but does not specify one.

## Ready-to-use research prompt for a coding agent

Copy the prompt below into a coding/research agent working from the repository root.

```text
You are performing an evidence-first adversarial research pass on a DESIGN DOCUMENT. Do not
implement code, scaffold components, create an implementation plan, or edit the approved spec or
decision log. Your job is to validate, reject, refine, and prioritize the findings in:

  docs/research/08-adversarial-design-review-research-brief.md

Repository root:
  /Users/I321170/Documents/Projects/trading-bot

Read these files completely, in this order:

1. docs/superpowers/specs/2026-07-20-trading-os-design.md
2. docs/research/RESEARCH-STATE.md
3. docs/research/08-adversarial-design-review-research-brief.md
4. docs/research/05-causal-analysis-synthesis.md
5. docs/research/06-india-mechanics.md
6. docs/research/07-us-sleeve-legal.md

Authority and invariant:

- RESEARCH-STATE.md is authoritative when the narrative spec merely omits or drifts from a locked
  decision.
- If locked decisions contradict each other, do not silently choose. Identify the conflict and
  recommend the smallest human decision needed.
- D4 is non-negotiable: LLMs propose; deterministic code disposes. No LLM-derived scalar, ordinal
  class, calibrated bucket, rationale, confidence, magnitude, expected return, volatility estimate,
  or hidden field may set or alter quantity, price, risk limits, exit thresholds, or compliance.
- Conviction may gate/rank candidates only. It may not scale size directly or indirectly.
- Do not pull v2 items into v1. Do not propose IBKR, WebResearchSpoke implementation, automatic KG
  edge admission, alternative data, intraday trading, leverage, shorting, derivatives, or
  heavyweight infrastructure.

Research requirements:

1. Evaluate every finding F01–F20. For each, return one verdict:
   CONFIRMED, CONFIRMED WITH MODIFICATION, NOT SUPPORTED, or NEEDS HUMAN/LEGAL DECISION.
2. Trace every alleged D4 seam numerically from input to final effect. Specifically investigate:
   - conviction_bucket -> CalibrationStore -> Kelly ceiling -> quantity;
   - MacroEvent magnitude/confidence -> Traversal -> exposure vector -> risk/quantity;
   - LLM-authored edge confidence -> Traversal -> exposure vector;
   - rationale/extra JSON fields crossing permissive schemas.
3. Prove or disprove the broker-protection guarantees for Kite and Alpaca across:
   - accepted order with lost acknowledgement;
   - full and partial fills before stop creation;
   - later partial fills increasing quantity;
   - process, host, broker, or database outage;
   - GTT/stop rejection, trigger, DAY expiry, gap-through, and no fill;
   - corporate-action cancellation and split/bonus quantity changes;
   - token expiry or re-authentication failure;
   - kill-switch cancellation racing a fill;
   - restart and reconciliation.
   Identify what each broker can guarantee atomically and what remains an unavoidable residual
   exposure window. Use current official broker documentation where available.
4. Validate every fail-direction in spec §6. Pay special attention to whether `CONTINUE` should be
   fail-closed for new exposure, whether existing exits must remain operational during HALT, and
   how stale workers are fenced after watchdog/dead-man activation.
5. Research the US-sleeve legal issues using current primary or near-primary sources:
   - RBI LRS cap, all-bank/PAN aggregation, repatriation not resetting the cap;
   - the 180-day rule, the clock-start event, allocation of reinvestment/repatriation, dividends,
     sale proceeds, unspent remittance balances, and cash sweeps;
   - OPI eligibility, Indian-issuer ADR exclusion, leveraged/inverse/synthetic/commodity ETFs,
     margin, shorting, derivatives, and cash-account requirements;
   - designated AD bank and correct remittance purpose code;
   - current TCS statute/rate/threshold;
   - Rule-115 conversion date/rate semantics;
   - foreign-share capital-gain rules, Schedule FA fields, Form 67, and W-8BEN treatment.
   Prefer RBI, SEBI, NSE, Income Tax Department/legislation, IRS, broker contracts/docs, and
   official circulars. Clearly label any conclusion that still rests on secondary commentary.
6. Validate the India mechanics using current primary sources:
   - SEBI/NSE retail-algo circular and effective requirements;
   - static-IP enforcement and how it can be verified before submission;
   - OPS thresholds and generic versus unique algo-ID tagging;
   - DDPI/TPIN requirements for autonomous delivery sells;
   - current Kite GTT, order, rate-limit, circuit-band, and token semantics;
   - T+1 settlement and current transaction-cost components.
7. Stress-test the data gate. Determine the minimum contents and validity rules for an immutable
   `ValidatedDataSnapshot`, for both India and the US, so no signal can read unvalidated or later
   mutated data. Cover CA factors, total-return versus split-adjusted series, universe membership,
   delistings, calendars, future timestamps, stale data, and disabled PIT fundamentals.
8. Stress-test event sourcing and replay. Enumerate every state item needed to reconstruct orders,
   positions, partial exits, protective coverage, trailing stops, time stops, approval state,
   kill-switch state, risk reservations, strategy attribution, FX lots, idle-FX lots, and
   calibration. Identify every side effect that is non-idempotent under crash/acknowledgement loss.
9. Validate two-currency accounting edge cases: fixed-point precision, fractional US quantities,
   integral India quantities, tick/quantity rounding, fees, taxes, dividends, withholding,
   settlement/value dates, rate corrections, realized-FX lot basis, LRS gross-versus-net amounts,
   and append-only correction events.
10. Evaluate cross-sleeve and cross-strategy concurrency: common risk reservations, pending orders,
    unsettled cash, asynchronous India/US cycles, FX moves, rule-null versus LLM attribution, netted
    physical positions, and protective-stop ownership.
11. Determine whether every component in §4 can be tested without a live broker, LLM, clock,
    calendar, FX feed, Neo4j instance, or regulatory service. Propose typed ports and test doubles
    only at the design level; do not write them.
12. Verify that D14a admission controls and D14/D10a evaluation requirements are all represented in
    the spec, including historical shock replay and precommitted numeric promotion thresholds.

Internet/source discipline:

- Browse because broker mechanics, laws, circulars, tax rules, and product/account terms are
  time-sensitive.
- Prefer current primary sources. Link directly to the exact circular, rule, FAQ, API page, account
  agreement, or statute section supporting each material claim.
- Record publication/effective dates and note conflicts between current and archived documents.
- Do not treat blogs, broker forums, marketing pages, AI summaries, or unverified arXiv papers as
  primary evidence. They may identify a question but cannot close a live-trading blocker.
- Do not exceed short quotation limits; summarize evidence and use brief quotes only when wording
  is legally or operationally decisive.
- Make inferences explicit.

Required output:

A. Executive verdict: whether the spec is safe to approve, with the count of confirmed blockers,
   majors, rejected findings, and unresolved legal/human decisions.

B. A table for F01–F20 with:
   - verdict;
   - severity after research;
   - exact spec line and Dxx decision;
   - evidence and direct links;
   - concrete failure trace;
   - smallest seam-safe proposed wording;
   - whether RESEARCH-STATE.md must also change.

C. A broker protection state/race analysis for Kite and Alpaca. Include timelines for at least:
   lost acknowledgement, partial fill, GTT/stop failure, CA cancellation, token failure, HALT/fill
   race, and restart. Clearly distinguish guaranteed, eventually detected, and impossible-to-
   guarantee states.

D. A compliance matrix grouped into pre-remittance, pre-order, post-fill/cash-event, periodic
   reporting, and verify-before-live blockers. Label every rule PRIMARY CONFIRMED, SECONDARY,
   INFERENCE, or OPEN LEGAL OPINION.

E. A seam audit showing every field allowed to cross from the slow plane, every deterministic
   consumer, and proof that changing any disallowed LLM field cannot alter quantity, price, exits,
   risk limits, or compliance.

F. A typed design-level state/recovery inventory and a fail-direction table with corrected terminal
   states. Do not provide code or an implementation task list.

G. A ranked top-five recommendation list.

H. An explicit `Human decisions required` section. Do not silently resolve D4/D5/D9b/D14/D24,
   D11/D12, D17/D18, D9a/D16, or D11/D20 conflicts.

Save the research report as a new Markdown file under `docs/research/`; do not modify the spec or
RESEARCH-STATE.md. Suggested name:

  docs/research/09-adversarial-findings-validation.md

Stop after producing the research report. Do not implement anything.
```

