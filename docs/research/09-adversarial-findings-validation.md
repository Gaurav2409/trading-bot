# 09 — Adversarial Findings Validation (F01–F20): Executive Synthesis

> **Status:** Research validation complete. No implementation. This synthesizes six evidence-first
> research streams (09a–09f) that validated the 20 findings in
> `docs/research/08-adversarial-design-review-research-brief.md` against **current primary sources**
> (broker API docs, RBI/SEBI/NSE/CBDT/IRS text) and by numeric seam-tracing.
> **Date:** 2026-07-20.
> **Spec under review:** `docs/superpowers/specs/2026-07-20-trading-os-design.md`.
> **Authoritative decisions:** `docs/research/RESEARCH-STATE.md`.
> **Sub-reports:** 09a (broker-protection F03/F04/F08), 09b (FEMA/LRS F05/F06/F12-US/F13-legal),
> 09c (India-mechanics F12-IN/F17-IN), 09d (seam type-safety F01/F02/F10/F18),
> 09e (event-sourcing/recovery F07/F09/F14/F15/F16/F17), 09f (data-snapshot/testability F11/F13/F19/F20).

---

## A. Executive verdict

**The spec is NOT safe to approve as written.** All 20 findings are validated:

- **CONFIRMED as stated:** F01, F02, F05, F06, F07, F09, F10, F11, F13-det, F14, F16, F17, F18, F19, F20.
- **CONFIRMED WITH MODIFICATION** (finding right, wording sharpened by primary evidence): F03, F04, F08, F12, F13-legal, F15.
- **NOT-SUPPORTED:** none.

**Counts after research:** 8 blockers (F01–F08), 12 majors (F09–F20).

**Two factual errors in the authoritative decision log were surfaced by primary sources** (neither was in the brief):
1. **Static-IP effective date** — D19/spec §7 say "since 2025-04-01"; current Zerodha FAQ says **2026-04-01** (09c).
2. **Algo-ID mechanics** — the tag is **exchange-issued via the broker**, mandatory on *every* order incl. below-TOPS (generic ID); D19's "unique algo-ID tagging" is imprecise (09c, NSE circular INVG67858 retrieved in full).

**Fixable now vs. needs your decision.** Findings split cleanly:
- **Directly fixable** (spec + decision-log edits I can apply): F03, F04, F08, F10, F11, F12, F13, F14, F15, F17, F18, F19, F20, plus the two factual corrections.
- **Human-decision-gated** (8 conflicts the brief flagged; I will grill these one at a time): HD-1…HD-8 below.

---

## B. Findings table (F01–F20)

