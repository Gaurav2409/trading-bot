# Production-Grade Autonomous/Algorithmic Trading Systems: Architecture Research

> Research stream 2 of 3 (Sonnet web-research gather). Compiled 2026-07-18.
> Raw sources: `/tmp/trading-os-research/architecture/` (75 files)
> NOTE: pending MoA adversarial verification pass.

---

## Topic 1: Deterministic Hot Path vs. LLM Research Path Separation

**Two-speed architecture is an invariant, not a guideline.** Slow research/signal path (LLMs allowed) vs fast deterministic execution path (LLMs forbidden).

**NautilusTrader single-threaded kernel** (canonical reference): MessageBus + actor dispatch, strategy logic, RiskEngine checks, ExecutionEngine routing, Cache — single thread, deterministic event ordering. Network I/O, persistence, adapters on separate threads/async runtimes, communicate via channels. Source: https://nautilustrader.io/docs/latest/concepts/architecture

**Order submission flow:** Strategy `submit_order()` → MessageBus command → RiskEngine validates (price precision, qty bounds, notional, balance, rate limits, trading state) in-process no-network no-LLM → ExecutionEngine routes to ExecutionClient adapter → adapter submits REST/WS → fills flow back venue→adapter→ExecutionEngine→Cache→strategy. **Deterministic path never calls an LLM.** LLM research (regime, sentiment, signals) runs async at minutes-to-hours cadence, writes signals to Cache that strategy reads. Source: https://nautilustrader.io/docs/latest/concepts/execution

**LMAX Disruptor / Actor model** inspiration (Martin Fowler LMAX architecture) — single-threaded core, no lock contention, pre-allocated ring buffers.

**Event types (QuantStart):** MARKET → SIGNAL → ORDER → FILL. 10-min heartbeat is natural boundary for LLM analysis in swing systems.

**Latency budget:** hot path responds to fills/risk in ms. LLM calls = 1–30s + non-deterministic → disqualifying for hot path. LLM output = typed structured object (position target, regime label, conviction) read by deterministic engine.

**Fail-fast:** panic on arithmetic overflow, NaN prices, invalid timestamps, negative qty. "Corrupt data is worse than no data." `panic=abort` in release → clean termination not corrupt continuation.

---

## Topic 2: Broker Adapter Abstraction Patterns

**Ports-and-adapters / hexagonal.** NautilusTrader `ExecutionClient` ABC = port; each broker = adapter. Strategy/risk never call broker-specific code; issue commands to ExecutionEngine which routes by venue ID. Source: https://nautilustrader.io/docs/latest/concepts/execution

**Canonical order schema:** 9 order types (Market, Limit, StopMarket, StopLimit, MarketToLimit, MarketIfTouched, LimitIfTouched, TrailingStopMarket, TrailingStopLimit) mapped to FIX 5.0 SP2 `OrdType<40>`. Adapter translates canonical↔broker-native.

**Order lifecycle FSM:** INITIALIZED → SUBMITTED → ACCEPTED → PARTIALLY_FILLED → FILLED. Terminal: DENIED, REJECTED, CANCELED, EXPIRED, FILLED. In-flight: SUBMITTED, PENDING_UPDATE, PENDING_CANCEL. Source: https://nautilustrader.io/docs/latest/concepts/orders

**Idempotent submission:** dual keys `client_order_id` (system) + `venue_order_id` (exchange). `trade_id` dedup enforced at `Order.apply()` — hard error on duplicate. Reconciliation sanitizer pre-filters on trade_id. **Reconciliation trade_ids are deterministic hashes of fill inputs** → restart replay is idempotent.

**Partial fills:** `PARTIALLY_FILLED` tracked; `leaves_qty` maintained; overfills handled (`allow_overfills` default False; `overfill_qty` tracks excess).

**Reconciliation reports (4):** OrderStatusReport, FillReport, OrderWithFills, PositionStatusReport.

**Other frameworks:** backtrader `BackBroker` (get_cash/get_value/getposition/get_orders_open + slippage models); freqtrade `exchange.py` wraps ccxt (encapsulates rate limits/order types/fees). Source: backtrader.com/docu/broker, freqtrade exchange.py

**OMS type abstraction:** NautilusTrader maintains "virtual positions" to run HEDGING strategy on NETTING venue.

---

## Topic 3: Multi-Agent LLM Decision Architectures

**"The model proposes; deterministic code disposes"** — recognized production pattern.

