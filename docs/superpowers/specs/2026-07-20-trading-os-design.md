# Trading OS — Design Document

> **Status:** Approved. The design-first hard gate was cleared on 2026-07-21. Implementation is governed
> by `docs/superpowers/plans/2026-07-21-trading-os-v1-implementation.md`.
> **Source of locked decisions:** `docs/research/RESEARCH-STATE.md` (D1–D30 + amendments D9a/D10a/D9b).
> Where this doc and the decision log disagree, the decision log wins and this doc is corrected.
> **Dates:** Created 2026-07-20. Last amended 2026-07-21 (F01–F20 adversarial review + HD-1..HD-8).

---

## 1. Purpose & scope

An autonomous **swing/positional** equity trading operating system spanning **two markets**:
India (NSE/BSE via **Zerodha Kite**) and the US (NYSE/NASDAQ via **Alpaca**). The end goal is
**fully autonomous live trading** in a controlled environment with **small disposable broker
balances**, reached by building and validating **paper-first** (a 90-day forward-paper gate).

**Honest naming (D9a):** what is actually being built is a **weekly/monthly factor-tilt portfolio
with a causal-KG event overlay**. The Tier-1 factors (12-1 momentum, trend/MA timing, quality
proxy) are statistically monthly-defined. The LLM decision path runs at the **slowest active
signal's cadence** (HD-6). Event triggers refresh labels/rationale for the next on-cadence
decision; they do NOT fire off-cadence trades.

**Out of scope (v1):** intraday (strictly excluded — daily-bar/EOD floor); IBKR (v2); alt-data
signal families; leverage, shorting, derivatives (also legally barred on the US sleeve).

### Success criteria (D10/D10a — all must clear before live capital)

Freeze and content-hash a `PromotionManifest` to the event log **before paper day 1** containing
all numeric bounds below. Promotion reads only the manifest's numbers — no post-hoc adjustment.

- Minimum decision count met (at monthly cadence, cross-sectional breadth compensates for low
  trade count — effective N = independent shock events, not raw stock×day cells)
- **Deflated Sharpe Ratio > 0** (N>1 trials, trial registry frozen in manifest)
- Max drawdown within tier-1 kill band
- Sim-vs-broker-paper tracking error within bound (validates `SimulatedBrokerAdapter`)
- Slippage/cost-model error within bound vs. real contract notes
- **Both the LLM path and the 3-factor rule-null beat buy-and-hold NIFTY/SPY net of cost**
- KG cross-sectional rank-correlation gate + **mandatory 2020-COVID and 2022-Russia/Ukraine
  historical replays** (a quiet paper window may contain no macro shock — replays are the only
  way to test KG quality)
- D9b N-threshold (N=30 per cell) frozen in the manifest

---

## 2. Core invariant (D4 + D30)

**"LLMs propose, deterministic code disposes."**

- A **slow LLM research path** (calendar-scheduled): cheap analysts gather →
  Mixture-of-Agents synthesizes a `ResearchTradeThesis` carrying **conviction + direction** —
  never a size, price, or quantity.
- A **fast deterministic hot path** (versioned, unit-tested Python, no LLM): sizing, VaR/CVaR,
  correlation, drawdown, gates, execution.
- **The seam (D30):** a deterministic projector converts `ResearchTradeThesis` → `HotPathCandidate
  {thesis_id (opaque), conviction_band (enum, gate/rank only), direction (enum)}`. `Sizer`
  accepts neither thesis type — only an admitted symbol + direction + deterministic inputs.
  `additionalProperties=false`, `extra='forbid'`, `frozen=True`, `allow_inf_nan=False`. Rationale
  and raw LLM JSON are structurally unreachable downstream. No number that determines size or
  price ever crosses from the LLM side — enforced by type, not convention.
- The **exposure vector** also crosses the seam, but it is produced by **deterministic
  `Traversal`** (code-owned weights from `EdgeWeightFitter`, not LLM scalars — see §3 Plane 2).
- Every LLM role is **model/provider-swappable via config** (`LLMRole.invoke(role, prompt,
  schema) → structured`). Cheap model gathers; MoA synthesizes/judges.

