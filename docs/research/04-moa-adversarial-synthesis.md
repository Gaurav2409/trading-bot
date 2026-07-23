# MoA Adversarial Synthesis — Trading OS Research

> Manual MoA aggregation (3 cross-family reference drafts → Opus aggregator). 2026-07-18.
> The `/moa` fan-out wrapper hit an accounting bug (float-inf); references + aggregator were run directly with identical MoA semantics (cross-family drafts synthesized by the Opus aggregator).

---

3 reference-model drafts received.

# Adversarial Synthesis: Trading OS Design Pressure-Test

> Note on inputs: two drafts treated the inlined files as raw gather (correctly noting they are not peer MoA drafts); one counted them as drafts. This aggregation synthesizes all three regardless. The single most important integrity finding — hallucinated arXiv IDs in stream 2 — comes from only one draft and is escalated below.

## 1. Verification verdicts on flagged gaps

| Claim | Verdict | Reason |
|---|---|---|
| **SEBI Feb 2025 circular substance** (broker-gatekeeper, algo tagging, strategy registration) | **PLAUSIBLE** | Direction matches SEBI's multi-year path (2021 consultation → 2022 pilot → SSAAP-2025 enforcement). Body never fetched. **Load-bearing missed detail:** an order-frequency threshold above which even retail algos need exchange registration — verify verbatim; strict enforcement could impose weeks-to-months per-strategy broker pre-approval. |
| **Kite: no sandbox** | **CONFIRMED** | Never offered; repeatedly community-confirmed. |
| **Kite ~₹2,000/mo** | **CONFIRMED** | Stable multi-year figure (+GST per app). |
| **Kite ~3 req/s** | **PLAUSIBLE, don't hard-code** | Community-derived, not in official docs; order cap reportedly ~10/s burst, ~3/s safe sustained; historical API has separate lower limit + daily quota. Instrument adapter to count requests and back off on 429. |
| **Alpaca from India** (195+, W-8BEN, no SSN, free paper, $1, cash-PDT-exempt) | **CONFIRMED (mechanics)** | Consistent across docs + Indian-user reports. Caveats: LRS wire funding is friction-heavy (banks flag Alpaca as non-standard beneficiary); paper uses **IEX not consolidated tape** → volume signals (OBV) diverge; Alpaca clearing has had multi-day outages. |
| **IBKR India** (LRS $250k/yr, TCS>₹10L, ib_insync paper) | **PLAUSIBLE, entity-route DUBIOUS** | LRS/TCS/ib_insync confirmed. **Two drafts flag the same error:** to trade US equities from India you open **IBKR LLC/Ireland under LRS**, NOT the SEBI-regulated India entity — stream 1 conflated these. This breaks the "IBKR≈Alpaca swappable adapter" assumption if margin/instrument/API differ. |
| **PDT elimination rumor** | **DUBIOUS→FALSE** | SEC proposals exist; no final rule. FB headline is not a rule change. Design as if PDT fully in force. |
| **"Forward-paper-after-cutoff is the ONLY honest LLM scorecard"** | **OVERSTATED** | Necessary, not sufficient (N≈1 path). Stronger: post-cutoff CPCV+DSR + frozen prompts + code review. Correct narrow claim: for the *incremental* LLM alpha vs a rule-based baseline, post-cutoff forward paper is the honest measure. |
| **MadEvolve / QuantCode-Bench / AlphaAgent arXiv IDs** | **CANNOT-VERIFY — INTEGRITY FLAG** | One draft flags arXiv:2605.23007, 2604.15151, 2502.16789 as implausible/future IDs — **the Sonnet gather likely hallucinated citations.** Conclusions (LLM codegen better at mechanical than forecasting) are directionally credible, but do not cite these IDs as evidence. Audit all arXiv refs in stream 2 before building on them. |
| **Alpha Arena S1** (4/6 LLMs lost money live) | **PLAUSIBLE** | Public nof1.ai result; directionally load-bearing. |
| **TrendYCMacro 7.05%/−25%DD/0.60 Sharpe** | **DUBIOUS / CANNOT-VERIFY** | Single Quantpedia source, no OOS/CI, suspiciously clean (exactly 2× Sharpe, ⅓ DD). Direction plausible; do not use numbers as sizing inputs. |
| **QMJ 4.7%/yr** | **CONFIRMED** | Asness/Frazzini/Pedersen, widely replicated. Caveat: sample favored quality; post-2018 mixed. |
| **Integrated > component multifactor** | **CONFIRMED (direction)** | AQR + Blitz/Hanauer; reduces internal cancellation. Not guaranteed every window; still measure vs benchmark. |
| **Short-term reversal large-cap-only** | **CONFIRMED** | Well-replicated tx-cost/liquidity-premium finding. |
| **OBV flash-crash failure** | **PLAUSIBLE (mechanism), CANNOT-VERIFY (quant)** | Cumulative sum permanently distorted by panic spike — real principle; single Fyers blog. Consider rate-of-change volume instead. |

