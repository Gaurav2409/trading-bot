# 09e — Event-Sourcing, Recovery, Concurrency & HITL-Ordering: Adversarial Design Analysis

> **Status:** Analytic adversarial pass. No code, no spec edits, no RESEARCH-STATE edits.
> **Date:** 2026-07-20.
> **Spec under review:** `docs/superpowers/specs/2026-07-20-trading-os-design.md`
> **Authoritative decisions:** `docs/research/RESEARCH-STATE.md` (D1–D24 + D9a/D10a/D9b).
> **Brief under review:** `docs/research/08-adversarial-design-review-research-brief.md`
> **Assigned findings:** F07, F09, F14, F15, F16, F17 (non-India-mechanics portions) + F08-adjacent replay/reservation analysis.
> **Invariant honored throughout:** D4 — LLMs propose, code disposes. None of the proposed state/recovery mechanisms below route an LLM output into a number. Every proposed durable event and reservation carries only deterministic scalars (quantities, prices, timestamps, broker IDs, version integers, source-typed confidence) or closed categorical labels; no LLM-emitted scalar/ordinal is persisted into a sizing/risk/exit path.

---

## Executive verdict (assigned scope only)

| Finding | Verdict | Residual severity |
|---|---|---|
| F07 — HITL ordering unsafe (submit-then-review; default-no-trade suppresses exits) | **CONFIRMED** (mechanics) **+ NEEDS-HUMAN-DECISION** (D17-vs-D18 exit-review semantics) | Blocker |
| F08-adjacent — append-only replay double-submits; needs IntentId + reconcile-before-retry + fencing token | **CONFIRMED** | Blocker |
| F09 — all-LLM-down conflicts D12-vs-D6/§6; null independence unproven | **CONFIRMED** (independence gap) **+ NEEDS-HUMAN-DECISION** (D11-vs-D12) **+ NEEDS-HUMAN-DECISION** (D11-vs-D20 quality proxy) | Major |
| F14 — local exit/recovery state not reconstructable | **CONFIRMED** | Major (blocker-adjacent: silent loss of protection policy) |
| F15 — async sleeve cycles overspend global risk/currency budget | **CONFIRMED-WITH-MODIFICATION** (fix correct; a simpler single-writer commit gate is the smallest edit) | Major |
| F16 — rule-null vs LLM netted attribution undefined | **CONFIRMED** **+ NEEDS-HUMAN-DECISION** (D9a-vs-D16 flagged; separate-accounts vs virtual-books) | Major |
| F17 — SessionReadiness / CredentialReadiness / BrokerCashEventIngestor missing | **CONFIRMED** (all three genuinely absent and necessary) | Major |

**Bottom line:** All seven assigned findings are real. Two (F07, F08-adjacent) are blockers. F14 is a silent-correctness blocker in disguise (a restart that recovers quantity but drops exit policy leaves positions under a *stale-in-memory* protection assumption while the broker holds a *stale or absent* stop). Four human decisions must be surfaced, not resolved: **D11-vs-D12**, **D17-vs-D18**, **D11-vs-D20**, **D9a-vs-D16**.

---

## F07 — HITL ordering is submit-then-review; default-no-trade can retain risk

### Does §5 actually submit then review? — YES.

Reading the numbered flow literally (spec §5, Phase E):

- **Step 11** (line 154): "`BrokerAdapter.submit()`. On fill → `ExitManager` immediately places the resting broker-side stop … + registers ATR-trail / time-stop / regime-flip locally (D18)."
- **Step 12** (line 157): "`HITLBackend` surfaces the proposed order set **before** submission in the review window; asymmetric HALT respected (D22); default-no-trade on timeout."

Step 12's *prose* says "before submission," but the *ordinal position* places it after step 11's `submit()`. This is a genuine ordering defect in the spec: the numbered sequence and the prose contradict each other. Step 10 (KillSwitch check) is the last gate before step 11 submits; there is no approval gate between the deterministic checks and `submit()`. The spec §4 description of `ExitManager` ("+ HITL review queue") and §9 line 259 ("pending exit changes surface to HITL before firing") confirm HITL is *intended* to be pre-action, but §5's numbering does not encode it. **CONFIRMED: the flow as numbered submits at 11 and reviews at 12.**

### Is default-no-trade dangerous for exits? — YES. Failure trace.

§6 line 181: "HITL timeout → FAIL-CLOSED → Default-to-NO-TRADE (D17); order expires unsubmitted." D18/§9 line 259 says pending *exit* changes (trailing ratchets, time-stop expiries, regime exits) also "surface to HITL before firing." Compose these two rules:

```
Trace T-F07-exit-suppression:
1. Position P is long, thesis stale; time-stop deadline reached → ExitManager wants to SELL P (risk-REDUCING).
2. D18/§9 routes the pending exit to HITL "before firing."
3. Reviewer is asleep (US session is overnight IST — D22 explicitly notes this).
4. HITL window expires. §6 rule fires: default-to-NO-TRADE → exit order expires unsubmitted.
5. RESULT: the risk-reducing exit is SUPPRESSED. The position is RETAINED past its exit condition.
   Default-no-trade, which is safe for entries, has now *increased* net risk held.
```

The asymmetry the spec never draws: **default-no-trade is safe only for exposure-INCREASING orders.** For exposure-REDUCING orders (any exit that lowers net risk), the safe default is the opposite — proceed. The broker-side resting stop (D18) is a partial mitigation (it protects against a *price* breach even if the OS is dead), but it does **not** cover the time-stop and regime-flip exits, which have no broker-side analogue — those live only in the OS and are exactly the ones default-no-trade would suppress.

### Is the proposed reorder correct and D4-safe? — YES, with one refinement.

