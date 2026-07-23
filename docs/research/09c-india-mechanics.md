# 09c — India Mechanics: Evidence-First Adversarial Validation (F12 + F17, India portions)

> **Status:** Research report. No implementation, no spec edit, no RESEARCH-STATE.md edit.
> **Date:** 2026-07-20. **Scope:** INDIA portions of F12 (compliance rule set incomplete + mixes
> lifecycle stages) and F17 (session/calendar/credential/token lifecycle flows missing), plus F12's
> claim that static-IP enforcement, algo-ID tagging, OPS throttle, DDPI, and long-delivery-only must
> be explicit pre-order gates.
> **Setup validated against:** India-resident retail individual; own + immediate-family accounts only;
> Zerodha Kite; swing/EOD (well under any OPS threshold); delivery (CNC) only; no intraday.
> **Reviews:** spec `2026-07-20-trading-os-design.md` §7; `RESEARCH-STATE.md` D18/D19/D16/D22; brief
> `08-adversarial-design-review-research-brief.md` F12/F17; and re-verifies `06-india-mechanics.md`
> against current primary sources.

---

## Executive verdict

**F12 (India): CONFIRMED-WITH-MODIFICATION.** The brief is right that D19 mixes lifecycle stages and
omits gates. Primary-source research surfaces a **material factual error the brief did not catch and
that D19 currently states wrongly:** the static-IP mandate for API order placement is effective
**1 April 2026, not "since Apr 1 2025."** The primary NSE circular also shows the algo-ID rule is more
demanding than either D19 or stream-06 recorded: **every algo order, below and above the 10-OPS
threshold, must be tagged with an exchange-provided ID, and even below-threshold algos require
exchange registration for a *generic* algo ID** — you cannot self-tag. The own/immediate-family
boundary and long-delivery-only gate are confirmed and correctly belong pre-order.

**F17 (India): CONFIRMED.** Kite access-token daily expiry, TokenException-no-auto-retry, the
Muhurat "timings notified subsequently" hazard, T+1 settlement, and CA-driven GTT cancellation are
all confirmed against primary Kite/NSE docs. The spec has no `SessionReadiness`/`CredentialReadiness`
gate; that gap is real.

**Static-IP / algo-ID / OPS / DDPI / long-delivery-only as explicit pre-order gates: CONFIRMED** as a
set, with two corrections (effective date; algo-ID is exchange-issued and mandatory below threshold).

**Decision-log impact:** **D19 must be amended** (static-IP date; algo-ID mechanics; add stage
structure). **D18 confirmed as-is** on DDPI/GTT (already correct). **D16 must be amended** to add a
fail-closed session/calendar readiness gate and a credential-readiness gate. **D22** should reference
the 6 AM token flush as a scheduled re-auth job constraint. The primary SEBI circular *body* is not
publicly rendered (JS page), but the **operative NSE implementation circular text (INVG67858) was
retrieved in full** — the stream-06 "circular text not inlined" blocker is now **largely closed**.

Counts: 1 India blocker-adjacent correction (static-IP date is wrong in the authoritative log),
2 confirmed-with-modification, 6 confirmed, 0 not-supported, 1 needs-human-decision (OPS/registration
applicability for a below-threshold personal algo — see F12-b).

---

## Primary sources retrieved (with dates)

