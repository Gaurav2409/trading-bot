# Equity Trading Signal Catalog — All-Horizon (Swing + Long-Term), Intraday Excluded

> Research stream 3 of 3 (Sonnet web-research gather → compiled section-by-section). 2026-07-18.
> Raw sources: `/tmp/trading-os-research/signal-catalog/` (151 files)
> NOTE: pending MoA adversarial verification pass.

## Scope & granularity floor

Per locked decision **D9**: comprehensive **all-horizon** catalog (swing/positional + long-term investing) but **intraday STRICTLY EXCLUDED**. Daily-bar / EOD is the granularity floor — nothing sub-daily, tick, or order-flow. Several oscillators (RSI, MACD, Bollinger, OBV, ADX, Keltner) *can* be computed intraday but are retained here **only in their daily-bar form**; their intraday variants are out of scope and must not be wired into the analyst layer.

**Entry format per signal:**
`Signal | horizon (swing/long/both) | what it measures | computation | evidence/effect | source`

**Confidence tiering** (drives analyst-layer weighting; multi-source = higher):
- **Tier 1 (robust, multi-source, effect-sized):** 12-1 momentum, trend-following/MA-timing, value (B/M, earnings yield), QMJ quality, gross profitability, Piotroski F-score, yield-curve/credit-spread regime, multi-factor composite.
- **Tier 2 (evidenced, single strong source or decayed):** short-term reversal, accrual anomaly, short interest, HMM regime, PMI factor-timing, RSI/Bollinger reversion, OBV.
- **Tier 3 (descriptive / gated / speculative here):** most alt-data (satellite, credit-card, web-scrape), Google-search trends, options skew, news-NLP sentiment.

---

## Family 1 — Momentum & Trend

| Signal | Horizon | Measures | Computation | Evidence | Source |
|---|---|---|---|---|---|
| **12-1 Momentum** (cross-sectional) | long | Past winners keep winning | Rank on return over past 12mo skipping most recent month (J=12,K=1); long top decile, short bottom; monthly rebal | ~8.3% indicative; long side > short (Griffin); worst DD >80% in 2009 | quantpedia |
| **Time-Series (absolute) Momentum** | swing/long | Own asset if own past return positive | Long if trailing (12mo) return >0, else flat/short; monthly | 20.7% / 15.7% vol (multi-asset) | quantpedia |
| **Trend-Following in Stocks** | swing/long | Ride persistent price trend | MA / breakout rules, monthly rebal | Positive significant alpha all rules; Sharpe > buy&hold | quantpedia, alphaarchitect |
| **10-month SMA timing** (Faber) | swing/long | In-market when price > 10mo SMA | Long if monthly close > 10mo SMA else cash | Outperforms 12mo MOM in regime tests; common benchmark | alphaarchitect |
| **MA Crossover** | swing | Short MA crosses long MA | 50/200-day (golden/death cross); SMA/EMA variants | Trend alpha; lagging in chop | alphaarchitect, zerodha-varsity |
| **MACD** | swing | Trend + momentum via EMA spread | 12-EMA − 26-EMA; signal=9-EMA; hist=MACD−signal; crossovers/divergence | No fixed OB level; pair with ADX to cut false signals | investopedia, tradingview |
| **ADX** | swing | Trend STRENGTH (not direction) | ADX + ±DI (Wilder); >25 trending, <20 non-trend | Confirmation filter for MACD/other | investopedia, tradingview |
| **52-week high proximity** | long | Nearness to 52wk high → continuation | price / 52wk-high ratio | Behavioral anchoring (momentum family) | quantpedia |
| **Optimal semi-Markov trend rule** | long | Theoretically-optimal MA rule | Resembles MACD (3 EMAs) under duration-dependent regime model | Beats 10mo SMA/12mo MOM but diffs not stat-significant | SSRN (Zakamulin-Giner) |

**Horizon guidance:** formation 3–12mo, hold 1–12mo; **monthly rebalancing is the floor**.
**Caveats:** momentum *crashes* (−80% in 2009), risk highly time-varying — vol-scaling ("risk-managed momentum") nearly doubles Sharpe (Barroso/Santa-Clara); crowding/decay; capacity limit (~$5B, Korajczyk).

---

## Family 2 — Value & Fundamental