- **Man Group AlphaGPT:** 3-agent (Idea Person → Implementer → Evaluator). Evaluator applies statistical-significance thresholds identical to human research. "Architecture designed to absorb hallucination rather than prevent it."
- **Two Sigma:** LLMs widen the top of the research funnel (hypothesis generators), shift bottleneck to evaluation. Not execution engines.
- **Bridgewater AIA fund (cautionary):** +11.9% 2025 vs Pure Alpha +33% vs S&P +. Full autonomy underperformed. "Machines generate; humans hold the veto."
- **QuantInsti guardrailed LLM risk manager (concrete):** LLM = risk manager not forecaster ("what exposure in this state?" not "will price rise?"). Monthly walk-forward builds fresh LLM policy table from historical regime stats. LLM outputs typed JSON policy `{state: action}`, action ∈ {LONG_FULL, LONG_HALF, FLAT}. Hard guardrails override LLM (vol stop, drawdown stop, cooldown). Warning zone at 60% of DD limit → halve. `MAX_FLAT_DAYS` deadlock fix. Strict JSON + retry + cache (key = month,symbol,model,version). Source: https://blog.quantinsti.com/ai-aapl-trading-risk-manager-deepseek-python/
- **CrewAI multi-desk:** 4 desks parallel (Market+Quant, News+Social, Fundamentals+Sector, Macro+Geopolitical) → bull-vs-bear debate → manager picks → trader plans → risk panel stress-tests → **typed validated object** (action, conviction, entry, stop, target, horizon, rationale, drivers, "what would change my mind"). "Typed boundary is the handoff, where the model's authority ends. Once it crosses the seam, no model call changes a number." Source: https://medium.com/data-science-collective/from-prompt-to-p-l...
- **AgentTrading:** 8-gate deterministic RiskEngine on every LLM action; HMAC-chained audit log; `DRY_RUN` gate (LLM can't submit live without explicit flag); JSON-Schema tools ("model cannot invent fields"). Source: https://medium.com/@gwrx2005/agenttrading...

**Non-reproducibility:** LLM committee = stochastic distribution not deterministic value. Log properly: (a) cache every response keyed (date,model,version,prompt-hash); (b) log full typed decision object; (c) evaluate distribution vs null (rule-based). Cherry-picking single good calls is invalid.

**LangGraph mechanics:** Nodes+Edges+State graph. Single-threaded super-steps (Pregel). Parallel nodes = same super-step. State = TypedDict/Pydantic. Reducers control update accumulation. `interrupt_before`/`interrupt_after` + checkpointer = HITL. Source: https://langchain-ai.github.io/langgraph/concepts/multi_agent/

---

## Topic 4: LLM Router / Model-Swappability

**LiteLLM as provider-agnostic interface.** `router.acompletion(model="logical-name", messages=[...])` — code calls logical role name, router maps to physical deployment(s).

`litellm.Router`: load balancing across deployments; routing strategies (weighted/rate-limit-aware/latency/least-busy/lowest-cost); reliability (cooldowns, fallbacks, timeouts, retries); Redis for cooldown+TPM/RPM state; per-deployment rpm/tpm.

**Role→provider pattern:** logical roles (`research`, `risk-assessment`, `signal-generation`) as model aliases → one or more physical provider+model. Swap in config, no code change. For trading: research=frontier model; regime-label=cheap fast; risk=deterministic rule (LLM fallback only).

**Invoke contract:** `invoke(role, prompt, schema) → TypedObject`. Schema = JSON-Schema constraining output. Router handles selection/retry/parsing. Caller gets Pydantic object never raw text. 100+ providers. Source: https://docs.litellm.ai/docs/routing

→ **Directly validates locked decision D3.**

---

## Topic 5: Position Sizing & Risk Engines

**Kelly:** full `f = p/l - q/g`. Too aggressive in practice (extreme drawdowns) → **half or quarter Kelly** standard. "Valid only for fully known probabilities, almost never the case." Source: en.wikipedia.org/wiki/Kelly_criterion

**Kelly multi-asset (Riskfolio-Lib):** "Logarithmic Mean Risk (Kelly) Portfolio Optimization" — 26 convex risk measures, 4 objectives. Maximize expected log return s.t. constraints.

**Confidence-adjusted Kelly:** regime detector outputs `confidence_boost` (ranging +0.1, volatile −0.5); Kelly × (1+boost); hard cap MAX_LEVERAGE=1.0.

**VaR (variance-covariance):** `VaR = P - P*(α(1-c)+1)`. $1M @ 99% ≈ $56,503 daily. Limits: assumes normality, no tails, backward-looking. Source: quantstart.com VaR

**CVaR/Expected Shortfall:** magnitude beyond threshold. Riskfolio-Lib: CVaR, EVaR, RLVaR, CDaR, EDaR.

**Ledoit-Wolf covariance shrinkage:** standard for correlation-adjusted sizing; shrinks sample cov toward structured estimator; `sklearn.covariance.LedoitWolf`; used in HRP/HERC.

**Drawdown throttle 3-tier:** (1) warning >60% of limit → halve; (2) hard stop >limit AND trend broken → exit+cooldown; (3) vol stop >threshold AND vol accel → exit+cooldown. Confirmation conditions prevent false exits (DD stop needs DD>limit AND 63d momentum negative AND price<50d MA).

**Kill switch (NautilusTrader TradingState):** ACTIVE (all allowed) / HALTED (new submit/modify denied, cancels pass) / REDUCING (only exposure-reducing).

**Pre-trade gate (RiskEngine):** validates every submit/modify — price precision, qty precision+bounds, GTD expiry, reduce_only, max_notional_per_order, cash balance, rate limit (RPM), trading state. Denial → `OrderDenied` with `CATEGORY_CONDITION: key=value` reason code.

---

## Topic 6: Overfitting & Paper→Live Validation — "Laundered Alpha"

**Critical 2026 finding:** LLMs with code interpreters run REAL sandboxed backtests — Sharpe is computed not hallucinated. New problem: **laundered alpha** = real figure from genuinely-executed code on a contaminated experiment.

**Four contamination channels:**
1. **Memorization:** LLMs recall exact historical prices during training-data periods. "Instructions to respect historical boundaries fail to prevent recall-level accuracy." Post-cutoff performance collapses. (arXiv:2504.14765)
2. **Silent best-of-N:** at $0.02/query, running 50 configs and showing the winner is p-hacking. "Backtest overfitting leads to NEGATIVE expected OOS returns, not zero." (Bailey/Borwein/López de Prado/Zhu, SSRN 2308659)
3. **Crowding:** models trained on same corpus → correlated strategies → homogeneous factors worsen crowding + decay. (AlphaAgent arXiv:2502.16789)
4. **Semantic misalignment:** code runs, computes Sharpe, implements a DIFFERENT strategy than specified. (QuantCode-Bench arXiv:2604.15151)

**Laundered-Alpha Litmus Test (5 Q):** (1) WINDOW: entire backtest after training cutoff? (2) TRIALS: how many configs before this? (DSR if >1) (3) NOVELTY: would 1,000 users get a different strategy? (4) SEMANTICS: does code implement exact spec? (read code not chart) (5) EVALUATOR: mechanical (crisp) or forecast (noisy)? trust former only.

**MadEvolve (arXiv:2605.23007):** LLM code evolution improves OOS Sharpe on *mechanical* subproblems (execution, portfolio construction) +0.62 to +1.83, while forecasting overfits. **Point LLM codegen at mechanical parts (execution, risk), never price forecasting.**

**Alpha Arena S1 (live forward test):** 6 models $10k each trading crypto live: Qwen3 Max +22.32%, DeepSeek +4.89%, Claude Sonnet 4.5 −30.81%, Grok 4 −45.3%, Gemini 2.5 Pro −56.71%, GPT-5 −62.66%. 4 of 6 lost money. StockBench v2: "most models struggle to beat buy-and-hold."

**Deflated Sharpe Ratio (Bailey/LdP, SSRN 2460551):** corrects selection bias under multiple testing. Required when multiple configs tested. Adjusts observed Sharpe by expected max from N trials.

**Walk-Forward (WFO):** rolling in-sample opt + OOS validation. E.g. 5Y in-sample, 1Y OOS, roll annually. Limits: window selection bias, regime lag (reacts not predicts), compute cost. Source: quantinsti WFO, IBKR campus.

**CPCV (López de Prado):** all train/test splits of k groups from N blocks, purging overlap. More powerful than WFO; produces distribution of Sharpes. CPCV + DSR = most defensible pre-live validation.

**Min paper period:** no peer-reviewed standard; empirical ≥3 months daily-freq, 6+ preferred; must cover ≥1 full regime (bull+correction or ranging+trending). **For LLM strategies: paper period MUST start AFTER model training cutoff to avoid recall contamination.** → forward paper is the ONLY honest LLM scorecard.

**"Double the cost" test (Rob Carver):** still positive expectancy if transaction costs doubled? Tests slippage robustness.

**Survivorship bias:** use point-in-time universe; current index constituents exclude dead/delisted → inflated alpha.

---

## Topic 7: Data Plane for Swing-Frequency Systems

**Kafka/NATS is overkill; Postgres + Redis + TimescaleDB sufficient.** Swing (hours-days) needs correct, not fast, data.

- **Kafka/NATS appropriate for:** HFT/market-making (sub-ms), 100s of strategies on same feed, multi-DC fan-out, event-sourcing replay at scale.
- **Postgres+Redis sufficient (swing):** daily/hourly OHLCV → Postgres/TimescaleDB; positions/portfolio/order state → Redis (sub-ms, hashes); LLM signals → Postgres table read at heartbeat; audit → Postgres (append-only ACID). TimescaleDB adds hypertables, continuous aggregates, compression, time_bucket(), retention.
- **Redis in finance:** real-time position tracking, OMS state, sub-ms portfolio queries. NautilusTrader uses Redis for state persistence/restart.
- **NautilusTrader data flow:** DataClient(WS) → MPSC channel → DataEngine → Cache(in-memory) → MessageBus publish → strategy on_quote_tick(). Cache write before publish. Persistence on separate Tokio runtime.
- **Corporate actions:** split-adjusted prices non-negotiable. `auto_adjust=True` mandatory — "split days produce fake return spikes that poison rolling vol, z-scores, trend scores." Point-in-time dividend adjustment for total return.

**Recommended swing stack:** historical OHLCV → TimescaleDB hypertables on (symbol,timestamp); real-time → Redis pub/sub + hash; orders/positions → Postgres; LLM outputs → Postgres JSONB with generated_at/model_version; session cache → Redis.

---

## Topic 8: HITL Approval Patterns

**Telegram + expiring tokens (Freqtrade reference):**
- Bidirectional Telegram control; per-event notification granularity (entry/entry_fill/exit/stop_loss/emergency_exit each on/silent/off).
- `authorized_users: ["1234567"]` — only listed IDs issue commands; others read-only.
- Commands: /forcebuy, /forcesell, /emergencysell, /stopbuy, /reload_config.
- REST API: JWT-secured, /api/v1/forcebuy etc., localhost-only + SSH tunnel/VPN (never internet-exposed).

**Expiring-token / default-to-no-trade pattern:**
1. Proposal → Telegram notification with inline Approve/Reject + "Expires in 10 min".
2. No response within timeout → **default to NO-TRADE** (conservative).
3. Approved → execute via REST with one-time HMAC-signed token (single-use, time-limited).
4. All decisions (approve/reject/timeout) logged with timestamp.

**Practical HITL progression:** Phase 1 (paper) 100% HITL; Phase 2 (early live) below-threshold auto, above-threshold HITL; Phase 3 (mature) HITL only for portfolio risk events / large trades. Kill switch always via Telegram /emergencysell → HALTED.

**LangGraph HITL:** `interrupt_before`/`interrupt_after` + checkpointer (Redis/Postgres); human review node blocks until external approval signal updates graph state.

---

## Concrete Patterns Directly Usable in Design

| Pattern | Contract | Source |
|---|---|---|
| Single-threaded kernel | Deterministic event ordering; no LLM in kernel | NautilusTrader |
| Ports-and-adapters brokers | ExecutionClient ABC; canonical FIX-mapped order schema | NautilusTrader |
| Idempotent submission | trade_id dedup; deterministic reconciliation hashes | NautilusTrader |
| LLM router | invoke(role,prompt,schema)→TypedObject via LiteLLM | LiteLLM |
| LLM as risk mgr not forecaster | Policy table (state→exposure) | QuantInsti |
| Typed decision handoff | LLM→validated Pydantic→deterministic modules | CrewAI/Medium |
| Hard guardrail override | Vol stop + DD stop + confirmation | QuantInsti |
| 3-tier risk throttle | Warning(halve)@60%, hard stop@100%, deadlock fix | QuantInsti |
| Walk-forward | 5Y IS / 1Y OOS rolling | QuantInsti/IBKR |
| Laundered-alpha litmus | 5-Q checklist for LLM strategies | jiripik.com |
| Deflated Sharpe | Apply when N>1 configs | SSRN 2308659/2460551 |
| LLM cutoff gate | Paper period after model cutoff | jiripik.com |
| TimescaleDB | Hypertables (symbol,timestamp); compression | TimescaleDB |
| Telegram HITL | authorized_users, per-event, default-no-trade | Freqtrade |
| TradingState | ACTIVE/HALTED/REDUCING kill switch | NautilusTrader |
| Fractional Kelly | Half/quarter Kelly for sizing | Wikipedia/Varsity |
