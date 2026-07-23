# 09f — Data-Snapshot, Two-Currency Accounting, Promotion-Precommitment & Testability

> **Status:** Adversarial design-analysis pass (no implementation). Analytic; two sources touched
> (survivorship magnitude + DSR mechanics) — the rest is design reasoning against the spec and D-log.
> **Spec under review:** `docs/superpowers/specs/2026-07-20-trading-os-design.md`
> **Authoritative decisions:** `docs/research/RESEARCH-STATE.md`
> **Findings owned here:** F11, F13 (data/accounting-determinism portion only — the LRS/FEMA-legal
> portion of F13 is owned by another agent), F19, F20.
> **Invariant:** D4 non-negotiable. No v2 pull-in (no auto-KG-edge admission, no `WebResearchSpoke`,
> no IBKR). **Date:** 2026-07-20.

---

## 0. Executive summary

| Finding | Verdict | RESEARCH-STATE.md change needed? |
|---|---|---|
| **F11** — correctness gate lacks an immutable, typed, content-addressed snapshot boundary; US-side correctness under-specified | **CONFIRMED** | **Yes** — D20 must add the sealed-snapshot boundary + US CA/delisting/membership source + factor→series binding + active-signal manifest. |
| **F13** (determinism portion) — two-currency accounting not deterministic/replay-safe | **CONFIRMED** | **Yes** — D21 must add fixed-point money, separated date fields, immutable native fills, rate-records-as-events, FX-lot method, rounding-then-rerun. |
| **F19** — promotion thresholds undefined & KG validation omitted (p-hacking + no macro-shock in a quiet window) | **CONFIRMED** | **Yes** — D10a must add the pre-paper hashed promotion manifest; D14's cross-sectional rank-correlation metric + 2020/2022 replays must be restored to the spec narrative and referenced from D10a. |
| **F20** — independent testability asserted but not designed | **CONFIRMED** | **No** (spec §4/§10 gain a typed-ports/fakes inventory) — **except** the Kite-no-sandbox contract-run rule, which is a spec addition, not a D-log change. |

Net: all four are real. Three force decision-log edits (D20, D21, D10a; plus D14 restoration into
the spec). One (F20) is a spec-only design build-out. **One latent human decision surfaces here:
D11-vs-D20** (the rule-based null's quality proxy vs. quality being DISABLED until PIT fundamentals
clear) — flagged in §5.

---

## 1. F11 — Content-addressed `ValidatedDataSnapshot` boundary (India + US)

### 1.1 Is the boundary the right fix? — YES

The spec's Phase A (§5 lines 129–135) computes CA-adjusted OHLC, validates against Bhavcopy, and
resolves a survivorship-free universe, then **fails closed** on a data-quality flag (D20). That is
the right *gate*, but it produces **no artifact**. Downstream stages (Phase B `Traversal`, Phase D
`Sizer`/`RiskEngine`, the §10 sim/eval) are described as reading tables, not a sealed object.
Two failure classes follow directly:

**Failure trace A — late CA revision mutates a queried table (TOCTOU).**
1. Day *D* EOD cycle: `CorrectnessLayer` validates RELIANCE OHLCV + CA factors → PASS. Signals compute.
2. Hours later, NSE issues a **revised bonus ratio** (a genuine, common event — CA feeds are
   corrected after initial publication). `DataIngest`/`CorrectnessLayer` writes the revised
   split/bonus factor into the CA-ledger table.
3. The still-running (or replayed) cycle's `Traversal`/`Sizer` re-query `latest` → now reads
   **factor rows that never passed the gate**. Signals silently computed on a mix of validated and
   post-validation-mutated data. The "fails-closed on bad data" guarantee is void because the bad
   data arrived *after* the flag check, and nothing pins the reader to the validated rows.
4. Replay of the same `eod.<sleeve>.<date>` event weeks later reads a *different* `latest` again →
   **non-reproducible cycle**, breaking the §5 "the cycle is replayable" claim and the D10
   forward-paper "frozen configs" guarantee.

**Failure trace B — US sleeve passes with no independent CA/delisting/membership ledger.**
Phase A (§5) and D20 are written India-first: "validates against **Bhavcopy**", "**NSE/BSE** CA
feeds", "India = NIFTY 500 + liquidity floor; US = *defined list*." A "defined list" is a static
universe — it has **no PIT membership history and no delisting handling**. So:
1. US cross-sectional momentum (D9 Tier-1) ranks a survivorship-biased universe (the ~3.5–4.4%/yr
   overstatement quantified in `06-india-mechanics.md` §4 applies to any market; US index add/drop
   and delistings are the same bias mechanism).
2. A US split/reverse-split or a special dividend is taken from the broker/vendor feed with **no
   independent second source** — exactly the failure D20 forbids for India ("never trust Kite's
   adjustment"). The US sleeve can pass Phase A while doing none of the D20 correctness work.
3. A delisted US name silently drops from the "defined list" with no delisting event → look-ahead
   survivorship on every historical replay.

**Conclusion: CONFIRMED.** A content-addressed `ValidatedDataSnapshotId` is the correct boundary —
it converts "the gate passed" into "these exact bytes passed," and makes every downstream reader
*require the token* so it structurally cannot read `latest`. This is the standard content-addressed
/ Merkle-manifest pattern (hash the manifest of component hashes; the ID changes iff any component
changes; a mutated CA row produces a *new* ID and *invalidates* the old token rather than silently
altering the answer). It also mechanizes D24's own promise (D24 already requires web content be
"content-addressed … so cycle replay uses the captured snapshot") — F11 simply extends the same
discipline to the Phase-A market/CA/universe data, which is *more* correctness-critical than web
enrichment.

