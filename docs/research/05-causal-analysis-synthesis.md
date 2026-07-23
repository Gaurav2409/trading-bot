# Causal Analysis Deep Research — Macro→Micro Propagation via Causal KG

> Manual MoA aggregation (3 cross-family reference drafts → Opus aggregator). 2026-07-19.
> Ran references + aggregator directly (the `/moa` wrapper hit its float-inf accounting bug again).
> Question: prior art + real-trading-bot practice for propagating macro/geopolitical/commodity shocks through a causal/relational graph to individual equities; implications for our two-layer causal-KG design.

---

3 reference-model drafts received.

## 1. Prior art map — who has solved macro→micro causal propagation, and how

| Approach / source (as titled) | Mechanism: shock → named stock | Evidence quality | Academic / deployed |
|---|---|---|---|
| **TRACE: Temporal Rule-Anchored Chain-of-Evidence on KGs** (arXiv 2603.12500) | Temporal KG (Company/Event/Product/TextSource); mined relation-sequence rules (`ACQUIRED∧CAUSED_INCREASE⇒UP`) constrain rule-admissible beam search from stock→news; verdict = max-confidence grounded path. Closest analogue to your Layer-1. | **PLAUSIBLE-but-suspicious.** ~4pp accuracy lift (55.1% vs ~51%) is slim. 41.7% return / 2.00 Sharpe is a no-cost, no-rebalance, single-hold Top-10 basket in a bull year — not tradable evidence. **The arXiv ID (2603.xxxxx, "16 Mar 2026") is future-dated; verify the paper exists before quoting any number.** Drafts disagreed (draft 3 called it "verifiable," draft 2 flagged the date as anomalous) — treat as unverified. | Academic; Aily Labs affiliation suggests partial industry work, unconfirmed. |
| **Predictive AI with External Knowledge Infusion / SmKG / TA-HKGE** (arXiv 2504.20058) | 20-yr NSE+NASDAQ temporal KG (macro indicators, corporate events, 1st/2nd-order Wikibase relations); edges modeled as heterogeneous Hawkes events; fused with transformer price embeddings to rank stocks 1/5/20-day. Macro events (COVID→pharma+/banks−) ripple via *learned* embeddings, not explicit paths. | **PLAUSIBLE.** Directly covers NIFTY500. Ranking-metric lift only; high variance across 24 windows; no cost analysis; performance degrades as training window lengthens (drift). Timestamp also looks future-dated — verify. | Academic. |
| **Predicting stock price movements in supply chain networks** (Rios, U. Iowa PhD 2021, DOI 10.17077/etd.005884) | Buyer-supplier graph (~2,600 firms, Mergent Horizon); HT-GNN+LSTM propagates neighbor stock signals to focal firm; community-based/2-hop neighbors beat direct-only. | **CONFIRMED mechanism, DUBIOUS alpha.** Real evidence that beyond-direct neighbors carry signal; but static 2020 graph (stale), modest AUC, self-described toy trading sim. | Academic. |
| **Estimating the impact of supply chain network contagion on financial stability** (Tabachová et al., JFS 2024) | Near-complete Hungarian firm-firm SCN + bank loans; multilayer cascade of a firm shock → defaults → bank-equity loss. SCN contagion amplifies EL/VaR/ES by 5.2/6.7/4.4×. | **CONFIRMED — strongest causal-identification paper in corpus.** But it is *credit-default* propagation, not equity returns; transferability to daily equity price is unproven. | Regulatory/central-bank risk; not equity trading. |
| **Oil Price Uncertainty Shocks and Global Equity Markets** (Salisu/Gupta/Demirer, JRFM 2022, GVAR) | 26-country GVAR; oil-uncertainty shock enters as global variable → IRFs on real equity prices. Oil exporters / high-complexity economies hit harder; recovery heterogeneous. | **CONFIRMED** for macro→equity direction. Quarterly, country-level — cannot name stocks. Critical: **GARCH-based uncertainty gave mostly *insignificant* IRFs; SV-based gave significant ones** — the uncertainty metric dominates the result. | Academic/policy. |
| **Geopolitical Risk Factors and Stock Returns: A Global Analysis** (Rafi & Ali, Nasdaq Foundation preprint) | GPR/GPA/GPT indices → HML beta factors across 40 country indices; Westerlund-Narayan predictive regressions. Threat factor (GPTF) strongest: significant in 58% at t-1. | **MIXED/PLAUSIBLE.** Sound method, survives FF5 in 33–45% of countries. **Predictability peaks at t-1 and is largely gone by t-4 (~4 days); effect ~0.23%/day; OOS R²>0 in only ~60% for GPTF.** Country-level, not firm-level. PDF metadata reads "Overleaf Example" — treat as preprint. | Academic. |
| **Understanding Geopolitical Risk in Investments** (MSCI blog) | Blended GPR+WUI regime indicator; high-GPR regimes → lower equity returns, higher vol; energy/materials/consumer-services most variable, healthcare/utilities least. Adds info beyond VIX. | **CONFIRMED practitioner adoption.** Regime/sector level; markets often react to *threat* as much as *realization*; medium-term impact "often limited." | Deployed-adjacent (MSCI exploring factor-model integration). |
| **Uncovering The Causal Effects of Commodity Price Shocks** (Curátola de Melo, FGV-EESP 2023) | Identification-through-heteroskedasticity using USDA Grain Stocks / OPEC days as variance instruments → contemporaneous causal effect on CDS, indices, FX. | **CONFIRMED.** Key warning: **OLS overstates commodity→equity effects (some shrink toward zero); oil instrument is *weak*.** Directly indicts correlation-based edge weights. | Academic. |
| **LLM-enhanced multi-causal event causality mining** (Springer JKSU-CIS 2025) | LLaMA extracts event tuples `(class,actor,action,object,time,location)`; GNN refines edge probabilities; transitive closure → indirect chains. | **PLAUSIBLE but CANNOT-VERIFY downstream.** Coherent authoring machinery; no trading eval; acknowledges implicit-causality & coreference false positives. | Academic. |
| **FinGPT: Dissemination-Aware…** (arXiv 2412.10823) | BERTopic-cluster news; cluster size/span = dissemination breadth; LLM predicts weekly direction. 63% vs 55% baseline. | **DUBIOUS as causal propagation** (sentiment, not structure). 380 obs / 20 firms / short window; no costs. | Open-source (HuggingFace/FinRobot). |
| **AInvest / Wisuno event-driven articles** | Practitioner playbooks: geopolitical shock → gold/oil/JPY/regional equities; reactions often reverse 24–72h. | **CANNOT-VERIFY / marketing.** No rigor; useful only as color. | Commercial content. |