| Signal | Horizon | Measures | Computation | Evidence | Source |
|---|---|---|---|---|---|
| **Value effect** (B/M, P/E, P/CF) | long | Cheap stocks outperform | Sort on book-to-market / earnings yield; long cheap decile | Robust global anomaly; tax-efficient w/ momentum | quantpedia, robeco |
| **Earnings / FCF Yield** | long | Inverse valuation multiple | E/P, FCF/EV | Value proxy; also loads on quality | alphaarchitect |
| **EV/EBITDA** | long | Enterprise value vs cash earnings | EV / EBITDA; lower cheaper (<10 rule-of-thumb) | Capital-structure-neutral value | investopedia |
| **DCF / Reverse DCF** | long | Intrinsic value vs price | PV of projected FCF at WACC; reverse DCF backs out implied growth | Valuation framework (not backtested signal) | investopedia, wallstreetprep |
| **Piotroski F-Score** | long | Fundamental strength of value stocks | 0–9 from 9 binary criteria (ROA, CFO, ΔROA, accruals, Δleverage, Δcurrent-ratio, dilution, Δmargin, Δturnover) | High-F portfolios outperform *within cheap B/M universe* | investopedia, escholarship |
| **Accrual Anomaly** | long | High accruals → low future returns | Sort on total accruals; long low, short high | Decayed mid-2000s, rebounded post-2008; pure alpha not risk | quantpedia, columbia |
| **Earnings Quality Factor** | long | Low-accrual / high-CF earnings | Composite percentile (accruals, leverage, ROE, CF) 0–400; long top 30% annual | Overlaps accrual anomaly | quantpedia |
| **Beneish M-Score** | long | Earnings-manipulation detector | 8 vars (DSRI,GMI,AQI,SGI,DEPI,SGAI,LVGI,TATA) | Short/risk-screen (caught Enron) | investopedia |
| **Altman Z-Score** | long | Bankruptcy/distress risk | Weighted profitability/leverage/liquidity ratios; <1.8 distress, >3 safe | Credit-risk screen | investopedia |
| **Earnings Announcement Premium** | swing | Positive drift around earnings dates | Hold over expected announcement window | quantpedia entry thin | quantpedia |

**Horizon guidance:** annual/quarterly rebal (fundamentals update slowly) → long-horizon.
**Caveats:** value underperforms for years at a time; accrual anomaly decayed; DCF hypersensitive to WACC/growth.

---

## Family 3 — Quality & Profitability

| Signal | Horizon | Measures | Computation | Evidence | Source |
|---|---|---|---|---|---|
| **QMJ (Quality Minus Junk, AQR)** | long | Profitable/stable/growing/high-payout firms | Composite of profitability, growth, safety, payout | Premium 4.7%/yr, SD 9.6%, Sharpe 0.5 (1958–2018); shines in down markets | aqr, alphaarchitect |
| **Gross Profitability** (Novy-Marx) | long | Gross profits / assets | GP / total assets; long high | Robust; captured by FF5 RMW | robeco |
| **FF5 Profitability (RMW)** | long | Robust-minus-weak op profitability | High op-profitability outperforms | FF5 (2015) factor | robeco |
| **FF5 Investment (CMA)** | long | Conservative-minus-aggressive asset growth | Low asset-growth firms outperform | FF5 factor; HML redundant under FF5 | robeco |
| **ROE / ROIC** | long | Capital efficiency | NI/equity; NOPAT/invested-capital | Core quality inputs | investopedia |
| **Low-Volatility / Low-Beta** | long | Low-vol stocks → higher risk-adj returns | Sort on trailing vol/beta; long low | Mispricing vs risk debate | aqr, lseg, stoxx |

**Horizon guidance:** long.
**Caveats:** **NO consistent quality definition across providers** (Hsu — "marketing optics"); only *profitability, accounting-quality (low accruals), payout, investment* show reliable premia — capital-structure/earnings-stability/growth do not; some "quality" just proxies low-vol; quality stocks are large → few limits to arbitrage → premia arbitrageable.

---

## Family 4 — Mean-Reversion & Oversold