| Source | Type | Pub/effective date | What it proves |
|---|---|---|---|
| SEBI circular SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013 "Safer participation of retail investors in Algorithmic trading" (sebi.gov.in) | PRIMARY (regulatory) | **Feb 04, 2025** | Circular exists, number + date confirmed. Body is JS-rendered; only masthead/date rendered. |
| **NSE circular INVG67858 / Ref 471/2025, "Implementation Standards…"** (nsearchives.nseindia.com/content/circulars/INVG67858.pdf) | **PRIMARY (regulatory, operative)** | **May 05, 2025** | Full Annexure text retrieved: static-IP standards, TOPS=10 OPS/exchange/segment, below-threshold registration + generic algo ID, tagging of ALL algo orders, OAuth/2FA, 5-yr audit trail, family-IP sharing. |
| Zerodha Kite support: "What is a static IP…" (support.zerodha.com/…/kite-api/articles/static-ip) | PRIMARY (broker operational, current) | **"effective 1 April 2026"** | Static IP mandatory for API order placement from **1 Apr 2026**; market-data/orderbook/positions exempt; max 2 IPs; 1 change/cal-week; family-only sharing via declaration. |
| Zerodha support: "What is CDSL TPIN…" + TPIN pre-auth | PRIMARY (broker/CDSL operational) | current | Non-DDPI/POA customers MUST enter CDSL TPIN + OTP to authorise every delivery sell; DDPI removes the Authorise step. Pre-auth valid max one day; max 100 instruments. |
| Kite Connect v3 — User (kite.trade/docs/connect/v3/user) | PRIMARY (API docs) | current | access_token "will expire at 6 AM on the next day (regulatory requirement)" unless invalidated earlier by logout/master-logout. |
| Kite Connect v3 — Exceptions (kite.trade/docs/connect/v3/exceptions) | PRIMARY (API docs) | current | TokenException (403) → "clear the user's session and re-initiate a login." Rate limits: 10 OPS, 400/min, 5000/day, 25 modifications/order. |
| Kite Connect v3 — GTT (kite.trade/docs/connect/v3/gtt) | PRIMARY (API docs) | current | GTT places a **DAY LIMIT** order on trigger; sample shows a triggered GTT whose limit order **failed** (below circuit) → gap-through-no-fill is real. Statuses incl. cancelled/expired/rejected. Validity ~365 days. |
| NSE "Market Timings & Holidays" (nseindia.com/resources/exchange-communication-holidays) | PRIMARY (exchange) | current | **"November 08, 2026 … trading holiday on account of Diwali Laxmi Pujan. Muhurat Trading will be conducted on that day. Timings … notified subsequently through a circular."** |
| Zerodha Z-Connect "Consequences of Short delivery" | PRIMARY-ish (broker) | current | T+1 rolling settlement; short delivery → exchange auction; auction band ±20% + 0.05%/day penalty; close-out ≥20% above. |
| Kite forum "earliest time to generate access token" | SECONDARY (community) | current | Tokens flushed ~5:00–7:30 AM; safe to generate at/after 7:30 AM. Corroborates the docs' 6 AM but widens the window. |

---

## F12 — India compliance: per-finding table