### 1.2 The spec **does** under-specify US-side correctness — confirmed

D20 enumerates four correctness pillars but instantiates them for India only:
- (1) CA factor ledger → "from **NSE/BSE** CA feeds";
- (2) survivorship-free universe → "India = NIFTY 500 + liquidity floor; **US = defined list**"
  (no PIT membership, no delisting source named; contrast the India "cross-check delisting notices");
- (3) PIT fundamentals blocker → market-agnostic (fine);
- (4) KG Layer-2 news → market-agnostic (fine).

Pillars (1) and (2) have **no US instantiation**. §5 Phase A names only Bhavcopy. So the US sleeve
can pass Phase A having validated nothing. This is the concrete "Phase A specifies India checks
only" gap F11 asserts — **confirmed**.

### 1.3 Minimum `ValidatedDataSnapshot` contents & validity rules (India + US)

The snapshot is an **immutable, content-addressed manifest**: `snapshot_id = H(canonical manifest)`
where the manifest lists each component and *its own* content hash + version + as-of date. Emitting
it is the last act of Phase A; **every** signal / `Traversal` / sim / eval interface takes
`snapshot_id` as a required argument and resolves component bytes *only* through it — never a
`SELECT … latest`. A missing / stale / future-dated / post-seal-revised required component makes the
snapshot **invalid**, not silently different (fail-closed, D20).

**Minimum contents (both sleeves, unless a row says otherwise):**

