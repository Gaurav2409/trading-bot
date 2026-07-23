# India Market Mechanics — Deep Research (Stream 06)

> Manual MoA aggregation (3 cross-family reference drafts → Opus aggregator). 2026-07-19.
> Ran references + aggregator directly (the `/moa` wrapper hit its float-inf accounting bug).

---

I received 3 reference-model drafts.

# India Market Mechanics — Ground-Truth Synthesis for a Zerodha Swing-Trading OS

**Skeptic's preamble:** The single most load-bearing weakness across all three drafts is that the actual **SEBI circular text and the NSE circular PDF (INVG67858) are NOT inlined**. Every regulatory "CONFIRMED" is confirmed *against Zerodha's or media's summary of the circular*, not the primary instrument. I downgrade accordingly below. Two numeric conflicts (rate limits, GTT count) and two "everyone knows" facts (Zerodha CNC brokerage, DP fee) are asserted without primary evidence in this corpus — flagged hard.

---

## 1. SEBI Retail Algo-Trading Registration — the India-live gatekeeper

| Claim | Verdict | Basis / caveat |
|---|---|---|
| Framework effective **Aug 1, 2025** | CONFIRMED (secondary) | ET + Marketfeed both state it |
| Retail self/client algo **≤10 OPS per segment per exchange ⇒ no exchange registration** | **PLAUSIBLE (high confidence)** — NOT primary-verified | Only Zerodha Z-Connect states the 10-OPS number, digesting NSE circular INVG67858. ET's own reporting says the threshold was "yet to be decided." The circular PDF is not inlined. Treat 10 OPS as the operating assumption, verify against the PDF before go-live. |
| **>10 OPS ⇒ exchange registration + unique algo ID** | PLAUSIBLE (Z-Connect) | Same source caveat |
| **Static IP mandatory for order placement from 1 Apr 2025**; non-order endpoints exempt; max 2 IPs; family-only sharing | **CONFIRMED** | Zerodha support FAQ — this is Zerodha's own operational rule, primary for our purposes |
| Static IP required **even below 10 OPS** | **CONFIRMED** | Zerodha support FAQ, explicit |
| Kite OPS limit **10/sec per client account**; 429 beyond; invalid orders also count | **CONFIRMED** | Kite exceptions doc + support FAQ |
| Orders tagged with algo ID (generic if unregistered ≤10 OPS; unique if registered) | PLAUSIBLE | Z-Connect table |
| Self-developed algos usable **only on own + immediate-family accounts** | PLAUSIBLE | Marketfeed + Z-Connect |
| Broker/vendor algos need per-strategy exchange approval; modifications re-approved | PLAUSIBLE | ET + Marketfeed corroborate; ET's wording sloppily implies *all* algos need approval — Z-Connect's carve-out for personal ≤10 OPS is the more precise reading |
| Black-box algos ⇒ RA license + research reports | PLAUSIBLE | ET + Marketfeed only; legal-review item before offering to anyone |
| Open APIs banned; OAuth/2FA required | PLAUSIBLE | Marketfeed + Z-Connect |
| Kite Publisher (manual click) is **outside** the algo framework | CONFIRMED | Kite FAQ |