---

## 3. Architecture — three planes

No LangGraph. No continuous agent loop. Orchestration = **calendar-aware scheduled jobs** (D16):
EOD ingest, rebalance at the slowest-signal cadence, label-refresh event triggers (no off-cadence
trades), Kite token refresh, restart reconciliation. Signal clock (daily/EOD) and risk/kill clock
(second-level) are never merged.

**Plane 1 — Slow LLM research path.** Analysts (cheap model, `AnalystReport`) →
`MoASynthesizer` → `ResearchTradeThesis{conviction, direction, rationale}`. MoA here for live
decision research and offline (meta-analyst post-mortems, self-critique). In v2, an optional
`WebResearchSpoke` (D24) enriches this plane only (fail-open, provenance-logged).

**Plane 2 — Causal-KG plane** (Neo4j Community Edition, D14). Nodes: Company / Sector /
(MacroDriver+Commodity, merged) / Geography. Typed edges with provenance + deterministic
evidence-confidence + as-of dates. **Two-layer D4 split:**

*(1) Deterministic traversal:* rule-admissible motifs + anti-hub penalty + code-owned weights
(from `EdgeWeightFitter`, offline mini-GVAR, never from price correlation) × β^hops × γ^days
+ hard depth cap ≤3 → per-stock **exposure vector**.

*(2) LLM role:* `NewsMacroAnalyst` classifies news into `MacroEventLabel` — **closed categoricals
only:** `{driver, source∈{supply,demand,uncertainty}, phase∈{threat,act,escalation},
direction∈{+,−}}`. The LLM also picks **≤3-rung closed ordinals** for magnitude (`LOW/MED/HIGH`)
and confidence (`WEAK/MODERATE/STRONG`); code owns the weight each rung maps to (versioned,
unit-tested); rungs may only **tighten** exposure (raise defensive tilt / shrink allowed size),
never inflate it. No LLM-emitted scalar enters traversal arithmetic (D14 §⑤ amendment, HD-2).
`MetaAnalyst` proposes KG edges offline (D14a six-gate admission: ① human approval, ② 2nd
independent source before evidence-confidence >0.5, ③ mandatory text provenance, ④ ≥0.85
precision bar on ~200 labeled claims before Layer-1 admission, ⑤ `valid_from ≤ prediction_date`
+ `last_confirmed` + planted-future-edge unit test, ⑥ ~30%/yr auto-decay + mandatory deprecation).

**Job = risk/exposure engine first** (defensive tilt + beneficiary ranking), not a news-reaction
engine. EOD floor holds — captures ~30–60% of the cross-sectional differential over 1–3 days.

**Plane 3 — Fast deterministic hot path.** Gate/rank → sizing → risk → compliance → execution →
kill-switch. Reproducible given (HotPathCandidate, exposure_vector, portfolio_snapshot,
risk_config). No LLM call anywhere in this plane.

**Permanent parallel 3-factor rule-null (D11):** momentum + trend + regime (quality auto-enables
when the self-built PIT panel clears D20). `RuleNullJob` input set = `(ValidatedDataSnapshotId,
DeterministicSignalConfig, DeterministicPortfolioState)` only — type-level prohibition on all
LLM-derived inputs. Null uses fixed-fractional sizing only, never reads CalibrationStore.
LLM/MoA path earns capital only if it beats the null (and buy-and-hold) net of cost on post-cutoff
forward paper. All-LLM-down suspends only the LLM path; the null continues (HD-4).

---

## 4. Components (each an independently testable unit, D29)

Every external boundary is a **typed port** with an offline fake (D29). Pure hot-path units
(Sizer, RiskEngine, ComplianceGate, KillSwitch, Traversal, EdgeWeightFitter) need no port —
already data-in/data-out deterministic.

