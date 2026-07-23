# 09d — D4 Seam / Type-Safety Adversarial Analysis (F01, F02, F10, F18)

> **Status:** Analytic finding-cluster report. No implementation, no spec/decision-log edits.
> **Date:** 2026-07-20.
> **Cluster:** D4 seam-leak — F01 (conviction→Kelly), F02 (LLM KG magnitude/confidence→traversal),
> F10 (seam not encoded by interfaces), F18 (D14a graph-admission gates dropped from spec narrative).
> **Spec under review:** `docs/superpowers/specs/2026-07-20-trading-os-design.md`
> **Authoritative decisions:** `docs/research/RESEARCH-STATE.md` (D4, D5, D9b, D14, D14a, D24).
> **Method:** numeric seam-tracing over the design's own data flow (§5 Phase A–F) + §9 sizing/risk +
> §3 planes. Web grounding on schema-strictness enforcement mechanisms only (see §7).

## The invariant being tested (D4, verbatim scope)

> LLMs propose; deterministic code disposes. No LLM-derived **scalar, ordinal class, calibrated
> bucket, rationale, confidence, magnitude, expected return, vol estimate, or hidden field** may
> set or alter **quantity, price, risk limits, exit thresholds, or compliance**. Conviction may
> **GATE / RANK only — never scale size, directly or indirectly.**

The operative word is **indirectly**. A value that is LLM-derived does not stop being LLM-derived
because a deterministic function is applied to it. `f(x)` where `x` is an LLM output is still an
LLM-derived number if `f` is injective / monotone in `x` over the operating range. That is the lens
used throughout.

---

## Executive verdict for this cluster

| Finding | Verdict | Leak real? | Proposed edit closes it? | RESEARCH-STATE.md must change? |
|---|---|---|---|---|
| **F01** conviction→Kelly ceiling→qty | **CONFIRMED** (leak is real) + **NEEDS-HUMAN-DECISION** (fix conflicts with D5/D9b) | Yes — two identical candidates, different buckets → different permitted qty | Eval-only fix closes it; but it directly contradicts D5's "¼-Kelly ceiling fed by calibration store at mature N" and D9b's "may feed the D5 ceiling" | **Yes** — D5 + D9b, not just spec narrative |
| **F02** LLM magnitude/confidence & edge-conf → traversal → exposure vector | **CONFIRMED** | Yes — LLM scalar is multiplied into `exposure(C,M)=Π(edge_conf)·β^hops·γ^days·magnitude_class_weight`; deterministic arithmetic does not launder provenance | Proposed edit (closed categoricals + deterministic evidence-confidence policy + `EdgeWeightFitter` sole numeric source) **fully closes** the leak and **preserves** the causal-KG value | **Yes** — D14 §⑤ and D14a `confidence`, if those fields were meant to be LLM-supplied numeric/ordinal |
| **F10** seam not encoded by interfaces | **CONFIRMED** | Yes — `TradeThesis{conviction,direction,rationale}` is a permissive shape; nothing structurally blocks `target_vol`/`stop_hint` or downstream `rationale` parsing | Two-type split (`ResearchTradeThesis` in Plane 1 + deterministic projector → `HotPathCandidate` closed-enum, `additionalProperties=false`) **is** the minimal enforceable encoding; needs boundary strict-validation (see §7) | **No** — this is an *encoding* of D4 already locked; spec narrative + interface contracts change, decision log does not (add a clarifying note only) |
| **F18** D14a admission gates missing from spec narrative | **CONFIRMED** | N/A (documentation-integrity leak, not numeric) | Restore the six gates into §3/§4/§11 narrative | **No** — all six gates are *present and correct* in D14a; only the spec narrative dropped them. Spec-only fix. |

**Two conflicts are flagged as HUMAN DECISIONS and are NOT resolved here:**
- **HD-1 (D4 vs D5/D9b):** D5/D9b explicitly wire the CalibrationStore into a live ¼-Kelly *ceiling*
  keyed by conviction bucket. F01's fix (evaluation-only store) removes that wire. The invariant and
  the two decisions cannot both stand as written. Human must choose.
- **HD-2 (D4 vs D14/D14a):** D14 §⑤ shock taxonomy and D14a admission both name a `confidence`
  (and D14 §⑤ a `magnitude`) field. If those are LLM-emitted numeric/ordinal values consumed by
  traversal, they leak. Human must confirm whether they were ever meant to be LLM-supplied numbers.

---

## 1. Numeric seam traces

### (a) F01 — conviction_bucket → CalibrationStore → ¼-Kelly ceiling → quantity