**Design implication (all drafts agree):** A swing/EOD system placing a handful of orders/day is trivially <10 OPS and needs **no per-strategy exchange registration for personal use**. Hard-code these compliance invariants from day 1: (a) static-IP whitelist check before any order; (b) throttle well under 10 OPS (draft 2's suggestion of ~2 OPS headroom is sound); (c) immutable, timestamped audit log of signal→order; (d) kill switch; (e) **own/family accounts only — never sell or share the strategy** (that trips vendor/RA obligations, a hard legal boundary). Monitor SEBI/NSE circulars for post-implementation goalpost moves.

---

## 2. Full India transaction-cost model (equity DELIVERY / CNC round-trip)

Rates from NSE's official fee page (updated 17 Apr 2026) unless noted.

| Cost | Buy leg | Sell leg | Verdict |
|---|---|---|---|
| **STT** | 0.10% | 0.10% | **CONFIRMED** (NSE table) — dominates cost |
| **Stamp duty** | 0.015% | — (buy only) | **CONFIRMED**; uniform nationwide since 1 Jul 2020 — **do NOT model state-varying rates** |
| **SEBI turnover fee** | 0.0001% (₹10/cr) | 0.0001% | **CONFIRMED** |
| **Exchange txn charge (NSE cash)** | ~0.00297–0.00325% | same | **PLAUSIBLE / rate-varying** — SMC gives a *range*, not a fixed rate; NOT on the primary NSE fee page in corpus. Parameterize by exchange+date. |
| **GST 18%** | on (brokerage + exch txn + SEBI fee) | same | **CONFIRMED** — not on STT/stamp/principal |
| **Brokerage — Zerodha CNC** | ? | ? | **CANNOT-VERIFY** — corpus has NO Zerodha rate card. "Zero delivery brokerage" is industry-known but not proven here. Do not hard-code ₹0. |
| **DP charge (sell)** | — | flat ~₹12–30 + GST **per ISIN per day** | **PLAUSIBLE / broker-varying** — SMC range; Zerodha's exact fee not in corpus |

**Worked ~₹1,00,000 round-trip** (excl. brokerage, using ~0.0031% exch charge):
- STT ₹200 · Stamp ₹15 · Exch ~₹6.2 · SEBI ₹0.20 · GST on services ~₹1.15 → **subtotal ≈ ₹222.5 (~0.222%)**
- Add DP sell (~₹14–35) → **~0.237%–0.258% round-trip**, before brokerage.

**Flags:**
- **STT is ~80% of friction.** DP charge is **flat per ISIN per day** — *regressive*: it obliterates tiny positions. The simulator MUST model DP as a fixed cost, not bps, and consolidation of same-day sells reduces it.
- Options STT rose to 0.15% (sell premium), futures to 0.05% (sell) from 1 Apr 2026 — irrelevant to equity CNC, a landmine if F&O is ever added.
- Two numbers (Zerodha CNC brokerage, exact DP fee) must be verified against Zerodha's public brokerage calculator/contract notes before locking the cost model. Reconcile against real contract notes during paper/shadow.
- Capital-gains tax (STCG 20%, LTCG 12.5% > ₹1.25L per Kotak) is not a fill cost but belongs in the reporting layer.

---

## 3. Order mechanics & rate limits (BrokerAdapter + Sim)

**Kite GTT — CONFIRMED semantics (support + API docs + Z-Connect):**
- **Broker-side resting**, not exchange-native. Exchanges cancel all pending orders daily; Zerodha stores the trigger server-side and places a DAY LIMIT order on trigger. **This survives OS/process downtime** — the client process need not be alive; the broker must be. This directly answers the "resting protection without the process running" question: **yes, protected while broker is up.**
- Validity **365 days**. Types: `single`, `two-leg`/OCO, plus UI trailing SL. GTT orders are **LIMIT only** (API spec).
- **Fires ONCE.** If the triggered limit order doesn't fill by EOD, it's cancelled and **does not re-fire** — must be re-placed manually. This is the single most dangerous operational fact (see Risk 2).
- Triggers only **during market hours**.
- On gap-open through the trigger, GTT fires and places the limit order at the pre-set limit price; if the limit is far from the gap, it won't fill and is cancelled EOD.
- Margins/holdings checked **at trigger**, not at creation.
- **Auto-cancelled on corporate actions >5% of market value** (bonus/split/rights/amalgamation) before ex/record date — broker does NOT adjust trigger prices, it cancels.
- **Sell GTT on holdings needs CDSL TPIN unless POA/DDPI** — automation requires DDPI in place.
- **Max active GTTs: conflict — older Z-Connect says 100, current support says 500.** Use **500** (newer source authoritative) but treat as broker-configurable. Flag as stale-constant risk.

**Kite rate limits — two documented conflicts:**

| Limit | Value | Verdict |
|---|---|---|
| Orders/sec | 10 | CONFIRMED (docs + FAQ) |
| Orders/min | **400** (Kite exceptions doc) vs **200** (forum) | **CONFLICT.** Drafts split: draft 3 trusts docs (400), draft 2 uses lower for safety. **Recommendation: use the conservative 200/min internally**, since the forum-vs-docs conflict signals doc lag; a swing system never approaches either. |
| Orders/day | **5,000** (docs) vs **3,000** (forum) | **CONFLICT.** Same reasoning — use conservative 3,000 internally. |
| Modifications/order | 25, then cancel+replace | CONFIRMED |
| Quote 1/s, Historical 3/s, other 10/s | **DUBIOUS** — forum post only, not an official answer | Treat as community-derived; verify |

*Note: the docs' own "400/min, 5000/day" vs forum's "200/min, 3000/day" is a genuine documentation inconsistency. For a swing OS it's academic, but the conservative floor is the safe engineering choice.*

**Other CONFIRMED order rules:** Market orders via API require non-zero **market protection** or are rejected → use LIMIT with protection band, not MKT.

**Exception taxonomy (CONFIRMED, Kite docs):** `TokenException`(403→relogin, never auto-retry), `OrderException`, `InputException`, `MarginException`, `HoldingException`, `NetworkException`, `DataException`, `GeneralException`. HTTP 429=rate limit, 502=OMS down, 503/504=API down/timeout → exponential backoff, not hard-fail. **Sim must model hard rejections separately from unfilled orders.**

**Circuit filters / price bands (CONFIRMED):**
- Stock bands **2%–20%** by liquidity/category. Orders **outside band → rejected**; orders **at band → pending** until relaxed.
- F&O-underlying stocks: **dynamic 10%** band, relaxed after **15-min cooling**, no fixed daily circuit.
- Market-wide: Nifty50 or Sensex (whichever first) **10/15/20%** → coordinated halts; duration by level+time; 20% closes for the day.
- **Gap for the sim (draft 3's sharp catch):** per-stock band width at a *historical date* is not trivially available in these sources — NSE surveillance reports exist but historical band-change scraping is non-trivial. **UNRESOLVED.**

**Sim implication:** With daily bars only, do NOT assume triggers fill. Model: (a) reject-if-outside-band, (b) low-fill-probability queue-at-band, (c) full market halts, (d) gap-through does not guarantee fill.

---

## 4. Data-correctness decisions (D20)

**Corporate actions / split adjustment:**
- Primary CA source: **NSE `/companies-listing/corporate-filings-actions` + BSE corporate actions** (both in corpus; give ex-date, record date, purpose, ratio).
- Kite historical "adjusted for splits and bonuses" rests on **one 2018 ValuePickr forum comment** — **PLAUSIBLE, thin.** No official Zerodha doc in corpus specifies methodology, timing, or dividend handling. **Dividends are typically NOT adjusted in Indian feeds** — the classic gotcha.
- **DO:** Maintain an **independent CA factor table** from NSE/BSE feeds; compute your own adjusted OHLC; store raw+adjusted. Use Kite as convenience feed, **validate against NSE Bhavcopy on 3–5 known split/bonus events** before live. Watch for double-adjustment. CA events must also invalidate resting GTT/stop logic (mirroring Zerodha's >5% cancellation).

**Point-in-time fundamentals:** screener.in (incomplete), Trendlyne (good coverage, PIT unproven), EODHD (thin for India: 5yr/10q non-US), iXBRLAnalyst. **No source proves PIT/restatement-safe India fundamentals — genuine gap, CANNOT-VERIFY.** **DO:** For v1, prefer price/volume/technical factors. If fundamentals needed, start **weekly self-snapshots with your own timestamps** (poor-man's PIT) now; impose conservative reporting lags; never claim PIT rigor for pre-snapshot data.

**Survivorship-free universe:** rkohli3 academic page quantifies material bias (**3.5–4.4%/yr** on Nifty 500 factor portfolios) — strong prior that correction is mandatory. Optuma (paid) claims Nifty 50 from Jan 2010, Nifty 500 from Feb 2008 (vendor claim). niftyhistory.in advertises free survivorship-free ledgers but corpus shows only a **bare landing page — CANNOT-VERIFY quality.** **DO:** **Never backtest on current constituents** (~3–4%/yr overstatement makes everything look profitable). Acquire a monthly add/drop ledger (Optuma or self-built from NSE index-change announcements); validate one source against another before trusting.

**KG Layer-2 news (GDELT):** Free, 15-min cadence, global, Google-hosted — CONFIRMED as a data source. **No evidence in corpus of India-equity signal quality, entity-resolution, or single-stock catalyst coverage.** Weak for Indian single-stock events (earnings, RBI, court orders). **DO:** Use as a broad news/event overlay after entity-mapping, dedup, source-scoring, and latency logging — **not a standalone alpha trigger.** Supplement with NSE/BSE announcement feeds (in corpus, scraper-only, no clean API).

---

## 5. Market calendar/session facts + ranked open risks

**Session (NSE equities), from Groww — verify against NSE official live (the NSE market-timings fetch in corpus mis-resolved to an SAP page):**
- Pre-open **09:00–09:08** (random close last minute); matching after.
- Regular **09:15–15:30**. Closing session **15:40–16:00**.
- Block deal windows **08:45–09:00** and **14:05–14:20** (draft 3 lists 02:05–02:20 — minor conflict; both are afternoon; verify against NSE).
- Muhurat trading **Sun 8 Nov 2026** (Diwali).

**Settlement: T+1 rolling — CONFIRMED via Zerodha Varsity** (ex-dividend = record date under T+1). Sim must use **T+1**, ex-date=record-date for dividends. SEBI's T+0 pilot is **not in corpus — CANNOT-VERIFY; stick with T+1.**

**Holiday calendar:** NSE `/resources/exchange-communication-holidays` is primary but the corpus scrape rendered a selector without the table; Groww gives a full 2026 list (16 trading holidays). **DO:** Ingest programmatically from NSE's official circular/CSV; use Groww/BSE only as fallback; **fail closed on unknown trading days.** Don't hardcode.

### Top 3 unresolved risks + what the evidence implies

**RISK 1 — Regulatory exactness (SEBI/NSE circular text not in corpus).** Every algo-compliance "fact" is a Zerodha/media summary. *Implication:* Before live, **obtain and encode the official SEBI + NSE circular/SOP.** Until then, operate strictly inside the safe envelope: static IP + throttle ~2 OPS + own/family accounts only + immutable audit log + kill switch + no strategy sale/sharing.

**RISK 2 — GTT is fire-once, auto-cancels on CA, market-hours-only.** A naive "set a stop, I'm protected" design silently fails on gap-through-no-fill, corporate actions, and partial fills — leaving unprotected positions. *Implication:* Build a **daily EOD reconciler** that (i) verifies every intended stop has an active GTT, (ii) re-places GTTs post-ex-date for CA >5%, (iii) treats triggered-but-unfilled GTTs as emergencies. Never assume standing protection.

**RISK 3 — Data bias trifecta: survivorship + CA adjustment + absent PIT fundamentals.** Corpus directly shows survivorship bias is material (3.5–4.4%/yr), CA adjustment is unverified in Kite, and no PIT India fundamentals source exists. *Implication:* **No production capital from backtests using current constituents or unverified adjusted/PIT data.** Restrict v1 to price/volume factors on a survivorship-free universe with self-validated CA factors; defer fundamental strategies until a timestamped snapshot panel accumulates.

*Lesser open risks:* rate-limit doc conflicts (200/400/min; 3000/5000/day) — use conservative floors; historical band-width-per-stock unavailable for sim; NSE data-vending TOS forbids redistribution (UI must not expose raw Kite ticks to third parties); short-delivery/auction penalties (~24% p.a. per SMC) unmodeled by naive sims; exact Zerodha brokerage/DP fees unverified in corpus.

<!-- MOA-SYNTHESIS SELF-AUDIT: sections 1-5 present; 3 reference drafts received -->