**Slow LLM research path:**
- `LLMRole` — `invoke(role, prompt, schema) → structured`; swappable per config.
- `Analyst` (cheap model) — context → `AnalystReport`.
- `NewsMacroAnalyst` — news → `MacroEventLabel` (closed categoricals + ≤3-rung ordinals).
- `MoASynthesizer` — cross-family → `ResearchTradeThesis{conviction, direction}` (no number).
- `SeamProjector` — deterministic projector → `HotPathCandidate` (closed, frozen, additionalProperties=false).
- `MetaAnalyst` (offline) — proposes KG edges → human-approval queue (D14a six gates).
- `WebResearchSpoke` (v2, D24) — allowlisted, fail-open, provenance-logged enrichment.

**Causal-KG plane:**
- `GraphStore` — Neo4j wrapper; nodes/edges with provenance + evidence-confidence + as-of dates.
- `Traversal` — deterministic exposure vector (motifs + anti-hub + code-owned weights + decay + depth cap).
- `EdgeWeightFitter` (offline) — fits weights from historical shock→return; never reads price correlation.

**Fast deterministic hot path:**
- `GateRank` — consumes `conviction_band` (gate/rank only); may demote/veto mature poorly-performing buckets (D5/D9b).
- `Sizer` — fixed-fractional × vol-target + caps → target quantities; reads no LLM-derived statistic.
- `RiskEngine` — INR-numeraire VaR/CVaR, cluster caps, exposure-vector tilt (tighten-only rungs).
- `ComplianceGate` — D19 rule set by lifecycle stage; rejects before submission.
- `ExitManager` — D18 layered exits + protection-coverage state machine + HITL veto queue.
- `BrokerAdapter` ABC (D6) + `Simulated` / `Kite` / `Alpaca` — durable `IntentId` + reconcile-before-retry.
- `KillSwitch` — ACTIVE/REDUCING/HALTED + per-symbol/market + durable generation/fencing token (D12/D26).
- `ProtectionSupervisor` — runs on risk clock; detects and repairs coverage deficits immediately (D25).

**Control/state plane:**
- `EventLog` (Postgres append-only, 14-event D15/D27) · `StateCache` (Valkey, projection-only)
- `Scheduler` (D16) · `SessionReadiness` · `CredentialReadiness` · `Watchdog`/dead-man (D22)
- `HITLBackend` (D17, HMAC, exposure-sign-dependent defaults) · `BrokerCashEventIngestor` (D16/D17)
- `CorporateActionMonitor` (D18/D20) · `CalibrationStore` (D9b, eval/monitoring + gate-rank in v1)
- `CorrectnessLayer` → emits `ValidatedDataSnapshotId` (D28)

---

## 5. Data flow — one EOD cycle

Triggered by `Scheduler` on a calendar-valid trading day after close, per sleeve. Every arrow
writes an immutable event to `EventLog` (D15) before the next stage reads it.

**Phase A — Session + credential readiness (fail-closed gates):**
1. `SessionReadiness` checks authoritative calendar + observed close. Unknown/ambiguous session
   (Muhurat timing unpublished, unscheduled closure, DST shift) → **FAIL-CLOSED**, cycle aborted.
2. `CredentialReadiness` verifies broker tokens. Kite `TokenException` → HALT new exposure +
   re-auth + reconcile; never auto-retried.

**Phase B — Ingest & correctness (deterministic, no LLM):**
3. `Scheduler` fires `eod.<sleeve>.<date>`; `Watchdog` heartbeat starts.
4. `DataIngest` pulls EOD OHLCV + CA feed + news + broker cash events
   (`BrokerCashEventIngestor` → dividends/withholding/fees/repatriations as durable events).
5. `CorrectnessLayer` emits a content-addressed **`ValidatedDataSnapshotId`** (D28) manifesting
   exact raw/split-adj/total-return OHLCV, CA/dividend/delisting ledger, PIT universe, calendar,
   news-cutoff, KG-edge version, FX rate set, enabled-signal manifest with quality=DISABLED until
   PIT panel clears. Any missing/stale/future-dated component → **FAIL-CLOSED**.