| # | Claim under review | Verdict | Primary evidence | Failure trace | Smallest correct edit | D-log? |
|---|---|---|---|---|---|---|
| F12-a | Static-IP mandatory for API order placement, effective **Apr 1 2025** | **CONFIRMED-WITH-MODIFICATION (date wrong)** | Zerodha static-IP FAQ (current): "effective **1 April 2026**"; NSE INVG67858 (May 5 2025) mandates static IP but the *broker enforcement date* is 1 Apr 2026 (Zerodha primary). Non-order APIs (ticks/orderbook/positions) exempt. | If the code trusts the recorded "since 2025-04-01," a verify-before-live checklist item is falsely marked satisfied a year early; conversely, as of today (2026-07-20) it IS in force, so an un-whitelisted egress IP → broker **rejects** every order. | In D19/§7 change "mandatory since 2025-04-01" → "mandatory for API order placement from **2026-04-01** (in force now); non-order endpoints exempt." Keep the pre-order egress-IP gate. | **D19 amend** |
| F12-b | Below 10 OPS ⇒ **no exchange registration**; generic tag if unregistered, unique if registered | **CONFIRMED-WITH-MODIFICATION (mechanics wrong)** | NSE INVG67858 §B.2–B.3: below-TOPS "**require registration with the Exchange and a generic algo ID shall be provided by the Exchange**." §G: "**All algo orders (Below and above the threshold) shall be tagged with a unique identifier provided by the Exchange.**" §C.1: >10 OPS ⇒ register per exchange for a registration ID. | Design that self-generates or omits an algo tag, or assumes "below threshold ⇒ untagged," produces **non-compliant orders**. The tag is **exchange-issued**, obtained via the broker; the OS cannot mint it. | D19: replace "unique algo-ID tagging" with "**broker-provisioned exchange algo-ID tag on every order** (generic ID for below-TOPS registration-free algos; the ID is issued by the exchange via Zerodha, never self-assigned)." Pre-order gate: reject any order lacking a configured broker-supplied algo tag. | **D19 amend** |
| F12-c | OPS throttle far under threshold | **CONFIRMED** | NSE INVG67858 §B.2/§F: TOPS = **10 OPS per exchange/segment**, broker may set lower per client. Kite docs: 10 OPS / 400 per min / 5000/day / 25 mods per order. | Swing/EOD places a handful of orders/day → trivially compliant; but a retry storm or loop bug could burst >10 OPS → 429 + potential OPS-breach. | Keep a conservative pre-submission throttle (≈2 OPS ceiling) as a hot-path gate; treat 429/`NetworkException` with backoff, never tight-loop retry. (Already the intent in stream-06.) | none (D19 wording ok) |
| F12-d | DDPI/TPIN precondition for autonomous sells | **CONFIRMED (hard pre-live blocker)** | Zerodha TPIN FAQ: non-DDPI/POA customers **must** enter CDSL TPIN + OTP for every delivery sell; DDPI removes the Authorise step. Pre-auth is manual, valid one day only, ≤100 instruments. | Without DDPI, every autonomous CNC sell (incl. a stop/exit) **stalls on a TPIN/OTP prompt** — no automation possible. This is a setup blocker, not a runtime gate. | Keep D18's "DDPI mandatory pre-live" lock; add a pre-order **capability check** (`ddpi_active == true`) that fail-closes sells if DDPI is not confirmed. | none (D18 already correct) |
| F12-e | Own/immediate-family-account-only; selling/sharing the strategy trips vendor/RA obligations | **CONFIRMED (hard legal boundary)** | NSE INVG67858 §A.7: static IPs may be shared only within "one family as defined in SEBI circular …/2024/169 (3 Dec 2024)," with written/2FA request. §D–E: broker-generated and algo-provider algos require empanelment + per-algo exchange registration + (for providers) RA-type obligations. Zerodha static-IP FAQ: declaration "used exclusively by me and/or my immediate family." | Sharing/selling the strategy or running it on a non-family account converts a registration-free personal algo into a **vendor/algo-provider** activity requiring empanelment/registration (and RA licensing for black-box/recommendations). | Keep pre-order **account allowlist** gate = {own + immediate-family client IDs}; add a design invariant "strategy is never sold, shared, or run for third parties." (Matches stream-06.) | none (add to D19 as invariant text) |
| F12-f | Long-delivery-only; short-delivery on CNC triggers auction penalties | **CONFIRMED** | Z-Connect short-delivery: selling CNC without shares in demat ⇒ short delivery ⇒ exchange **auction** at ±20% band + **0.05%/day** penalty; close-out ≥20% above. Kite margins doc: 20% delivery margin blocked on demat/T1 sells. | A sell order for quantity exceeding settled demat holdings (e.g. T1 not yet settled under T+1, or a reconciliation error) → short delivery → auction penalty. | Pre-order gate: **CNC sell quantity ≤ settled demat holding** (exclude unsettled T1); reject otherwise. Long-only, no shorting. | none (add explicit gate to D19) |

### F12 lifecycle-staging critique (brief's core claim)

**CONFIRMED.** D19/§7 currently lists India rules as a flat sentence mixing a pre-order gate
(static IP, algo tag, OPS ceiling, cadence, DDPI capability) with a pre-live setup precondition
(DDPI enrollment). It omits: the **own/family account allowlist** as an explicit gate; the
**long-delivery-only / no-short-delivery** gate; and any **post-fill/reporting** stage
(capital-gains tax lots STCG/LTCG, though those live in the reporting layer, not the fill path).
The brief's proposed India pre-order list is correct; the two corrections above (static-IP date,
exchange-issued algo tag) must be folded in.

---

## F17 — India lifecycle flows: per-finding table