| Signal | Horizon | Measures | Computation | Evidence | Source |
|---|---|---|---|---|---|
| **RSI** | swing | Momentum oscillator / OB-OS | 100 − 100/(1+RS), RS=avg gain/avg loss, 14-period (Wilder); >70 OB, <30 OS | Reversion signal; thresholds shift with trend (Brown); also trend tool | investopedia, tradingview |
| **Bollinger Bands** | swing | Volatility-relative price extremes | 20-SMA ± 2σ; touch upper=OB, lower=OS; squeeze precedes breakout | Reversion + breakout dual use | investopedia, tradingsim |
| **Keltner Channels** | swing | ATR-based volatility channel | EMA ± mult × ATR (vs Bollinger σ) | Smoother than Bollinger | chartmill, puprime |
| **Short-Term Reversal** | swing | Last week's losers bounce | Long 10 worst of prior week, short 10 best of prior month; 100 largest caps; weekly | Works ONLY in large caps (tx costs); liquidity-providing; risky in crises | quantpedia |
| **Put-Call ratio (contrarian)** | swing | Sentiment extreme → reversal | Put vol / call vol; high = excessive bearishness (bullish contrarian) | Contrarian at extremes | investopedia, aaii |

**Horizon guidance:** days-to-weeks (swing OK; sub-daily excluded).
**Caveats:** short-term reversal killed by tx costs outside large caps; RSI/Bollinger thresholds regime-dependent — false signals in strong trends.

---

## Family 5 — Volume & Liquidity

| Signal | Horizon | Measures | Computation | Evidence | Source |
|---|---|---|---|---|---|
| **OBV (On-Balance Volume)** | swing | Cumulative volume-flow / smart money | Running total: +vol if close>prev, −vol if close<prev; watch price/OBV divergence | Volume precedes price; accumulation signal | investopedia, truedata |
| **Volume confirmation** | swing | Volume validates price trend | Rising price + rising volume = strong | Supportive filter, not standalone | investopedia, zerodha-varsity |
| **Short Interest (contrarian long)** | long | Very-low short interest → positive returns | Sort by short-interest ratio; hold lowest percentile, equal-wtd, monthly | Low-SI heavily-traded stocks earn significant + abnormal returns (Boehmer/Huszar/Jordan) | quantpedia, ihsmarkit |
| **Short Interest Ratio / Days-to-Cover** | swing/long | Short-selling pressure & squeeze risk | Short interest / avg daily volume | High = bearish or squeeze fuel | investopedia |
| **Liquidity factor** | long | Illiquid stocks earn premium | Amihud illiquidity / turnover | Classic factor | quantpedia |
| **Promoter Holding / Pledged Shares** (India) | long | Insider ownership & pledge risk | % promoter holding; % pledged; rising pledge = red flag | Governance/stability screen | truedata, vivekam |

**Horizon guidance:** swing–long.
**Caveats:** **OBV misleads in flash crashes** — cumulative volume distorted by panic spikes → false trend confirmation (fyers); high-SI effect transient/debatable economic significance.

---

## Family 6 — Sentiment & News

| Signal | Horizon | Measures | Computation | Evidence | Source |
|---|---|---|---|---|---|
| **News NLP / FinBERT** | swing | Sentiment polarity of financial text | BERT fine-tuned on financial headlines → +/−/neutral | Headline sentiment → direction | researchgate, sciencedirect |
| **Analyst EPS Revisions** | swing/long | Upward revisions predict returns | Sort on revision ratio / direction of consensus EPS changes | Positive drift on upgrades | academic (alphaarchitect source dead) |
| **Put-Call Ratio (sentiment gauge)** | swing | Aggregate bullish/bearish option bets | Total puts / calls volume | Broad market-sentiment measure | investopedia, aaii |
| **Options Skew / Implied Volatility** | swing | Option-implied fear/direction | IV levels, put-vs-call skew | Forward-looking sentiment | investopedia |
| **Google Search Trends (SVI)** | swing | Retail attention | Abnormal search-volume-index changes | quantpedia strategy GATED (named only) | quantpedia |
| **FII/DII flows** (India) | swing | Institutional net buy/sell flows | Daily net purchase by FII/DII (EOD) | Directional flow sentiment | nseindia, moneycontrol |

**Horizon guidance:** days-to-weeks.
**Caveats:** sentiment signals noisy/short-lived; Google-trends & analyst-revision primary sources gated/dead in this corpus.

---

## Family 7 — Alt-Data