**Phase C — Slow research (LLM, no numbers):**
6. `NewsMacroAnalyst` → `MacroEventLabel` (closed categoricals + ≤3-rung ordinals, tighten-only).
   `Analyst`(s) → `AnalystReport`(s). `MoASynthesizer` → `ResearchTradeThesis{conviction,
   direction}`. No size, no price. Cached; skipped if already ran this cadence (D9a gate).
7. `Traversal` takes `MacroEventLabel` + offline-fitted graph → deterministic `exposure_vector`.
   (Deterministic code — the LLM produced only categorical labels in step 6.)

**Phase D — The seam:**
8. `SeamProjector` converts `ResearchTradeThesis` → `HotPathCandidate{thesis_id, conviction_band,
   direction}`. The `exposure_vector` from step 7 also crosses here. These two objects are the
   **only things that cross** the boundary. No LLM scalar crosses: `conviction_band` and
   `direction` are closed enums; the exposure_vector's every number is code-owned (EdgeWeightFitter
   + categorical-label→code-owned-weight mappings). Everything downstream is deterministic.

**Phase E — Fast deterministic decision (no LLM):**
9. `GateRank` — gates/ranks candidates using `conviction_band` + mature CalibrationStore learning
   (veto if consistently poor). Never scales size.
10. `Sizer` → target quantities (fixed-fractional × vol-target × caps; no CalibrationStore read).
11. `RiskEngine` → INR-numeraire VaR/cluster-caps/exposure-vector tilt; may shrink or veto.
12. `ComplianceGate` → D19 rule set per sleeve+stage; rejects illegal orders before submission.
13. `KillSwitch` state check → HALTED/REDUCING blocks new exposure.
14. **HITL gate (D17/HD-3):** exposure-INCREASING orders → APPROVAL required, default-no-trade on
    timeout. Exposure-REDUCING exits → VETO window, default-proceed at expiry. Approval binds to
    `(order_set_hash, snapshot_version, expiry)`; re-validates cash/risk/compliance/protection
    immediately before submit. Broker-side protective stops never HITL-gated.

**Phase F — Execution & protection:**
15. `BrokerAdapter.submit()` with durable `IntentId` (D26). On fill → `ExitManager` immediately
    places resting broker-side stop (Kite GTT OCO / Alpaca stop). `ProtectionSupervisor` tracks
    coverage state → SUBMITTED_UNCONFIRMED → PROTECTION_PENDING → PROTECTED.
16. Coverage deficit (partial fill, GTT cancel, CA-cancel, gap-through-unfilled) → symbol→REDUCING
    + immediate repair by `ProtectionSupervisor`; HALT never cancels a protective order.

**Phase G — Reconcile & persist:**
17. EOD reconciler verifies every open position has active stop coverage (backstop after
    `ProtectionSupervisor`). GTTs cancelled by CA>5% re-placed with CA-adjusted quantity.
18. `EventLog` seals the cycle. `StateCache` updated (projection only). `CalibrationStore` records
    `thesis→outcome` for closed positions (written once at episode close, D9b). `OrderReservation`
    released after confirmed commit.

**Two invariants this flow enforces:** (1) the seam at step 8 carries only `HotPathCandidate` +
`exposure_vector` — no LLM scalar; (2) every stage is an append-only event, so crash at any point
resumes from the log, never from in-memory state (Valkey is projection-only, D27).

---

## 6. Error handling & failure modes

Fail-direction is a **property of the failure class**, not a runtime judgment. Each row is a unit test.