**The wire, per spec + decisions:**
- §9: "Kelly demoted to a **¼-Kelly ceiling only, fed exclusively by the `CalibrationStore`** once a
  conviction bucket is mature (D9b: Beta-Bernoulli shrinkage above an explicit N-threshold)."
- D9b schema: `(model, prompt_version, conviction_bucket, market, regime, hit_rate, payoff,
  sample_n, estimated_at)`. Write-path: each closed position writes realized outcome **keyed by the
  conviction bucket at entry**. "A bucket is 'mature' (may feed the D5 ¼-Kelly ceiling) only above
  an explicit N-threshold."
- Kelly fraction `f* = (b·p − q)/b` where `p = hit_rate`, `q = 1−p`, `b = payoff`. The ceiling is
  `qty ≤ ¼·f*·(equity/price)` (or an equivalent notional cap).

**The trace (numeric):**
```
conviction_bucket  = LLM/MoA output (an ordinal class emitted by the synthesizer)
        │  (used as a table KEY — this is the leak vector)
        ▼
CalibrationStore.lookup(model, prompt_version, conviction_bucket=HIGH,  market, regime)
        → (hit_rate_H, payoff_H, sample_n ≥ N)          # mature bucket
CalibrationStore.lookup(..., conviction_bucket=MEDIUM, ...)
        → (hit_rate_M, payoff_M, sample_n ≥ N)          # different row
        │
        ▼
f*_H = (b_H·p_H − q_H)/b_H          f*_M = (b_M·p_M − q_M)/b_M
        │                                   │
        ▼                                   ▼
ceiling_H = ¼·f*_H·equity/price     ceiling_M = ¼·f*_M·equity/price
        │                                   │
        ▼                                   ▼
qty_H = min(base_size, ceiling_H)   qty_M = min(base_size, ceiling_M)
```
**Counterexample that proves the leak:** take two *identical* candidates — same symbol, same
`base_size` from fixed-fractional × vol-target, same price, same caps — differing **only** in the
LLM conviction bucket (HIGH vs MEDIUM). If `p_H > p_M` at mature N (which is exactly the empirical
relationship the store is built to capture and the reason it is consulted), then
`f*_H > f*_M ⇒ ceiling_H > ceiling_M`. Whenever the ceiling binds (`ceiling < base_size`),
`qty_H > qty_M`. **The LLM-emitted ordinal changed permitted quantity.** That is D4's "may not
alter quantity … directly or indirectly" — violated indirectly, through a deterministic Kelly
function of an LLM-keyed statistic.

The determinism of Beta-Bernoulli shrinkage and of the Kelly formula is irrelevant: the *key* into
the statistic is the LLM class, so the output number is a monotone function of the LLM output. This
is the same "deterministic arithmetic does not launder provenance" argument as F02.

**Note — the leak is *worse* than "conviction scales size":** D5 forbids conviction *scaling*
size, but the calibration ceiling lets conviction *cap* size differently per bucket. A cap that
differs by LLM class is still the LLM class altering the permitted number. It merely leaks through
the `min(base, ceiling)` operator instead of a multiply.

**Does the F01 fix (CalibrationStore evaluation-only in v1) close it?** Yes, completely. If
`Sizer`, `RiskEngine`, `ExitManager`, `ComplianceGate` are forbidden from reading *any* statistic
keyed by `model | prompt_version | conviction_bucket | thesis_id` (or any other LLM output), there
is no wire from bucket → number. The store still records `thesis → outcome` for later maturity
scoring (§5 step 14 is preserved as a *write-only-then-read-by-humans/eval* path).

**Conflict → HD-1.** This fix **contradicts D5 and D9b as written**. D5 says the ceiling is "fed
exclusively by the calibration store once conviction buckets have mature realized hit-rates"; D9b
says a mature bucket "may feed the D5 ¼-Kelly ceiling." Both decisions *intend* the exact wire that
F01 identifies as the leak. Therefore **editing the spec narrative is insufficient — D5 and D9b
must be amended** (or the invariant relaxed). Do not silently resolve: this is a human decision
about whether a *calibrated, empirically-mature* per-bucket statistic counts as "LLM-derived" for
D4 purposes. (Adversarial reading: yes, because the bucket label is LLM-authored and the whole
point of keying on it is that different labels yield different sizes.)

### (b) F02 — MacroEvent{magnitude, confidence} → Traversal → exposure_vector → risk tilt / allowed position