The brief's proposal (move HITL before submission; bind approval to immutable order-set hash + snapshot version + expiry; re-run all checks after approval; default-no-trade applies to exposure-increasing only; broker-side protective stops never need approval; risk-reducing exits proceed at expiry) is correct and **fully D4-safe**: an order-set hash, a snapshot version integer, an expiry timestamp, and an approve/reject boolean are all deterministic scalars. No LLM output is consumed. The human approves/vetoes a *deterministically-computed* order set; the human is not an LLM and is outside the D4 boundary by construction (D17 is a human control plane, not a model).

Refinement (smallest correct edit): the reorder must classify each order in the set by **exposure sign**, computed deterministically from `(order.side, current_position_sign, current_position_qty)`:
- `EXPOSURE_INCREASING` (opens/adds, or a "reducing" order that would flip to a larger opposite position) → default-no-trade on timeout.
- `EXPOSURE_REDUCING` (closes/trims toward flat, never crossing zero) → default-**proceed** on timeout (visible during window; human may veto in time, but silence ≠ suppression).
- Broker-side protective stops (GTT/stop placed on fill) are `PROTECTION` and are never gated by HITL at all — they are the safety net and must place unconditionally.

**Approval binding must re-validate after approval (D4-critical):** because HITL now precedes submission, an approval issued at snapshot version *v* must be rejected if the live snapshot has advanced to *v+1* (price moved, FX moved, another sleeve committed). This is the same compare-and-swap discipline as F15 — bind approval to `(order_set_hash, snapshot_version, expiry)` and re-run cash/risk/compliance/protection/kill-switch immediately before `submit()`. This closes the TOCTOU gap that moving HITL earlier would otherwise open.

### Verdict, edit, decision-log impact

- **Verdict: CONFIRMED (mechanics) + NEEDS-HUMAN-DECISION (semantics).**
- **Smallest correct design edit:** Renumber §5 so an approval gate sits between step 10 (KillSwitch) and `submit()`; add exposure-sign classification with sign-dependent timeout defaults; add post-approval re-validation bound to snapshot version.
- **Decision-log impact: YES.** D17 currently says "default-to-NO-TRADE-on-timeout" globally; D18 says pending exits "surface to HITL before firing." These two, composed, produce the suppression bug. **This is the D17-vs-D18 human decision — DO NOT RESOLVE:** *Is exit review an approval, a veto, or a notification?* The three answers give materially different fail-directions:
  - **Approval** (exit needs a human YES) → default-no-trade suppresses risk-reducing exits (the bug). Unsafe unless combined with the broker-side stop covering *all* exit types, which it does not.
  - **Veto** (exit proceeds unless human says NO within window) → safe for risk-reduction; human retains override.
  - **Notification** (exit fires; human is told) → safest for risk, weakest for human control.
  The analysis recommends **veto** for `EXPOSURE_REDUCING` exits and **approval** for `EXPOSURE_INCREASING` entries, but the choice is the user's.

---

## F08-adjacent — append-only replay double-submits; IntentId + reconcile-before-retry + fencing token

> F08 proper is another agent's; here the replay/reservation side.

### Does append-only replay double-submit? — YES. This is the classic non-idempotent-consumer bug.

§5 line 127: "Every arrow writes an immutable row to `EventLog` before the next stage reads it — the cycle is replayable." §6 lines 189–191: "a crash resumes by replaying the log … rebuild positions from the log." The unstated assumption is that replay is *safe* because events are immutable. It is not: **an immutable record of intent is not an idempotent effect.** The event log records that the OS *intended* to submit; it cannot record whether the broker *received* it, because the crash happens precisely in the acknowledgement gap.

```
Trace T-F08-double-submit:
1. OS writes OrderIntent(symbol=X, qty=100, side=BUY) to EventLog. [durable]
2. OS calls BrokerAdapter.submit(). Broker ACCEPTS and queues the order.
3. Broker's ACK is lost (network drop) OR OS crashes after send, before recording the ACK.
4. Watchdog restarts OS. Reconciliation job replays the log.
5. Replay sees OrderIntent with no corresponding FillEvent/AckEvent → concludes "not yet submitted."
6. Replay calls submit() again → SECOND order → 200 shares bought. Exposure doubled, unprotected surplus.
```

The same race applies to every broker effect, not just entries: GTT/stop **create, replace, modify, cancel** each have an ACK gap where replay can duplicate. A duplicate GTT-cancel followed by a re-create can momentarily leave a position unprotected; a duplicate GTT-create can leave two resting stops that both fire.

### Is durable IntentId + reconcile-before-retry + fencing token the right pattern? — YES.

This is the **Idempotent Consumer pattern** (microservices.io / Eventuate Tram `SqlTableBasedDuplicateMessageDetector`): a durable unique `IntentId` per broker effect, recorded in the same transaction as the intent, with the broker effect keyed by that ID so a retry is detectably a duplicate. Three layers, in order of strength:

1. **Native broker idempotency key on submit (D6 already mandates this).** D6's `OrderRequest` carries an "idempotency key on submit." If the broker honors it (Alpaca supports a `client_order_id`; Kite's order tagging is weaker and does *not* guarantee dedup server-side), a duplicate submit with the same key is rejected by the broker. This is the strongest layer where available. **Kite is the weak link** — its tag is not a dedup key — so Kite effects fall to layer 2.

2. **Reconcile-before-retry.** Before *any* retry of a broker effect, query the broker's order/trade book (D6 `reconcile()`) for the `IntentId`/client-order-id/tag. If found → the effect already happened; record the observed outcome as a reconciliation event, do **not** resubmit. If not found and outcome is genuinely unknown → enter `OUTCOME_UNKNOWN`, block related exposure, reconcile; never blind-retry. (Matches F08-proper's proposal and F03's ambiguous-fill state machine.)