| Failure | Direction | Behavior |
|---|---|---|
| Unknown/ambiguous session (Muhurat, DST, unscheduled closure) | **FAIL-CLOSED** | No EOD work; alert HITL (D16 SessionReadiness). |
| Kite TokenException on order/protection job | **FAIL-CLOSED for new exposure** | Re-auth + reconcile required; never auto-retry (D22 CredentialReadiness). |
| Phase-B data-quality flag (stale/future-dated/missing) | **FAIL-CLOSED** | No signal computed; cycle aborted (D20/D28). |
| `WebResearchSpoke` down/slow (v2) | **FAIL-OPEN** | Proceed on vetted feeds; log gap (D24). |
| One analyst / one MoA ref down | **CONTINUE degraded** | MoA proceeds on surviving refs; conviction capped + logged. |
| ALL LLM providers down | **SUSPEND LLM path only** | No new theses; null (D11) continues trading independently (HD-4). |
| Broker disconnect >N s | **FAIL-CLOSED → REDUCING/HALTED** | Kill-switch trips (D12); broker-side stops remain safety net. |
| Protection-coverage deficit (GTT cancelled/rejected/unfilled, partial fill growth) | **FAIL-CLOSED for new exposure; symbol→REDUCING** | `ProtectionSupervisor` repairs or liquidates; no deferred EOD (D25/F04). |
| Reconciliation mismatch | **FAIL-CLOSED** | HALT; surface to HITL; never trade against uncertain position (D26). |
| HITL timeout, exposure-INCREASING | **FAIL-CLOSED** | Default-no-trade; order expires (D17/HD-3). |
| HITL timeout, exposure-REDUCING exit | **FAIL-OPEN (proceed)** | Default-proceed; human may veto in window (D17/HD-3). |
| Ambiguous fill / lost ACK | **OUTCOME_UNKNOWN** | Block related exposure; reconcile-before-retry; never blind-retry (D26). |
| Stale worker after HALT/restart | **FENCED** | Rejected by submission gate (stale generation token, D22/D26). |
| Reservation stale (snapshot version advanced) | **REJECTED** | Recompute against current version (D27). |
| Main loop silent (watchdog dead-man) | **FAIL-CLOSED** | HALT + alert; localhost re-auth to lift (D22). |

**Kill-switch tiers (D12/D23):** ACTIVE → soft-alert (−8%) → REDUCING (−15%) → HALTED (−25%)
drawdown bands + vol-percentile bands; thresholds frozen in PromotionManifest. **HALT is
asymmetric (D22):** Telegram may HALT; only localhost dashboard with re-auth may lift. HALT never
cancels protective orders.

**Crash recovery (D15/D27):** append-only log → crash resumes by replaying durable events (14
exit-policy events cover full exit state, not just quantity). Reconciliation runs first on restart:
rebuild from log, diff against live broker; disagreement → FAIL-CLOSED.

**Irreducible residual windows (stated honestly, not hidden):** (1) submit→first-confirm (bounded
by fast reconcile + IntentId lookup); (2) fill→stop-active (Alpaca bracket shrinks it; Kite
separate GTT call is wider; never zero); (3) broker/OMS-down (no resting stops survive broker
death); (4) Kite fire-once EOD gap (triggered-but-unfilled GTT is gone at close; `ProtectionSupervisor`
re-places, but requires a live process).

---

## 7. Compliance & legal invariants (D19)

Organized by lifecycle stage. A deterministic `ComplianceGate` blocks every violating order
**before submission**.

**India pre-order (every order, before submit):**
- Egress IP ∈ static whitelist (in force from **2026-04-01**; non-order APIs exempt)
- Order carries **broker-provisioned exchange-issued algo-ID tag** (generic ID for below-TOPS
  algos, issued by exchange via Zerodha — never self-minted)
- OPS throttle ≤~2/s (hard under 10/exch/seg)
- Account ∈ {own + immediate-family} allowlist; strategy never shared/sold
- CNC sell qty ≤ settled demat holding (long-delivery-only)
- Per-signal minimum-cadence gate (D9a)

**India pre-live setup (hard blockers, one-time):**
CDSL DDPI active · static IP provisioned (≤2, 1 change/wk) · OAuth/2FA + daily logout · 5-yr audit trail

**US pre-order:**
- Cash-account-only + settled-cash-only
- Whitelist = long common stock + >50%-equity, non-leveraged, non-inverse, non-commodity,
  non-synthetic ETFs
- REJECT: margin / short / derivative / leveraged-inverse-ETF / FX / crypto /
  Indian-issuer ADR / Indian-company security listed abroad

**Pre-remittance gate** (separate from pre-trade, D19):
- Requires current PAN-wide FY LRS utilisation across ALL banks/purposes (AD-bank statement or
  signed remitter attestation); **fail-closed on unknown/stale**