**Hallucination flags (reconciled across drafts):** the two most design-relevant papers — **TRACE (2603.12500) and SmKG (2504.20058) — carry future-dated timestamps.** Drafts split on whether TRACE is verifiable. **Do not treat their numbers as ground truth until an author/venue is independently confirmed.** The Nasdaq GPR paper is an unreviewed preprint; AInvest/Wisuno/ResearchGate fragments are not evidence.

## 2. What to STEAL for our two-layer causal-KG design

**Layer 1 (deterministic traversal → exposure vector):**

- **Rule-admissible motifs, not free walks (TRACE).** Version + unit-test a fixed motif library, e.g. `MacroEvent(OIL_SUPPLY_SHOCK) → priced_in → Commodity(CRUDE) → depends_on⁻¹ → Sector(AIRLINES) → contains → Company`. Each motif has a sign convention and max depth.
- **Lexicographic path scoring w/ anti-hub penalty (TRACE).** Steal `(rule_completion, coverage, recency, anti-hub, −length)`. The **anti-hub term is the single most important theft** — without it "global economy"/"oil" hubs make everything exposed to everything.
- **Multiplicative confidence × hop-decay × time-decay.** `exposure(C,M)=Π(edge_conf)·β^hops·γ^days_since·magnitude_class_weight`, β≈0.4–0.6, cap depth ≤3 (TRACE D_max=3; Rios shows signal dies past 2–3 hops). All numbers owned by code.
- **Multilayer cascade math (Tabachová et al.)** is directly reusable for iterated propagation with decay — but note their 4–7× amplification is the *warning* to cap iterations, not license to propagate freely.
- **Shock taxonomy, not just direction (GVAR + Curátola + MSCI).** Encode `MacroEvent{driver, source∈{supply,demand,uncertainty}, phase∈{threat,act,escalation}, direction}`. "Oil up" is not one causal object; supply vs uncertainty vs demand have different equity signs.
- **Sector priors from the literature as versioned seed data (GVAR/MSCI).** Hard-code, with provenance, `exposed_to(oil)` weights: energy/materials/industrials high; healthcare/utilities ≈0. No LLM needed to seed these.
- **Structured supply-chain edges from filings (Tabachová/Rios), not only LLM extraction.** For NSE, seed `supplies`/`depends_on` from MCA/annual-report disclosures; LLMs miss private relationships.
- **Emit top contributing paths for audit** (`Iran war threat → Hormuz shipping → crude transport → jet fuel → IndiGo`). For debugging/review, never sizing.