3. **Fencing token / kill-switch generation counter** for stale workers. The literature (Redis distributed-locks doc §"Disclaimer about consistency"; Kleppmann's Redlock analysis) is explicit: a lease/lock is insufficient because a paused-then-resumed worker can act after its lease expired. The fix is a **monotonic fencing token** that the *resource side* (here: the submission path / broker gateway) checks and rejects if lower than the highest token seen.

```
Trace T-F08-stale-worker (why fencing is needed even with IntentId):
1. Worker W1 begins an EOD cycle, holds "submit authority" generation G=5.
2. W1 stalls (GC pause / VM freeze). Dead-man timer (D22) fires → HALT → un-HALT bumps generation to G=6; W2 starts.
3. W1 resumes, mid-submit, still believing G=5. Its IntentId dedup only prevents *its own* duplicate,
   not a submission that HALT intended to forbid.
4. FIX: every submit carries the generation token; the submission gate rejects any token < current (6).
   W1's stale submit (token 5) is fenced out. This is the "durable kill-switch generation/fencing token
   so stale workers cannot submit after HALT" from F08's proposal.
```

**CAS + version stamp** (from the CAS literature: AtomicStampedReference / tagged-pointer to defeat ABA) is the same primitive applied to the risk/cash reservation in F15 — the snapshot version *is* the fencing token for the reservation path.

- **Verdict: CONFIRMED.** Durable `IntentId` + reconcile-before-retry + monotonic fencing/generation token is the correct, literature-grounded pattern. All three are deterministic — no D4 exposure.
- **Decision-log impact:** D15 (event log as source of truth) should be clarified: *the event log is intention-truth, the broker is custody-truth*; reconciliation appends an observed event, never rewrites history (this also serves F14). D6's "idempotency key on submit" should be strengthened to require reconcile-before-retry and note Kite's weaker guarantee. D12 should gain a durable generation counter incremented on every HALT/un-HALT.

---

## F09 — all-LLM-down conflict + null independence unproven

### Is there a genuine D11-vs-D12 contradiction? — YES.

- **D12 / spec §6 line 176 header ("Kill-switch tiers") and D12 body:** "Triggers: … **all-LLM-providers-down** … HALTED = cancels allowed, new exposure never." So *all-LLM-down is a HALT trigger* — halts the whole market.
- **Spec §6 line 176 behavior column:** "ALL LLM providers down → FAIL-CLOSED (research) → No new theses; **rule-based null (D11) still trades** — degrades to rules-only."

These are directly contradictory. D12 says all-LLM-down → HALTED → **no new exposure for anyone**, including the null. §6 says all-LLM-down → the null **keeps trading**. An implementer reading D12 halts the null; an implementer reading §6 lets it run. **CONFIRMED contradiction.** This is the **D11-vs-D12 human decision — DO NOT RESOLVE.** The correct framing to hand the user: *does "all LLM providers down" HALT the market (D12's list treats it as a kill trigger) or does it merely SUSPEND the LLM strategy while the deterministic null continues (§6/D11's intent)?* These cannot both hold.

The analysis's recommendation (to inform, not resolve): all-LLM-down should **suspend only the LLM strategy**, not HALT the market — *provided* the null is provably independent (next section). If independence cannot be proven, D12's HALT is the safe reading and the "degrades to rules-only" promise in §6 is false and must be struck.

### Can the rule-null be made provably LLM-independent given the shared data plane (D13) and universe? — ONLY WITH EDITS. Hidden dependencies traced.

The null is described (D11) as "a pure rule-based Tier-1 composite (momentum + trend + quality proxy + regime gate)." "Pure rule-based" is asserted, not enforced. Trace every input the null consumes and check for LLM contamination:

```
Trace T-F09-hidden-LLM-deps (null's real input surface):
1. UNIVERSE. §5 step 3 resolves "the survivorship-free universe as-of today." If universe membership is
   ever narrowed/ranked by an LLM-derived signal (it should not be, but the spec does not forbid it),
   the null's cross-sectional momentum silently inherits an LLM choice. → MUST pin the null to the
   deterministic PIT-membership universe only (D20), never an LLM-curated candidate list.
2. CALIBRATION STORE (D9b). Keyed by (model, prompt_version, conviction_bucket, ...). If the null's sizing
   ever reads the ¼-Kelly ceiling (D5), it reads an LLM-keyed statistic → contamination AND a D4 leak
   (this is F01's leak, reachable from the null path). → the null MUST use fixed-fractional only; it must
   not read any model/prompt/conviction-keyed row.
3. KG EXPOSURE VECTOR / TRAVERSAL. Traversal is deterministic, but it is DRIVEN BY a MacroEvent LABEL the
   LLM authored (§3 lines 76–79) and by edges the LLM authored (D14a). So the exposure vector, though
   computed by deterministic code, is a FUNCTION OF LLM output. If the null consumes the exposure-vector
   defensive tilt (RiskEngine, §4 line 111), it is NOT LLM-independent. → the null MUST NOT consume the
   exposure vector or any KG output; its regime gate must be the deterministic HMM/vol gate only (D9),
   not the KG regime.
4. THESIS / REPORTS. Trivially LLM. Null must not read theses or AnalystReports. (Already implied.)
5. LLM HEALTH. The null must not condition on LLM provider health (else its behavior changes when the LLM
   is down — a covert coupling).
```

So the brief's proposal is correct and necessary: **`RuleNullJob` consumes only (a) the sealed validated market snapshot [F11's `ValidatedDataSnapshotId`], (b) deterministic signal config, (c) deterministic portfolio state.** It must not read theses, reports, KG output, calibration data, prompt/model state, LLM health, or an LLM-curated universe. With those exclusions, independence is *provable by construction* (the null's input type set contains no LLM-sourced type). Without them, "degrades to rules-only" is false.

### D11-vs-D20: does the null include a DISABLED signal? — YES. Flag it.

D11 defines the null's Tier-1 composite as "momentum + trend + **quality proxy** + regime gate." D20 states: "the **D9 quality-proxy signal stays DISABLED (haircut to zero)** until a restatement-free PIT-fundamentals vendor is sourced." So the null, as literally specified in D11, **includes a signal that D20 disables.**

```
Trace T-F09-disabled-quality:
- Null composite (D11) = f(momentum, trend, quality_proxy, regime).
- quality_proxy is haircut to zero (D20) until PIT fundamentals exist.
- If the null implementation includes quality at nonzero weight → it violates D20 (trades on faked/restated
  data → false alpha, the exact thing D10/D20 guard against).
- If the null implementation zeroes quality → the "Tier-1 composite" benchmark is NOT the composite D11
  describes; the three-way scoreboard (D10a) is comparing the LLM against a DIFFERENT null than documented.
  Either way the scoreboard's baseline is mis-specified until this is reconciled.
```

This is the **D11-vs-D20 human decision — DO NOT RESOLVE.** The framing for the user: *does the v1 null run a 3-factor composite (momentum + trend + regime, quality disabled per D20) and is the scoreboard re-baselined accordingly, or is go-live gated on sourcing PIT fundamentals so the 4-factor null D11 describes can actually run?* The analysis recommends the former (3-factor v1 null, explicitly re-baselined) since D20 makes quality a hard production blocker — but the user must confirm the scoreboard baseline.

- **Verdict: CONFIRMED (independence gap real) + NEEDS-HUMAN-DECISION ×2 (D11-vs-D12, D11-vs-D20).**
- **Smallest correct design edit:** Define `RuleNullJob`'s input type set as exactly `(ValidatedDataSnapshotId, DeterministicSignalConfig, DeterministicPortfolioState)` with a compile-time/type-level prohibition on thesis/report/KG/calibration/LLM-health types; pin its universe to PIT membership; run it at 3-factor weight (quality=0) until D20 clears.
- **Decision-log impact: YES.** §6 line 176 and D12's trigger list must be reconciled (D11-vs-D12). D11's composite definition must be reconciled with D20's quality-disable (D11-vs-D20).

---

## F14 — local exit/recovery state is not reconstructable (restart recovers quantity, loses exit policy)

### Confirmed. The failure.

§5 step 11: ExitManager "**registers ATR-trail / time-stop / regime-flip locally**." §6 crash-recovery: "rebuild **positions** from the log." Positions = quantity + symbol. The exit *policy* (trail ratchet level, entry regime, time-stop deadline, the specific broker GTT ID, approval expiry, any risk reservation) is "local" — in process memory or Valkey (which D13/D15 call a *rebuildable cache*, i.e., non-durable). Replay reconstructs quantity from fills; it does **not** reconstruct exit policy because exit policy was never written as durable events.

```
Trace T-F14-lost-exit-policy:
1. Position P filled 10 days ago. ATR-trail has ratcheted stop up 4 times (in Valkey). Time-stop deadline
   is day 30 (in Valkey). Entry regime = "risk-on" (in memory).
2. Host crashes; Valkey is flushed (it is a cache, not source of truth).
3. Restart replays EventLog → reconstructs qty=100 of P. 
4. But: trail ratchet level is GONE → new trail restarts from a LOWER stop (gives back ratcheted profit,
   or worse, computes a stop below current price → immediate/incorrect exit).
   Time-stop deadline is GONE → position may be held indefinitely past its intended exit.
   Entry regime is GONE → regime-flip exit cannot compare against entry regime.
   Broker GTT ID is GONE → OS cannot MODIFY/CANCEL the existing stop; may create a DUPLICATE stop (F08 race)
   or leave the real stop unmanaged.
5. RESULT: quantity recovered, exit policy silently wrong. This is worse than a clean failure because the
   system believes it is protected.
```

### Exact enumeration of state items that MUST become durable events

For a restart to reconstruct the **full exit policy**, not just quantity, the following must each be append-only events in the EventLog (all deterministic; no LLM scalar enters any of them):

| # | Durable event | Key fields (all deterministic) | Why replay needs it |
|---|---|---|---|
| 1 | `PositionEpisodeOpened` / `...Closed` | `position_episode_id` (unique), symbol, sleeve, open_ts, entry_snapshot_version | Episode identity for calibration keying (D9b) + spans multi-day partial exits |
| 2 | `FillAllocated` | episode_id, broker_trade_id, qty, price, side, exchange_trade_date, settlement_date, strategy_book_id | Reconstruct quantity + attribution (F16) + tax lots + FX lots (D21) |
| 3 | `StopIntentPlaced` / `StopAckReceived` | episode_id, intent_id, broker_gtt_id/stop_id, stop_price, stop_qty, ack_ts | Recover the broker-side stop's ID so OS can modify/cancel; detect coverage |
| 4 | `ProtectionCoverageChanged` | episode_id, covered_qty, position_qty, coverage_state ∈ {UNPROTECTED, PENDING, PROTECTED} | F03/F04 coverage state machine; restart knows if a deficit exists |
| 5 | `TrailRatcheted` | episode_id, new_stop_price, ratchet_ts, atr_snapshot_version | Recover the *ratcheted* (monotone-up) stop level, not a reset |
| 6 | `TimeStopDeadlineSet` | episode_id, deadline_date | Recover the deterministic hold-until date |
| 7 | `EntryRegimeRecorded` | episode_id, regime_label (deterministic HMM state, NOT an LLM class), entry_snapshot_version | Regime-flip exit needs the entry regime to compare against |
| 8 | `ApprovalDecision` | order_set_hash, snapshot_version, decision ∈ {APPROVED, REJECTED, EXPIRED}, expiry_ts, decider_id | Recover HITL state (F07) so a mid-approval restart is unambiguous |
| 9 | `OrderReservationCommitted` / `...Released` | reservation_id, snapshot_version, cash_reserved, risk_budget_reserved, sleeve, cas_token | Recover the F15 CAS reservation across restart; stale reservations rejected |
| 10 | `StrategyAttribution` | episode_id, strategy_book_id (LLM-book vs null-book) | F16 three-way scoreboard; who owns which fill/exit |
| 11 | `FxLotOpened` / `...Consumed` | lot_id, native_ccy, native_amt, tax_fx_rate (Rule-115), live_fx_mark, value_date | D21 dual-rate accounting, replay-safe |
| 12 | `IdleFxLotOpened` / `...Disposed` | lot_id, origin, value_date, amount, remaining, legal_deadline | F17/F05 180-day FEMA clock; survives restart |
| 13 | `CalibrationRecorded` | position_episode_id, conviction_bucket, regime, realized_outcome, sample_n | D9b write-path; **written ONCE at episode close** (item 1's `...Closed`), not incrementally |
| 14 | `KillSwitchGenerationBumped` | generation_int, reason, ts | F08 fencing token; stale workers fenced after restart/HALT |

**Confirm Valkey must be projection-only: YES.** D13/D15 already call Valkey a "rebuildable cache." The finding's requirement makes that binding: Valkey holds *only* a projection derived by replaying the events above; it is never the source of any exit-policy fact. Any field that would be silently lost on a Valkey flush must have a corresponding durable event above. **A field that is not derivable from the event log is a bug.**

### Calibration keying

Brief's proposal confirmed: calibration keyed by `position_episode_id`, **written once after the episode reaches zero** (including multi-day partial exits — the episode is not "closed" until net qty returns to zero). This prevents double-counting a partially-exited position and keeps the D9b write-path deterministic. D4 note: calibration *records* realized outcomes (deterministic P&L) keyed to a bucket; it must remain **evaluation-only** in v1 (F01) — the null and the Sizer must not read it into a number.

- **Verdict: CONFIRMED.**
- **Smallest correct design edit:** Add the 14 durable events above to §8/D15; state explicitly that Valkey is a projection of the event log and holds no authoritative exit-policy state; state event-log = intention-truth, broker = custody-truth, reconciliation appends observed events.
- **Decision-log impact: YES.** D15 must enumerate exit-policy events (not just order/fill/position-change) and declare the intention-vs-custody split. D18 must state that every exit-policy datum it "registers locally" is a durable event.

---

## F15 — async sleeve cycles overspend global risk/currency budget

### Is the overspend real given async India/US cycles on one portfolio? — YES.

§5 line 125: the cycle is "per sleeve." D16 schedules India and US as **independent calendar-aware jobs** (US session is overnight IST — D22). D21: RiskEngine uses a "single common-numeraire covariance" — i.e., there is **one global risk budget** spanning both sleeves. Two independent jobs against one shared budget with a read-then-write gap is a classic lost-update / double-spend.

```
Trace T-F15-double-spend:
1. Global remaining risk budget = R (one number, INR-numeraire, spans both sleeves).
2. India job reads snapshot S(v=7): sees remaining budget R. Sizes orders consuming 0.9R. Not yet committed.
3. US job (independent schedule) reads the SAME snapshot S(v=7): also sees remaining budget R
   (India's commit hasn't landed). Sizes orders consuming 0.9R.
4. Both submit. Combined committed exposure = 1.8R → cluster/currency-risk cap BREACHED.
5. Worse with pending orders (uncommitted but live), unsettled cash (T+1/T+2), and FX drift between reads.
```

The same race hits the **currency/LRS budget** (D19 LRS meter, D21 FX) and **cash** (settled-cash-only, D19). Any global scalar read by two async jobs is exposed.

### Is versioned global snapshot + CAS reservation the right fix? — YES (D4-safe). Any simpler option?

The brief's fix (versioned GLOBAL snapshot containing both sleeves + open/pending orders + unsettled cash + protection deficits + live FX; compare-and-swap durable cash/risk reservation before submission) is correct and directly implements the optimistic-concurrency / CAS pattern from the literature (read version → compute → CAS against that version; on mismatch, reject and recompute; version stamp defeats the ABA problem). It is **D4-safe**: the snapshot version is an integer, the reservation carries deterministic cash/risk amounts, and CAS compares integers. No LLM output participates.

**Simpler option (the actual smallest edit):** because this is a single-host, swing-frequency system (D22: one always-on host; D13: "Kafka/NATS overkill"), the contention is *low* and the writers are *few* (two sleeve jobs). The minimal correct fix is a **single-writer risk-commit gate**: serialize the *commit* step (not research, not sizing) through one durable, monotonically-versioned reservation table, so that only one order-set can commit against a given snapshot version at a time; the loser re-reads and recomputes. This is CAS with a degenerate (serialized) writer — same correctness, less machinery. Full CAS is warranted only if commits ever become concurrent (multi-host, v2). Research and sizing can still run concurrently per the brief; only the **risk/cash reservation commit** must be serialized/CAS-guarded.

- **Verdict: CONFIRMED-WITH-MODIFICATION** (fix is correct; the smallest v1 edit is a single-writer versioned commit gate, which is CAS specialized to the single-host low-contention case).
- **Smallest correct design edit:** Add a global versioned portfolio snapshot and a durable `OrderReservation` (event #9 above) obtained via CAS/single-writer commit against the snapshot version immediately before `submit()`; stale-version reservations rejected and recomputed. This reservation is *also* what F07's post-approval re-validation and F08's fencing token key against — one mechanism serves three findings.
- **Decision-log impact: YES.** D16 (independent per-sleeve jobs) must state that the *risk/cash commit* is globally serialized even though research is per-sleeve. D5/D21 must state the risk budget is committed via reservation, not merely read.

---

## F16 — rule-null vs LLM execution attribution undefined

### Is netted-execution attribution genuinely broken for the three-way scoreboard? — YES.

D11 runs the null "**live in parallel forever**" with the LLM path. D10a's three-way scoreboard (LLM vs null vs index) requires per-strategy P&L, cost, and exit behavior. But the broker holds **one net position per symbol** and (D18) **one resting stop per position**. If both strategies act on the same symbol:

```
Trace T-F16-unattributable:
1. LLM path decides BUY 100 X; null path also decides BUY 60 X (same symbol, same cadence).
2. Broker executes one net order → holds 160 X, ONE GTT stop covering 160.
3. Later the null's time-stop wants to exit 60 while the LLM's thesis says hold.
   The broker has ONE position and ONE stop — whose exit fires? Whose fill is whose?
4. P&L, transaction cost (STT/GST/slippage), and the exit outcome cannot be split between books
   without an allocation rule that does not exist in the spec.
5. RESULT: the D9b calibration (keyed per episode) is mis-attributed; the D10a three-way scoreboard
   compares two strategies whose individual P&L is undefined → the go/no-go decision is invalid.
```

**CONFIRMED: netted execution makes the scoreboard's per-strategy P&L undefined, and D10a's promotion decision rests on that P&L.**

### Separate accounts vs virtual books — trade-offs.

| Option | Attribution correctness | Cost | Ops | Physical stop coverage | Verdict |
|---|---|---|---|---|---|
| **Separate broker accounts/subaccounts** (LLM-book, null-book) | Exact — two positions, two stops, two P&Ls, native | Doubles some fixed costs; may need two Kite/Alpaca logins | 2× ops, 2× reconciliation | Native — each account has its own stop | Cleanest; heaviest ops. D22 flagged "running both live = 2× ops for ~0 diversification" for *brokers* — same tax here. |
| **Single netted account + virtual `StrategyBook`s** | Requires a deterministic allocation rule (fill allocation, virtual tax lots, cost allocation, conflicting-exit resolution, physical-stop-coverage assignment) | Single account cost | 1× broker ops + virtual-book bookkeeping | **Hard problem**: one physical stop must be deterministically split/assigned across books | Feasible but the allocation rule is intricate and must be D4-safe (deterministic, no LLM input) |
| **Paper-only overlap** (v1) | Null and LLM both run in Sim/paper where positions can be truly separate | free | low | trivial (simulator) | **Recommended for v1** — the scoreboard is a *paper-gate* metric (D10/D10a run on forward paper), so the null and LLM can be fully separated in the SimulatedBrokerAdapter with independent books; netting only becomes a live problem after promotion |

The key observation: **D10a's three-way scoreboard is evaluated on forward paper**, and the SimulatedBrokerAdapter (D7) can maintain fully separate books trivially. The netted-attribution problem is a *live* problem, not a paper-gate problem. So the smallest v1-correct edit is: **run the null and LLM as separate `StrategyBook`s in Sim/paper (fully separated), and defer the live netting decision** — but define now that if they ever share a live account, a deterministic fill-allocation + virtual-tax-lot + cost-allocation + conflicting-exit-resolution + physical-stop-coverage rule is required, and aggregate risk across all books regardless (so F15's global budget still binds across books).

### D9a-vs-D16 flag

The task asks to flag the **D9a-vs-D16 human decision**. D9a (min-cadence gate: LLM/decision path runs at the slowest active signal's cadence, never a daily heartbeat) constrains *when* the LLM path decides. D16 permits **event triggers** as a scheduled job class ("event triggers" appears in both D16 and §3). If an event trigger fires the LLM decision path off-cadence (e.g., a macro-shock news event mid-month), it trades *outside the validated slowest-signal horizon* — contradicting D9a. This also interacts with F16: an event-triggered LLM trade and a monthly-cadence null trade on the same symbol deepen the netting/attribution problem (different cadences → interleaved fills that are even harder to attribute). **This is the D9a-vs-D16 human decision — DO NOT RESOLVE:** *may event triggers move the LLM decision/trade path off the slowest-signal cadence, or may they only refresh labels/rationale for the next on-cadence decision?* The framing matters for both horizon validity (D9a) and attribution (F16).

- **Verdict: CONFIRMED + NEEDS-HUMAN-DECISION (D9a-vs-D16; and separate-accounts-vs-virtual-books is a design choice for live).**
- **Smallest correct design edit:** Define separate immutable `StrategyBook`s with independent capital/risk budgets; run them fully separated in Sim/paper for the v1 scoreboard; declare the live-netting allocation rule as a v1-design/-v2-build item; aggregate risk across all books (ties to F15's global reservation).
- **Decision-log impact: YES.** D10a/D11 must state that the scoreboard requires per-book separation and how it is achieved (separate paper books v1). D16/D9a must resolve the event-trigger cadence question.

---

## F17 (non-India portion) — SessionReadiness / CredentialReadiness / BrokerCashEventIngestor missing

All three are genuinely absent from the spec and each closes a distinct failure. Checked against §3 (three planes), §4 (components), §5 (data flow), §8 (data & state):

### SessionReadiness — MISSING and necessary.

§5 line 125: the cycle triggers "on a calendar-valid trading day **after close**." §3 line 62: "calendar-aware scheduled jobs." But nowhere does the spec define *how* "after close" is determined authoritatively or what happens on an *unknown* session. DST (US clocks shift twice a year; IST does not — so the IST→ET offset changes), Muhurat trading (NSE's special evening session on Diwali), and unscheduled closures (exchange halts) all move the true close relative to the wall clock.

```
Trace T-F17-session:
1. US DST ends; ET close is now 1 hour later in IST terms, but the scheduler still fires "after close"
   at the old IST time.
2. EOD ingest runs BEFORE the true session close → partial/incorrect OHLCV → signals compute on incomplete
   bars → §5 step 3 correctness layer may not catch it if the calendar it validates against is also wrong.
3. RESULT: the whole cycle runs on pre-close data. Silent, because the calendar is assumed correct.
```

**Fix (brief, confirmed):** `SessionReadiness` using a **versioned authoritative calendar + observed close** (e.g., confirm the session is actually closed via broker/exchange signal, not just wall-clock); **unknown sessions fail closed** (do not run EOD work on a date the calendar cannot classify). D4-safe (calendars and timestamps are deterministic).

### CredentialReadiness — MISSING and necessary.

D12 mentions "degrades gracefully on Kite daily-token-refresh failure (positions stay visible)." §3 line 63 lists "Kite token refresh" as a scheduled job. But there is **no pre-flight credential check before each order/protection job**, and Kite's daily token expiry is a hard, scheduled event.

```
Trace T-F17-credential:
1. Kite daily access token expires overnight (Kite tokens are daily; require re-auth).
2. A CA>5% cancels a protective GTT (D18/D20 §6 line 179). CorporateActionMonitor tries to re-place it.
3. The re-place call hits Kite with an expired token → TokenException.
4. If TokenException is auto-retried (naive), it loops and never repairs; if it is swallowed, the position
   is UNPROTECTED and the OS believes protection is pending.
5. RESULT: a position is unprotected while the OS shows "protection pending," precisely because a
   credential check did not gate the protection job.
```

**Fix (brief, confirmed):** `CredentialReadiness` before **every** order/protection job; Kite `TokenException` is **not auto-retried** — it requires re-authentication (D22's localhost re-auth) **plus reconciliation before new exposure**. This composes with F08 (don't blind-retry) and F14 (protection coverage is a durable event, so the OS knows the deficit). D4-safe.

### BrokerCashEventIngestor — MISSING and necessary.

§5's cycle ingests OHLCV + corporate-action feed + news (step 2). It does **not** ingest **broker cash events**: dividends received, dividend withholding tax, interest/sweep income, fees, reversals, repatriations, cash-in-lieu (from fractional CA outcomes). D21 (dual-currency accounting) and D19 (LRS meter, Schedule FA, Form 67, idle-FX watchdog) all *depend* on these cash events, but no component *produces* them.

```
Trace T-F17-cash-event:
1. US position pays a dividend → USD credited to the Alpaca account, minus 25% W-8BEN withholding (D19).
2. Nothing ingests this. The idle USD is not tracked as an IdleFxLot (F05/F14 item #12) → the 180-day FEMA
   clock never starts for it → potential FEMA breach.
3. The gross dividend + withholding is not recorded → Form 67 (foreign tax credit) and Schedule FA
   (peak/closing balance, income) are incomplete → tax filing wrong.
4. RESULT: legal/accounting state silently diverges from broker reality.
```

**Fix (brief, confirmed):** `BrokerCashEventIngestor` for dividends, withholding, interest/sweep income, fees, reversals, repatriations, cash-in-lieu — feeding accounting (D21 dual-rate ledger), idle-FX (F05 lots), Schedule FA, and Form 67 state. Each is a durable event (F14 items #11–12 depend on it). D4-safe (all deterministic broker-reported amounts).

- **Verdict: CONFIRMED (all three absent and necessary).**
- **Smallest correct design edit:** Add three components to §4 and wire them into §5: `SessionReadiness` (fail-closed on unknown session, gates the whole cycle at Phase A), `CredentialReadiness` (gates every order/protection job; TokenException → re-auth + reconcile, never auto-retry), `BrokerCashEventIngestor` (Phase A/F ingest of all cash events → durable events → accounting/idle-FX/Schedule-FA/Form-67).
- **Decision-log impact: YES.** D16 must add SessionReadiness as the first gate of every cycle. D22/D12 must state CredentialReadiness gates protection jobs and TokenException is not auto-retried. D21/D19 must state cash events are ingested as durable events by a named component.

---

## Typed design-level state/recovery inventory

All fields below are deterministic scalars, closed enums, timestamps, IDs, or version integers. **No field carries an LLM-emitted scalar or ordinal** — D4 holds across the entire recovery surface. (LLM outputs — thesis, MacroEvent label, edge proposals — live only in Plane 1 / Postgres JSONB and are never persisted into an exit/sizing/risk/reservation field.)

| Aggregate | Durable event(s) | Recovery role | D4 status |
|---|---|---|---|
| PositionEpisode | Opened / Closed | episode identity, calibration key, multi-day-exit span | deterministic |
| Fill | FillAllocated | qty/price/dates/book — quantity + attribution + tax/FX lot basis | deterministic |
| Protection | StopIntentPlaced / StopAckReceived / ProtectionCoverageChanged | broker stop ID recovery + coverage state machine | deterministic |
| Trailing stop | TrailRatcheted | monotone-up stop level recovery | deterministic |
| Time-stop | TimeStopDeadlineSet | hold-until date recovery | deterministic |
| Regime | EntryRegimeRecorded | HMM entry-state for regime-flip exit | deterministic (HMM state, not LLM class) |
| HITL | ApprovalDecision | approve/reject/expire bound to order_set_hash + snapshot_version | deterministic (human decision, outside D4) |
| Reservation | OrderReservationCommitted / Released | CAS cash/risk reservation across restart (F15) | deterministic |
| Attribution | StrategyAttribution | LLM-book vs null-book ownership (F16) | deterministic |
| FX | FxLotOpened / Consumed | dual-rate (Rule-115 + live) lots (D21) | deterministic |
| Idle-FX | IdleFxLotOpened / Disposed | 180-day FEMA clock (F05/F17) | deterministic |
| Calibration | CalibrationRecorded | written once at episode close (D9b) | deterministic; evaluation-only in v1 (F01) |
| Kill-switch | KillSwitchGenerationBumped | monotonic fencing token (F08) | deterministic |
| Cash events | DividendReceived / WithholdingApplied / InterestAccrued / FeeCharged / Reversal / Repatriation / CashInLieu | accounting + idle-FX + Schedule FA + Form 67 (F17) | deterministic |
| Session | SessionReadinessConfirmed / SessionUnknownHalt | fail-closed session gate (F17) | deterministic |
| Credential | CredentialReadinessConfirmed / TokenExpiredHalt | gate order/protection jobs (F17) | deterministic |

**Valkey:** projection-only. Every field it holds is derivable by replaying the above. A Valkey flush is a non-event for correctness.

**Truth model:** EventLog = intention-truth; broker = custody-truth. On divergence, reconciliation **appends** an observed event; it never rewrites history (serves F08, F14).

---

## Corrected fail-direction table

Which CONTINUE states must be fail-closed-for-new-exposure; which exits stay operational during HALT; how stale workers are fenced.

| Situation | Spec §6 says | Corrected fail-direction | Rationale |
|---|---|---|---|
| HITL timeout, order is **exposure-INCREASING** | FAIL-CLOSED (no trade) | **FAIL-CLOSED** (unchanged) | Default-no-trade safe for entries (F07) |
| HITL timeout, order is **exposure-REDUCING** exit (time-stop/regime-flip) | FAIL-CLOSED → suppresses exit | **FAIL-OPEN for risk-reduction** (proceed at expiry; human may veto in window) | Default-no-trade retains risk (F07). Pending D17-vs-D18 human decision. |
| Broker-side protective stop placement | (implicit, on fill) | **Unconditional — never HITL-gated** | It is the safety net (F07/D18) |
| ALL LLM providers down | §6: null continues; D12: HALT | **SUSPEND LLM strategy only, null continues** *iff* null proven LLM-independent; else HALT | D11-vs-D12 human decision (F09) |
| HALTED kill-switch | cancels allowed, new exposure never | **HALTED must NOT cancel a protective order** except during a confirmed replace; existing exits/stops stay operational | An exit/stop is risk-reducing; HALT should not strip protection (F04-adjacent, F07) |
| REDUCING | no new exposure, existing managed | **Exits/stops remain fully operational**; only exposure-INCREASING orders blocked | Reducing must be able to reduce |
| Protection-coverage deficit (unprotected qty) | (not modeled) | **FAIL-CLOSED for exposure increases; symbol → REDUCING; repair or controlled-liquidate** | F03/F04/F14 coverage state |
| Ambiguous fill / lost ACK | (blind replay → double-submit) | **OUTCOME_UNKNOWN → block related exposure → reconcile-before-retry; never blind-retry** | F08 idempotency |
| Stale worker after HALT/restart | (not modeled) | **Fenced by monotonic generation token; submission gate rejects token < current** | F08 fencing (Redis/Kleppmann) |
| Unknown/misclassified session | (assumed calendar correct) | **FAIL-CLOSED — do not run EOD work** | F17 SessionReadiness |
| Kite TokenException on order/protection job | D12: "degrades gracefully" | **FAIL-CLOSED for new exposure; re-auth + reconcile; NOT auto-retried**; existing broker-side stops remain the net | F17 CredentialReadiness |
| Reservation stale (snapshot version advanced) | (not modeled) | **Reject reservation; recompute against current version** | F15 CAS |

---

## Human decisions flagged (NOT resolved)

1. **D11-vs-D12 (F09):** all-LLM-down — HALT the market (D12) or suspend only the LLM strategy while the null continues (§6/D11)? Cannot both hold.
2. **D17-vs-D18 (F07):** is exit review an **approval**, a **veto**, or a **notification**? Approval + default-no-trade suppresses risk-reducing exits.
3. **D11-vs-D20 (F09):** the null's Tier-1 composite includes a quality proxy that D20 disables until PIT fundamentals exist — run a 3-factor null and re-baseline the scoreboard, or gate go-live on sourcing PIT fundamentals?
4. **D9a-vs-D16 (F16):** may event triggers move the LLM decision/trade path off the slowest-signal cadence (violating D9a's horizon), or only refresh labels for the next on-cadence decision?

---

## Self-audit

I confirmed all seven assigned findings against the exact spec lines (§5 steps 11–12; §6 fail-direction table; §8 D15/D21; §9) and the authoritative decisions (D11, D12, D15, D16, D17, D18, D20, D21, D22, D9a, D9b, D10a). I traced each failure concretely and gave the smallest D4-safe edit; every proposed durable event and reservation carries only deterministic scalars/enums/IDs/version-integers — no LLM output is routed into a number, so D4 is preserved across the entire recovery surface. I grounded the F08-adjacent replay analysis in event-sourcing literature (idempotent-consumer PROCESSED_MESSAGE dedup — microservices.io/Eventuate Tram; CAS + version-stamp for ABA — algomaster; monotonic fencing token + Kleppmann's Redlock critique — redis.io distributed-locks doc, sources saved under `/tmp/es-lit/`). I flagged all four human decisions (D11-vs-D12, D17-vs-D18, D11-vs-D20, D9a-vs-D16) and deliberately did NOT resolve them. Limitations: broker-specific idempotency guarantees (Kite tag vs Alpaca client_order_id) are stated from D6 + general knowledge, not re-verified against live broker docs in this pass (that is F08-proper / the India-mechanics agent's scope and the brief's verify-before-live blockers); the F16 live-netting allocation rule is scoped as a design-now/build-later item, not fully specified. I did not edit the spec or RESEARCH-STATE.md.