- LRS meter = gross FX remitted; TCS + bank spread as separate lines
- Hard-stop before USD 250k/FY (PAN-aggregate); soft-warn at ₹10L (TCS 20%); 80% soft-warn
- Repatriation NEVER resets FY meter; Alpaca account purchases don't consume additional cap
- S0001 purpose code; designated AD bank + Form A2

**Idle-FX `IdleFxLot` watchdog (D19/D21):**
- Clock per realized-FX credit (remittance remainder/sale proceeds/dividend/refund), not per wire
- Alert day 150; trigger disposition action ~day 175; terminal action = reinvest-into-OPI or
  repatriate with confirmed broker/bank disposition before day 180
- FDIC/MMF sweep treated as **idle** until written FEMA-CA opinion says otherwise
- Repatriation treated as **manual** until a tested automated path is confirmed

**Post-event/reporting:** Form 67 (before ITR deadline) · Schedule FA calendar-year snapshot ·
Rule-115 SBI TTBR (last day of prior month, holiday fallback defined) · 24-month LTCG boundary ·
no US wash-sale on India books · ITR-2 + FSI/TR/OS/CG/Form-67 pack

**Verify-before-live hard blockers (must all clear before real capital):**
1. Primary Finance Act §206C(1G)/IT-Act-2025 §506 confirming TCS ₹10L/20% + LTCG dates
2. Written Alpaca confirmation of cash/no-margin account + India-resident onboarding legality
3. Written FEMA-CA opinion: (a) Alpaca FDIC sweep ≠ "reinvested"?  (b) can repatriation be automated?
4. CA + US cross-border opinion: trade frequency/profile stays "investment," not business-income
5. Zerodha SOP: below-TOPS exchange registration + tag-provisioning path

---

## 8. Data & state

**Data plane (D13):** TimescaleDB (OHLCV) + Postgres (fundamentals + LLM outputs JSONB) + Valkey
(hot state). All open-source, no license fees.

**Data correctness (D20/D28):** `ValidatedDataSnapshotId` boundary — every signal/traversal/sim
reads only from a sealed snapshot, never `latest`. Independent CA factor ledger; three OHLCV
series (raw / split-adj / total-return) with per-factor bindings; survivorship-free PIT universe
(India NIFTY 500; US PIT-membership list, not static); independent US CA/delisting source.
Self-built PIT fundamentals panel (weekly snapshots from day 1, conservative lags): quality proxy
auto-enables once the panel has sufficient validated history (D20/HD-5).

**Portfolio state (D15/D27):** Postgres append-only event log (14 exit-policy events, intention-
truth) + Valkey rebuildable projection (custody-truth = broker). Reconciliation appends observed
events; never rewrites history. Global versioned portfolio snapshot + CAS `OrderReservation`
before every commit (D27).

**Two-currency accounting (D21):** fixed-point decimal; four date fields per event; immutable
native fills + immutable rate records; all corrections and cash events as separate append-only
events. Equity P&L anchored at held-constant entry rate; realized-FX gain = sole currency-move
line; RiskEngine live-rate = risk projection only, never summed into accounting ledger. LRS meter
= gross FX remitted (Form A2; Rule 115).

**HITL (D17):** Telegram (approve/reject, /emergencysell→HALTED) + localhost dashboard, one
HMAC-signed-token backend. Localhost-only, never internet-exposed. Exposure-sign-dependent
defaults (entries=approval/no-trade; exits=veto/proceed). Approval bound to
`(order_set_hash, snapshot_version, expiry)`; re-validates before submit.

**Ops & survivability (D22):** always-on host + watchdog + dead-man HALT + asymmetric lift
(Telegram HALT only; localhost re-auth to un-HALT) + durable kill-switch generation/fencing
token + nightly Postgres backup + structured JSON logs + Telegram alerts + CredentialReadiness
(Kite re-auth ≥07:30 IST, never auto-retry TokenException).

---

## 9. Sizing & risk

- **Fixed-fractional (1–2% account risk) × vol-target + hard per-position & per-correlation-
  cluster caps (D5).** `Sizer` reads no LLM-derived statistic.