| F | Verdict | Sev | Touches (spec / Dxx) | Primary evidence / trace | Smallest seam-safe edit | D-log change? | Human decision? |
|---|---|---|---|---|---|---|---|
| **F01** conviction→Kelly | CONFIRMED | Blocker | §9; D4/D5/D9b | Identical candidates, HIGH vs MED bucket → `f*_H>f*_M` → `ceiling_H>ceiling_M` → `qty_H>qty_M` when ceiling binds. LLM ordinal alters qty *indirectly* (09d §1a). | CalibrationStore **evaluation-only in v1**; Sizer/Risk/Exit/Compliance/KillSwitch read no statistic keyed by model/prompt/conviction/thesis. | **Yes — D5 + D9b** | **HD-1** |
| **F02** LLM KG magnitude/confidence→exposure | CONFIRMED | Blocker | §3/§5; D4/D14/D14a | `exposure=Π(edge_conf)·β^hops·γ^days·w(m_llm)` monotone in LLM `c_llm,m_llm` → exposure vector → risk tilt (09d §1b). | `MacroEventLabel`=closed categoricals only (driver/source/phase/direction); `EdgeProposal`=endpoints+relation+citations only; deterministic evidence-confidence policy; `EdgeWeightFitter` sole numeric source; magnitude ≤3 fixed rungs→code weights. | **Yes — D14 §⑤ + D14a** (if fields were LLM numbers) | **HD-2** |
| **F03** broker-protection guarantee false | CONFIRMED | Blocker | §5/§6; D6/D12/D18/D22 | Kite: "placement does not guarantee receipt/execution"; no atomic fill→GTT. Alpaca bracket stop "not active until first order completely filled" (09a K1-3, A8). | Protection-coverage state machine (`SUBMITTED_UNCONFIRMED`→`PARTIALLY_FILLED_UNPROTECTED`→`PROTECTION_PENDING`→`PROTECTED`); PROTECTED iff broker-confirmed exit qty ≥ reconciled position qty; deficit blocks new exposure; deadline→controlled-liquidate or `HALTED_UNVERIFIED`. | **Yes — D18/D22** (condition the guarantee); **D12** (coverage-deficit→REDUCING) | no |
| **F04** GTT fail-direction wrong | CONFIRMED-W-MOD | Blocker | §5/§6; D12/D18/D20 | Kite GTT can be `triggered` yet embedded limit `rejected` (circuit) — firing≠protection; fire-once/DAY/CA-cancel (09a K9-11). | Coverage deficit → **fail-closed for exposure increase**, symbol→REDUCING; **risk-clock `ProtectionSupervisor`** detects cancel/reject/expire/unfilled-trigger/partial-fill-growth *immediately*; EOD=backstop; HALTED never cancels a protective order except during confirmed replace; treat triggered-but-unfilled as first-class unprotected; prefer two-leg (OCO) GTT. | **Yes — D18 §6 rows; D12/D16** (ProtectionSupervisor on risk clock) | no |
| **F05** 180-day watchdog can't prevent breach | CONFIRMED | Blocker | §7; D19 | RBI FAQ Q4 (primary): clock per realized-FX credit; only reinvest-or-repatriate cures; block-new-buys never reaches compliant terminal state. Alpaca sweep = "uninvested cash" → likely NOT a cure (09b). | `IdleFxLot` per remittance-remainder/sale/dividend/refund w/ origin/value-date/deadline/disposition; terminal action = reinvest-or-repatriate w/ broker/bank-confirmed disposition; treat sweep as idle; if no tested auto-repatriation → verified manual, else US sleeve can't go live. | **Yes — D19 amend + D21 schema add** | **HD-8** (sweep-as-cure + auto-repat = pre-live legal blockers) |
| **F06** local ledger can't enforce PAN cap | CONFIRMED | Blocker | §7/§8; D19/D21 | RBI FAQ Q1/Q7/Q8 (primary): USD 250k/FY PAN-aggregate all-banks/all-purposes, no reset on repatriation; meter = outbound wire (09b). | Split `PreRemittanceGate` from `PreTradeGate`; pre-remittance requires current PAN-wide utilisation (AD-bank statement or signed attestation), **fail-closed** on unknown/stale; repatriation never decrements; settled-cash purchases don't consume cap; S0001 + designated AD + Form A2. | **Yes — D19 add external-state/fail-closed; D21 label local meter a lower bound** | no |
| **F07** HITL ordering unsafe | CONFIRMED | Blocker | §5/§9; D17/D18/D22 | §5 numbers submit@11, review@12 (prose contradicts). Default-no-trade suppresses a time-stop/regime exit when reviewer asleep → retains risk (09e). | Move approval gate between step 10 and submit; bind approval to `(order_set_hash, snapshot_version, expiry)`; re-validate after approval; **default-no-trade for exposure-INCREASING only, proceed for exposure-REDUCING**; broker-side stops never HITL-gated. | **Yes — D17/D18** | **HD-3** (exit review = approval/veto/notification?) |
| **F08** append-only ≠ idempotent | CONFIRMED-W-MOD | Blocker | §5/§6/§10; D6/D15/D16/D18 | **Kite has NO idempotency key** (tag non-unique, 1-call-2-orders documented). **Alpaca client_order_id** rejects dup only for *active* order (422), not replay-idempotent (09a K4-6, A3). | Durable client-side `IntentId` + **reconcile-before-retry**; unknown outcome→`OUTCOME_UNKNOWN`, block related exposure, never blind-retry; `capabilities().has_native_client_order_id`; durable **kill-switch generation/fencing token** so stale workers can't submit post-HALT; contract test: no duplicate economic effect under ack loss. | **Yes — D6 (spell out IntentId+reconcile+cap flag); D15 (intention-truth vs custody-truth); D12/D22 (fencing token)** | no |
| **F09** all-LLM-down conflict + null independence | CONFIRMED | Major | §3/§6; D11/D12/D20 | D12 lists all-LLM-down as HALT trigger; §6 says null keeps trading — contradiction. Null's independence unproven (hidden deps: calibration, KG exposure vector, LLM-curated universe) (09e). | Define `RuleNullJob` input set = `(ValidatedDataSnapshotId, DeterministicSignalConfig, DeterministicPortfolioState)` only; type-level prohibition on thesis/report/KG/calibration/LLM-health; pin to PIT universe; LLM failure suspends LLM strategy only (iff null provably independent). | **Yes — reconcile §6 vs D12; D11 composite vs D20** | **HD-4** (D11-vs-D12), **HD-5** (D11-vs-D20) |
| **F10** seam not encoded by interfaces | CONFIRMED | Major | §3/§5; D4 | `TradeThesis{…,rationale}` + JSONB is permissive; nothing blocks `target_vol`/`stop_hint` or rationale-parsing (09d §2). | `ResearchTradeThesis` stays Plane 1; deterministic projector→`HotPathCandidate{thesis_id,conviction_band,direction}`, `additionalProperties=false`, `extra='forbid'`, closed enums, all-required, `frozen`, `allow_inf_nan=False`; Sizer accepts neither thesis type; rationale/JSON structurally unreachable. | **No** — spec/interface only (1-line clarifying note) | no |
| **F11** no immutable snapshot boundary; US under-specified | CONFIRMED | Major | §5/§8; D20 | Late CA revision mutates `latest` after gate passes → replay diverges. US = static "defined list" → no PIT membership/delisting/independent CA (09f). | Phase A emits content-addressed `ValidatedDataSnapshotId` (raw/split-adj/total-return OHLCV + CA/dividend/delisting ledger + PIT universe + calendar + news-cutoff + KG-edge version + FX set + enabled-signal manifest w/ per-factor series binding); every consumer requires the token, cannot read `latest`; add independent **US** CA/delisting/PIT-membership source. | **Yes — D20 amend** | no |
| **F12** compliance incomplete + mixes stages | CONFIRMED-W-MOD | Major | §7; D19 | India: static-IP date wrong (2026 not 2025); algo-ID exchange-issued+mandatory-below-TOPS; own/family + long-delivery gates. US: Indian-issuer ADR + leveraged/synthetic ETF exclusions must be explicit (09b/09c). | Organize D19 by stage (pre-remittance / pre-order / post-fill / periodic / verify-before-live); name Indian-issuer exclusion + precise ETF def; correct static-IP date; algo-ID = broker-provisioned exchange ID; add own+family allowlist + CNC-sell≤settled-holding gates. | **Yes — D19 restructure + 2 corrections** | (HD-7 = below-TOPS registration = pre-live broker-SOP check, not a design decision) |
| **F13** two-currency accounting not deterministic | CONFIRMED-W-MOD | Major | §8; D21 | Float non-associativity + in-place fill updates + holiday-missing Rule-115 rate + omitted cash events → replay diverges; equity mark-to-INR + separate realized-FX line double-count same FX move (09f). Legal: gross-basis LRS meter; **Form A2** not 15CA/CB; **Rule 115** not 115A (09b). | Fixed-point money; 4 separate date fields; immutable native fills + immutable rate records; FX-obs/corrections/cash-events as append-only events referencing rate ids; rate source/direction/holiday-fallback/rounding/stale policy; FX-lot method; **equity P&L at anchor rate vs realized-FX-only line vs risk-view live rate — never summed**; round-then-rerun; LRS meter = gross w/ TCS+spread separate; cite Rule 115 + Form A2. | **Yes — D21 amend (det + legal)** | no |
| **F14** exit/recovery state not reconstructable | CONFIRMED | Major | §5/§6; D15/D18 | ATR-trail/entry-regime/time-stop/GTT-id/approval-expiry live in memory/Valkey → restart recovers qty, loses exit policy (09e T-F14). | 14 durable events (episode/fill-alloc/stop-intent+ack/coverage/trail-ratchet/time-stop/entry-regime/approval/reservation/attribution/FX-lot/idle-FX-lot/calibration/killswitch-gen); Valkey projection-only; calibration keyed by `position_episode_id`, written once at close. | **Yes — D15 enumerate exit-policy events + intention/custody split; D18 durable-events** | no |
| **F15** async sleeves overspend global risk | CONFIRMED-W-MOD | Major | §5/§8; D5/D15/D16/D21 | Two async sleeve jobs read same snapshot, each spends 0.9R → 1.8R breach (09e T-F15). | Versioned **global** snapshot (both sleeves + open/pending orders + unsettled cash + protection deficits + live FX); durable `OrderReservation` via **CAS / single-writer commit gate** before submit; stale-version→reject+recompute. One mechanism serves F07/F08/F15. | **Yes — D16 (risk/cash commit globally serialized); D5/D21 (reservation)** | no |
| **F16** null-vs-LLM attribution undefined | CONFIRMED | Major | §1/§3; D10/D10a/D11 | Both paths buy same symbol → one net position + one stop → per-strategy P&L undefined → three-way scoreboard invalid (09e T-F16). | Separate immutable `StrategyBook`s + budgets; fully separated in Sim/paper for v1 scoreboard (it's a paper-gate metric); live-netting allocation rule = design-now/build-later; aggregate risk across all books. | **Yes — D10a/D11 (per-book separation); D16/D9a (event-trigger cadence)** | **HD-6** (D9a-vs-D16 event-trigger cadence) |
| **F17** session/credential/cash-event flows missing | CONFIRMED | Major | §3/§5; D16/D19/D21/D22 | DST/Muhurat/unscheduled-close → EOD runs pre-close; Kite TokenException while CA cancels a GTT → silent unprotected; US dividend → untracked idle USD (09c/09e). | Add `SessionReadiness` (authoritative calendar + observed close, unknown→fail-closed), `CredentialReadiness` (before every order/protection job; TokenException→re-auth+reconcile, never auto-retry), `BrokerCashEventIngestor` (dividends/withholding/interest/fees/reversals/repatriations/cash-in-lieu → durable events → accounting/idle-FX/Schedule-FA/Form-67). | **Yes — D16 (SessionReadiness first gate); D22/D12 (CredentialReadiness); D21/D19 (cash-event ingest)** | no |
| **F18** D14a admission gates dropped from spec | CONFIRMED | Major | §3/§4/§11; D14a | Gates ②(2nd-source>0.5), ③(provenance-blocks-traversal), ④(0.85 precision bar mis-scoped as v2), ⑥(30%/yr decay+deprecation) dropped from narrative; ⑤ half-present (09d §4). | Restore all six D14a gates into §3/§4/§11 verbatim; restore ② with F02's *deterministic* confidence reading. | **No** — D14a intact; spec-only restoration | no |
| **F19** promotion thresholds undefined; KG validation omitted | CONFIRMED | Major | §1/§10; D9b/D10a/D14 | Every D10a bound is an unfilled "within bound" → post-hoc p-hacking; quiet quarter → KG never tested; naive DSR under-deflated (N under-reported) + inflated sample (dependent cross-sectional cells) (09f). | Pre-paper hashed `PromotionManifest` (bounds + trial registry + costs + windows + cross-sectional sample def + benchmarks + D9b N); restore D14 cross-sectional rank-correlation + mandatory 2020/2022 replays into spec; effective-N = independent-shock clustering for both DSR terms. | **Yes — D10a amend; D9b state N; restore D14 into spec** | (HD-... D9b N-value chosen during grill) |
| **F20** testability asserted not designed | CONFIRMED | Major | §4/§10; D3/D6/D10/D15 | CorporateActionMonitor→live Kite, GraphStore→Neo4j, contract suite→live Kite orders (no sandbox) (09f). | Typed port + offline fake per boundary (13 ports); pure contract/mapping tests (fakes+fixtures, CI, no creds) vs credentialed smoke; **Kite behavior proven on Simulated + Alpaca-paper + recorded-Kite fixtures; CI never places a live Kite order**; live-order wire-fidelity = human-gated/read-only/disposable/out-of-band. | **No** — spec §4/§10 build-out | no |

---

## C. Broker protection state/race summary (09a)

Kite GTT and Alpaca stops are both **broker-resident** and survive client/host death — but only for a
*pre-existing, active, fully-covering, unexpired* stop *while the broker is up*. Irreducible residual
windows (cannot be eliminated, only bounded + detected): (1) submit→first-confirm; (2) fill→stop-active
(no atomic primitive on either broker; Alpaca bracket shrinks it); (3) broker/OMS-down; (4) Kite
fire-once EOD gap. Everything else (partial-fill growth, CA cancel, token expiry, HALT/fill race,
restart) is detectable+repairable by a risk-clock `ProtectionSupervisor` + reconcile-before-retry.
**Key correction:** neither broker offers a Stripe-style idempotency key — Kite has none, Alpaca's is
active-scoped duplicate-prevention — so the durable client-side `IntentId` + reconcile-first is the
load-bearing mechanism.

## D. Compliance matrix (09b/09c) — labels: PRIMARY / SECONDARY / INFERENCE / OPEN

- **Pre-remittance (PRIMARY):** USD 250k/FY PAN-aggregate all-banks/all-purposes; no reset on
  repatriation; meter = outbound wire (gross, TCS+spread separate); S0001 code; designated AD + Form A2;
  TCS 20%>₹10L. **INFERENCE:** external-state/attestation + fail-closed (local ledger is a lower bound).
- **Idle-FX 180-day (PRIMARY):** reinvest-or-repatriate within 180d, clock per realized-FX credit;
  reinvestment cures. **INFERENCE:** block-new-buys ≠ cure. **OPEN:** FDIC/MMF sweep as cure (evidence
  leans NO); autonomous repatriation feasibility (likely manual). → **pre-live legal blockers.**
- **US pre-order (PRIMARY/near-primary):** long/cash/settled only; reject margin/short/derivative/FX/
  crypto/leveraged-inverse/commodity/synthetic ETF; reject Indian-issuer ADRs; ETF must be >50% equity.
- **India pre-order (PRIMARY):** egress-IP ∈ static whitelist (in force **2026-04-01**, non-order APIs
  exempt); broker-provisioned **exchange-issued** algo-ID on every order; OPS≤~2 (hard <10/exch/seg);
  account ∈ {own+family}, strategy never shared/sold; CNC-sell ≤ settled demat holding; LIMIT+protection.
- **India pre-live setup (PRIMARY):** CDSL **DDPI active**; static IP provisioned (≤2, 1 change/wk);
  OAuth/2FA + daily logout; 5-yr audit trail. **OPEN:** below-TOPS generic-ID registration requirement
  (NSE §B.3 vs operational practice) → broker-SOP check.
- **Periodic/session (PRIMARY):** SessionReadiness fail-closed on unknown session (Muhurat timings from
  same-day circular); CredentialReadiness re-auth after ~07:30 IST flush, TokenException never
  auto-retried; daily GTT integrity reconcile.
- **Reporting (PRIMARY):** Schedule FA calendar-year snapshot; Form 67; W-8BEN 25% DTAA; Rule 115
  (SBI TTBR last-prior-month, holiday fallback); 24-mo LTCG; no US wash-sale on India books.

## E. Seam audit (09d) — what may cross slow→fast

Exactly two objects cross (post-fix): `HotPathCandidate{thesis_id (opaque), conviction_band (enum,
gate/rank only), direction (enum)}` and `exposure_vector[symbol]` (float, from **deterministic**
Traversal whose every input is code-owned or a categorical-label→code-owned-weight after F02).
**Structurally unreachable downstream:** rationale, raw LLM JSON, any LLM magnitude/confidence scalar,
target_vol/stop_hint/size_pct, any calibration statistic keyed by model/prompt/conviction/thesis (F01),
nested extras{}, non-finite numbers. The ∂=0 proof (perturbing any disallowed LLM field cannot change
quantity/price/exits/risk/compliance) **holds only if F01+F02+F10+F18 all land together**.

## F. Corrected fail-direction table (09a/09e) — deltas from spec §6

| Situation | Corrected direction |
|---|---|
| HITL timeout, exposure-INCREASING | FAIL-CLOSED (unchanged) |
| HITL timeout, exposure-REDUCING exit | **proceed** (human may veto in window) — pending HD-3 |
| Broker-side protective stop placement | **never HITL-gated** (the safety net) |
| ALL LLM providers down | suspend LLM strategy only, null continues **iff** null proven independent; else HALT — pending HD-4 |
| HALTED | **must NOT cancel a protective order** except during confirmed replace; exits/stops stay operational |
| REDUCING | exits/stops fully operational; only exposure-increasing blocked |
| Protection-coverage deficit | FAIL-CLOSED for increases; symbol→REDUCING; repair or controlled-liquidate |
| Ambiguous fill / lost ACK | `OUTCOME_UNKNOWN` → block related exposure → reconcile-before-retry; never blind-retry |
| Stale worker after HALT/restart | fenced by monotonic generation token |
| Unknown/misclassified session | FAIL-CLOSED (no EOD work) |
| Kite TokenException on order/protection job | FAIL-CLOSED for new exposure; re-auth+reconcile; never auto-retry |
| Reservation stale (snapshot advanced) | reject reservation; recompute |

---

## G. Ranked top-5 changes (most valuable first)

1. **Close the D4 seam by construction** — remove conviction-keyed Kelly (F01/HD-1); strip LLM
   magnitude/confidence from KG (F02/HD-2); two-type `HotPathCandidate` projection (F10); restore D14a
   gates (F18). Together they make D4 a type property, not a promise.
2. **Replace the false always-protected guarantee** with a broker-confirmed protection-coverage state
   machine + risk-clock `ProtectionSupervisor` (F03/F04); fail-closed on coverage deficit.
3. **Make every broker side-effect crash-safe** — durable `IntentId` + reconcile-before-retry +
   fencing token; append-only ≠ idempotent (F08). Neither broker gives a real idempotency key.
4. **Make FEMA/LRS operationally enforceable** — per-lot reinvest-or-repatriate idle-FX (F05),
   PAN-wide pre-remittance gate with external state + fail-closed (F06). Two pre-live legal blockers.
5. **Freeze the ruler before the measurement** — pre-paper hashed `PromotionManifest` + restored KG
   cross-sectional/replay validation + effective-N accounting (F19); content-addressed
   `ValidatedDataSnapshot` so signals never read mutated `latest` (F11).

---

## H. Human decisions required (do NOT resolve silently — grill one at a time)

| # | Conflict | The question |
|---|---|---|
| **HD-1** | D4 vs D5/D9b | May a mature, empirically-calibrated per-conviction-bucket statistic feed a live ¼-Kelly ceiling, or is the bucket key "LLM-derived" and barred from altering quantity? (F01 fix = eval-only store.) |
| **HD-2** | D4 vs D14/D14a | Were `MacroEvent.magnitude`, `MacroEvent.confidence`, and edge `confidence` meant to be LLM-supplied numbers feeding traversal (leak → must strike them) or always deterministic/code-owned (clarify only)? |
| **HD-3** | D17 vs D18 | Is exit review an **approval**, a **veto**, or a **notification**? (Approval + default-no-trade suppresses risk-reducing exits.) |
| **HD-4** | D11 vs D12 | Does "all LLM providers down" **HALT the market** (D12 trigger list) or **suspend only the LLM strategy** while the null continues (§6/D11)? |
| **HD-5** | D11 vs D20 | The null's Tier-1 composite includes a quality proxy that D20 **disables** until PIT fundamentals exist. Run a 3-factor null (re-baseline the scoreboard) or gate go-live on sourcing PIT fundamentals? |
| **HD-6** | D9a vs D16 | May **event triggers** move the LLM decision/trade path off the slowest-signal cadence (violating D9a's horizon), or may they only refresh labels/rationale for the next on-cadence decision? |
| **HD-7** | D9b N-threshold | The decision log requires a calibration maturity N-threshold but does not specify one. What N? (Also gates whether HD-1's ceiling could ever mature.) |
| **HD-8** | FEMA legal (F05) | Two pre-live legal blockers: (a) does an Alpaca FDIC/MMF cash sweep count as "reinvested" under RBI FAQ Q4 (evidence → NO)? (b) can Alpaca→AD-bank repatriation be automated+tested, or must it be manual (US sleeve gated behind verified manual repatriation)? — both need a written FEMA-CA opinion. |

Note: HD-7 and HD-8 are partly *fact-gathering that terminates in your call*; HD-8's two sub-items are
external legal opinions that become verify-before-live blockers regardless of the design.

---

## I. Decision-log amendment map (what changes where, once HDs are resolved)

- **D5** — CalibrationStore evaluation-only in v1; no conviction-keyed Kelly ceiling (pending HD-1).
- **D6** — spell out durable `IntentId` + reconcile-before-retry + `capabilities().has_native_client_order_id`.
- **D9b** — state the N-maturity threshold (HD-7); calibration eval-only in v1 (HD-1).
- **D10a** — pre-paper hashed `PromotionManifest`; per-book scoreboard separation; effective-N accounting.
- **D11** — reconcile all-LLM-down behavior (HD-4); reconcile quality-in-null vs D20 (HD-5); null input-set = deterministic only.
- **D12** — coverage-deficit→REDUCING; HALT preserves protective orders; durable fencing/generation token; reconcile all-LLM-down trigger (HD-4).
- **D14 §⑤ / D14a** — strike LLM magnitude/confidence, redefine edge confidence as deterministic (pending HD-2); (D14a gates themselves are intact — the *spec narrative* is restored, F18).
- **D15** — enumerate the 14 exit-policy/recovery durable events; intention-truth vs custody-truth; reconciliation appends, never rewrites.
- **D16** — SessionReadiness (first gate, fail-closed) + CredentialReadiness; risk/cash commit globally serialized (CAS/single-writer); ProtectionSupervisor on risk clock; event-trigger cadence (HD-6).
- **D18** — conditional protection guarantee (coverage state machine); fail-closed GTT-failure/CA-cancel; exit-policy data are durable events.
- **D19** — restructure by lifecycle stage; correct static-IP date (2026-04-01); algo-ID = broker-provisioned exchange ID; add own+family + CNC-sell≤settled gates; name Indian-issuer + precise-ETF exclusions; PreRemittanceGate external-state + fail-closed; per-lot reinvest-or-repatriate idle-FX; verify-before-live blockers (HD-8 + below-TOPS registration).
- **D20** — content-addressed `ValidatedDataSnapshotId`; independent US CA/delisting/PIT-membership source; quality DISABLED in active-signal manifest (pending HD-5).
- **D21** — fixed-point money; 4 date fields; immutable fills + rate records; cash-event ingest; equity-anchor-rate vs realized-FX vs risk-view-rate never summed; gross LRS meter (Form A2, Rule 115); idle-FX-lot schema.
- **D22** — conditional broker-safety-net wording; fencing token; CredentialReadiness; re-auth job ≥07:30 IST.

New decisions to record after grill: **D25** (protection-coverage state machine + ProtectionSupervisor), **D26** (broker-effect idempotency: IntentId + reconcile + fencing), **D27** (event-sourced recovery inventory + global reservation), **D28** (ValidatedDataSnapshot boundary), **D29** (PromotionManifest + KG validation + effective-N), **D30** (typed ports + Kite-no-sandbox test rule), plus HD resolutions folded into existing D-numbers.

---

## J. Self-audit

- All 20 findings assigned a verdict (15 CONFIRMED, 5 CONFIRMED-WITH-MODIFICATION, 0 NOT-SUPPORTED),
  severity, spec/Dxx anchor, primary evidence or numeric trace, smallest seam-safe edit, and D-log impact.
- Broker protection race analysis (C), compliance matrix (D), seam audit (E), corrected fail-direction
  table (F), top-5 (G), 8 human decisions (H), and full decision-log amendment map (I) all present.
- Two factual errors in the authoritative log surfaced by primary sources (static-IP date; algo-ID mechanics).
- D4 preserved across every proposed fix (all recovery/state/reservation mechanisms carry only
  deterministic scalars/enums/IDs/version-integers; no LLM number routed into a number).
- Sub-reports 09a–09f are the evidence base; primary sources fetched 2026-07-20 and cited therein.
- Spec and RESEARCH-STATE.md are NOT edited by this synthesis — edits happen in the next step, after
  the 8 human decisions are grilled.
