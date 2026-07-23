# 09a — Broker-Side Protection & Idempotency (F03 / F04 / F08)

> **Status:** Adversarial research validation. No implementation, no spec/decision-log edits.
> **Date:** 2026-07-20.
> **Scope:** F03 (broker-side protection guarantee), F04 (GTT/stop fail-direction), F08
> (append-only replay double-submit / broker-effect idempotency), for **Zerodha Kite Connect**
> and **Alpaca**.
> **Reviewer authority:** RESEARCH-STATE.md (D6/D12/D15/D16/D18/D20/D22) is authoritative where the
> narrative spec drifts. D4 is not touched by these findings (none of F03/F04/F08 is a seam leak).
> **Source discipline:** PRIMARY = official broker API docs / official support KB. SECONDARY =
> forum / GitHub / blog — used only to *illustrate* a failure, never to *close* a guarantee.

---

## 0. Executive verdict for these three findings

| Finding | Verdict | Severity (after research) |
|---|---|---|
| **F03** — absolute broker-side protection guarantee is false | **CONFIRMED** | Blocker |
| **F04** — GTT-cancel / fired-but-unfilled have the wrong fail-direction | **CONFIRMED WITH MODIFICATION** | Blocker |
| **F08** — append-only events do not make broker effects idempotent | **CONFIRMED WITH MODIFICATION** | Blocker |

All three brief findings are **upheld on primary evidence**. The two "with modification" verdicts
sharpen the brief:
- **F04**: the brief's fix (a risk-clock `ProtectionSupervisor`, fail-closed on coverage deficit,
  never cancel a stop under HALT except during a confirmed replace) is correct; I add that the
  Kite two-leg GTT (OCO) is available and the `ProtectionSupervisor` must treat "GTT `triggered`
  but embedded LIMIT `rejected`/unfilled" (a distinct primary-documented state) as a first-class
  unprotected event, not only "no fill."
- **F08**: the brief is right that append-only logging alone is not idempotent, but its wording
  ("Use native client IDs/tags where available") over-credits the brokers. **Kite has no
  idempotency key at all** (the `tag` is a non-unique label). **Alpaca `client_order_id` is a
  duplicate-*rejecter* scoped to *active* orders, not a Stripe-style idempotent-replay** — it
  cannot by itself prove the outcome of a lost-ack submit. The seam-safe design must therefore
  be **reconcile-before-retry keyed on a durable `IntentId`**, exactly as F08 proposes, and must
  NOT rely on the broker key as a replay primitive.

**These are execution-safety/idempotency blockers, not D4 seam leaks** — they do not let the LLM
move a number; they let the *deterministic* hot path double-submit or carry unprotected exposure.

---

## 1. Primary-source evidence base

### 1.1 Kite Connect (kite.trade/docs/connect/v3, fetched 2026-07-20)