| # | Claim under review | Verdict | Primary evidence | Failure trace | Smallest correct edit | D-log? |
|---|---|---|---|---|---|---|
| F17-a | Kite access-token daily expiry; TokenException must NOT be auto-retried; requires re-auth | **CONFIRMED** | Kite User docs: token "will expire at **6 AM** on the next day (regulatory requirement)"; also invalidated by master-logout or login elsewhere. Exceptions docs: TokenException(403) → "clear the user's session and re-initiate a login." Forum: flush window ~5:00–7:30 AM. | A scheduled order/protection job firing on a stale token gets 403 TokenException. Auto-retrying re-hits 403 forever; meanwhile a CA may have cancelled a protective GTT and local state still "looks" protected but is unverifiable. | Add a **`CredentialReadiness`** precondition before every order/protection job: on TokenException, HALT new exposure, surface re-auth to HITL (localhost, D22-asymmetric), and **reconcile positions/GTTs before resuming**. Daily re-auth job scheduled after ~07:30 IST (not before flush). | **D16 amend** (+ D22 note) |
| F17-b | Market calendar: NSE holiday source, Muhurat special session, unscheduled closures; "session close observed vs scheduled" must fail closed | **CONFIRMED** | NSE holidays page (primary): 2026 list is exchange-authoritative; **Nov 08 2026 Diwali = trading holiday with Muhurat Trading, timings "notified subsequently through a circular."** So the special-session window is **not known ahead of time** — it must be read from a same-day circular. | If the scheduler runs EOD work on scheduled close (15:30) on a Muhurat day, or on an unscheduled closure (special holiday, halt), it operates on an un-closed or non-existent session → trades on incomplete/absent data. | Add a **`SessionReadiness`** gate: authoritative calendar (ingest NSE holiday CSV/circular programmatically, versioned) + **observed close** confirmation; **unknown/ambiguous session ⇒ FAIL-CLOSED** (no EOD cycle). Muhurat timings must be fetched from the day's circular, never assumed. | **D16 amend** |
| F17-c | T+1 settlement | **CONFIRMED** | Z-Connect: equity delivery is **T+1 rolling** (buy T, receive T+1; sell T, proceeds T+1). | Sim/accounting assuming T+2 (older docs) mis-times settled-cash and demat availability → false short-delivery or false buying-power. | Keep T+1 in Sim + accounting; ex-date = record-date under T+1. (SEBI T+0 pilot not relied upon.) | none |
| F17-d | Corporate-action cash events (dividends) create obligations; CA >5% cancels protective GTT | **CONFIRMED** | Kite GTT: GTTs auto-cancel on corporate actions and the broker does **not** adjust trigger prices. GTT statuses include `cancelled`. (Consistent with D18/D20.) Dividends are cash credits (not adjusted in most Indian feeds — D20). | A dividend/split cancels a resting stop; local state shows "protected"; a Kite-token expiry then prevents verification → silent unprotected position. Dividends also create INR cash-in obligations for accounting. | Keep D18 CA-monitor that re-places GTTs post-ex-date for CA >5%. Add a **broker cash-event ingest** for dividends (feeds D21 accounting). India dividends are domestic INR income — no Form-67/idle-FX (that is the US sleeve); do not conflate. | none (D18/D20 cover it) |

### F17 staging critique (brief's core claim)

**CONFIRMED.** The spec's §3/§5 describe a calendar-aware scheduler and a Kite-token-refresh job but
encode **no fail-closed session gate** (Muhurat/unscheduled-closure) and **no credential-readiness
gate** before order/protection work. Both are real omissions. The dividend cash-event flow is
partially covered by D18/D20/D21 but is not wired as an explicit ingest in §5.

---

## India compliance matrix by lifecycle stage

Labels: **PRIMARY-CONFIRMED** (regulatory or broker-operational primary), **SECONDARY** (media/blog
corroboration only), **INFERENCE** (design deduction from primary facts), **OPEN** (unresolved / needs
human decision).

### PRE-ORDER (deterministic gate, every order, before submission)