**Layer 2 (LLM authors edges + classifies MacroEvent):**

- **BERTopic clustering before classification (FinGPT).** Feed the classifier a centroid article + cluster size/span; cluster size → magnitude class. Cuts cost and hallucination; provides an event-magnitude proxy.
- **Six-element event schema (JKSU-CIS)** as the constrained, verifiable MacroEvent output.
- **Offline authoring vs online inference on different timescales (TRACE).** Make the boundary a hard code separation, not just conceptual. LLM = extractor/relation-selector/validator; deterministic code converts everything to categorical labels.
- **Mandatory text provenance per edge (TRACE EXTRACTED_FROM).** No citeable source ⇒ edge blocked from traversal.

## 3. What to AVOID — documented failure modes

- **Look-ahead in KG construction [DIRECT THREAT].** Any edge derived from post-date news leaks. Enforce `valid_from ≤ prediction_date`; unit-test against planted future edges. This is the #1 way this project silently manufactures fake alpha.
- **Spurious/inflated causal edges [DIRECT].** Curátola: OLS commodity→equity effects are 2–10× too large; oil instrument weak. Never seed weights from price co-movement.
- **Hub over-propagation [DIRECT].** Without anti-hub caps, one shock hits every name.
- **Stale edges [DIRECT].** Supply chains and sanctions flows change; Rios's graph is a frozen 2020 snapshot. Require `last_confirmed`; auto-decay ~30%/yr for unconfirmed edges; authoring cycle must *deprecate*, not only add.
- **Second-order cascade drowning signal [DIRECT].** Rios: 2-hop helps only when community-selected; naive 2-hop degrades. Hard depth cap + min-confidence path threshold.
- **Accuracy ≠ net-of-cost alpha.** Every corpus number is accuracy/ranking/no-cost return. TA-HKGE degrades under drift.
- **LLM edge hallucination.** No corpus paper demonstrates reliable autonomous LLM causal-edge authoring; TRACE uses LLMs only to *filter/validate*, not create edges. Expect meaningful false-positive causal links.

## 4. Where the evidence CHALLENGES our design decisions