| Signal | Horizon | Measures | Computation | Evidence | Source |
|---|---|---|---|---|---|
| **Insider Trading (legal Form 4) premium** | long | Corporate insider net buying predicts returns | Aggregate open-market purchases (SEC Form 4); long after cluster buying | quantpedia page GATED (named); insiders = officers/directors/10% holders | quantpedia, investopedia |
| **Satellite imagery** | long | Physical activity (parking, oil tanks, crops) | Count/measure from geospatial imagery | Hedge-fund alpha source | cfainstitute, passby |
| **Credit-card / transaction data** | long | Consumer spend nowcast of revenue | Aggregated card panels (e.g. Second Measure) | Revenue prediction ahead of earnings | secondmeasure, cfainstitute |
| **Web-scraping (pricing/jobs/reviews)** | long | Scraped web signals for fundamentals | Automated extraction of prices/listings/sentiment | Research input | kadoa, webscrapingapi |
| **PMI / macro-nowcasting** | swing/long | Leading business-conditions survey | ISM/Markit PMI; >50 expansion, <50 contraction | See Family 8 | investopedia, spglobal |

**Horizon guidance:** mostly long (data latency, monthly panels).
**Caveats:** expensive, short backtests, crowding; legality/coverage concerns; most alt-data sources here descriptive (no effect sizes). **Deprioritize for v1** — high cost, thin evidence.

---

## Family 8 — Macro & Regime

| Signal | Horizon | Measures | Computation | Evidence | Source |
|---|---|---|---|---|---|
| **Credit Spreads (equity timing)** | swing/long | Corp−Treasury yield spread signals economy | (corp yield − Treasury), bps; widening bearish, narrowing bullish | quantpedia strategy GATED (named); "best broad-economy indicator" | quantpedia, investopedia |
| **Yield Curve / Inversion** | long | 10y−3m (or 10y−2y) predicts recession/bear | Negative spread = inversion = recession lead | Robust recession lead; YC+trend combo boosted Sharpe 0.52→0.55, cut DD | quantpedia, federalreserve |
| **HMM Regime Detection** | swing/long | Latent bull/bear/vol states | Fit Gaussian HMM (2–3 states) on returns; disallow trades in high-vol regime | Improves Sharpe by filtering high-vol trades (QSTrader) | quantstart, arxiv |
| **VIX / Volatility regime** | swing | Market fear gauge | Implied-vol index; high = risk-off | Regime filter | investopedia |
| **PMI factor-timing** | swing/long | PMI conditions factor returns | Relate PMI level/change to Value/Momentum for allocation | alphaarchitect investigates PMI→factor relationship | alphaarchitect |
| **Money supply / Global liquidity** | long | Liquidity drives equity levels | M2 / global-liquidity growth | Positive relation to market | researchgate, nism |
| **Macro composite (Trend+YC+Macro)** | long | Multi-signal market timing | Long MKT if Trend&YC positive OR INDPROD/RSALES/DIVIDEND jointly positive | **TrendYCMacro: 7.05% ann, −25% max DD (⅓ of MKT), Sharpe 0.60** — doubles MKT Sharpe, cuts DD ⅔ | quantpedia |
| **International regime allocation** | long | Tactical allocation across macro regimes | Momentum-window & USD-SMA rules (EM vs EAFE, 1970–2025) | Sharpe/Calmar improvements | quantpedia |
| **USD Index (DXY)** | swing/long | Dollar strength macro factor | Trade-weighted USD index | Risk-on/off & EM signal | investopedia |

**Horizon guidance:** swing–long (monthly signals).
**Caveats:** economists' predictions have low predictive value (alphaarchitect); yield-curve *alone* didn't help — only *jointly with trend*; "this time is different" inversion skepticism.

---

## Family 9 — Cross-Sectional Ranking & Combination