## 2. Contradictions & tensions across the streams

1. **Paper-first vs no-Kite-sandbox.** `SimulatedBrokerAdapter` is not a footnote — it's a multi-week load-bearing component that must replicate Kite fill semantics, order FSM, **lot sizes, STT/CTT/stamp/GST, T+2 settlement, circuit filters, rejection reasons**. It has its own validation problem (who validates the simulator?). A sim that ignores lot-size + STT produces paper results that don't translate.
2. **Kite ~3 req/s vs multi-analyst cadence.** 4 analysts × 20-stock backfill = 80+ bursted calls (~27s serialized). Fine for swing *only if* rate-limited at the adapter, not the caller. **Reconciliation-on-restart** (orders+positions+holdings across a wide book, two brokers) is the real burst risk.
3. **Two clocks conflated.** Signal clock = daily/EOD; risk/kill clock = tick/second. The streams never name this. Make it explicit or the scheduler merges them.
4. **LLM-as-forecaster (stream 3) vs LLM-as-risk-policy (QuantInsti, stream 2).** The locked design uses LLMs as forecast synthesizers with deterministic risk — the *opposite* of the evidence-based QuantInsti pattern. Neither stream flags this. It's defensible but the tension is real.
5. **Monthly-rebalance evidence vs "swing" branding + daily heartbeat.** Tier-1 signals (12-1 mom, value, QMJ) are statistically defined monthly+. Firing daily on them = trading outside the validated horizon + eating costs. Enforce a per-signal minimum-cadence gate; LLM path runs at the slowest signal's cadence, not 10-min.
6. **Two jurisdictions, one risk engine.** VaR/CVaR spans INR (NSE) + USD (US) positions. Covariance needs a common numeraire + FX rates. Numeraire undecided.
7. **Cash-account T+1 vs swing re-entry.** Exit-then-reenter next day is blocked by unsettled funds — constrains turnover/sizing. Unflagged.
8. **Fractional (Alpaca) vs whole-lot (Zerodha).** Sizing engine must map notional targets → integer qty with min-ticket, odd-cash residuals, FX, lot constraints.

## 3. Blind spots ALL THREE streams missed

- **Indian corporate actions.** Splits/bonuses/rights/mergers/ISIN changes; Kite's adjustment logic is opaque and historically buggy around bonus record dates. Must track adjustment factors independently. `auto_adjust` was only discussed for US/yfinance.
- **Full India transaction-cost model.** STT (0.1% delivery, both legs), stamp duty (state-varying), exchange/SEBI/GST — ~0.3–0.5%/round-trip can consume the entire Tier-2 edge. Apply Carver's "double-the-cost" test to the *Indian* structure.
- **Tax-lot accounting, two jurisdictions.** India STCG/LTCG (12mo threshold, post-2024 rates), US W-8BEN 30% dividend withholding, Schedule FA / Form 67. Must track lots per-jurisdiction from day 1 or you can't file.
- **Point-in-time fundamentals vendor.** Every Family-2/3 signal needs restatement-free PIT data. yfinance is restated. India PIT is *harder* than US (TrueData/Refinitiv/Tijori — unpriced, unvalidated). Production blocker for any fundamental analyst.
- **Kite daily-token refresh.** access_token expires daily via browser-click OAuth — autonomous operation needs token-refresh automation (Zerodha ToS approval required). Material daily operational risk.
- **Time-zone/session orchestration.** NSE 09:15–15:30 IST vs US 19:00/14:30 IST; DST bites twice/yr; dual-market EOD reconciliation; prevent LLM firing mid-session on stale data.
- **Broker outage & restart reconciliation.** Deterministic-hash reconciliation cited but never *designed*: restart with 3 open orders + 2 partial fills across two brokers.
- **MoA cost at scale.** 4 analysts × synthesis × 20 stocks × frontier models × daily ≈ $0.50–2.00/cycle → $180–730/yr — can exceed profits on a disposable balance. Never costed.
- **Short-sale constraints.** India equity shorting mostly intraday/derivatives; US shorting needs margin/borrow (conflicts with cash-account/PDT simplicity). Long-short factors need long-only adaptation.
- **LLM-provider governance.** All-providers-degraded fallback; prompt/account-data leakage; model/version drift (need decision cache keyed on prompt-hash + model-ID + schema-version).