| Rule | Label | Source |
|---|---|---|
| Egress IP matched to broker static-IP whitelist (in force **from 2026-04-01**; non-order APIs exempt) | PRIMARY-CONFIRMED | Zerodha static-IP FAQ; NSE INVG67858 §A |
| Order carries broker-provisioned **exchange-issued algo-ID tag** (generic for below-TOPS registration-free algos; never self-minted) | PRIMARY-CONFIRMED | NSE INVG67858 §B.3, §G |
| OPS throttle ≤ conservative ceiling (≈2), hard-under 10 OPS/exch/segment | PRIMARY-CONFIRMED | NSE INVG67858 §B.2/§F; Kite exceptions |
| Account is in {own + immediate-family} allowlist; strategy never shared/sold | PRIMARY-CONFIRMED | NSE INVG67858 §A.7/§D–E; Zerodha declaration |
| CNC sell quantity ≤ settled demat holding (long-delivery-only; no short delivery) | PRIMARY-CONFIRMED | Z-Connect short-delivery; Kite margins |
| Per-signal minimum-cadence gate (slowest active signal) | INFERENCE (design) | D9a; not a regulatory rule |
| Order type = LIMIT with market-protection (API MKT needs protection band) | PRIMARY-CONFIRMED | stream-06 / Kite order rules |
| **Whether a below-threshold personal API algo must be exchange-registered for a generic ID before it can trade** | **OPEN** | NSE INVG67858 §B.3 says below-TOPS algos "require registration with the Exchange and a generic algo ID"; Zerodha's operational rollout treats personal ≤10 OPS as registration-free-but-tagged. Reconcile with Zerodha's live onboarding SOP before go-live. |

### PRE-LIVE SETUP (one-time capability precondition — hard blocker, not a per-order gate)

| Rule | Label | Source |
|---|---|---|
| CDSL **DDPI active** (else every delivery sell stalls on TPIN/OTP) | PRIMARY-CONFIRMED | Zerodha TPIN/DDPI FAQ |
| Static IP provisioned + whitelisted in Kite developer console (≤2 IPs, 1 change/cal-week) | PRIMARY-CONFIRMED | Zerodha static-IP FAQ |
| OAuth/2FA login flow; API session logged out daily before next trading day | PRIMARY-CONFIRMED | NSE INVG67858 §A.8, §I(c–d) |
| 5-year audit trail of signal→order (broker keeps; OS keeps its own append-only log) | PRIMARY-CONFIRMED | NSE INVG67858 §I(a) |

### PERIODIC / SESSION-BOUNDARY (scheduler-time, fail-closed)

| Rule | Label | Source |
|---|---|---|
| `SessionReadiness`: authoritative NSE calendar + observed close; unknown/ambiguous ⇒ FAIL-CLOSED; Muhurat timings read from same-day circular | PRIMARY-CONFIRMED (hazard) / INFERENCE (gate design) | NSE holidays page |
| `CredentialReadiness`: re-auth after ~07:30 IST token flush; TokenException ⇒ HALT + reconcile, never auto-retry | PRIMARY-CONFIRMED | Kite User + Exceptions docs |
| Daily GTT integrity reconcile: every open position has an active GTT; re-place post-ex-date for CA >5%; triggered-but-unfilled = emergency | PRIMARY-CONFIRMED | Kite GTT docs; D18 |

### POST-FILL / REPORTING (not a fill-path gate)

| Rule | Label | Source |
|---|---|---|
| Capital-gains tax lots (STCG / LTCG) — reporting layer only | SECONDARY | stream-06 (rates not re-verified here; out of this pass's scope) |
| Dividend cash-in recorded (INR domestic income; no Form-67/idle-FX — that is the US sleeve) | INFERENCE | D21; Kite margins |

### VERIFY-BEFORE-LIVE BLOCKERS (add to §7)

1. **Confirm the static-IP enforcement date and current status with Zerodha** (FAQ says 1 Apr 2026 — now in force; correct the "since 2025-04-01" error in D19). **PRIMARY available.**
2. **Confirm with Zerodha whether a personal below-TOPS API algo needs prior exchange registration for a generic algo ID, and how the tag is provisioned** (NSE §B.3 vs operational practice). **OPEN — broker SOP needed.**
3. **Confirm DDPI is active** on the trading account before any autonomous sell. **PRIMARY available.**
4. The **primary SEBI circular body** is not publicly rendered (JS page); the **operative NSE implementation circular INVG67858 is public and retrieved in full** — so the regulatory requirements are now primary-confirmed. Pull the SEBI PDF via an authenticated/rendered fetch only if a lawyer needs the verbatim SEBI text; it is **no longer a hard blocker** for the mechanics.

---

## Observable static-IP verification (F12 question: can the system verify its own egress IP?)

**Yes — verifiable pre-submission, in two layers:**
1. **Observed egress IP check (INFERENCE, sound):** before submitting, resolve the process's public
   egress IP (e.g. an allowlisted IP-echo endpoint or the known VPS static IP) and compare to the
   configured whitelisted static IP(s). Mismatch ⇒ FAIL-CLOSED (do not submit). This is the brief's
   "observed egress IP matched to the broker whitelist" gate and it is implementable without the broker.
2. **Broker-reject backstop (PRIMARY):** if egress does not match the Kite-whitelisted IP, Kite
   **rejects** the order at the API. So the residual risk of a wrong-IP order actually reaching the
   exchange is nil — but relying on rejection alone wastes an order attempt and muddies reconciliation,
   so the observable pre-check is the correct primary gate with broker-reject as defense-in-depth.

Note the whitelist can be changed at most **once per calendar week** (NSE §A.6 / Zerodha FAQ) — a
dynamic-IP host is unworkable; the always-on host (D22) must have a genuine static IP.

---

## Corrections this pass makes to `06-india-mechanics.md` and D19

1. **Static-IP effective date: 2025-04-01 → 2026-04-01.** Stream-06 recorded "1 Apr 2025 (CONFIRMED,
   Zerodha FAQ)"; the *current* Zerodha FAQ says **1 April 2026**. The 2025 figure appears to have been
   a mis-read of an earlier draft/rollout; the live primary source is unambiguous. D19 and spec §7
   inherit this error and must be corrected.