**The wire, per spec + decisions:**
- §3 / D14 §⑤: LLM `NewsMacroAnalyst` classifies news into
  `MacroEvent{driver, source, phase, direction, magnitude, confidence}`.
- 05-synthesis §2 Layer-1 traversal scoring:
  `exposure(C,M) = Π(edge_conf) · β^hops · γ^days_since · magnitude_class_weight`.
- §5 step 8: `RiskEngine → … exposure-vector defensive tilt; may shrink or veto.`

**The trace (numeric):**
```
MacroEvent.confidence = c_llm  ∈ [0,1]   (LLM-emitted scalar)
MacroEvent.magnitude  = m_llm            (LLM-emitted scalar or ordinal)
        │
        ▼   (Traversal is "deterministic" but multiplies the LLM scalar in)
exposure(C,M) = [Π edge_conf] · β^hops · γ^days · w(m_llm)          # and/or × c_llm
        │
        ▼
exposure_vector[C]  (per-stock)
        │
        ▼   §5 step 8
RiskEngine defensive tilt: allowed_position[C] = g(exposure_vector[C], caps, VaR)
```
**Counterexample that proves the leak:** hold the graph, the event class, hops, and days fixed;
let the LLM emit `confidence = 0.9` vs `0.4`, or `magnitude = HIGH` vs `LOW`. Because `exposure`
is *monotone increasing* in both `c_llm` and `w(m_llm)`, the exposure vector changes, so the
defensive tilt / allowed position changes. **An LLM-emitted scalar altered a risk-limit-adjacent
number.** D4 names "confidence" and "magnitude" *explicitly* in its prohibited list — this is a
textbook violation. "Deterministic traversal" is a red herring: `Π(edge_conf)·β^hops·γ^days·w(m)`
is deterministic *in its inputs*, but one of its inputs is an LLM scalar, so the output is
LLM-derived.

Same structure applies to **LLM-authored edge confidence** (path c): if the offline meta-analyst's
proposed `edge_conf` becomes the numeric weight in `Π(edge_conf)`, then LLM-chosen numbers set the
exposure magnitude. D14a's human-approval gate reduces *how often* a bad edge enters, but a
human clicking "approve" on an LLM-proposed *confidence number* does not convert that number into a
non-LLM number — the human approves admission, not the calibration of the scalar.

**Does the F02 fix close it? — YES, fully, and it preserves the KG's value.** The proposed edit:
1. **`MacroEventLabel` = CLOSED CATEGORICAL only:** `driver`, `source∈{supply,demand,uncertainty}`,
   `phase∈{threat,act,escalation}`, `direction∈{+,−}`. **No LLM `magnitude`, no LLM `confidence`.**
2. **`EdgeProposal` = endpoints + relation + citations only.** No LLM `weight`, no LLM `confidence`.
3. **A DETERMINISTIC policy assigns evidence-confidence** from `source_type`, `corroboration_count`,
   `age`, `admission_state` — a pure function of *observable metadata*, identical for any author.
4. **`EdgeWeightFitter` (offline, mini-GVAR per driver class) is the ONLY numeric-weight source;**
   D14 already mandates weights are fitted offline and *never* seeded from price correlation.

Why this fully closes it: after the edit, every number entering `exposure(C,M)` is either (i) a
deterministic function of *categorical* LLM labels (a label selects a *versioned, code-owned*
`magnitude_class_weight` and `sector_prior` — the label is a GATE/selector, not a scalar), or
(ii) an offline-fitted weight from `EdgeWeightFitter`, or (iii) a deterministic
evidence-confidence from metadata. **No LLM-emitted scalar survives into the arithmetic.** The
KG still does its D14 job — "know your macro exposure, tilt defensively, surface beneficiaries" —
because the *structure* (edges, motifs, taxonomy) is still LLM/human-authored; only the *numbers*
are code-owned. This is exactly the two-layer split D14 already claims to enforce; F02 is the part
of that split that the `{magnitude, confidence}` fields quietly broke.

**Residual leak check (is a categorical label still a covert scalar?):** A closed enum with K
levels mapping to K code-owned weights is *bounded and auditable* — the LLM picks among K
pre-vetted rungs, it cannot emit an arbitrary real. This is the same status as "conviction gates/
ranks": the label **selects a bucket** but does not **author the number in the bucket**. That is
D4-compliant **iff** the mapping table is versioned, unit-tested, and identical across events
(a GATE/RANK use). One residual to watch: if `magnitude_class_weight` has many fine rungs
(effectively continuous), the enum degenerates back toward a scalar. **Keep the magnitude class
to a small fixed ordinal set (e.g. 3 rungs) with code-owned weights** so it stays a gate, not a
dial. Flag this as the single residual to nail in the interface contract; it does not reopen the
leak if the rung count is small and fixed.