## 4. Design decisions the evidence challenges

**Conviction → fixed-fractional → Kelly — RISKIEST for real-money loss.** All three drafts converge: Kelly needs calibrated edge; LLM conviction is not probability. Feeding conviction into Kelly lets the LLM covertly size, violating the invariant. **Fix:** v1 = fixed fractional (1–2% risk) + vol-targeting + position/correlation caps; Kelly used only as a *ceiling/sanity check*, ¼-Kelly at most, and only fed by a **calibration store** mapping conviction buckets → realized hit-rate (Beta-Bernoulli shrinkage; only mature buckets size).

**MoA in the live path — second-riskiest.** Evidence (Alpha Arena 4/6 losses, Bridgewater AIA underperformance, laundered-alpha) argues against per-symbol/daily MoA. Latency isn't the problem for swing — *cost, non-reproducibility, and uncalibrated narrative confidence* are. The design's "propose/dispose + conviction-never-size" already encodes the right discipline. **Mandate a null hypothesis:** a pure rule-based Tier-1 composite. If MoA doesn't beat it on post-cutoff forward paper, remove the LLM path. Run MoA offline/daily, cost-capped, only on candidates crossing materiality thresholds.

**Three-tier paper model — most supported, most implementation-fragile.** Correct structure. Gates are only meaningful if (a) `SimulatedBrokerAdapter` models Indian microstructure faithfully (lots, STT, T+2, partials on illiquid mid-caps) and (b) paper starts after LLM training cutoff. Both are non-trivial; budget for them explicitly.

**Comprehensive all-horizon catalog — challenges breadth for v1.** ~50 signals × 9 families = combinatorial overfitting surface; most are forecasting (where LLMs overfit), not mechanical (where they help). **Cut Family 7 (alt-data) from v1; mark Family 2/3 long-tilt-only.** Start with smallest defensible set: time-series + cross-sectional momentum, trend/MA timing, one quality proxy (if PIT exists), HMM/vol regime gate. Expand only after the null is rejected on forward paper.

## 5. Ranked open questions for the human

**1. Slot-C broker pick (Alpaca vs IBKR vs both).** Determines US-adapter design, funding rail, paper strategy, operational surface. Drafts split but reconcilable: **Alpaca as primary paper + v1 live** (free identical-API paper is the load-bearing gift for the paper-first gate; cash-account PDT-exemption fits swing; $1 min fits disposable balances). **IBKR as v2** for scale/global/reconciliation — but *first resolve the IBKR-LLC-vs-India-entity route*. Running both on a small balance multiplies ops (two reconciliation loops, two token flows, two cost models) for near-zero diversification benefit. Draft 2's "IBKR live / Alpaca paper" is inferior for v1 because it forces the harder onboarding + adapter before any live proof.

**2. Evaluation plane + calibration store.** The largest failure mode is believing false alpha, not latency. **Answer:** CPCV + Deflated Sharpe (N>1 trials) + post-cost sim + post-cutoff forward paper + frozen configs/prompt-hash/model-ID; no strategy goes live from MoA narrative. Calibration store schema: `(model, prompt_version, conviction_bucket, market, regime, hit_rate, payoff, sample_n, estimated_at)` — feeds sizing only at mature N. This is required *because* of the Kelly risk above.

**3. Kill-switch semantics.** Adopt NautilusTrader `ACTIVE/REDUCING/HALTED` verbatim, extended with **per-symbol** and **per-market suspend** (suspend NSE leg during outage while US continues). Triggers: manual (Telegram), DD-tier-2, vol-tier-3, broker-disconnect>N s, all-LLM-providers-down, reconciliation-mismatch. Cancels allowed in HALTED; new exposure never. Must degrade gracefully when Kite token-refresh fails (positions stay visible in state store).

**Lower priority (evidence is settled):** Data plane = TimescaleDB(OHLCV)+Postgres(fundamentals/LLM JSONB)+Redis(hot state) — hard part is correctness (adjusted prices, PIT, calendars, survivorship-free universe), not throughput. Portfolio state store = Postgres append-only event log as source-of-truth + Redis cache (Redis-only is insufficient). Scheduler = calendar-aware jobs (EOD ingest, monthly rebalance, event triggers, token refresh, reconciliation) — avoid continuous agent loops. HITL = Freqtrade-Telegram + expiring HMAC token + default-no-trade, never internet-exposed — solved pattern.

<!-- MOA-SYNTHESIS SELF-AUDIT: sections 1-5 present; 3 reference drafts received -->