2. **Algo-ID tagging: below-threshold is NOT self-tagged/untagged.** NSE §B.3 + §G: below-TOPS algos
   require exchange registration for a **generic** algo ID, and **all** orders (below and above) carry an
   exchange-provided identifier. Stream-06's "generic if unregistered ≤10 OPS" was directionally right
   but understated the registration requirement; D19's "unique algo-ID tagging" is imprecise.
3. **Everything else in stream-06 §1/§3/§5 that this pass touched is corroborated by primary sources**
   (10 OPS TOPS, family-only sharing, OAuth/2FA, 5-yr audit, GTT DAY-limit/fire-once/CA-cancel,
   TokenException semantics, T+1, Muhurat). The stream-06 skeptic's "regulatory text not inlined"
   caveat is now **resolved for the NSE implementation circular** (retrieved in full).

---

## Decision-log amendment summary

- **D19 — amend (required):** (a) static-IP mandate effective **2026-04-01** (in force), not 2025;
  (b) algo-ID tag is **broker-provisioned, exchange-issued**, mandatory on every order incl.
  below-TOPS (generic ID); (c) restructure India rules by lifecycle stage (pre-order / pre-live-setup /
  periodic / reporting); (d) add explicit **own+family account allowlist** and **long-delivery-only /
  CNC-sell ≤ settled-holding** gates; (e) add verify-before-live blocker on the below-TOPS registration
  question.
- **D16 — amend (required):** add fail-closed **`SessionReadiness`** (authoritative calendar + observed
  close; Muhurat timings from same-day circular) and **`CredentialReadiness`** (re-auth after token
  flush; TokenException ⇒ HALT + reconcile, never auto-retry) as scheduler preconditions.
- **D18 — confirmed as-is:** DDPI-mandatory-pre-live, GTT fire-once/DAY-limit/recreate, CA >5% GTT
  re-placement are all primary-confirmed. No change.
- **D22 — minor note:** the daily Kite re-auth job must run **after the ~05:00–07:30 IST token flush**
  (schedule ≥07:30 IST); un-HALT/re-auth remains localhost-asymmetric.

## Needs-human-decision

- **The one OPEN item:** whether a personal below-TOPS API algo must be **exchange-registered for a
  generic algo ID before trading**, and the exact tag-provisioning path. NSE INVG67858 §B.3 reads as
  "registration required + generic ID issued"; common operational understanding treats personal
  ≤10 OPS as registration-free-but-tagged. This is a broker-SOP/legal question, not resolvable from
  the circular alone — flag for the pre-live legal/broker check.

---

_Self-audit: F12 (a–f + staging) and F17 (a–d + staging) each carry a verdict, primary source, failure
trace, smallest edit, and D-log impact; static-IP/algo-ID/OPS/DDPI/long-delivery pre-order-gate claim
validated with two corrections; compliance matrix organized by lifecycle stage with every rule labeled;
one OPEN item escalated; two errors in the authoritative log (static-IP date, algo-ID mechanics)
identified against current primary sources. No spec or RESEARCH-STATE.md file was edited._