- **Gate/rank (D5/D9b):** `conviction_band` gates trade/no-trade and ranks candidates. Mature
  calibration buckets (N≥30) may demote/veto via gate/rank. Never scales size.
- **No live Kelly ceiling in v1 (HD-1):** CalibrationStore is eval/monitoring only for sizing
  until a bucket is demonstrated to be a calibrated probability.
- Exits (D18/D25): broker-side resting stop on fill (protection-coverage state machine) +
  chandelier/ATR trailing + time-stop + regime-flip; all deterministic; the LLM never decides
  an exit; exit review = veto (default-proceed on reviewer silence, HD-3).

---

## 10. Testing strategy (D29)

**Typed-port / offline-fake boundary (D29, 13 ports):** ClockPort · CalendarPort ·
MarketDataPort/CAPort · FxRatePort · SecurityMasterPort · GraphStorePort · EventStorePort ·
StateCachePort · BrokerTransportPort · LLMRolePort · SecretsPort/CredentialReadiness ·
HITLTransportPort · NotifierPort.

**Pure hot-path units** (Sizer, RiskEngine, ComplianceGate, KillSwitch, Traversal,
EdgeWeightFitter) need no port — already data-in/data-out deterministic.

**Two test classes:**
1. **Pure contract/mapping tests** (fakes + recorded fixtures, CI, no credentials): D6 ABC
   (idempotent submit, reconcile round-trip, honest `capabilities()`); every §6 fail-direction
   row; ack-loss; duplicate scheduler fires; partial + later-partial fills; GTT
   reject/expire/gap-through-no-fill; CA replacement; token expiry; stale FX; DST/holiday edges;
   extra-LLM-field rejection (prompt-injection: `target_vol`/`stop_hint`/`size_pct` rejected at
   seam, D30); stale-worker fencing.
2. **Credentialed smoke tests** (minimal, opt-in, separately tagged, never in CI for live orders).

**Kite-no-sandbox rule (D29):** Kite adapter behavior proven on Simulated + Alpaca-paper +
recorded-Kite fixtures. **CI never places a live Kite order.** Live-order wire-fidelity = human-
gated, read-only-plus-manual, disposable-balance, out-of-band step.

**Sim fidelity gate (D10a):** sim-vs-broker-paper tracking error within bound — a promotion
blocker. Slippage/cost-model error within bound vs. real contract notes.

**Evaluation gate (D10/D10a):** CPCV + DSR (N>1, trial registry frozen) + post-cutoff forward-
paper + frozen configs/prompt-hash/model-ID + three-way scoreboard (LLM vs 3-factor null vs
index) with separate `StrategyBook`s in Sim + KG cross-sectional rank-correlation + mandatory
2020/2022 historical replays + pre-frozen PromotionManifest.

**Replay & recovery tests:** kill process at each event boundary → assert log-replay resumes to
identical state; assert reconciliation FAIL-CLOSES on injected broker/log divergence.

**Not tested for correctness:** LLM thesis accuracy (unknowable). CalibrationStore measures it
empirically over time. We test that the LLM is *contained* (no number crosses the seam), not
that it is *right*.

---

## 11. Phasing

**v1:** Zerodha + Alpaca; vetted-feeds-only research; factor-tilt + causal-KG overlay;
3-factor null (quality auto-enables when self-built PIT panel clears); full paper-first gate
with pre-frozen PromotionManifest; CalibrationStore eval/monitoring + gate-rank only.

**v2:** IBKR adapter (after resolving LRS/entity route); `WebResearchSpoke` (D24); auto-add-
above-threshold KG edges once edge-precision measured on held-out set (D14a); conviction-keyed
Kelly ceiling once a bucket is demonstrated to be a calibrated probability (HD-1); expanded
signal families as they earn their place on forward paper.

---

## Appendix — decision index

Full text for every decision (D1–D30 + amendments D9a/D10a/D9b) lives in
`docs/research/RESEARCH-STATE.md`. This document is the narrative design; the decision log is
the authoritative record.