**(a) Fixed traversal vs learned GNN — partially challenged, defensible.** TRACE's *rule-mined* traversal beats a T-GNN baseline (55.1 vs 52.8), and multi-hop/temporal ablations carry the lift — but "rule-mined" ≠ "hand-authored." Rios/HKGE show *learned* aggregators beat manual weights and adapt to regime change; your static graph cannot. **Reconciliation of drafts: don't hand-pick weights — *fit* them offline from historical shock→return responses (mini-GVAR per driver class), keep inference deterministic.** This preserves the invariant (no LLM/GNN numeric emission in hot path) while closing most of the performance gap. Plan a GNN comparison for v2.

**(b) LLM-authored edges — genuinely challenged.** No corpus evidence that LLMs author reliable causal financial edges; TRACE deliberately restricts LLMs to selection/validation. Your human-approval gate is therefore *required*, not optional. Add: every edge cites a source doc; a second corroborating source (SEC/MCA filing, analyst report) required before confidence >0.5.

**(c) EOD floor vs decay — seriously challenged but survivable.** GPR predictability peaks at t-1 and is ~gone by t-4; commodity price jumps absorb within-session; MSCI says medium-term impact "often limited." **But GVAR shows multi-quarter equity effects, and Rios/SC anomalies persist 1–3 days.** Conclusion (converged across drafts): **EOD cannot capture the initial move; it can plausibly capture 30–60% of the cross-sectional differential over the following 1–3 days.** Frame the KG as a *defensive-tilt / beneficiary-ranking* tool, **not** an event-reaction engine. Do not market it as "reacts to war news."

**(d) Net-of-cost alpha — unproven.** Nobody in the corpus demonstrates it for a causal KG. TRACE's return is no-cost/bull-year; Rios's sim is toy; GPR utility gains are index-level. Closest real evidence is the classic lagged-supplier-return anomaly (Cohen-Frazzini, Menzly-Ozbas) — likely partially arbitraged. **The KG's v1 justification rests on risk/exposure management, not alpha.**

## 5. Ranked recommendations for the human

1. **Reframe the KG as a risk/exposure engine first, alpha engine second.** Evidence supports "know your macro exposure and tilt defensively / surface beneficiaries" (JFS contagion, GVAR, MSCI); it does *not* support "beat the market by propagating news." *Riskiest unknown:* whether beneficiary-surfacing beats a plain sector-tilt baseline net of cost.
2. **Enforce anti-hub penalty + hard depth cap (≤3) + min-confidence path threshold before the first live trade.** Prevents the catastrophic "everything exposed to US-Iran war." *Riskiest unknown:* the degree threshold separating a legitimate junction (Strait of Hormuz) from a spurious hub ("global economy") — must be calibrated on known events. (Note: your verbatim 3-hop chain barely survives a ≤3 cap; consider merging MacroDriver+Commodity to keep it at 2.)
3. **Fit edge weights/decay offline from structural estimates; never from price correlation.** Directly answers Curátola's endogeneity warning and the fixed-vs-learned challenge while keeping inference deterministic. *Riskiest unknown:* firm-level structural estimates don't exist in the literature — LLM+provenance must compensate, and fitted coefficients may not be regime-stable (2019/2020/2022).
4. **Enforce as-of `valid_from`/`last_confirmed` on every edge, unit-tested against planted future edges; gate LLM edges behind provenance + human approval.** Kills look-ahead (the top fake-alpha source) and the edge-hallucination risk. *Riskiest unknown:* dating retrospective-document edges (use source publication date, not the relationship's stated start), and whether the news classifier itself leaks via future-trained embeddings.
5. **Define v1 success as cross-sectional rank correlation on shock events, plus historical event replays (2020 COVID, 2022 Russia-Ukraine), all net-of-cost.** Accuracy is the wrong metric; you need "did we rank who-gets-hit correctly." *Riskiest unknown:* too few live macro shocks in the paper window for significance — hence the mandatory historical-replay validation track. Add a measured LLM edge-precision bar (e.g. ≥0.85 on ~200 expert-labeled claims) before edges enter Layer-1.

<!-- MOA-SYNTHESIS SELF-AUDIT: sections 1-5 present; 3 reference drafts received -->