| Component | Minimum content | Validity rule |
|---|---|---|
| **OHLCV series (raw)** | per-symbol raw OHLCV up to `as_of_date`, unadjusted | every bar ≤ `as_of_date` (no future bar); no gaps across valid trading days; hash pins exact bytes |
| **OHLCV series (split/bonus-adjusted)** | separately stored, computed from the CA ledger below | must be recomputable from raw + CA factors *in the snapshot* (reproducibility check) |
| **OHLCV series (total-return)** | separately stored (dividends reinvested) | dividends sourced from the CA ledger; **never** conflated with split-adjusted (see §1.4) |
| **CA factor ledger** | split/bonus/rights/spin-off factors + **dividends** + cash-in-lieu, with ex-date & record-date, **India: NSE/BSE independent of Kite; US: independent source (see below)** | each factor validated against a 2nd source (India: Bhavcopy on ≥3–5 known events per `06`; US: independent vendor vs broker); **any post-seal CA revision → new snapshot_id, old token invalid** |
| **Universe membership (PIT)** | survivorship-free constituent set as-of `as_of_date` with add/drop history; **India: NIFTY 500 + liquidity floor; US: PIT-membership index/list, not a static "defined list"** | every member's `valid_from ≤ as_of_date`; no current-constituent leakage; cross-sectional signals reject any symbol not in the PIT set |
| **Delisting / corporate-death ledger** | delisting, suspension, merger, bankruptcy events with effective dates; **India: NSE/BSE delisting notices; US: independent delisting source** | a symbol delisted ≤ `as_of_date` is excluded from tradable universe but retained (not silently dropped) for replay integrity |
| **Market calendar** | authoritative trading-day + session-close calendar for the sleeve (India: NSE holidays/Muhurat; US: NYSE/NASDAQ + DST) | `as_of_date` must be a valid trading day; unknown/ambiguous session → snapshot invalid (fail-closed, matches F17/`06` "fail closed on unknown trading days") |
| **News cutoff** | timestamp cutoff for any news/GDELT feed feeding the KG Layer-2 label | no news item with timestamp > cutoff may be visible to the classifier (anti-look-ahead) |
| **Enabled-signal manifest** | which signals are ACTIVE this snapshot + each signal→series binding + each factor's data version | **quality proxy must read DISABLED** until PIT fundamentals clear D20 (see §1.5) |
| **KG edge set version** | the `valid_from`/`last_confirmed`-filtered edge set as-of `as_of_date` (D14a) | only edges with `valid_from ≤ as_of_date` visible (kills look-ahead — the `05` #1 fake-alpha source) |
| **FX rate set** (US sleeve) | the exact FX rate records referenced this cycle (see F13) | pinned by rate-record hash; live-mark vs Rule-115 rate stored separately |

**Factor→series binding rule (F11's "bind every factor to raw/split-adjusted/total-return"):**
every factor declares which series it consumes. Momentum/trend → **total-return** (a price-return
series understates momentum by the dividend yield and misranks high-yield names). Anything comparing
absolute price levels across a split → **split-adjusted**. Anything needing the actually-traded print
(e.g., circuit-band checks in the sim) → **raw**. An unbound factor is a snapshot-validity failure,
not a default-to-`latest`.

### 1.4 Total-return vs split-adjusted — the classic conflation

Storing "adjusted" as a single series (the common vendor default) silently merges two different
operations: split/bonus adjustment (multiplicative share-count change, no economic gain) and
dividend reinvestment (economic total return). `06` §4 already flags "**Dividends are typically NOT
adjusted in Indian feeds** — the classic gotcha." The snapshot **must** carry three distinct series
(raw, split/bonus-adjusted, total-return) as D20 already says — F11's contribution is to make the
*binding* explicit and snapshot-pinned so a factor can never silently read the wrong one.

### 1.5 Active-signal manifest & the D11-vs-D20 human decision

F11's "active-signal manifest shows quality DISABLED until PIT fundamentals clear D20" is correct and
directly encodes D20 pillar (3). But it **surfaces the F19-adjacent D11-vs-D20 conflict** (also listed
as human-decision #7 in `08`):

- D20: the D9 **quality proxy stays DISABLED (haircut to zero)** until a restatement-free PIT
  fundamentals vendor exists.
- D11: the **rule-based null** is a "momentum + trend + **quality proxy** + regime gate" composite
  that trades live *forever* as the benchmark.

If the snapshot honestly marks quality DISABLED, then the null is **momentum + trend + regime only**
— which is *not* the D11 composite as written. Either (a) the null is redefined to exclude quality
while disabled (and the three-way scoreboard compares a 3-factor null), or (b) quality is somehow
enabled (violating D20's anti-false-alpha stance). **This is a human decision — flagged in §5.** The
snapshot's active-signal manifest is the right place to *enforce* whichever way it is decided (the
null job reads the same manifest and cannot enable a DISABLED signal), but it cannot decide it.

### 1.6 Smallest correct design edit (F11)

Add to **D20** (decision-log edit): "Phase A emits a content-addressed `ValidatedDataSnapshotId`
manifesting exact raw/split-adjusted/total-return OHLCV, the CA-factor + dividend + delisting ledger,
PIT universe membership, market calendar, news cutoff, KG-edge-set version, FX rate set (US), and the
enabled-signal manifest with per-factor series binding. Every signal/traversal/sim/eval consumes the
token and cannot query an unsealed `latest`; any missing/stale/future-dated/post-seal-revised required
component invalidates the token (fail-closed). Add an **independent US CA/delisting/PIT-membership
source** symmetric to the NSE/BSE requirement; replace 'US = defined list' with a PIT-membership US
universe. The quality proxy reads DISABLED in the manifest until PIT fundamentals clear D20."
No v2 items pulled in. No code.

---

## 2. F13 (determinism portion) — deterministic, replay-safe two-currency accounting

### 2.1 Enumerated accounting edge cases (each breaks replay today)

D21 as written stores "every fill in native currency AND INR at two rates" (Rule-115 SBI TTBR
last-day-of-prior-month + a live FX mark) and puts realized FX gains on a separate ledger line. It
does **not** specify money type, date semantics, mutability, or rate-record identity. Concrete
non-determinism:

1. **Fractional US fill settling next day.** Alpaca supports fractional shares → quantity is not
   integral. Float money (e.g., `0.1 + 0.2`) is non-associative → replay on a different summation
   order yields a different INR total. **Trade timestamp ≠ settlement/value date**, so which day's FX
   applies is ambiguous unless dates are stored separately.
2. **Live FX correction.** The live mark observed at fill time is later corrected (vendor revision).
   If the fill row is *updated* in place, the append-only log (D15) is violated and the pre-correction
   replay is unrecoverable.
3. **SBI prior-month date on a holiday.** Rule-115 uses the TTBR of the *last day of the prior
   month*. If that day is a bank holiday there is **no rate** — undefined behavior. Two engineers
   (or two replays after a data patch) pick different fallback days → different tax INR value.
4. **Omitted fees / withholding / cash-in-lieu.** US dividend withholding (W-8BEN 25% DTAA),
   brokerage/regulatory fees, and CA **cash-in-lieu** (fractional-share residue on splits/mergers)
   are cash events that move both native and INR balances. If they are not events, equity and cash
   don't reconcile and the LRS/idle-FX meters (D19/F05/F06, other agent) are fed wrong numbers.
5. **Updating a fill violates append-only → divergent recompute.** Any in-place edit (correction,
   settlement backfill, FX revision) means replay-from-log no longer reproduces state — the core D15
   guarantee is broken precisely where money correctness matters most.
6. **Equity vs realized-FX double-count (the subtle one — see §2.3).**

### 2.2 Does the proposed fix make replay deterministic? — YES, with the pieces named

The F13 proposal is sufficient **if** all of these hold together:

- **Fixed-point decimal** for all quantities and money (no binary float; `Decimal`/scaled-integer),
  with an explicit scale per currency. Kills edge case 1's non-associativity.
- **Four separate date fields per economic event:** `trade_ts` (event instant), `exchange_trade_date`
  (T), `settlement_value_date` (T+1 India / T+1 US), `tax_recognition_date` (for Rule-115 month
  selection). Kills the "which day's FX" ambiguity (edge 1/3).
- **Native fills immutable.** The native-currency fill is the append-only truth (D15). Nothing ever
  updates it.
- **Rate records are first-class immutable entities**, and `TaxFxRateAssigned` / `LiveFxMarkObserved`
  / `FxMarkCorrected` are **separate events that *reference* a rate-record id** — they never mutate
  the fill and never store a bare number. A live-FX correction is a *new* `FxMarkCorrected` event
  pointing at a new rate record (edge 2/5 fixed; append-only preserved; replay deterministic because
  the log now contains the full ordered history of observations *and* corrections).
- **Rate-source policy fully specified:** source (SBI TTBR for tax; named live source for mark),
  **direction** (INR-per-USD vs USD-per-INR — a silent inversion is a 1/x bug), timestamp,
  **holiday fallback** (deterministic rule, e.g., "last preceding banking day with a published TTBR"),
  **rounding** (round-half-even at declared scale), and **stale-rate behavior** (max age → else
  fail-closed, matching the snapshot discipline in §1). Kills edge 3.
- **Approved FX-lot method** (e.g., FIFO on `IdleFxLot`s per F05/F06) so realized-FX gain has a
  deterministic basis — same input log → same lot matching → same realized FX.
- **All cash events modeled:** fees, taxes, dividends (gross + withholding), remittances,
  repatriations, cash-in-lieu — each an event with native + INR@both-rates. Kills edge 4.
- **Round to venue/broker precision *then* rerun risk/compliance** on the rounded quantities (so the
  numbers risk/compliance saw are the numbers that trade — no post-hoc drift).

With those, replay is a **pure fold** over an immutable, totally-ordered event log using fixed-point
arithmetic and content-addressed rate records → **bit-identical result every replay**. **CONFIRMED.**

### 2.3 Where equity vs realized-FX gains double-count

This is the sharpest part of F13 and it is real. A USD position's INR P&L decomposes into **two
independent sources**: the USD-denominated price move (equity gain) and the INR/USD move (FX gain).
The double-count happens when a naive implementation does *both* of:

- marks the **open** position to INR at the **live** rate (unrealized INR P&L already contains the FX
  component), **and**
- on close, books a **separate realized-FX line** computed over the *same* period from remittance/entry
  FX to exit FX —

without netting out the FX portion already reflected in the marked equity line. The FX move from
entry→exit gets counted **once in the equity mark-to-INR and again in the realized-FX ledger**.

**Correct decomposition (deterministic, no double-count):**
- Equity gain (INR) must be measured at a **held-constant FX** (e.g., the entry/remittance rate, or
  each leg at its own trade-date rate consistently) so the equity line carries *only* the USD price
  move translated at a fixed rate.
- Realized-FX gain is the **separate** ledger line capturing the currency move on the *cost basis*
  (per the approved FX-lot method), computed exactly once at realization against the `IdleFxLot`
  acquisition rate.
- Total INR P&L = equity-in-INR (at fixed rate) + realized-FX. The tax split (equity gain vs FX gain
  taxed differently — D21) then falls out cleanly, and the RiskEngine's live-rate INR conversion (a
  *risk* view for covariance) stays *separate from* the *accounting* books (they must not be summed).

The design must state which rate anchors the equity line and that the RiskEngine live-rate view is a
risk projection, **not** a P&L ledger entry — otherwise the same FX move contaminates both.

### 2.4 Smallest correct design edit (F13, determinism portion)

Add to **D21** (decision-log edit): "All quantities and money are fixed-point decimal at a declared
per-currency scale. Every economic event stores `trade_ts`, `exchange_trade_date`,
`settlement_value_date`, `tax_recognition_date` separately. Native fills are immutable; FX rate
records are immutable first-class entities; `TaxFxRateAssigned`/`LiveFxMarkObserved`/`FxMarkCorrected`
and all cash events (fees, dividends+withholding, remittances, repatriations, cash-in-lieu) are
separate append-only events referencing rate-record ids — never in-place updates. Specify FX rate
source/direction/timestamp/holiday-fallback/rounding/stale-rate behavior and an approved FX-lot
method. **Equity P&L (INR) is measured at a held-constant anchor rate; realized-FX gain is the sole
separate currency-move line; the RiskEngine live-rate conversion is a risk projection, not a ledger
entry — the two are never summed (prevents FX double-count).** Round to venue/broker precision, then
rerun risk/compliance on the rounded quantities." The **LRS/FEMA-legal** aspects (gross-vs-net LRS
amounts, AD-bank certificates, idle-FX repatriation) are the other agent's F13/F05/F06 scope; this
edit is determinism-only.

---

## 3. F19 — Precommitted promotion manifest + restored KG validation

### 3.1 Is post-hoc threshold selection a real p-hacking risk given D10/D10a? — YES

D10a lists the promotion gates *qualitatively*: "minimum decision count met, DSR > 0, max-DD within
tier-1, sim-vs-broker-paper tracking error **within bound**, slippage-model error **within bound**,
both paths beat buy-and-hold net of cost." **Every "within bound" and "minimum" is an unfilled
numeric.** D9b similarly says the calibration N-maturity threshold is "set at design-doc time" but
D9b does **not state a number**, and human-decision #8 in `08` confirms "the decision log requires a
maturity threshold but does not specify one."

**Failure trace (p-hacking / researcher-degrees-of-freedom):**
1. Paper runs 90 days. The operator sees the LLM path had tracking error 1.9% and max-DD 14%.
2. Because no bound was frozen *before* day 1, the operator (even with pure intentions) sets
   "tracking-error bound = 2%, DD band = 15%" *after* seeing the results → the path passes.
3. This is textbook selection-on-the-outcome. It's exactly the failure D10 was built to prevent
   ("largest failure mode = believing false alpha"): freezing prompts/model-ID/config but leaving the
   *acceptance thresholds* floating re-introduces the degrees of freedom through the back door.

**CONFIRMED.** The forward-paper gate is only honest if the *ruler* is fixed before the *measurement*.

### 3.2 Is a precommitted, hashed promotion manifest the fix? — YES

Freeze + hash, **before paper day 1**, a `PromotionManifest` containing:
- all numeric bounds (tracking-error, slippage/cost-model error, DD bands, DSR threshold, min
  decision count, min maturity window, D9b N-maturity threshold);
- the **trial registry** (every strategy/config variant that will be tried — this is the *N* that
  DSR deflates by; see §3.4);
- cost assumptions (the ~$180–730/yr MoA cost, India ~0.24–0.26%/round-trip + DP-per-ISIN from `06`,
  US fees) — so "net of cost" is a fixed function, not a tunable;
- min decision windows / cadence (D9a slowest-signal cadence);
- the **cross-sectional sample definition** (which shock events, which universe, which as-of dates);
- per-sleeve benchmarks (NIFTY for India, SPY for US — the three-way scoreboard's index leg).

Hash it, write it to the D15 event log before the first paper cycle. Promotion evaluation then reads
*only* the manifest's numbers; a changed manifest = a new hash = an admission that the ruler moved
(auditable, and it resets the clock). This is the same content-addressed discipline as F11/§1 applied
to the *acceptance criteria*. **CONFIRMED.**

### 3.3 Did D14's cross-sectional rank-correlation metric + 2020/2022 replays drop out of the spec? — YES

`RESEARCH-STATE.md` D14 ⑥ is explicit: "v1 success metric = **cross-sectional rank correlation on
shock events + historical replays (2020 COVID, 2022 Russia-Ukraine), net-of-cost** — NOT prediction
accuracy." `05` §5 rec 5 makes the historical replay **mandatory** ("Too few live macro shocks in a
paper window → historical replay is mandatory"). The spec's §10 evaluation gate lists CPCV + DSR +
tracking-error + three-way scoreboard but **never mentions cross-sectional rank correlation, and
never mentions the 2020/2022 replays**. §1 success criteria likewise omit them. So the KG's *own*
v1 success metric and its only viable validation track are **absent from the design narrative** —
meaning a 3-quiet-month paper window (no macro shock) would promote the system with the KG's quality
**never tested**. **CONFIRMED** — this is a spec-narrative regression from D14/`05`.

### 3.4 How dependent cross-sectional observations shrink effective N (and why it matters for DSR)

The Deflated Sharpe Ratio (Bailey & López de Prado) deflates an observed Sharpe by the *expected
maximum* Sharpe achievable under **N independent trials** — the more configs you try, the higher the
bar. Two dependence problems bite this design:

1. **Trial-count N (multiple testing).** Each strategy/config/prompt variant tried is a trial. The
   frozen **trial registry** (§3.2) is what pins N *honestly* — otherwise the operator under-reports N
   (claims "1 trial") and DSR is under-deflated → false promotion. So the manifest is a *prerequisite*
   for DSR being meaningful, not merely a p-hacking guard.
2. **Effective sample size < nominal observations (autocorrelation + cross-sectional dependence).**
   DSR also depends on track-record *length* (sample size). But at monthly cadence, 90 paper days ≈
   **3–4 decisions** (D9a) — the nominal N is tiny to begin with. Worse, the KG's cross-sectional
   observations are **not independent**: on a single macro shock (e.g., an oil spike), all
   oil-exposed names move *together* — they share the shock factor. Counting 400 stock-level
   rank observations on one shock day as 400 independent data points massively overstates the sample.
   The **effective N** collapses toward the number of *independent shock events*, not the number of
   (stock × day) cells. With only 2–3 shocks in a quiet quarter, effective N for the KG metric may be
   ~2–3, which is why the 2020/2022 **historical replays are mandatory** — they are the only way to
   raise the independent-shock count. The manifest must therefore **state the effective-N accounting**
   (e.g., cluster observations by shock event; report the count of independent shocks, not raw cells),
   so the DSR trial-count *and* the sample-size term are both computed on honest, dependence-adjusted
   numbers.

**CONFIRMED and load-bearing:** without the effective-N adjustment, both legs of DSR (trial-count
deflation and sample-length) are computed on inflated numbers and the >0 gate is meaningless.

### 3.5 Smallest correct design edit (F19)

Add to **D10a** (decision-log edit) + restore into spec §10/§1: "Before paper day 1, freeze and
content-hash a `PromotionManifest` (all numeric bounds incl. the D9b N-maturity threshold, the trial
registry that fixes DSR's N, cost assumptions, min decision windows, cross-sectional sample
definition, per-sleeve benchmarks) to the D15 log; promotion reads only the manifest. Restore D14's
**net-of-cost cross-sectional rank-correlation** metric and the **mandatory 2020-COVID and
2022-Russia/Ukraine historical replays** as KG-validation gates. State the effective-N accounting:
cluster cross-sectional observations by independent shock event; DSR's sample-length and trial-count
terms use dependence-adjusted counts, not raw (stock × day) cells." **D9b** must also be amended to
state an actual N (currently unspecified — human-decision #8). No v2 pull-in.

---

## 4. F20 — Independent testability: typed ports + offline fakes (design-level only)

### 4.1 Can EVERY §4 component be tested without live broker/LLM/clock/calendar/FX/Neo4j? — YES, by design, once ports exist

Today they **cannot** (F20's premise, confirmed): `CorporateActionMonitor` reaches live Kite,
`GraphStore` needs a live Neo4j, calendar logic reads the real clock, and the D6 contract suite that
"runs against Simulated/Kite/Alpaca" (§10) would place **live orders on Kite (no sandbox** — `06` §3,
`07`, D7). Every §4 component either *is* pure-deterministic already (hot path) or sits behind exactly
one external boundary. Give each boundary a typed port + offline fake and the whole of §4 becomes
unit-testable off-line. The seam invariant (D4) actually *helps*: the hot path is already pure and
reproducible given `(thesis, exposure_vector, portfolio_snapshot, risk_config)` — so `Sizer`,
`RiskEngine`, `ComplianceGate`, `KillSwitch`, `Traversal` need **no** ports at all; they take data in,
data out. The ports are needed only at the *edges*.

### 4.2 Typed-ports / test-doubles inventory (design-level; no code)

| Port (typed boundary) | Backs which §4 component(s) | Real impl | Offline fake — what it makes testable deterministically |
|---|---|---|---|
| **ClockPort** | `Scheduler`, `Watchdog`, `ExitManager` (time-stops), calendar logic | system clock | injectable frozen/steppable time → duplicate scheduler fires, watchdog dead-man timeout, time-stop expiry, DST/holiday edges |
| **CalendarPort** | `Scheduler`, `SessionReadiness`, Phase-A calendar check | NSE/NYSE calendar feed | fixture calendar → Muhurat, unscheduled closure, DST shift, "unknown trading day → fail-closed" |
| **MarketDataPort / CAPort** | `DataIngest`, `CorrectnessLayer`, `CorporateActionMonitor` | Kite/Alpaca/NSE/BSE feeds | recorded OHLCV + CA fixtures → CA >5% cancellation, split/bonus quantity change, revised-CA re-seal, Bhavcopy-mismatch fail-closed |
| **FxRatePort** | D21 accounting, `RiskEngine` | SBI TTBR + live FX source | fixture rates → stale FX, holiday-fallback, live-mark correction, direction/rounding |
| **SecurityMasterPort** | `ComplianceGate`, universe resolution | broker/vendor master | fixture master → ADR/derivative/leveraged-ETF reject (US), delisting, PIT membership |
| **GraphStorePort** | `GraphStore`, `Traversal`, `EdgeWeightFitter` | Neo4j Community | in-memory fixture graph → anti-hub cap, depth-≤3, planted **future-dated edge** look-ahead test (D14a ⑤), motif admissibility — **no Neo4j needed** |
| **EventStorePort** | `EventLog`, reconciliation replay | Postgres append-only | in-memory append-only log → replay-to-identical-state, reconciliation FAIL-CLOSE on injected divergence, idempotent-intent replay |
| **StateCachePort** | `StateCache` | Valkey | in-memory map → projection rebuild-from-log |
| **BrokerTransportPort** | `BrokerAdapter` (Simulated/Kite/Alpaca), `ExitManager` GTT/stop | Kite/Alpaca SDK | scripted transport → **ack-loss**, partial fill, later-partial-fill growth, GTT reject/expire/gap-through-no-fill, CA replacement, token expiry, HALT-races-fill, duplicate submit |
| **LLMRolePort** | `LLMRole`, `Analyst`, `NewsMacroAnalyst`, `MoASynthesizer`, `MetaAnalyst` | Hermes MoA / cheap model | canned structured responses → schema conformance, **extra/prompt-injected LLM fields rejected at seam** (D4/F10), degraded-quorum, all-providers-down, malformed-JSON |
| **SecretsPort / CredentialReadiness** | token refresh, all credentialed jobs | Keychain / encrypted store | fixture creds → Kite `TokenException` → re-auth-required, no-auto-retry, no-exposure-until-reconciled |
| **HITLTransportPort** | `HITLBackend` | Telegram / localhost dashboard | in-memory channel → timeout→default-no-trade, HALT-asymmetry (Telegram HALT / localhost-only un-HALT), HMAC-token binding |
| **NotifierPort** | Telegram alerts, reconciliation report | Telegram | capture sink → alert-on-fail assertions |

**Two test classes (F20's separation, confirmed correct):**
- **Pure contract / mapping tests** — run entirely on fakes + **recorded fixtures**; deterministic; no
  credentials; this is where the D6 ABC contract (idempotent submit, reconcile round-trip, honest
  `capabilities()`), all §6 fail-direction rows, ack-loss, partial fills, GTT/CA/token/FX/DST edges,
  and stale-worker fencing are proven. These run in CI on every commit.
- **Credentialed smoke tests** — a tiny, separately-tagged, opt-in suite proving the *real* adapter
  maps to the same contract. Kept minimal precisely because Kite has no sandbox (see §4.3).

### 4.3 Kite has NO sandbox — how is the contract suite run safely?

This is the concrete hazard F20 raises and the current §10 wording ("one suite runs against
Simulated / Kite / Alpaca") would, run naively, **place live Kite orders**. The safe design:

1. **The full contract suite runs against `SimulatedBrokerAdapter` and Alpaca-paper** (both have safe
   non-live modes; Alpaca's free identical-API paper is the D8 load-bearing gift). This is where
   idempotency, reconcile round-trip, ack-loss, partial fills, and all edges are *proven*.
2. **The Kite contract obligations are proven against a `BrokerTransportPort` fake driven by recorded
   Kite fixtures** (real Kite response payloads captured once, then replayed) — this tests the
   Kite *mapping/adapter* logic (canonical `OrderRequest` ↔ Kite fields, exception taxonomy →
   fail-direction, GTT semantics) **without any live order**.
3. **A minimal credentialed Kite smoke test** exercises only **non-order, idempotent, read/safe**
   endpoints (auth/token, `get_positions`, `get_account`, quote) — never `place/modify/cancel` against
   the live market — plus, at most, a manually-gated one-off order placement/cancellation on a
   disposable balance far outside market hours or at a price that cannot fill, run by a human, never
   in CI. The design rule: **CI never touches Kite order-placement; live-order verification is a
   human-gated, disposable-balance, out-of-band step**, matching D7 ("Sim is primary vehicle … Kite
   has NO sandbox") and the D22 disposable-balance posture.

So the contract *guarantee* is split: **behavior** is proven on Simulated + Alpaca-paper + Kite
fixtures (deterministic, CI-safe); **wire-fidelity** to live Kite is a tiny read-only/manual-gated
smoke suite. No live order ever fires from an automated test. **CONFIRMED with the added run-safety
rule.**

### 4.4 Smallest correct design edit (F20)

Spec §4/§10 edit (no D-log change): "Every external boundary is a typed port with an offline fake
(clock, calendar, market-data/CA, FX, security-master, graph-store, event-store, state-cache,
broker-transport, LLM-role, secrets/credential, HITL-transport, notifier). Separate **pure
contract/mapping tests** (fakes + recorded fixtures, CI, no credentials — proving the D6 ABC, every §6
fail-direction, ack-loss, duplicate scheduler fires, partial/later-partial fills, GTT
reject/expire/gap-through, CA replacement, token expiry, stale FX, DST/holiday edges, extra-LLM-field
rejection, stale-worker fencing) from **credentialed smoke tests**. **Because Kite has no sandbox, the
Kite contract suite runs against Simulated + Alpaca-paper + recorded-Kite fixtures; CI never places a
live Kite order; live-order wire-fidelity is a human-gated, read-only-plus-manual, disposable-balance,
out-of-band step.**" No new D-log decision required (it operationalizes D3/D6/D7/D10/D15).

---

## 5. Human decision flagged from this pass

**D11 vs D20 (human-decision #7 in `08`) — surfaces directly in F11's active-signal manifest.**
D20 disables the quality proxy (haircut to zero) until a restatement-free PIT fundamentals vendor
exists; D11 defines the permanent rule-based null as a *momentum + trend + **quality proxy** + regime*
composite that trades live forever. If the snapshot honestly marks quality DISABLED, the null cannot
be the D11 four-factor composite. **Decision required:** either (a) redefine the null (and the D10a
three-way scoreboard) as a 3-factor momentum+trend+regime composite while quality is disabled — the
snapshot manifest then enforces it and re-enables quality only when PIT clears — or (b) accept a
quality proxy on non-PIT data for the null only (contradicts D20's anti-false-alpha stance). Do not
silently resolve. The `ValidatedDataSnapshot` active-signal manifest is the enforcement point for
whichever is chosen, but the choice is a human/D-log decision.

---

## 6. Per-finding summary table

| Finding | Verdict | Failure trace (shortest) | Smallest correct edit | D-log change |
|---|---|---|---|---|
| **F11** | **CONFIRMED** | Late CA revision mutates `latest`; signals read post-validation rows; replay diverges. US sleeve passes Phase A with no independent CA/delisting/PIT-membership source. | Phase A emits content-addressed `ValidatedDataSnapshotId` (raw/split-adj/total-return OHLCV + CA/dividend/delisting ledger + PIT universe + calendar + news-cutoff + KG-edge version + FX set + enabled-signal manifest w/ per-factor series binding); every consumer requires the token, cannot read `latest`; add independent **US** CA/delisting/PIT-membership source. | **D20 amend** |
| **F13** (determinism) | **CONFIRMED** | Float non-associativity + in-place fill updates + holiday-missing Rule-115 rate + omitted cash events → replay diverges; equity mark-to-INR + separate realized-FX line double-count the same FX move. | Fixed-point money; 4 separate date fields; immutable native fills; immutable rate records; FX-observations/corrections/cash-events as append-only events referencing rate ids; full rate-source policy; FX-lot method; equity P&L at anchor rate vs realized-FX-only line vs risk-view live rate (never summed); round-then-rerun. | **D21 amend** |
| **F19** | **CONFIRMED** | No pre-frozen bounds → thresholds chosen after seeing paper results (p-hacking); quiet quarter has no macro shock → KG quality never tested; naive DSR under-deflated (N under-reported) and sample inflated (dependent cross-sectional cells). | Pre-paper hashed `PromotionManifest` (bounds + trial registry + costs + windows + sample def + benchmarks + D9b N); restore D14 cross-sectional rank-correlation + mandatory 2020/2022 replays; state effective-N = independent-shock clustering for both DSR terms. | **D10a amend; D9b (state N); restore D14 into spec** |
| **F20** | **CONFIRMED** (+ run-safety rule) | `CorporateActionMonitor`→live Kite, `GraphStore`→Neo4j, calendar→real clock, contract suite→live Kite orders (no sandbox). | Typed port + offline fake per boundary; pure contract/mapping tests (fakes+fixtures, CI) vs credentialed smoke; Kite behavior proven on Simulated + Alpaca-paper + recorded-Kite fixtures; **CI never places a live Kite order**; live-order wire-fidelity is human-gated/read-only/disposable/out-of-band. | **No D-log change** (spec §4/§10 build-out) |

---

## 7. Minimum `ValidatedDataSnapshot` contents spec — consolidated (India + US)

`snapshot_id = H(canonical_manifest)`; manifest = ordered list of `(component, content_hash, version,
as_of_date, source)`. Emitted as the last Phase-A act; required argument to every signal / `Traversal`
/ sim / eval; any missing/stale/future-dated/post-seal-revised required component → invalid (fail-closed).

- **Raw OHLCV** (both sleeves) — unadjusted, all bars ≤ as_of.
- **Split/bonus-adjusted OHLCV** — recomputable from raw + CA factors in-snapshot.
- **Total-return OHLCV** — dividends reinvested; distinct from split-adjusted.
- **CA-factor + dividend + cash-in-lieu ledger** — India: NSE/BSE independent of Kite, validated vs
  Bhavcopy on ≥3–5 known events. **US: independent vendor vs broker (symmetric requirement).**
- **Delisting/corporate-death ledger** — India: NSE/BSE notices. **US: independent source.**
- **PIT universe membership** — India: NIFTY 500 + liquidity floor with add/drop history. **US:
  PIT-membership list with add/drop history (not a static "defined list").**
- **Market calendar** — India NSE (holidays/Muhurat); US NYSE/NASDAQ (+DST); unknown session → invalid.
- **News cutoff** — no item > cutoff visible to the KG classifier.
- **KG edge-set version** — only edges with `valid_from ≤ as_of` (anti-look-ahead).
- **FX rate set** (US) — pinned rate-record ids; Rule-115 (SBI TTBR last-prior-month, holiday-fallback)
  and live mark stored separately.
- **Enabled-signal manifest** — ACTIVE signals + per-factor series binding (momentum/trend→total-return;
  cross-split level→split-adjusted; sim microstructure→raw). **Quality proxy = DISABLED until PIT
  fundamentals clear D20** (enforcement point for the D11-vs-D20 human decision).

---

## 8. Typed-ports / test-doubles inventory — consolidated

ClockPort · CalendarPort · MarketDataPort/CAPort · FxRatePort · SecurityMasterPort · GraphStorePort ·
EventStorePort · StateCachePort · BrokerTransportPort · LLMRolePort · SecretsPort/CredentialReadiness ·
HITLTransportPort · NotifierPort. Pure hot-path units (`Sizer`, `RiskEngine`, `ComplianceGate`,
`KillSwitch`, `Traversal`, `EdgeWeightFitter`) need **no** port — they are already
data-in/data-out deterministic under D4. Two test classes: pure contract/mapping (fakes + recorded
fixtures, CI, no creds) vs credentialed smoke (minimal, opt-in). Kite order-placement is never in CI.

---

## 9. Self-audit

All four assigned findings (F11, F13-determinism, F19, F20) verified: **all CONFIRMED** (F13 scoped
to determinism/accounting only, LRS-legal portion left to the owning agent; F20 confirmed with an
added Kite-run-safety rule). Each carries a concrete failure trace, the smallest correct design edit,
and its RESEARCH-STATE.md impact (D20, D21, D10a/D9b + D14-restoration for F11/F13/F19; none for F20).
Minimum `ValidatedDataSnapshot` contents (India + US) and the typed-ports/test-doubles inventory are
provided. D4 invariant respected throughout (no LLM number added to any hot-path or accounting number;
snapshot/manifest/ports are all deterministic). No v2 items pulled into v1 (no auto-KG-edge admission,
no `WebResearchSpoke`, no IBKR). The **D11-vs-D20** human decision (null quality proxy vs disabled
quality) is flagged (§5), not silently resolved. Spec and RESEARCH-STATE.md were **not** edited.
Two external sources touched (survivorship magnitude carried from `06`; DSR mechanics confirmed);
remainder is design reasoning. Report saved to `docs/research/09f-data-snapshot-testability.md`.