| Signal | Horizon | Measures | Computation | Evidence | Source |
|---|---|---|---|---|---|
| **Multi-factor composite** (Value+Quality+Momentum) | long | Combine complementary factors | Percentile-rank per factor, sum ranks; long top / short bottom | **Integrated (single combined score) > component** — avoids one sleeve buying what another sells; more tax/tx efficient | alphaarchitect, quantpedia |
| **Composite quality score** | long | Sum of standardized quality metrics | Percentile each (accruals/leverage/ROE/CF) 0–400; long top 30% annual | See Family 2/3 | quantpedia |
| **MV-optimized momentum** | long | Weight momentum by decile structure | MV-optimize using expected-return vector reflecting only decile-1/10 outperformance | Sharpe 52.8% vs 29.3% equal-weight | quantpedia |
| **Value+Momentum combination** | long | Negatively-correlated factor pair | 50/50 or integrated ranking | Classic diversification (AQR "Value & Momentum Everywhere") | quantpedia |
| **Factor timing via macro** | swing/long | Condition factor weights on regime | Tilt exposure by PMI/HMM/YC state | Evidence mixed | alphaarchitect |
| **Signal ensembling w/ regime filter** | swing/long | Overlay HMM/vol filter on base signals | Disallow/scale positions in high-vol regime | Improves Sharpe (quantstart) | quantstart |

**Horizon guidance:** long (annual/monthly rebal).
**Caveats:** **integrated beats component**; factor timing hard & mixed evidence; crowding/decay; quality "factors" have low mutual correlation (not one hidden factor).

---

## Design implications for the analyst layer

1. **Signal families map to analyst roles.** Fundamental analyst → Families 2, 3. Technical analyst → Families 1, 4, 5. Macro analyst → Family 8. Sentiment analyst → Family 6. Alt-data analyst → Family 7 (deprioritized v1). Signal aggregator → Family 9.
2. **Confidence tier flows into weighting.** Analysts emit per-signal readings; the aggregator/MoA weights Tier-1 signals heavily, treats Tier-3 as tie-breakers only.
3. **Integrated composite > component sleeves** — the aggregator produces ONE combined cross-sectional score, not independent per-factor votes. This is a load-bearing design choice (family 9 evidence).
4. **Regime filter is a global overlay, not a signal.** HMM / YC / vol state gates whether to trade at all (Family 8), applied deterministically *after* synthesis — consistent with D4 (deterministic line after synthesis).
5. **Rebalancing cadence = the swing/long floor.** Monthly is the natural rebalance boundary for factor signals; the scheduler must not tick faster than daily bars (D9 granularity floor).

---

## Source-quality / exclusion notes (for MoA verification)

- **DEAD (404, no content):** 5–6 short alphaarchitect blog posts (VQM, "TA debunked", MA-strategies, analyst-revisions, Piotroski-update, macro-timing). Signals corroborated elsewhere, but the specific "TA debunked" caveat text is **not** retrievable here.
- **GATED (landing/boilerplate only):** quantpedia value-effect, quality-factor, credit-spreads, google-search, insider-trading, MA-timing, RSI-as-trend, trend-following, yield-curve. Names/keywords captured; formulas/effect-sizes NOT in-file.
- **FULL CONTENT quantpedia:** momentum-factor, short-interest, short-term-reversal, accrual, earnings-quality, avoid-bear-markets-part-3 (**TrendYCMacro numbers**), international-regimes.
- **AQR pages** (QMJ, low-vol) thin/gated — QMJ effect size recovered via alphaarchitect Swedroe summary.
- **INTRADAY FLAGS:** none of the retained signals are intraday-only. OBV, RSI, Bollinger, MACD, ADX, Keltner *can* compute intraday but retained here **daily-bar only**. FII/DII and put-call are daily/EOD. No tick/order-flow/1-min signals present.
- **Unread PDFs (likely corroborating):** lseg/stoxx low-vol whitepapers, federalreserve/bis yield-curve, escholarship/anderson F-score, columbia earnings-quality, sciencedirect factor papers, zerodha-varsity (MA & equity-research chapters — India-context tutorials).

## Key gaps / verification flags for MoA pass

1. **TrendYCMacro effect sizes** (7.05% / −25% DD / 0.60 Sharpe) — single quantpedia source; verify plausibility & OOS.
2. **QMJ 4.7%/yr premium** — recovered via secondary (Swedroe) summary, not AQR primary; verify.
3. **Short-term reversal "large-cap only"** claim — verify tx-cost sensitivity.
4. **OBV flash-crash failure** — single source (fyers); is it a general caveat or India-specific anecdote?
5. **"Integrated > component" multifactor** claim — load-bearing for the aggregator design; verify strength of evidence.
6. **Gated signals** (credit-spreads, insider-trading, google-search) — names only; MoA should confirm these are real, evidenced anomalies before we build analysts around them.