**Conflict → HD-2.** D14 §⑤ literally lists `magnitude, confidence` in the MacroEvent schema, and
D14a repeatedly says "edge confidence >0.5", "every edge carries … confidence." If those were
intended to be **LLM-supplied** numeric/ordinal values feeding traversal, **D14 and D14a must be
amended** to (a) strike LLM `magnitude`/`confidence` from `MacroEvent`, and (b) redefine edge
`confidence` as a *deterministic* function of source-type/corroboration/age rather than an
LLM-authored number. If instead the design always intended `confidence` to be the deterministic
evidence-confidence (author proposes text+citations; code computes confidence), then D14/D14a need
only a *clarifying* amendment, not a substantive one. **Human must confirm the intent.**

### (c) rationale / extra JSON fields crossing a permissive schema (feeds F10)

**The wire:** §3 / §4 store `TradeThesis{conviction, direction, rationale}`; §5 step 6 says the
`TradeThesis` "crosses into the hot path." §8/D13 stores "LLM outputs (JSONB)" in Postgres.
**The leak:** a JSONB blob + a free-text `rationale` are *permissive by construction*. Nothing
structural stops (i) a future prompt from adding `target_vol`, `stop_hint`, `size_pct`, or a nested
`extras{}` that a later `Sizer`/`ExitManager` revision reads; or (ii) downstream code from
regex/LLM-parsing `rationale` for a number ("target 12% vol"). Both are D4 violations that the
*type* does not currently prevent — "merely omitting a `size` field is inadequate" (F10). Traced
fully in §1(d)/§2 below.

---

## 2. F10 — is the two-type split the minimal enforceable encoding, and what boundary enforcement is needed?

**The split (proposed):**
- `ResearchTradeThesis{thesis_id, conviction, direction, rationale, …}` — **stays entirely in
  Plane 1.** Never imported by any hot-path module.
- A **deterministic projector** (Plane-1→seam, no LLM) emits
  `HotPathCandidate{thesis_id, conviction_band: enum, direction: enum}` — closed enums,
  `additionalProperties=false`, no rationale, no raw JSON.
- **`Sizer` accepts neither thesis type.** It accepts an *admitted* `symbol` + `direction` +
  **deterministic** market/portfolio/risk inputs. `conviction_band` is consumed **only** by the
  gate/rank stage (trade/no-trade + ordering), never by the sizing arithmetic (D5).

**Verdict: this is the minimal enforceable encoding.** It is minimal because it (a) removes the
only two leak surfaces — permissive fields and rationale reachability — without adding machinery,
and (b) turns D4 from a *convention* ("we promise not to read the number") into a *type property*
("the number/rationale is structurally unreachable downstream"). Anything less (e.g. keeping one
thesis type but adding a linter) is convention, not encoding, and fails F10's own test.