| # | Fact (PRIMARY unless noted) | Source |
|---|---|---|
| K1 | "Placing an order … **does not guarantee the order's receipt at the exchange**." | orders/ ("Placing orders") |
| K2 | "When an order is successfully placed, the API returns an `order_id`. **The status of the order is not known at the moment of placing**." | orders/ |
| K3 | "**Successful placement of an order via the API does not imply its successful execution.** To know the true status … scan the order history or retrieve … using its `order_id`." | orders/ (Note) |
| K4 | `tag` = "an arbitrary string … can be a unique ID … When the orderbook is retrieved, this value will be present in the `tag` field." **No dedup semantics stated.** Max 20 chars, alphanumeric. | orders/ ("Tagging orders"), postbacks/ |
| K5 | Order tags "are only visible in response. **It won't show up on Kite.**" (tag is a filter label, not a control key) — SECONDARY (Kite staff "sujith", forum). | forum/3501 |
| K6 | Documented case: a single API call produced **two distinct order_ids one second apart** — SECONDARY, but shows the client cannot assume one-call ⇒ one-order under network conditions. | forum/6557 |
| K7 | Interim order statuses include `PUT ORDER REQ RECEIVED`, `VALIDATION PENDING`, `OPEN PENDING`, `TRIGGER PENDING`, `CANCEL PENDING` — an order sits in-flight through several states; terminal = `OPEN`/`COMPLETE`/`CANCELLED`/`REJECTED`. | orders/ ("Order statuses") |
| K8 | **GTT is broker-resident.** Validity in the sample = 365 days (`created_at` 2019-09-12 → `expires_at` 2020-09-12). Types: `single`, `two-leg` (OCO). Embedded order is **`order_type: LIMIT`** only. | gtt/ |
| K9 | GTT statuses: `active`, `triggered`, `disabled`, `expired`, `cancelled` ("**cancelled by our system**"), `rejected`, `deleted`. | gtt/ ("Status") |
| K10 | **A `triggered` GTT can still fail**: the primary sample shows `status: "triggered"` with the embedded order `order_result.status: "failed"`, `rejection_reason: "…lower than the current lower circuit limit…"`. → firing ≠ protection. | gtt/ (retrieve-trigger sample) |
| K11 | GTT is broker-side, not exchange-native; survives OS/process downtime while the **broker** is up; fires **once**, places a **DAY** limit, does **not re-fire**; triggers **market-hours only**; **auto-cancelled on corporate actions >5%**; sell GTT on holdings needs **CDSL DDPI/TPIN**. | stream 06 (§3) corroborating Zerodha support KB / Z-Connect (SECONDARY-primary: Zerodha's own operational rule) |
| K12 | Postbacks: "get arbitrary updates to your orders **reliably** … (`COMPLETE`, `CANCEL`, `REJECTED`, `UPDATE`)." `UPDATE` = open-order modify **or partial fill**. **For individual developers, Postbacks over WebSocket is recommended.** No documented **replay/resend** of a postback missed during client downtime. | postbacks/ |
| K13 | Exceptions: `TokenException` (403 → **relogin, do not auto-retry**), `NetworkException` ("API was unable to communicate with the OMS" — **ambiguous outcome**), `OrderException`, HTTP 502 = OMS down, 503/504 = API down/timeout. | exceptions/ |
| K14 | Rate: 10 orders/sec, 400/min, **5000/day** (hard risk cap), 25 modifications/order then cancel+replace. | exceptions/ ("API rate limit") |

**Kite bottom line:** placement is **fire-and-forget with an ambiguous ack** (K1–K3, K13). There is
**no idempotency key** (K4–K6). GTT is genuinely broker-resident and survives host death (K8, K11),
but **firing is not filling** (K10) and it is fire-once/DAY/market-hours/CA-cancellable (K11).

### 1.2 Alpaca (docs.alpaca.markets + official learn/errors KB, fetched 2026-07-20)

| # | Fact (PRIMARY unless noted) | Source |
|---|---|---|
| A1 | "Each order has a unique identifier (`client_order_id`) that could be provided by you … automatically generated by the system if not provided." (≤128 chars trading API / ≤48 broker API). | orders-at-alpaca; reference/postorder; broker-api orders.md |
| A2 | "Once an order is placed, it can be **queried using either the client-provided order ID or the system-assigned unique ID** to check its status." → outcome of an ambiguous submit **is** discoverable by client_order_id lookup. | orders-at-alpaca |
| A3 | **"client_order_id must be unique (HTTP 422)… a duplicate `client_order_id` was used for another *active* order. Make sure to use a unique `client_order_id` for each *active* order."** → uniqueness is enforced but **scoped to active orders**, and it **errors (422)** rather than returning the original order. It is **duplicate-prevention, not idempotent-replay.** | learn/how-to-fix-common-trading-api-errors ("11.") |
| A4 | Updates on open orders "are also delivered through the streaming interface, which is the **recommended method for maintaining order state**." | orders-at-alpaca; broker-api orders.md |
| A5 | `trade_updates` stream carries `event` (`new`,`fill`,`partial_fill`,`canceled`,`rejected`,…), an `event_id` (ULID), and full order object. **No documented since-cursor / gap-replay** on reconnect. | websocket-streaming (payload sample) |
| A6 | Stop order: "Once the order is **elected**, the stop order becomes a **market order**." "**Stop orders and trailing stops are elected on the consolidated print**" (NBBO-gated). → stop is **Alpaca-managed / server-resident**, not a client poll loop; survives client death. | orders-at-alpaca ("Stop Order", "Extended-hours/election") |
| A7 | Stop "does **not guarantee** the order will be filled at a certain price after it is converted to a market order." Trailing stop "may fill above or below the stop trigger price." → election ≠ protected price. | orders-at-alpaca |
| A8 | **Bracket / OTO** submit entry + protective stop in one request, but "the second and third orders **won't be active until the first order is completely filled**." → atomic *submission*, but stop *activation* still lags the fill. | orders-at-alpaca ("Bracket") |
| A9 | OCO "currently only exit order is supported … add take-profit and stop-loss **after** you open the position." → for an already-open unprotected position, OCO is the one-shot protective attach. | orders-at-alpaca ("OCO") |
| A10 | GTC non-marketable limit orders "are subject to price adjustments to offset corporate actions." For **trailing stops**, "Alpaca reserves the right to **cancel or adjust**… based upon its own discretion … corporate actions or incorrect price data may cause a trailing stop to be **triggered prematurely**." | orders-at-alpaca ("Trailing stop", CA note) |
| A11 | 422 catalogue: invalid type, invalid TIF, missing stop_price, non-unique client_order_id, insufficient buying power/shares (403). | learn/how-to-fix-common-trading-api-errors |
| A12 | Websocket disconnect on the client's own network may not fire `on_close`; reconnect is the client's responsibility (SECONDARY, forum). | forum/2713 |

**Alpaca bottom line:** the stop is genuinely server-resident and survives client/host death (A6),
`client_order_id` gives **real duplicate-prevention** (A3) and the submit outcome is **discoverable**
by lookup (A2) — materially stronger than Kite. But (i) 422-on-duplicate is **not** replay-idempotent
and is **active-scoped**; (ii) bracket/OTO still leave a **fill→stop-active lag** (A8); (iii) election
≠ guaranteed fill (A7); (iv) `trade_updates` has **no gap-replay** (A5) so a missed fill event during
downtime must be recovered by reconciliation, not by the stream.

---

## 2. Race / failure timeline analysis (all 9 timelines × both brokers)

Legend — **ATOMIC** = broker guarantees it with no residual window; **DETECTABLE** = eventually
recoverable via reconciliation (query orders/positions/GTT); **RESIDUAL** = irreducible window that
no design can eliminate, only bound.

### Timeline 1 — Order accepted, acknowledgement LOST (network drop after submit)

- **Kite.** POST returns nothing usable; K1–K3 say placement never even implies exchange receipt,
  and K13 `NetworkException` is explicitly "unable to communicate with the OMS" (outcome unknown).
  There is **no client key** to correlate. Recovery = poll order history / `get_orders` and match on
  (symbol, side, qty, price, timestamp window, `tag`). Because `tag` is non-unique (K4–K5) and one
  call can yield two orders (K6), the match is **heuristic, not exact**. → **DETECTABLE but
  ambiguous**; a **RESIDUAL** window exists between submit and the first successful reconcile poll.
- **Alpaca.** If the client set `client_order_id`, recovery is an **exact** lookup by that ID (A2):
  either the order exists (accepted) or it does not (safe to retry). This is the correct primitive.
  Caveat: if the client did *not* set it, Alpaca auto-generated one the client never saw → lookup
  impossible, same ambiguity as Kite. → **DETECTABLE and unambiguous *iff* client sets
  client_order_id before submit**; otherwise RESIDUAL.
- **Verdict feed:** F03 confirmed (residual window is real on both; irreducible on Kite). F08
  confirmed-with-mod (Alpaca lookup is the correct recovery, but only because client_order_id is
  durably logged *before* submit — this is the `IntentId` discipline, not a broker gift).

### Timeline 2 — Full fill BEFORE a protective stop exists (fill-to-stop atomicity)

- **Kite.** Entry order and GTT are **two separate API calls**. GTT margins/holdings are checked
  **at trigger, not creation** (K11). There is **no atomic fill→GTT** primitive. Gap = time from
  fill-detection (postback/poll) to a successful `POST /gtt/triggers`. → **RESIDUAL gap always**;
  widened to unbounded if the host is down when the fill lands (ExitManager never runs).
- **Alpaca.** **Bracket/OTO** submit entry + stop in one request (A8) — but the stop leg "won't be
  active until the first order is **completely filled**." So the *submission* is atomic, the
  *activation* is not: between fill and leg-activation there is still a broker-internal gap, plus
  Alpaca only accepts exit orders against an existing position (working-with-orders). → **RESIDUAL
  gap reduced but not eliminated**; materially smaller than the separate-call path.
- **Verdict feed:** F03 confirmed on both. The spec's §5 line 154–155 claim that ExitManager
  "immediately places the resting broker-side stop … on fill" is only reachable *if the process is
  alive and the fill was observed* — precisely the assumption F03 destroys.

### Timeline 3 — Partial fill, then a LATER partial fill above protected quantity

- **Kite.** GTT quantity is fixed at creation; a later fill that grows the position leaves the
  **excess quantity unprotected** until the GTT is modified (K8 modify endpoint) or replaced.
  Partial fills arrive as `UPDATE` postbacks (K12) — if missed during downtime, the growth is
  invisible until reconcile. → **DETECTABLE, with a RESIDUAL under-coverage window.**
- **Alpaca.** Same structural issue: a stop/OCO leg covers the quantity known at attach time; a
  subsequent `partial_fill` event (A5) that increases held quantity requires the client to
  re-size/replace the protective order. `trade_updates` has no gap-replay (A5). → **DETECTABLE, with
  a RESIDUAL under-coverage window.**
- **Verdict feed:** directly substantiates F03's "later partial fill can increase position quantity
  above protected quantity" and F04's demand that the supervisor watch **partial-fill growth**, not
  just cancellation. The protection invariant must be *coverage(active_exit_qty) ≥
  reconciled_position_qty*, re-evaluated on every fill event — exactly F03's proposed state machine.

### Timeline 4 — Process / host / broker / DB outage while a position is open

- **Kite GTT: broker-resident — CONFIRMED survives host/process death** (K8, K11). If the trigger
  fires while the OS is dead, the DAY LIMIT is placed by Zerodha. **Caveats that break "always
  protected":** (a) fires **once** — a fired-but-unfilled GTT is gone by EOD and there is no process
  alive to re-place it (K10, K11); (b) **market-hours only**; (c) if the **broker/OMS** is down
  (K13 502), nothing is resident anywhere. → **ATOMIC survival of *client* death; RESIDUAL on broker
  death and on fire-once expiry.**
- **Alpaca stop/bracket: broker-resident — CONFIRMED** (A6 election on consolidated print is
  Alpaca-side, not client-side). Survives client/host/DB death. Caveats: election ≠ fill (A7); a
  DAY-TIF stop expires at close; GTC survives. If Alpaca itself is down, nothing is resident. →
  **ATOMIC survival of client death (with GTC); RESIDUAL on broker death / DAY-expiry.**
- **Verdict feed:** the spec's §6 "Two guarantees" (line 192–196) — "resting stops protect positions
  even when the OS is dead" — is **true only for the narrow case of a *pre-existing, active,
  correctly-quantified, unexpired* broker stop while the *broker* is up.** F03 confirmed: the
  guarantee as stated is absolute and therefore false; it must be conditioned.

### Timeline 5 — GTT/stop rejection, trigger, DAY-expiry, gap-through-no-fill

- **Kite.** Primary evidence K10: a GTT can be `triggered` while its embedded LIMIT order is
  `rejected` (circuit-limit breach in the sample). Gap-through a LIMIT trigger → order placed at the
  pre-set limit, unfilled if price ran past it, **cancelled at EOD, does not re-fire** (K11). GTT can
  also be `rejected`/`cancelled`/`expired` outright (K9). → **All four states are DETECTABLE only by
  polling `/gtt/triggers` (7-day window) or the orderbook; none self-heals.** This is the core of F04.
- **Alpaca.** Stop "does not guarantee fill" post-election (A7); a gap-through converts to a market
  order that fills at the gapped price (protection degraded, not absent). A stop can be `rejected`
  (A11, e.g. insufficient shares on a sell-stop after a prior exit). → **DETECTABLE via
  `trade_updates` / order lookup; gap-through fills at market (worse price), not "no protection".**
  Alpaca is structurally safer here than Kite's LIMIT-on-trigger GTT.
- **Verdict feed:** **F04 CONFIRMED.** The spec §6 rows "GTT fired-but-unfilled (gap-through) →
  CONTINUE + escalate" and "GTT auto-cancelled by CA>5% → CONTINUE + repair" both leave the position
  **unprotected while the system merely CONTINUEs to next EOD**. Correct fail-direction = the
  affected symbol goes **REDUCING immediately** (fail-closed for exposure increase) and a risk-clock
  supervisor repairs or liquidates — the brief's fix.

### Timeline 6 — Corporate-action cancellation of a GTT; split/bonus quantity change

- **Kite.** **Primary/operational: GTT is auto-cancelled on CA >5%** (bonus/split/rights/amalgamation)
  before ex/record date; Zerodha does **not** adjust the trigger, it **cancels** (K11, stream 06 §3).
  → position silently unprotected from cancellation until re-placement. Quantity also changes on
  split/bonus, so any re-placed GTT must use the CA-adjusted quantity (D20 ledger). → **DETECTABLE via
  GTT status poll + CA feed; requires active repair.**
- **Alpaca.** GTC limit orders are CA-price-adjusted by Alpaca; trailing stops Alpaca "reserves the
  right to cancel or adjust" and CA "may cause a trailing stop to be triggered prematurely" (A10). →
  protection may be **silently mutated or prematurely fired** around CAs. → **DETECTABLE, needs
  monitoring.**
- **Verdict feed:** confirms F04's "CA cancellation can also occur **before the ex-date** while repair
  is deferred to a later EOD cycle" — the spec §6 "CONTINUE + repair … re-places post-ex-date" repairs
  **too late** (protection is gone from the cancellation instant, which precedes ex-date).

### Timeline 7 — Token expiry / re-auth failure mid-position

- **Kite.** `TokenException` (403) — daily token; must **relogin, never auto-retry** (K13). While the
  token is dead the client **cannot place/modify/cancel or reliably poll**, but the **already-resident
  GTT still stands** (K8). So token death = "can't act, but existing protection persists" — *provided*
  a correctly-quantified GTT already exists (Timelines 2/3 caveats). → **existing protection ATOMIC;
  ability to repair is LOST until re-auth** → any coverage deficit at token-death time is a RESIDUAL.
- **Alpaca.** API-key auth (not daily); less fragile, but a revoked/expired key similarly blocks
  action while the server-resident stop persists (A6). → same shape, lower probability.
- **Verdict feed:** substantiates the spec §6 "Broker disconnect > N s → FAIL-CLOSED → REDUCING/
  HALTED; resting stops remain the safety net" — correct **only** if the resting stop was already
  established and fully covers current quantity. Reinforces F03/F04: the safety net is conditional.

### Timeline 8 — Kill-switch cancellation racing an incoming fill

- **Kite.** HALT cancels open orders; if a fill lands in the same instant, the cancel may hit an
  already-`COMPLETE` order (no-op) or the position grows just as protection is being torn down. If the
  kill-switch cancels the **protective GTT** as part of "cancels-only," it can **remove protection
  from a live position** — the exact anti-pattern F04 warns against ("`HALTED` must never cancel a
  protective order except during a confirmed replace"). → **RESIDUAL race**; needs a fencing token so
  a stale worker cannot submit after HALT (F08).
- **Alpaca.** Same race; `trade_updates` `fill` can arrive after a `canceled` request was issued.
  Server-resident stop should be preserved through HALT, not cancelled. → **RESIDUAL race**.
- **Verdict feed:** F04 + F08 confirmed. Two design invariants fall out: (a) HALT semantics must
  **distinguish exposure-increasing orders (cancel) from protective exits (preserve)**; (b) a durable
  **kill-switch generation / fencing token** (F08) must gate every submit so a stale/replayed worker
  cannot re-arm exposure after HALT.

### Timeline 9 — Restart + reconciliation

- **Kite.** On restart the client rebuilds from the D15 event log, then must **reconcile against
  live broker state**: `get_orders` + `get_positions` + **`GET /gtt/triggers`** (active + last 7
  days). Any intent whose outcome is unknown (Timeline 1) must be resolved **before** any retry; blind
  replay of an order-intent event double-submits (F08) because Kite has no dedup (K4–K6). → replay is
  **safe only if gated by reconcile-first**.
- **Alpaca.** Reconcile via `GET /orders` + `GET /positions` + **lookup by client_order_id** (A2).
  Replaying a submit is caught by the 422 duplicate check **only while the prior order is still
  active** (A3); once it is filled/closed, the same client_order_id may be reusable → replay could
  double-submit. So even Alpaca's key is **not** a safe standalone replay guard. → replay **safe only
  if gated by reconcile-first**.
- **Verdict feed:** **F08 CONFIRMED WITH MODIFICATION.** The brief's core ("reconcile that intent
  against broker orders and trades before any retry; unknown outcome → `OUTCOME_UNKNOWN`, block
  related exposure, never blindly retry") is correct and necessary on **both** brokers. The
  modification: the brief's "use native client IDs/tags where available" must be qualified —
  **Kite's tag is not an idempotency key at all**, and **Alpaca's client_order_id is active-scoped
  duplicate-prevention, not idempotent-replay** — so the durable `IntentId` + reconcile-first is the
  load-bearing mechanism, with client_order_id used as the *correlation handle* for the lookup.

---

## 3. Atomic vs. detectable vs. irreducible — summary matrix

| Property | Kite | Alpaca |
|---|---|---|
| Idempotent submit (dedup on client key) | **NONE** (tag is a non-unique label, K4–K6) | **PARTIAL** — 422 rejects duplicate client_order_id, but only for *active* orders; errors instead of replaying (A3) |
| Lost-ack outcome discoverable | Heuristic match only (no key) → **ambiguous** | **Exact** via client_order_id lookup *iff* client set it before submit (A2) |
| Fill→stop atomic | **No** (two calls; GTT checked at trigger) | **No**, but bracket/OTO shrink the window (submission atomic, activation lags fill) (A8) |
| Resting stop survives client/host death | **Yes** (GTT broker-resident) (K8/K11) | **Yes** (stop elected server-side) (A6); use GTC not DAY |
| Resting stop survives broker/OMS death | **No** (K13 502) | **No** |
| Firing ⇒ filling | **No** — triggered GTT can be rejected/unfilled (K10) | **No** — election ⇒ market order, may fill worse (A7) |
| Fire-once / re-fire | Fire-once, DAY, no re-fire (K11) | Stop persists (GTC) until filled/cancelled; no single-shot expiry if GTC |
| CA handling of the stop | **Auto-cancel on CA >5%, no adjust** (K11) | Price-adjust GTC limits; may cancel/adjust or prematurely trigger trailing stops (A10) |
| Missed fill event replay on reconnect | Postback: no documented replay; poll orderbook (K12) | trade_updates: no since-cursor; reconcile by lookup (A5) |
| **Irreducible residual** | submit→first-reconcile window; broker-down window; fire-once EOD gap | submit→lookup window (if no client key set); broker-down window; election-slippage |

---

## 4. Findings table (F03 / F04 / F08)

| F | Verdict | Sev | Spec / Dxx | Key evidence | Concrete failure trace | Seam-safe edit (smallest) | Decision-log impact |
|---|---|---|---|---|---|---|---|
| **F03** | CONFIRMED | Blocker | §5 L153–163, §6 L177–196; D6/D12/D18/D22 | K1–K3, K10, K11 (Kite); A6–A8 (Alpaca) | Kite accepts entry; ack lost; fill lands while host down; no GTT ever created; position naked. Later a 2nd partial fill grows qty above any stop's qty. | Replace the absolute guarantee with a **protection-coverage state machine** (`SUBMITTED_UNCONFIRMED` → `PARTIALLY_FILLED_UNPROTECTED` → `PROTECTION_PENDING` → `PROTECTED`); PROTECTED iff broker-confirmed exit qty ≥ broker-reconciled position qty; any deficit blocks new exposure; failure to protect by deadline → controlled liquidation or `HALTED_UNVERIFIED`. State the residual window explicitly. | **Yes.** Amend **D18** (drop "protection survives the process being offline" as unconditional; condition it on a pre-existing, active, fully-covering, unexpired broker stop *while the broker is up*). Amend **D22** "Two guarantees (1)" wording. **D12** gains a coverage-deficit → REDUCING trigger. |
| **F04** | CONFIRMED WITH MODIFICATION | Blocker | §5 L159–161, §6 L179–180; D12/D18/D20 | K9, K10, K11 (Kite GTT states, fire-once, CA-cancel, triggered-but-rejected); A7, A10 (Alpaca) | Gap-through fires the DAY-limit GTT; limit unfilled; GTT cancelled at EOD; system "CONTINUEs" and carries a **naked position overnight**. Separately a CA >5% cancels the GTT **before ex-date**; repair deferred to a later EOD → naked in between. | Any coverage deficit is **fail-closed for exposure increases**; affected symbol → **REDUCING**. A risk-clock **`ProtectionSupervisor`** detects GTT `cancelled`/`rejected`/`expired`/`triggered-but-unfilled`/**partial-fill growth** immediately and repairs or liquidates. EOD reconcile = backstop only. **`HALTED` never cancels a protective order except during a confirmed replace.** *Modification:* treat "GTT `triggered` + embedded LIMIT `rejected`" (K10) as a first-class unprotected event; prefer Kite **two-leg (OCO)** GTT where a stop+target is wanted. | **Yes.** Amend **D18** §6 rows: change "GTT fired-but-unfilled → CONTINUE + escalate" and "GTT auto-cancelled by CA>5% → CONTINUE + repair" to **fail-closed → REDUCING + immediate risk-clock repair**. Adds a `ProtectionSupervisor` on the D12 risk clock (distinct from the D16 EOD signal clock). |
| **F08** | CONFIRMED WITH MODIFICATION | Blocker | §5 L126–127, §6 L189–191, §10 L269–270; D6/D15/D16/D18 | K2–K6 (Kite: no dedup, ambiguous ack, 1-call-2-orders); A2–A3 (Alpaca: active-scoped 422, not replay-idempotent) | Order-intent event written; broker accepts; ack lost; process crashes; on restart the log replays the intent and **re-submits → double exposure**. GTT create/replace/modify/cancel have the same race. | Every broker effect starts with a durable unique **`IntentId`**; on replay, **reconcile that intent against live broker orders/trades/GTTs before any retry**; unknown outcome → **`OUTCOME_UNKNOWN`**, block related exposure, never blind-retry. Use Alpaca **client_order_id as the correlation handle** for the lookup (set & logged *before* submit); on Kite reconcile heuristically (symbol/side/qty/price/window + tag) since no key exists. Add a durable **kill-switch generation / fencing token** so stale workers can't submit after HALT. Contract test: **no duplicate economic effect under acknowledgement loss**. *Modification:* the brief's "use native client IDs/tags where available" over-credits the brokers — **neither key is a Stripe-style idempotency key**; the `IntentId` + reconcile-first is the guarantee, the broker key is only a lookup handle. | **Yes.** Amend **D6** (`BrokerAdapter` contract): the "idempotency key on submit" must be spelled out as **client-side IntentId + mandatory reconcile-before-retry**, and `capabilities()` must expose **`has_native_client_order_id`** (true Alpaca / false Kite) so the reconcile strategy differs per broker. Amend **D15/D16** restart-reconciliation to be **intent-outcome-resolving**, not state-rebuild-only. Add fencing token to **D12/D22**. |

---

## 5. Decision-log amendment summary (D6 / D12 / D15 / D16 / D18 / D22)

| Decision | Needs amendment? | What changes |
|---|---|---|
| **D6** (BrokerAdapter contract) | **Yes** | "idempotency key on submit + reconcile()" → make explicit: **durable client-side `IntentId`**, **reconcile-before-retry**, and a `capabilities()` flag `has_native_client_order_id`. Kite path = heuristic reconcile (no key); Alpaca path = client_order_id lookup. Contract test asserts no duplicate economic effect under ack loss (both adapters). |
| **D12** (kill-switch) | **Yes** | Add a **protection-coverage-deficit** trigger → `REDUCING`. HALT semantics must **distinguish exposure-increasing orders (cancel) from protective exits (preserve)**; never cancel a stop except during a confirmed replace. Add **fencing/generation token** so stale workers can't submit post-HALT. |
| **D15** (append-only event log) | **Yes (clarify)** | The event log is **intent/audit truth; the broker is authoritative for current custody**. Replay must **resolve unknown intent outcomes against the broker before retry**, never blindly re-emit a side effect. |
| **D16** (scheduler; restart reconcile) | **Yes** | Restart reconciliation must be **intent-outcome-resolving** (Timeline 1/9), and a **`ProtectionSupervisor` runs on the risk clock** (second-level), separate from the EOD signal clock — F04. |
| **D18** (exit policy / resting stop) | **Yes** | Replace the unconditional "broker-side resting stop the moment it fills … protection survives the process being offline" with the **conditional** coverage-state-machine wording (F03) and **fail-closed** GTT-failure/CA-cancel handling (F04). Note fill→stop is **not atomic** on either broker; state the residual window. |
| **D22** (ops/survivability) | **Yes** | Amend "Two guarantees (1)" — the broker-side safety net is **conditional** (pre-existing, active, fully-covering, unexpired stop, broker up), not absolute. Add fencing token to the watchdog/dead-man design. |

**Note on D20:** already correctly requires the independent CA factor ledger; F04/F06 only add that a
CA event must **immediately** trigger GTT re-evaluation on the risk clock (not deferred to EOD), and
re-placed GTTs must use CA-adjusted quantity. No contradiction with D20, an extension of it.

---

## 6. What is genuinely irreducible (be honest in the spec)

1. **Submit→first-confirm window** (both brokers): between a submit and the first successful status
   read, the outcome is unknown. Bounded by fast reconcile + (Alpaca) client_order_id lookup; **never
   zero**. Kite is worse — no key, so the correlation is heuristic.
2. **Fill→stop-active window** (both brokers): no atomic fill-to-protection primitive exists. Alpaca
   bracket/OTO shrinks it; Kite (separate GTT call) is wider. **Never zero.**
3. **Broker/OMS-down window** (both): if the *broker* is down, nothing is resident anywhere; the
   only mitigations are pre-existing GTC/GTT + not increasing exposure. **Never zero.**
4. **Kite fire-once EOD gap**: a triggered-but-unfilled GTT is gone at close and there is no
   exchange-native re-arm; only a live supervisor re-places it. **Irreducible without a live process.**

Everything else (partial-fill growth, CA cancel, token expiry, HALT/fill race, restart) is
**DETECTABLE and repairable** by a risk-clock `ProtectionSupervisor` + reconcile-before-retry — which
is exactly what F03/F04/F08 prescribe.

---

## 7. Sources (fetched 2026-07-20; saved under /tmp/f0308/sources/)

PRIMARY (broker-official):
- Kite Connect v3 — Orders: https://kite.trade/docs/connect/v3/orders/
- Kite Connect v3 — GTT: https://kite.trade/docs/connect/v3/gtt/
- Kite Connect v3 — Postbacks/WebHooks: https://kite.trade/docs/connect/v3/postbacks/
- Kite Connect v3 — Exceptions: https://kite.trade/docs/connect/v3/exceptions/
- Kite Connect v3 — WebSocket: https://kite.trade/docs/connect/v3/websocket/
- Alpaca — Orders at Alpaca: https://docs.alpaca.markets/docs/orders-at-alpaca
- Alpaca — Working with /orders: https://docs.alpaca.markets/docs/working-with-orders
- Alpaca — Create an Order (POST /orders reference): https://docs.alpaca.markets/reference/postorder
- Alpaca — Websocket streaming (trade_updates payload): https://docs.alpaca.markets/docs/websocket-streaming
- Alpaca — Common Trading API errors (client_order_id-must-be-unique, 422 catalogue): https://alpaca.markets/learn/how-to-fix-common-trading-api-errors-at-alpaca
- Alpaca Broker API — Orders (client_order_id, by_client_order_id lookup): https://github.com/alpacahq/alpaca-docs/blob/master/content/api-references/broker-api/trading/orders.md

SECONDARY (illustrative only — never used to close a guarantee):
- Kite forum 3501 (tag is response-only, Zerodha staff): https://kite.trade/forum/discussion/3501/how-to-place-order-with-tag
- Kite forum 6557 (one call → two orders): https://kite.trade/forum/discussion/6557/duplicate-orders-placed-with-a-single-api-call
- Alpaca forum 15801 (idempotency question, unanswered): https://forum.alpaca.markets/t/idempotency-on-order-create/15801
- Alpaca forum 2713 (websocket reconnect is client's job): https://forum.alpaca.markets/t/websocket-disconnects-how-to-reconnect/2713
- Stream 06 (docs/research/06-india-mechanics.md) — corroborating Kite GTT operational semantics.

---

## 8. Self-audit

- **Findings covered:** F03 (CONFIRMED), F04 (CONFIRMED WITH MODIFICATION), F08 (CONFIRMED WITH
  MODIFICATION) — all 3 present with verdict, severity, evidence, failure trace, seam-safe edit, and
  decision-log impact (§4).
- **Timelines covered (all 9, both Kite & Alpaca, §2):** (1) lost ack, (2) full fill before stop,
  (3) later partial fill above protected qty, (4) process/host/broker/DB outage, (5) GTT/stop
  rejection/trigger/DAY-expiry/gap-through, (6) CA cancellation + split/bonus qty change, (7) token
  expiry / re-auth failure, (8) kill-switch cancel racing a fill, (9) restart + reconciliation.
- **Atomic / detectable / irreducible** distinguished (§3, §6). Decision-log impacts on
  **D6/D12/D15/D16/D18/D22** enumerated (§5); D20 noted as extension-not-contradiction.
- **D4 not implicated** — F03/F04/F08 are execution-safety/idempotency blockers, not seam leaks.
- Secondary sources labeled SECONDARY throughout; no live-trading guarantee rests on a forum/blog.
- **All 3 findings + 9 timelines are covered.**