**Schema-level enforcement required at the boundary (grounded in §7):**
1. **`additionalProperties: false`** on `HotPathCandidate` and every nested object — reject *any*
   field not in the closed set. (This is exactly what OpenAI strict-mode structured output *also*
   mandates, so the two align: the LLM's structured output can be validated the same way.)
2. **All fields required, closed enums** for `conviction_band` and `direction` — no optionals, no
   open strings. (Pydantic: `enum` types; OpenAI strict: all-required + `enum`.)
3. **Reject extra fields at parse time** — Pydantic `model_config = ConfigDict(extra='forbid')`
   raises on any unexpected key (default `'ignore'` would *silently drop* an injected `target_vol`
   — still safe for the number, but `'forbid'` fails loudly and is the auditable choice; never
   `'allow'`, which would store it in `__pydantic_extra__` and make it reachable).
4. **Reject non-finite numbers** — even though `HotPathCandidate` carries *no* free numeric field,
   any numeric field anywhere on the seam (e.g. an exposure-vector transport type) must set
   `allow_inf_nan=False` (Pydantic `Field`) so `nan`/`inf` cannot poison a downstream `min`/compare
   (a `nan` silently defeats `min(base, ceiling)` and every risk comparison).
5. **`frozen=True` / immutability** on the projected candidate so no later stage can mutate it.
6. **No JSONB/rationale on the seam type at all** — the raw LLM JSON and `rationale` live only in
   the Plane-1 store; the hot path is given the projected type by value, with no handle to the
   originating row. `thesis_id` is an opaque audit key, not a fetch-the-blob capability for
   hot-path code.
7. **Boundary test (mirrors F20 / spec §10):** a prompt-injection test that feeds an
   `AnalystReport`/thesis carrying `target_vol`, `stop_hint`, `size_pct`, and a nested `extras{}`,
   and asserts the projector/loader **rejects or structurally drops** them and that no hot-path
   type can even *represent* them.

**Decision-log impact: none.** D4 already *is* "no number crosses; enforced by type." F10 is the
faithful *encoding* of D4, not a change to it. The spec narrative (§3/§5) and the interface
contracts change; RESEARCH-STATE.md needs at most a one-line clarifying note that the seam type is
`HotPathCandidate` (closed) and `ResearchTradeThesis` never crosses.

---

## 3. F01 fix assessment — evaluation-only CalibrationStore

Covered numerically in §1(a). Summary of the assessment the task asked for:

- **Is eval-only the right fix?** For upholding D4 as written, **yes** — it is the *only* fix that
  removes the wire entirely; any "use deterministic variables instead of conviction to key the
  ceiling" alternative still needs a new design decision (F01 says so) and still risks re-keying on
  a correlate of conviction.
- **Does it conflict with D5/D9b?** **Yes, squarely.** D5 = "¼-Kelly ceiling fed by the calibration
  store once buckets are mature"; D9b = mature bucket "may feed the D5 ¼-Kelly ceiling." The fix
  deletes precisely that path. → **HD-1, human decision.** Recommended framing for the human: keep
  the CalibrationStore as an *evaluation/monitoring* instrument for v1 (it still answers "are HIGH
  buckets actually more profitable?"), and treat "let a mature bucket move the ceiling" as a
  **separate, later, explicitly-argued decision** that must first show the bucket is a *calibrated
  probability* (the exact property the MoA red-team said an LLM conviction is **not** — see
  RESEARCH-STATE "Kelly = RISKIEST decision").
- **Not resolved here.** Flagged only.

---

## 4. F18 — which D14a gates are present in RESEARCH-STATE.md but MISSING from the spec narrative

**All six D14a gates are present and correct in RESEARCH-STATE.md (D14a, lines ~35).** The spec
narrative (§3 lines 71–82, §4 lines 101–107, §11 lines 287–291) mentions only a subset. Gate-by-gate:

| D14a gate (authoritative) | In RESEARCH-STATE.md? | In spec narrative? | Status |
|---|---|---|---|
| **① Human-approval queue** for meta-analyst edges (paper + early live) | Yes | **Partial** — §4 line 101 "human-approval queue (provenance + 2nd source + confidence)"; §3 line 78 "human-gated" | Mentioned but thin |
| **② 2nd corroborating source required before confidence > 0.5** | Yes | **MISSING** — the "0.5 confidence" threshold and "2nd independent source" rule appear nowhere in §3/§4/§11 (only "2nd source" is name-dropped in §4 line 101 with no threshold) | **Dropped** |
| **③ Mandatory text provenance (no citeable source ⇒ edge blocked from traversal)** | Yes | **Partial** — §3 line 74 & §4 line 105 say edges carry "provenance"; the *blocking* rule ("no source ⇒ traversal-ineligible") is **absent** | **Rule dropped** |
| **④ Measured LLM edge-precision bar (~0.85 on ~200 expert-labeled claims) before edges enter Layer-1** | Yes | **MISSING** from §3/§4; appears **only** in §11 line 290 as "auto-add-above-threshold … once edge-precision is measured on a held-out set" — but that frames it as a *v2 auto-add* precondition, **not** a *v1 Layer-1 admission* bar | **Dropped / mis-scoped** |
| **⑤ As-of dating `valid_from ≤ prediction_date` + `last_confirmed`, unit-tested vs planted future edges** | Yes | **Partial** — "as-of dates" in §3 lines 74–75 & §4 line 105; the **planted-future-edge look-ahead test** *is* in §10 line 268 ("planted future-dated edge test … D14a"); but `last_confirmed` and the explicit `valid_from ≤ prediction_date` rule are **absent from the narrative** | Test present; the two dating fields + rule dropped |
| **⑥ Auto-decay ~30%/yr for unconfirmed edges; authoring must DEPRECATE not only add** | Yes | **MISSING** — neither the 30%/yr decay nor the "deprecate, not only add" duty appears in §3/§4/§11 | **Dropped** |

**Confirmed: F18 is correct.** The gates most consequential for fake-alpha prevention — **②
(2nd-source>0.5), ③ (provenance-blocks-traversal), ④ (0.85 precision bar as a v1 Layer-1 gate),
⑥ (30%/yr decay + mandatory deprecation)** — dropped out of the spec narrative, and **⑤**'s two
dating fields are only half-present (the unit-test survived, the field/rule wording did not).

**Decision-log impact: none.** D14a is intact and authoritative; only the **spec narrative** must be
corrected to restore the six gates (per the doc's own rule: "Where this doc and the decision log
disagree, the decision log wins and this doc is corrected"). This is a **spec-only** fix — **do not
edit D14a**. Note the interaction with F02: gate ② speaks of "edge confidence > 0.5", which is
exactly the `confidence` field HD-2 must reclassify as *deterministic evidence-confidence*; restore
gate ② with that reading so F18's restoration does not re-introduce F02's leak.

---

## 5. SEAM AUDIT — every field allowed to cross slow→fast, every deterministic consumer

**Crossing surface (§5 Phase C, step 6):** exactly two objects cross the boundary together — the
projected candidate and the exposure vector.

### 5.1 Fields ALLOWED to cross (post-fix)

| # | Field | Type | Origin | Crosses as | Consumer(s) | Permitted use | D4 basis |
|---|---|---|---|---|---|---|---|
| 1 | `thesis_id` | opaque id | Plane-1 | audit key | EventLog only | audit/attribution; **no fetch-blob capability** | not a number |
| 2 | `conviction_band` | closed enum (e.g. LOW/MED/HIGH) | LLM/MoA (label) | `HotPathCandidate` | **Gate/Rank stage only** | trade/no-trade + candidate ordering | GATE/RANK, never scales size (D5) |
| 3 | `direction` | closed enum {LONG} (long-only v1) | LLM/MoA (label) | `HotPathCandidate` | Sizer (as sign only), Compliance | selects side; long-only whitelist still enforced | categorical, not a magnitude |
| 4 | `exposure_vector[symbol]` | float per stock | **deterministic `Traversal`** | vector | RiskEngine (defensive tilt) | shrink/veto/tilt within code-owned caps | every input to it is code-owned or a categorical label→code-owned weight (post-F02) |

**Explicitly NOT allowed to cross (must be structurally unreachable downstream):**
`rationale`, raw LLM JSONB, any `magnitude`/`confidence` LLM scalar, `target_vol`, `stop_hint`,
`size_pct`, expected return, vol estimate, any `hit_rate`/`payoff`/Kelly statistic keyed by
model/prompt/conviction/thesis (F01), any nested `extras{}`/provider-specific field (F10),
any non-finite number.

### 5.2 Every deterministic hot-path consumer and what it may read

| Consumer (§4) | May read (post-fix) | May NOT read |
|---|---|---|
| **Gate/Rank** (pre-Sizer) | `conviction_band` (trade/no-trade + order), `direction` | any numeric statistic keyed by an LLM output |
| **Sizer** (§5.7) | `symbol`, `direction` (sign), fixed-fractional %, vol-target, price, caps, portfolio snapshot | `conviction_band` **as a scale**; CalibrationStore (F01); rationale; any LLM scalar |
| **RiskEngine** (§5.8) | `exposure_vector`, INR-numeraire covariance, cluster caps, VaR/CVaR | LLM `confidence`/`magnitude`; calibration statistics keyed by LLM output |
| **ComplianceGate** (§5.9) | order, account flags, D19 rule set (deterministic) | any LLM output; any calibration statistic |
| **ExitManager** (§5.11) | fill, ATR, time-stop, regime (HMM), broker stop id | LLM output; conviction; calibration statistic |
| **KillSwitch** (§5.10) | DD/vol bands (calibration *of thresholds* is code-owned, not LLM-keyed) | LLM output |

### 5.3 Proof: changing any DISALLOWED LLM field cannot alter quantity/price/exits/risk/compliance

Let `Q, P, X (exits), R (risk limits), Comp` be the protected outputs. Post-fix, each is a pure
function of only the allowed inputs above:

- **`Q = Sizer(symbol, direction, fixed_frac, vol_target, price, caps, portfolio)`.** None of its
  arguments is an LLM scalar, and (F01 fix) it does not read any calibration statistic keyed by an
  LLM output. `conviction_band` reaches only the *gate/rank* stage, which is upstream of `Sizer`
  and can only *drop* or *reorder* a candidate — a boolean/ordering, not a term in the size
  arithmetic. ∴ `∂Q/∂(any disallowed LLM field) = 0`.
- **`R`-adjacent `exposure_vector`** is, post-F02, a function of code-owned fitted weights,
  categorical-label→code-owned-weight selectors, and deterministic evidence-confidence — **no LLM
  scalar term remains** — so perturbing an LLM `confidence`/`magnitude` field has no path into it
  (the field no longer exists on the label). ∴ `∂R/∂(LLM scalar) = 0`.
- **`P, X, Comp`** consume no LLM output at all (table above). ∴ unaffected by construction.
- **Structural backstop (F10):** the disallowed fields are **not representable** on any hot-path
  type (`additionalProperties=false`, `extra='forbid'`, no rationale/JSONB handle). A value that
  cannot be represented cannot be read; a field that cannot be read cannot appear in any of the
  functions above. This converts the four "∂=0" claims from *convention* into *type-level
  guarantees* — which is the whole point of F10.

**The proof holds only if all four fixes land together.** Gaps if any is skipped:
- Skip F01 ⇒ `Q` regains a conviction-keyed Kelly ceiling term (leak (a) reopens).
- Skip F02 ⇒ `exposure_vector` regains an LLM `confidence`/`magnitude` term (leak (b)/(c) reopens).
- Skip F10 ⇒ the "∂=0" claims are convention only; a permissive schema can reintroduce
  `target_vol`/`stop_hint`/`extras{}` and a future consumer can read them (leak (d) reopens).
- Skip F18 ⇒ no numeric seam leak, but a one-source, undated, non-decaying LLM edge can still
  enter *traversal* and (even post-F02) distort the *structure* the exposure vector is computed
  over — i.e. F18 protects the **graph admission** boundary that F02 assumes is clean.

---

## 6. Per-finding disposition table

| Finding | Verdict | Numeric trace | Edit closes leak? | Smallest seam-safe wording | RESEARCH-STATE.md change? |
|---|---|---|---|---|---|
| **F01** | **CONFIRMED** + **NEEDS-HUMAN-DECISION (HD-1)** | §1(a): identical candidates, HIGH vs MED bucket → `f*_H>f*_M` → `ceiling_H>ceiling_M` → `qty_H>qty_M` when ceiling binds | Eval-only store closes it fully | "CalibrationStore is **evaluation/monitoring only** in v1. `Sizer`/`RiskEngine`/`ExitManager`/`ComplianceGate`/`KillSwitch` MUST NOT read any statistic keyed by model, prompt_version, conviction_bucket, or thesis_id. No executable conviction-keyed Kelly ceiling in v1." | **Yes — D5 + D9b** (they mandate the wire the fix removes) |
| **F02** | **CONFIRMED** + **NEEDS-HUMAN-DECISION (HD-2)** on field intent | §1(b),(c): `exposure=Π(edge_conf)·β^hops·γ^days·w(m_llm)` monotone in `c_llm`,`m_llm` → exposure_vector → tilt/allowed position | Closed-categorical `MacroEventLabel` + `EdgeProposal{endpoints,relation,citations}` + deterministic evidence-confidence + `EdgeWeightFitter` sole numeric source **closes fully & keeps KG value** | "`MacroEventLabel` = {driver, source, phase, direction} closed enums only — **no LLM magnitude/confidence**. `EdgeProposal` = endpoints+relation+citations only — **no LLM weight/confidence**. Evidence-confidence and all traversal numbers are **code-owned** (deterministic policy + `EdgeWeightFitter`). Magnitude class ≤3 fixed rungs → code-owned weights." | **Yes — D14 §⑤ (strike LLM magnitude/confidence) + D14a (redefine `confidence` as deterministic)**, IF those were LLM-supplied numbers |
| **F10** | **CONFIRMED** | §1(d),§2: permissive `TradeThesis{…,rationale}`/JSONB → `target_vol`/`stop_hint`/rationale-parse reachable | Two-type split + strict boundary validation **is** the minimal encoding | "`ResearchTradeThesis` stays in Plane 1. Deterministic projector → `HotPathCandidate{thesis_id, conviction_band, direction}`, closed enums, `additionalProperties=false`, `extra='forbid'`, `frozen`, `allow_inf_nan=False` on any numeric seam field. `Sizer` accepts neither thesis type. Rationale/raw JSON structurally unreachable downstream." | **No** — spec narrative + interface contracts only (optional 1-line clarifying note) |
| **F18** | **CONFIRMED** | N/A (integrity, not numeric) | Restore six gates into §3/§4/§11 | "Restore verbatim D14a: ① human queue; ② 2nd independent source before evidence-confidence >0.5; ③ no citeable source ⇒ traversal-ineligible; ④ ~0.85 precision on ~200 labeled claims **before v1 Layer-1 admission**; ⑤ `valid_from ≤ prediction_date` + `last_confirmed`, planted-future-edge test; ⑥ ~30%/yr decay + mandatory deprecation." | **No** — D14a intact; spec narrative corrected. (Restore ② with F02's *deterministic* confidence reading.) |

---

## 7. Enforcement-mechanism grounding (schema strictness)

Cited to justify the F10 boundary mechanisms (the only place web grounding was warranted; the rest
of this report is analytic over the design's own data flow).

- **OpenAI Structured Outputs, strict mode** — `additionalProperties: false` is *mandatory across
  all object definitions*, **all properties must be listed in `required`** (no optional fields),
  and **closed `enum`s are fully supported**. This means the *LLM's own structured emission* of
  `ResearchTradeThesis` can be constrained the same way the seam type is, and any injected extra
  field is rejected at generation.
  (developers.openai.com/api/docs/guides/structured-outputs — fetched 2026-07-20.)
- **Pydantic v2** — `model_config = ConfigDict(extra='forbid')` raises a validation error on any
  unexpected field ("providing extra data is not permitted"); default `'ignore'` *silently drops*
  it, `'allow'` *stores it* in `__pydantic_extra__` (reachable — must not be used on the seam).
  `frozen=True` gives immutability. (pydantic.dev/docs/validation/latest/concepts/models — fetched
  2026-07-20.) `allow_inf_nan=False` (a `Field`/`ConfigDict` numeric knob, standard Pydantic v2)
  rejects `nan`/`inf` so a non-finite value cannot silently defeat a downstream `min`/comparison
  in `Sizer`/`RiskEngine`.

Combined: the seam type should be validated with **both** the LLM-side strict schema (generation)
**and** the hot-path-side Pydantic model with `extra='forbid'`, closed enums, all-required,
`frozen=True`, and `allow_inf_nan=False` on numerics (defense-in-depth: reject at emit *and* at
parse).

---

## 8. Human decisions (do not resolve here)

- **HD-1 — D4 vs D5/D9b:** May a *mature, empirically-calibrated* per-conviction-bucket statistic
  feed a live ¼-Kelly ceiling, or is the bucket key "LLM-derived" for D4 and therefore barred from
  altering quantity? F01's fix (eval-only) presumes the latter; D5/D9b as written presume the
  former. Requires an amendment to D5 **and** D9b whichever way it lands.
- **HD-2 — D4 vs D14/D14a:** Were `MacroEvent.magnitude`, `MacroEvent.confidence`, and edge
  `confidence` ever intended to be **LLM-supplied** numeric/ordinal values consumed by traversal
  (leak) — or always deterministic/code-owned (no leak, only a wording clarification needed)?
  Determines whether D14 §⑤ and D14a need substantive amendment or only clarification.

(F10 and F18 carry **no** human-decision conflict: F10 is an encoding of the already-locked D4;
F18 is a spec-narrative correction toward the already-locked D14a.)

---

## 9. Bottom line

- **F01: CONFIRMED leak** (identical candidates → different permitted qty via bucket-keyed Kelly),
  **fix conflicts with D5/D9b → HD-1**, decision log must change.
- **F02: CONFIRMED leak** (LLM magnitude/confidence/edge-conf multiplied into exposure vector),
  **proposed fix fully closes it and preserves KG value**; one residual (keep magnitude class to a
  few fixed rungs); **field-intent is HD-2**, D14/D14a change if fields were LLM numbers.
- **F10: CONFIRMED**, two-type split + strict boundary (`additionalProperties=false`,
  `extra='forbid'`, closed enums, all-required, `frozen`, `allow_inf_nan=False`) is the **minimal
  enforceable encoding**; spec/interface change only, no decision-log change.
- **F18: CONFIRMED**, six D14a gates present in RESEARCH-STATE.md but ②/③/④/⑥ dropped and ⑤
  half-dropped from the spec narrative; **spec-only** restoration, no decision-log change.

<!-- SELF-AUDIT: All 4 context files read in full. All 4 assigned findings (F01,F02,F10,F18) given a verdict + numeric trace + close-the-leak assessment + smallest wording + RESEARCH-STATE-change flag. Seam audit table (allowed fields + deterministic consumers + ∂=0 proof) present. Two D4-vs-D5/D9b and D4-vs-D14/D14a conflicts flagged as HUMAN DECISIONS, not resolved. No spec or RESEARCH-STATE.md edits made. Web grounding limited to schema-strictness mechanisms (§7). -->
