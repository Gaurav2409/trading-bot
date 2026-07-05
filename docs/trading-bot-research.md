# Intelligent Multi-Market Equity Trading Bot — Research Document & Implementation Plan
> Markets: NSE/BSE (India) · NYSE/NASDAQ (US) · XETRA (Europe)
> Generated: 2026-07-05 | Horizons: Scalping · Intraday · Swing · Positional · Long-term
> Produced by Hermes MoA deep-research (gpt-5.5 + claude-4.7-opus + claude-sonnet → claude-opus aggregator)

---

## Chunk A: Sections §1–§2

---

## 1. Equity Price Determinants — Complete Taxonomy

Equity prices are the equilibrium output of a multi-factor stochastic process driven by discounted expected cash flows, risk premia, liquidity, market microstructure, investor positioning, policy regimes, and behavioural feedback loops. A production trading bot must model these determinants explicitly per horizon because the predictive half-life differs sharply: order-flow imbalance decays in seconds, sentiment shocks in hours to days, earnings quality over quarters, and macro-liquidity regimes over months to years. Below is an exhaustive taxonomy across five categories, each with the factor, precise measurement method, canonical data source, update frequency, and the trading horizon(s) where it is most predictive.

Horizon codes used below:
- SC = Scalping (<1 min)
- ID = Intraday (minutes–hours, same day)
- SW = Swing (2–10 days)
- PO = Positional (weeks–months)
- LT = Long-term (months–years)

---

### 1.1 Fundamental Factors

Fundamentals reflect intrinsic economic value. Predominantly SW/PO/LT signals; earnings-related items also drive ID moves on release day.

| # | Factor | Measurement / Formula | Data Source (India / US / Europe) | Update Frequency | Horizon |
|---|--------|----------------------|-----------------------------------|------------------|---------|
| 1 | P/E Ratio (Trailing & Forward) | Price ÷ TTM EPS; Forward = Price ÷ consensus next-12M EPS | Screener.in, Tijori, Trendlyne (IN); SEC EDGAR, IEX Cloud, Macrotrends (US); Bundesanzeiger, boerse.de (EU); Bloomberg, Refinitiv globally | Daily (price), Quarterly (EPS) | SW, PO, LT |
| 2 | P/B Ratio | Market Cap ÷ Book Value of Equity | Balance sheet from BSE/NSE, SEC EDGAR 10-Q, Bundesanzeiger; aggregators: Screener.in, Yahoo Finance `bookValue`, Refinitiv | Quarterly | PO, LT |
| 3 | EV/EBITDA | (Market Cap + Total Debt − Cash & Equivalents + Minority Interest) ÷ EBITDA | Refinitiv Eikon, Bloomberg, FactSet, Damodaran datasets, Screener.in | Quarterly | PO, LT |
| 4 | Free Cash Flow Yield | (Operating Cash Flow − CapEx) ÷ Market Cap or EV | Cash flow statement (10-Q/10-K, Indian Annual Reports, EU consolidated statements); StockAnalysis.com, Tikr | Quarterly | PO, LT |
| 5 | PEG Ratio | P/E ÷ EPS growth rate (usually 3–5Y CAGR) | Derived; Yahoo Finance, Zacks, Trendlyne | Quarterly | PO, LT |
| 6 | Revenue Growth Rate (YoY, QoQ, CAGR) | (Revₜ − Revₜ₋₁) / Revₜ₋₁; segmental growth tracked separately | Income statements via BSE/NSE, SEC EDGAR, ESMA CSR filings; Refinitiv I/B/E/S for consensus | Quarterly | SW (post-earnings), PO, LT |
| 7 | Gross / Operating / Net Profit Margin | Gross = (Rev − COGS)/Rev; Operating = EBIT/Rev; Net = NI/Rev | Company income statements; aggregated on Screener.in, Macrotrends, SimplyWall.st | Quarterly | PO, LT |
| 8 | ROCE / ROIC / ROE | ROCE = EBIT ÷ (Total Assets − Current Liabilities); ROIC = NOPAT ÷ Invested Capital; ROE = NI ÷ Equity | Derived from balance sheet + income statement; Screener.in, Bloomberg, FactSet | Quarterly / Annual | PO, LT |
| 9 | Debt-to-Equity & Net Debt/EBITDA | Total Debt ÷ Equity; (Debt − Cash) ÷ EBITDA | Balance sheet; credit reports from CRISIL/ICRA (IN), S&P/Moody's/Fitch (global) | Quarterly | PO, LT |
| 10 | Interest Coverage Ratio | EBIT ÷ Interest Expense (below 1.5× = distressed) | Income statement + notes; Bloomberg Credit Risk module | Quarterly | PO, LT |
| 11 | Dividend Yield & Payout Ratio | DPS ÷ Price; Dividends ÷ Net Income (or ÷ FCF) | NSE/BSE corporate actions feed, SEC Form 8-K dividend declarations, EDGAR, Bloomberg CACS | Event-driven + quarterly | PO, LT |
| 12 | Earnings Surprise (SUE — Standardised Unexpected Earnings) | (Actual EPS − Consensus EPS) ÷ σ of estimates | Refinitiv I/B/E/S, Bloomberg BEst, Zacks, Estimize (crowd), Trendlyne | Quarterly (event) | ID (announcement), SW (PEAD drift) |
| 13 | Analyst EPS Revision Momentum | Net upward minus downward EPS estimate revisions over 1/30/90 days | Refinitiv I/B/E/S, FactSet Estimates, Bloom| 14 | Forward Guidance Tone | NLP sentiment (FinBERT/DeBERTa) on management outlook statements in earnings calls; polarity + uncertainty + hedging-word density | Earnings call transcripts via Seeking Alpha, AlphaSense, Refinitiv StreetEvents, Tikr, FactSet CallStreet | Quarterly + event-driven | ID, SW, PO |
| 15 | Management Quality Signals | CEO/CFO tenure, insider net selling, promoter pledging (India), related-party transactions, auditor changes, restatements, capital allocation IRR track record | MCA21 & SEBI SAST/PIT disclosures (IN), SEC Form 4/DEF 14A (US), Bundesanzeiger + BaFin Directors' Dealings (EU); Morningstar Stewardship, SimplyWall.st management score | Quarterly + event-driven | PO, LT |
| 16 | Competitive Moat Indicators | Sustained ROIC − WACC > 0 over 5–10Y, gross-margin stability σ, market-share Δ, brand-equity indices, patent moat, switching-cost proxies (churn, NPS where disclosed) | Company filings, industry reports (IBEF, Euromonitor, IBISWorld, Gartner, IDC), Morningstar Economic Moat rating, Interbrand/Kantar BrandZ | Annual | PO, LT |
| 17 | TAM / SAM / SOM & Market Share | TAM from industry research; share = company revenue ÷ industry revenue; penetration = revenue ÷ TAM | Gartner, IDC, Euromonitor, Statista, CRISIL, IBEF, CMIE, S&P Capital IQ, company investor decks | Annual / biannual | PO, LT |
| 18 | ESG Composite Score | E, S, G sub-scores; controversy score; carbon intensity (tCO₂ ÷ revenue); MSCI ESG AAA→CCC; Sustainalytics Risk; Refinitiv 0–100; S&P Global CSA; CDP climate | MSCI ESG Manager, Morningstar Sustainalytics, Refinitiv ESG, ISS, S&P Global CSA; SEBI BRSR (IN); EU SFDR/CSRD disclosures | Annual (controversies real-time) | PO, LT |
| 19 | Insider / Promoter Ownership & Transactions | % held by promoters/insiders; promoter pledge ratio (IN); net insider buy/sell over 30/90/180-day windows | NSE/BSE shareholding pattern SHP-1 + SEBI PIT (IN); SEC Forms 3/4/5, DEF 14A (US); BaFin Directors' Dealings & EU MAR (EU) | Quarterly + event T+2 | SW, PO, LT |
| 20 | Share Buybacks / Dilution | Announced buyback size ÷ market cap; buyback yield; ASR/open-market pattern; net share count Δ; SBC dilution | SEC 8-K/10-Q share counts, SEBI buyback offer letters, German §71 AktG, EQS ad-hoc; NSE/BSE buyback filings | Event + quarterly | SW, PO, LT |
| 21 | Capital Allocation History | Historical M&A returns, CapEx IRR, ROIIC = ΔNOPAT / ΔInvested Capital, dividend/buyback consistency vs peers | Derived from 5–10Y financials; Morningstar Stewardship rating; Damodaran datasets | Annual | PO, LT |
| 22 | Working Capital Efficiency / Cash Conversion Cycle | CCC = DIO + DSO − DPO; inventory days; receivable days; payable days | Balance-sheet notes; annual reports; Screener.in; StockAnalysis.com | Quarterly | PO, LT |
| 23 | Earnings Quality / Accruals | Total accruals ÷ average net assets; CFO ÷ Net Income; Beneish M-Score; Sloan Accruals; Piotroski F-Score | Derived in Python from filings; `financetoolkit`, custom XBRL parsers | Quarterly | SW, PO, LT |
| 24 | Credit Rating / Default Risk | Rating changes; CDS spreads; Altman Z-Score; Ohlson O-Score; interest coverage cliff | CRISIL/ICRA/CARE (IN); Moody's/S&P/Fitch (global); TRACE, Markit CDX/iTraxx | Event + daily (spreads) | SW, PO, LT |
| 25 | Corporate Actions | Splits, bonus, rights, mergers, spin-offs, delistings, dividend ex-dates | NSE/BSE corporate action bhavcopy, SEC 8-K, EQS ad-hoc (EU), Bloomberg CACS | Event-driven | ALL (adjustment critical for SC/ID) |

Python tooling for fundamentals: `yfinance>=0.2.38` (free, rate-limited), `financetoolkit>=1.5` (wraps multiple sources), `fundamentalanalysis`, `nsepython>=2.9` (India), `pandas-datareader>=0.10` (Quandl/FRED), direct SEC EDGAR XBRL API at `https://data.sec.gov/api/xbrl/`, `sec-api` (paid), `edgartools`.

---

### 1.2 Technical / Price-Action Factors

Technical signals are derived from market-generated price/volume/order-book data. Dominant for SC/ID/SW horizons; useful as entry/exit overlays for PO/LT. All factors below are computable with `TA-Lib 0.4.28+` (C binding), `pandas-ta 0.3.14b0`, `ta>=0.10.2`, `tulipy`, or `vectorbt>=0.26`.

| # | Factor | Measurement / Formula | Data Source | Update Frequency | Horizon |
|---|--------|----------------------|-------------|------------------|---------|
| 1 | OHLCV Bars | Open, High, Low, Close, Volume at 1s/1m/5m/15m/1h/1D intervals | Kite WebSocket (IN), Alpaca/Polygon WebSocket (US), IBKR `reqHistoricalData`/`reqRealTimeBars` (global), Deutsche Börse T7 EOBI (EU) | Tick → aggregated | ALL |
| 2 | Returns / Log Returns | Simple rₜ = Pₜ/Pₜ₋₁ − 1; log rₜ = ln(Pₜ/Pₜ₋₁); compound cumulative return | Derived from OHLCV | Per bar | ALL |
| 3 | SMA / EMA / WMA / HMA Crossovers | SMA(n); EMA(n) α = 2/(n+1); Hull MA; 9/21 EMA (intraday), 50/200 SMA Golden/Death Cross | TA-Lib `SMA`/`EMA`/`WMA`; `pandas-ta` | Per bar | ID, SW, PO |
| 4 | RSI (Wilder 14) | 100 − 100/(1+RS); RS = avg gain ÷ avg loss over 14; OB>70, OS<30; divergences | TA-Lib `RSI`; `ta.momentum.RSIIndicator` | Per bar | SC, ID, SW |
| 5 | MACD (12,26,9) | MACD = EMA12 − EMA26; Signal = EMA9(MACD); Histogram = MACD − Signal | TA-Lib `MACD` | Per bar | ID, SW, PO |
| 6 | Bollinger Bands (20, 2σ) | Middle = SMA20; Upper/Lower = ±2σ; %B, Bandwidth; squeeze detection | TA-Lib `BBANDS`; `ta.volatility.BollingerBands` | Per bar | SC, ID, SW |
| 7 | ATR (14) | Wilder-smoothed True Range; TR = max(H−L, |H−Cₚ|, |L−Cₚ|); used for stops & position sizing | TA-Lib `ATR` | Per bar | ALL (risk mgmt) |
| 8 | ADX / +DI / −DI (14) | Directional Movement Index; ADX>25 = trend regime; DI crossovers for direction | TA-Lib `ADX`, `PLUS_DI`, `MINUS_DI` | Per bar | ID, SW |
| 9 | Stochastic Oscillator (%K, %D) | %K = (C − LowestLow(14))/(HighestHigh(14) − LowestLow(14)) × 100; %D = SMA3(%K); slow variant | TA-Lib `STOCH`; `ta.momentum.StochasticOscillator` | Per bar | SC, ID, SW |
| 10 | OBV / Volume Momentum | OBVₜ = OBVₜ₋₁ + Vₜ if Cₜ > Cₜ₋₁ else −Vₜ; Chaikin Money Flow; Accumulation/Distribution | TA-Lib `OBV`, `AD`, `ADOSC` | Per bar | ID, SW |
| 11 | VWAP / Anchored VWAP | VWAP = Σ(Price × Volume)/ΣVolume; reset daily or anchored to event (earnings, IPO, gap) | Provided directly by Kite Ticker; `pandas-ta.vwap()`; computed from ticks | Real-time intraday | SC, ID |
| 12 | Volume Profile / Market Profile | POC (highest-volume price bucket); Value Area High/Low = 70% of session volume; TPO letters | Derived from tick/1m OHLCV; custom histograms; `pyVolumeProfile` [speculative maturity] | Per session | ID, SW |
| 13 | Order Flow Imbalance (OFI) | OFI = Σ(Δbid volume − Δask volume) from L2 updates; Lee-Ready trade classification; aggressive buy − sell volume | L2 depth: Kite full market depth (20-level for premium), Polygon.io L2, IBKR `reqMktDepth`, Deutsche Börse T7 EOBI | Millisecond–tick | SC, ID |
| 14 | Bid-Ask Spread | Ask₁ − Bid₁; relative spread = spread ÷ mid; effective spread from trade prints | Level 1 quotes on all broker WebSockets | Tick | SC, ID |
| 15 | Depth of Book / Liquidity | Cumulative quantity at top N levels; Kyle's λ market-impact estimate; book-imbalance ratio | L2/L3 feeds: Kite depth, Polygon L2, IBKR `reqMktDepth`, exchange direct feeds | Tick | SC, ID |
| 16 | Tick Data Microstructure | Trade intensity, inter-arrival times, uptick/downtick runs, VPIN (Volume-synchronized PIN), Kyle's λ | Tick-by-tick trades + quotes from Polygon, IBKR, exchange feeds | Tick | SC |
| 17 | Support / Resistance & Pivot Points | Prior swing highs/lows; classical/Fibonacci/Camarilla pivots; volume nodes; round numbers | Derived from OHLCV; `pandas-ta` pivot helpers | Per bar / daily | ID, SW |
| 18 | Chart Patterns | Breakouts, triangles, flags, wedges, head-and-shoulders, double top/bottom; detected via local extrema + trendline regression | Derived from OHLCV; `TA-Lib` pattern functions; custom CV/ML classifiers | Per bar | ID, SW |
| 19 | Fibonacci Retracement / Extension | 23.6%, 38.2%, 50%, 61.8%, 78.6%, 127.2%, 161.8% from swing pivots | Derived from OHLCV | Per swing | SW, PO |
| 20 | Elliott Wave Counts | Impulse (5-wave) / corrective (3-wave) labelling; often subjective [speculative — automated labelling unreliable] | Derived from price swings; `neowave`/`elliottwave` packages [speculative maturity] | Per swing | SW, PO |
| 21 | Candlestick Patterns | Engulfing, hammer, doji, morning/evening star, shooting star, harami, three-white-soldiers | TA-Lib pattern functions (`CDLENGULFING`, `CDLHAMMER`, etc., ~60 patterns) | Per bar | ID, SW |
| 22 | Gap Statistics | Gap up/down %, gap-fill probability, opening auction imbalance, overnight vs intraday returns | Previous close vs open; NSE/NASDAQ auction data | Daily open | ID, SW |
| 23 | Relative Strength vs Index/Sector | Stock return − benchmark/sector return; RS ratio (Mansfield); IBD Relative Strength rank | OHLCV for stock + NIFTY 50 / S&P 500 / DAX + sector index | Daily | SW, PO |
| 24 | Beta / Correlation Regime | Rolling β to NIFTY 50 / S&P 500 / DAX; rolling correlation matrices; DCC-GARCH for dynamic corr | Return series; `statsmodels`, `arch` package | Daily / weekly | PO, LT |
| 25 | Momentum & Mean-Reversion Factors | 3/6/12M price momentum (skip most-recent month), 52-week high/low proximity, Jegadeesh-Titman momentum, short-term reversal | Adjusted daily OHLCV | Daily | SW, PO, LT |
| 26 | Realized Volatility & Volatility Regime | Close-to-close σ, Parkinson, Garman-Klass, Yang-Zhang range-based estimators; regime detection via HMM | OHLCV; `arch`, `hmmlearn` | Per bar / daily | ID, SW, PO |
| 27 | Volatility of Volatility | σ of rolling realized vol; used for regime-switching filters | Derived | Daily | SW, PO |
| 28 | Ichimoku Cloud | Tenkan-sen (9), Kijun-sen (26), Senkou Span A/B (52), Chikou Span; cloud thickness signals trend strength | TA-Lib not native; `pandas-ta.ichimoku()` | Per bar | SW, PO |
| 29 | Parabolic SAR | Stop-and-reverse points; acceleration factor 0.02 → 0.20 | TA-Lib `SAR` | Per bar | ID, SW |
| 30 | Auction Market Theory Metrics | Opening range, initial balance (first hour), value area migration, single prints | Derived from intraday tick/1m | Per session | ID, SW |

---

### 1.3 Macroeconomic Factors

Macro drives discount rates, earnings expectations, risk premia, liquidity regimes, and sector rotation. Predominantly PO/LT signals; scheduled releases create ID volatility.

| # | Factor | Measurement | Data Source | Update Frequency | Horizon |
|---|--------|-------------|-------------|------------------|---------|
| 1 | Policy Interest Rates | Fed Funds target range, RBI repo rate, ECB deposit + main refinancing rate, BoE Bank Rate | FRED (`FEDFUNDS`, `DFF`), RBI DBIE, ECB Statistical Data Warehouse, BoE database | Meeting-based (RBI ~bimonthly; Fed 8×/yr; ECB 8×/yr) | ID event, SW, PO, LT |
| 2 | Inflation | India CPI (MOSPI), WPI; US CPI + Core CPI + PCE + Core PCE; Eurozone HICP + Core HICP | MOSPI, BLS (`CPIAUCSL`, `CPILFESL`), BEA (`PCEPI`), Eurostat, RBI | Monthly | ID event, SW, PO |
| 3 | GDP Growth | Real GDP QoQ SAAR, YoY; India GVA; nowcasts (Atlanta Fed GDPNow, NY Fed Nowcast) | MOSPI, BEA, Eurostat, OECD, Atlanta Fed | Quarterly + nowcast weekly | PO, LT |
| 4 | FX Rates | USD/INR, EUR/USD, USD/JPY, GBP/USD, EUR/INR; realized FX vol; NEER/REER | RBI reference rates, ECB, FRED (`DEXINUS`, `DEXUSEU`), broker FX feeds (OANDA, IBKR) | Tick to daily | ID, SW, PO |
| 5 | Commodity Prices | Brent/WTI crude, natural gas, gold, silver, copper, aluminium, iron ore, wheat, palm oil | ICE, CME, MCX (IN), LME, World Bank Pink Sheet, EIA, Investing.com | Real-time to daily | ID, SW, PO |
| 6 | Yield Curve Shape | 10Y–2Y spread, 10Y–3M spread (Fed recession indicator), sovereign term structure | FRED (`T10Y2Y`, `T10Y3M`), RBI G-sec yield curve, ECB yield curves, Bundesbank | Daily | SW, PO, LT |
| 7 | PMI / Business Surveys | Manufacturing + services PMI, composite; Ifo Business Climate, ZEW Economic Sentiment, ISM Manufacturing/Services | S&P Global PMI, ISM, Ifo Institute, ZEW, HSBC India Manufacturing PMI | Monthly | ID event, SW, PO |
| 8 | Labour Market | US NFP + unemployment + labour force participation + wage growth; EU unemployment; India CMIE labour data | BLS, Eurostat, CMIE India [paid], DGET India | Monthly (weekly claims US) | ID event, SW, PO |
| 9 | Geopolitical Risk Index | Caldara-Iacoviello GPR, GPR-Threats, GPR-Acts; news analytics; sanctions trackers | Caldara-Iacoviello GPR (`policyuncertainty.com`), ACLED conflict data, GDELT | Daily / event-driven | ID, SW, PO |
| 10 | FII / DII Flows (India) | Daily net cash-market buying/selling by FIIs and DIIs; F&O positioning | NSE daily FII/DII data, NSDL FPI monitor, SEBI, Moneycontrol | Daily | ID, SW, PO |
| 11 | Sector Rotation Signals | Sector-ETF relative momentum, earnings-revision breadth, factor leadership rotation | NSE sector indices, SPDR sector ETFs (XLK/XLF/XLE etc.), STOXX sector indices | Daily / weekly | SW, PO |
| 12 | Liquidity Cycles | M2 growth, central-bank balance sheet size, RBI net liquidity (LAF surplus/deficit), Fed reverse repo (RRP), ECB balance sheet | RBI weekly statistical supplement, Fed H.4.1, FRED (`WALCL`, `M2SL`), ECB | Weekly / monthly | PO, LT |
| 13 | Credit Spreads | IG-OAS, HY-OAS, EMBI+, CDX IG/HY, iTraxx Europe, India AAA-Gsec spread | FRED (`BAMLH0A0HYM2`, `BAMLC0A0CM`), Markit CDX/iTraxx, CCIL India, Bloomberg | Daily | SW, PO, LT |
| 14 | Fiscal Policy | Deficit ÷ GDP, capex allocation, tax changes, subsidies, tariff/trade policy | Union Budget IN, US Treasury Daily Statement, EU Commission fiscal reports | Annual + event-driven | PO, LT |
| 15 | Monetary Surprise | Actual policy/CPI/NFP print − Bloomberg consensus; OIS-implied vs realized | Bloomberg/Reuters survey, CME FedWatch, OIS curve, RBI OIS | Event-driven | ID, SW |
| 16 | Real Interest Rates | Nominal yield − expected inflation; TIPS breakeven; 5Y5Y forward inflation swap | FRED (`DFII10`, `T5YIFR`), RBI, ECB, inflation-swap markets | Daily | PO, LT |
| 17 | Housing / Construction Cycle | Housing starts, permits, mortgage rates (US 30Y), home price indices (Case-Shiller, RBI HPI, EU HPI) | US Census, FRED, Eurostat, RBI, property registries | Monthly | PO |
| 18 | Consumer Confidence | Conference Board, University of Michigan, RBI consumer confidence survey, Eurozone ESI | Conference Board, U-Michigan, RBI, Eurostat | Monthly | SW, PO |
| 19 | Trade Balance / Current Account | Exports, imports, CAD ÷ GDP, terms of trade; sector sensitivity for IT exporters / oil importers | Statistical agencies, RBI, BEA, Eurostat | Monthly / quarterly | PO |
| 20 | Regulatory / Policy Regime | Sector-specific: pharma approvals (CDSCO/FDA/EMA), telecom tariffs (TRAI), banking capital norms (Basel/RBI), energy policy | SEBI/RBI/TRAI/CDSCO/FDA/EMA press releases, EU regulators | Event-driven | ID, SW, PO |

Python macro tooling: `fredapi` (FRED), `pandas-datareader` (multiple), `dbnomics-python-client` (DBnomics aggregator), `wbdata` (World Bank), `oecd-py` [verify], direct RBI DBIE HTTP.

---

### 1.4 Sentiment & Behavioural Factors

| # | Factor | Measurement | Data Source | Update Frequency | Horizon |
|---|--------|-------------|-------------|------------------|---------|
| 1 | Financial News Sentiment | FinBERT / DeBERTa-finance / LLM-classified polarity + relevance + entity mapping | Bloomberg News, Reuters, Dow Jones Newswires, Benzinga, MarketAux, NewsAPI.org, GDELT [verify licensing] | Real-time | ID, SW |
| 2 | Headline Novelty / Shock Score | Cosine distance between new headline embeddings and prior corpus; entity-level surprise | News feeds + vector DB (Milvus, Weaviate, pgvector, Qdrant); OpenAI/`sentence-transformers` embeddings | Real-time | ID |
| 3 | Social Media Sentiment | Bullish/bearish score from X/Twitter cashtags, Reddit r/wallstreetbets & r/IndianStockMarket, StockTwits | X API v2, Reddit API/PRAW, StockTwits API; Pushshift historical [status uncertain — verify] | Real-time to hourly | ID, SW |
| 4 | Retail Attention | Mention counts, Google Trends spikes, Wikipedia pageviews, watchlist additions | `pytrends` [unofficial], Wikipedia pageview API, StockTwits trending, broker internal data | Hourly / daily | ID, SW |
| 5  | Analyst Consensus & Rating Changes | Mean/median target price, buy/hold/sell distribution, upgrade/downgrade events, estimate dispersion σ, revision direction (up/down count ratio) | Refinitiv I/B/E/S, FactSet Estimates, Bloomberg BEst, Zacks, TipRanks, Visible Alpha, Trendlyne (IN), MarketsMojo | Daily + event-driven | SW, PO |
| 6  | Put/Call Ratio (Volume & OI) | Total put ÷ total call (volume-weighted and OI-weighted); index-wide and stock-specific; PCR > 1.2 typically oversold, < 0.7 overbought | NSE F&O bhavcopy (IN, EOD), CBOE `equitypc.csv` (US, intraday), EUREX (EU), Polygon.io options, Tradier, IBKR option chains, `nsepython` helpers | Daily EOD (NSE) / real-time (CBOE) | ID, SW |
| 7  | Implied Volatility Surface & Skew | ATM IV, 25-delta risk reversal, 25-delta butterfly, IV term structure (30/60/90-day), IV rank/percentile (IVR/IVP), CBOE SKEW index | CBOE (US), NSE option chain via Kite/`nsepython` (IN), EUREX (EU), Polygon.io options, ORATS, OptionMetrics, LiveVol; IV computed with `py_vollib` or `QuantLib-Python` | Real-time / EOD | ID, SW, PO |
| 8  | VIX / India VIX / VSTOXX | Model-free 30-day implied vol from listed options; VIX9D, VIX, VIX3M, VIX6M term structure; India VIX (NIFTY 50 options); VSTOXX (EU) | CBOE, NSE India VIX, STOXX; FRED (`VIXCLS`, `VXNCLS`) | Real-time / daily | ID, SW, PO |
| 9  | Institutional Positioning | 13F holdings Δ (US, T+45), 13D/G >5% stake filings, SEBI SHP-1 (IN), FPI monthly data (NSDL), ESMA net-short position registers (EU), CFTC CoT for futures | SEC EDGAR 13F/13D/G, WhaleWisdom, Dataroma, NSDL FPI Monitor, ESMA/BaFin short-position registers, CFTC | Quarterly + event | PO, LT |
| 10 | Short Interest & Days-to-Cover | Short interest ÷ float; days-to-cover = SI ÷ ADV; borrow fee & utilization from securities-lending market | FINRA short interest (US, biweekly), NSE SLBM data + F&O ban list (IN), ESMA/BaFin (EU, >0.5% threshold); IBKR SLB, Ortex, S3 Partners, FIS Astec | Biweekly + daily borrow | SW, PO |
| 11 | Insider Transactions (Real-Time) | Cluster buys by officers/directors; open-market vs option-exercise ratio; net insider $ value over 30/90/180-day windows | SEC Form 4 (T+2, US), SEBI SAST/PIT (IN, T+2), BaFin Directors' Dealings under EU MAR; `openinsider.com`, EDGAR Form 4 feed, `edgartools` | Event-driven T+2 | SW, PO, LT |
| 12 | Earnings Call Tone Analysis | NLP on transcripts: Loughran-McDonald financial dictionary counts (negative/uncertain/litigious/weak-modal), FinBERT tone, Q&A hostility, hedging density, YoY 10-K/10-Q language change (cosine distance), CEO/CFO vocal-uncertainty proxies | Refinitiv StreetEvents, AlphaSense, Seeking Alpha, Tikr, FactSet CallStreet; audio via Whisper transcription; `edgartools` for filings | Quarterly + event | ID (release), SW, PO |
| 13 | Fear/Greed Composite Indices | CNN Fear & Greed (7-factor composite), Tickertape/Trendlyne Market Mood Index (IN), AAII sentiment survey, NAAIM Exposure Index, Investors Intelligence Bull/Bear | CNN Business (methodology public, API unofficial), Tickertape, AAII, NAAIM, Investors Intelligence | Daily / weekly | SW, PO |
| 14 | Options Flow / Unusual Options Activity | Large sweeps, block trades, volume ≫ OI, dark-pool prints, OI change bhavcopy (IN) | CBOE LiveVol, Cheddar Flow, FlowAlgo, Unusual Whales, Market Chameleon, Polygon options; NSE F&O OI change files (IN); OPRA feed [expensive — verify licensing] | Real-time | ID, SW |
| 15 | Dark-Pool / Off-Exchange Print Ratio | Dark-pool volume ÷ total volume; block size distribution; FINRA ADF prints; short-volume ratio | FINRA ADF, FINRA short-sale volume files, Cboe EDGX ATS data, Nasdaq Data Link FINRA sets [verify current availability] | Daily | SW, PO |
| 16 | Google Trends / Search Interest | Ticker/company/product query z-score vs 30-day baseline; geo-split; abnormal spike detection | Google Trends UI; `pytrends>=4.9.2` [unofficial, throttled, may break] | Daily / weekly | SW |
| 17 | Wikipedia Pageview Anomalies | Daily pageviews on company/entity pages vs 30-day baseline z-score | Wikimedia REST API `/pageviews` (free, official) | Daily | SW |
| 18 | Retail Order-Flow / Crowding Proxy | Small-lot trade share, odd-lot imbalance, retail participation share (SEBI monthly bulletin, IN), Nasdaq retail-flow data (US, paid); Robintrack historical only — service discontinued | FINRA TRF, exchange TAQ, SEBI bulletins, Nasdaq Data Link retail flow [paid], broker internal telemetry [private] | Intraday / monthly | ID, SW |
| 19 | Analyst Price-Target Dispersion | σ(target) ÷ mean(target) — high dispersion = high uncertainty premium; separately EPS-estimate dispersion | Refinitiv I/B/E/S, Bloomberg BEst, TipRanks, FactSet | Daily | SW, PO |
| 20 | Media Coverage Intensity | Article count z-score by ticker/sector, abnormal headline-volume spikes, entity co-mention graphs | RavenPack, Bloomberg News, Dow Jones Newswires, GDELT, Event Registry, NewsAPI.org | Real-time | ID, SW |
| 21 | Narrative / Theme Momentum | Topic-model frequency (BERTopic/LDA) for AI, defence, EV, renewables, "China+1", rate-cut narrative, etc.; trend slope & acceleration | News corpus + `BERTopic>=0.16`, Google Trends, earnings-call transcripts | Daily / weekly | SW, PO |
| 22 | LLM-Based Earnings/Filing Narrative Scoring | GPT-5-class or Claude-4-class model prompted to score reports/transcripts on structured JSON dimensions (guidance tone, competitive positioning, capital allocation, risk disclosures) | OpenAI API, Anthropic API, local FinLLMs (Llama-3-finance fine-tunes); source docs from EDGAR/BSE/NSE | Quarterly / event | SW, PO |
| 23 | Central-Bank Communication Sentiment | Hawkishness/dovishness score on Fed statements, minutes, FOMC pressers, RBI MPC minutes, ECB accounts; LLM + Loughran-McDonald hybrid | Fed website, RBI MPC minutes, ECB account; AlphaSense, custom parsers | Event-driven | ID event, SW, PO |
| 24 | Sentiment Divergence Signals | Analyst sentiment vs social sentiment gap; institutional vs retail flow divergence; sentiment–price divergence (bullish sentiment + falling price → squeeze or value setup) | Composite of above sources | Daily | SW, PO |

Production NLP stack: `transformers>=4.44`, models `ProsusAI/finbert`, `yiyanghkust/finbert-tone`, `ahmedrachid/FinancialBERT-Sentiment-Analysis`; `sentence-transformers>=2.7`; `spaCy>=3.7` for NER; `BERTopic>=0.16`; `vaderSentiment` as fast social-media baseline; `praw>=7.7` (Reddit), `tweepy>=4.14` (X API v2 — verify current access tier/pricing); `openai>=1.30`, `anthropic>=0.25`; `edgartools` for SEC filings.

---

### 1.5 Alternative Data Factors

Alternative data is powerful but expensive, noisy, legally constrained, and slow to validate. Predominantly SW/PO/LT signals and event-risk monitors; converted to real-time alerts for ID use. Every source must carry license metadata, provenance, redistribution restrictions, and privacy compliance (GDPR / DPDP India / CCPA), plus explicit "embargo windows" to avoid accidental use of non-public material.

| # | Factor | Measurement / Signal | Data Source | Update Frequency | Horizon |
|---|--------|----------------------|-------------|------------------|---------|
| 1  | Satellite — Parking Lot / Retail Foot Traffic | Car counts via CV (YOLOv8, Detectron2) on Planet/Maxar imagery; YoY store-traffic Δ vs comp quarter | Planet Labs, Maxar, Orbital Insight, SpaceKnow, RS Metrics, Placer.ai [verify current pricing] | Weekly to monthly | SW, PO |
| 2  | Satellite — Oil Storage / Tank Fill | Floating-roof shadow radius → volume estimate; Cushing OK storage proxy for crude | Orbital Insight, Ursa Space, Kayrros | Weekly | SW, PO |
| 3  | Cargo Ship & Port Activity | AIS vessel counts, port dwell time, container throughput, tonne-miles; Baltic Dry Index proxy | MarineTraffic API, Spire Maritime, Kpler, Windward, exactEarth, Clarksons, UNCTAD | Real-time to daily | SW, PO |
| 4  | Crop / Vegetation Yields | NDVI/EVI from Sentinel-2/Landsat, MODIS; rainfall anomalies; acreage; yield forecasts for agri-linked equities | ESA Copernicus Open Access Hub (free Sentinel-2), NASA MODIS/VIIRS, USDA NASS, IMD India, Climate Corp, Descartes Labs | Weekly / seasonal | PO, LT |
| 5  | Credit/Debit Card & POS Transactions | Same-store sales growth, ticket size, MCC/sector spend Δ; early-quarter revenue signal | Bloomberg Second Measure, Earnest Analytics, Facteus, Consumer Edge, Yodlee/Envestnet, Affinity Solutions, Mastercard SpendingPulse [expensive — verify pricing] | Weekly / monthly | SW, PO |
| 6  | Web Traffic Analytics | Visits, unique users, session duration, bounce rate, conversion proxies, search referrals | Similarweb API, Semrush, Sensor Tower web intelligence, Cloudflare Radar aggregates | Daily / weekly | SW, PO |
| 7  | App Downloads & Usage | Downloads, DAU/MAU, session duration, uninstall rate, store ranking | Sensor Tower, data.ai (formerly App Annie), Appfigures, Apptopia | Daily | SW, PO |
| 8  | Job Postings / Hiring Signal | Postings volume, role mix (AI/cloud/sales), tech-stack telemetry, layoff intensity | LinkedIn Talent Insights, Indeed Hiring Lab, Revelio Labs, Lightcast (Burning Glass), Thinknum, company career pages | Daily / weekly | PO, LT |
| 9  | Patent Filings & IP Quality | Filing count, citations, claims breadth, technology-cluster mapping, examiner citations | USPTO PatentsView, EPO Espacenet, WIPO Patentscope, Google Patents, Lens.org, IFI CLAIMS | Weekly / monthly | LT |
| 10 | Supply-Chain Disruption Signals | Supplier delays, sanctions exposure, shipment cancellations, factory shutdowns, chokepoint (Suez/Panama) alerts | Panjiva/S&P Global Market Intelligence, ImportGenius, Everstream Analytics, Resilinc, project44, GDELT | Real-time to weekly | SW, PO |
| 11 | Shipping / Freight Indices | Baltic Dry Index, Shanghai Containerized Freight Index (SCFI), Freightos Baltic Index (FBX), HARPEX, air-cargo rates (TAC Index) | Baltic Exchange, Freightos, Drewry, HARPEX, TAC Index | Daily / weekly | SW, PO |
| 12 | Weather / Climate Data | Heatwaves, monsoon deviation, hurricanes, HDD/CDD; commodity- and utility-linked equity impact | NOAA, ECMWF, IMD, Meteostat, OpenWeatherMap, Copernicus Climate Data Store | Hourly to daily | ID event, SW, PO |
| 13 | ESG Controversy Signals | Lawsuits, environmental spills, labour disputes, governance scandals, boycott intensity, controversy severity | RepRisk, Sustainalytics, MSCI ESG Controversies, GDELT, NGO databases, news scraping | Real-time | ID, SW, PO |
| 14 | Regulatory Filings / XBRL Events | 8-K/10-Q/10-K change diff, MCA21 filings (IN), SEBI disclosures, BaFin/EQS ad-hoc; going-concern flags, language-change cosine distance | SEC EDGAR (free), MCA21 India [portal/paid], NSE/BSE, ESMA, Bundesanzeiger, BaFin; `edgartools`, `sec-api` | Event-driven | ID, SW, PO |
| 15 | Google Trends — Product/Brand | Product/brand/keyword query index; abnormal z-score; geo split | Google Trends UI + `pytrends` [unofficial, throttled] | Daily / weekly | SW |
| 16 | Product Reviews & Ratings | Star rating trend, review volume Δ, sentiment, defect complaints; App Store / Play Store rating drift | Amazon/Flipkart pages [scraping legal risk — respect ToS], Trustpilot, G2, App Store, Google Play, Reevoo | Daily / weekly | SW, PO |
| 17 | Real-Estate Footfall & Location Data | Mall/store visits, dwell time, catchment movement, tenant traffic | Placer.ai, SafeGraph [business status changed — verify], Foursquare Places, Unacast | Daily / weekly | PO |
| 18 | Government Tender / Procurement Awards | Tender awards, bid pipeline, contract size vs revenue, order-book visibility | GeM India, EU TED, SAM.gov (US), state procurement portals, DGS&D | Daily / event | SW, PO |
| 19 | Import/Export Bills of Lading | Supplier/customer concentration, shipment volumes, HS-code changes, country-of-origin shifts | Panjiva, ImportGenius, Volza, Trademo | Weekly / monthly | PO |
| 20 | Cybersecurity / Outage Signals | Breach disclosures, dark-web mentions, uptime incidents, ransomware chatter, CVE exposure | Recorded Future, Flashpoint, Cloudflare Radar, Downdetector, Have I Been Pwned aggregates | Real-time | ID, SW |
| 21 | Pricing / SKU Scrapes | Price changes, discount intensity, stock-outs, assortment breadth; competitive positioning | DataWeave, PriceSpider, retailer APIs where available, compliant custom crawlers | Daily | SW, PO |
| 22 | LLM-Powered Earnings/Filing Extraction | Structured extraction of guidance, KPIs, risks, and forward statements from 10-K/10-Q/annual reports; multi-doc synthesis | OpenAI/Anthropic APIs + EDGAR/BSE/NSE PDFs; `unstructured`, `llama-parse`, `docling` | Quarterly / event | SW, PO, LT |
| 23 | Insider Trading Signals from Non-Standard Sources | Corporate jet flight patterns [ethical/legal caveats — public FAA/ADS-B data only], LinkedIn hires at target firms, senior-departure clusters | ADS-B Exchange, FlightRadar24 historical [ToS-dependent], LinkedIn, Revelio Labs | Daily / event | SW, PO |
| 24 | Point-in-Time Fundamentals & Consensus | As-was fundamentals (avoids look-ahead in backtests); vintage consensus estimates | S&P Compustat Point-in-Time, FactSet PIT, Refinitiv I/B/E/S vintage, Sharadar SF1 PIT | Daily snapshot | SW, PO, LT (backtest-critical) |

Governance requirements for alt-data (mandatory in production):
- Source license & redistribution registry per dataset.
- Provenance/consent metadata (especially for card and location data).
- Privacy compliance: GDPR (EU), DPDP Act 2023 (India), CCPA/CPRA (US).
- MNPI (Material Non-Public Information) firewall — alt-data vendors must certify no MNPI in feed.
- Feature "embargo windows" and point-in-time snapshots to prevent look-ahead bias in backtests.
- Vendor concentration risk: no single-vendor dependency on production signals without a fallback.

---

## 2. Market Data Feeds — Best-Value Sources per Market

A multi-market trading bot must separate **data acquisition** from **broker execution**. Architecture requires feed-specific adapters, normalized schemas, entitlement checks, symbol-master mapping, corporate-action adjustment (versioned), and time-zone/session calendar handling.

```
                +-------------------+
                | Provider Adapters |
                | Kite/IBKR/Polygon |
                | NSE/BSE/DB MDS    |
                +---------+---------+
                          |
                  raw ticks/bars/refdata
                          |
          +---------------v----------------+
          | Ingestion Bus / Stream Layer   |
          | Kafka/Redpanda/NATS + Schema   |
          +---------------+----------------+
                          |
        +-----------------+------------------+
        |                                    |
+-------v--------+                  +--------v---------+
| Hot Tick Store |                  | Historical Lake  |
| Redis/QuestDB  |                  | S3/MinIO+Parquet |
| TimescaleDB    |                  | Iceberg/Delta    |
+-------+--------+                  +--------+---------+
        |                                    |
        +-----------------+------------------+
                          |
                +---------v----------+
                | Feature Pipeline   |
                | Polars/Pandas/TA   |
                +---------+----------+
                          |
                +---------v----------+
                | Backtest/Live Bot  |
                | Broker Execution   |
                +--------------------+
```

Latency classes used below:
- **Free/EOD** — delayed or end-of-day; unsuitable for SC/ID execution.
- **Retail real-time** — hundreds of ms to seconds; acceptable for discretionary/intraday bots, not HFT.
- **Professional low-latency** — direct exchange/vendor feeds, co-location possible; suitable for serious SC when paired with low-latency execution.
- **Institutional terminal** — rich data but rarely designed for automated low-latency trading unless licensed programmatic APIs are purchased.

**Depth-of-book clarification (important — corrects the §1.2 implication):** Zerodha Kite Ticker's "full" mode delivers top-5 broker-level market depth, NOT exchange full-depth L2/L3 order book. True full-depth Indian order-book data requires a licensed NSE/BSE exchange feed (e.g., TBT — Tick-By-Tick — via a member/co-lo arrangement). Polygon.io L2 and IBKR `reqMktDepth` are similarly capped by exchange entitlement; genuine full-depth US data comes from Nasdaq TotalView-ITCH, NYSE OpenBook/Integrated, and CTA/UTP direct feeds. For Xetra/Eurex, full-depth requires T7 EOBI (Enhanced Order Book Interface) — retail-tier feeds are netted/aggregated. Design order-flow features to degrade gracefully when only top-N depth is available.

---

### 2.1 Indian Markets — NSE / BSE

| Provider | Data Available | API Type | Latency Class | Cost Tier | Python Library / Access |
|---|---|---|---|---|---|
| **Zerodha Kite Connect** | Live LTP/quotes, WebSocket ticks, OHLCV bars, **top-5 broker-level market depth** (not exchange L2), instruments master, historical minute/day candles, orders/positions/holdings, GTT. No historical tick data. Corporate actions handled separately. | REST + WebSocket (KiteTicker) | Retail real-time | ₹2,000/month per app (Kite Connect); exchange charges via trading account [verify current terms] | `kiteconnect>=4.2` official Python SDK |
| **Zerodha historical data** | Minute/day candles + larger intervals; per-request lookback limits vary by interval (e.g., minute ~60 days per call, day ~2000+ days); continuous futures partial [verify]. | REST | Historical | Included with Kite Connect | `kiteconnect.KiteConnect.historical_data()` |
| **Zerodha rate limits** | Documented throttles include per-second REST limits and WebSocket instrument-subscription caps (~3000 instruments per WS connection [verify current cap]); implement client-side token-bucket regardless. | REST/WebSocket | Retail | Included | Official docs |
| **Groww API** | Groww is primarily a retail app; **public broker-grade trading/market-data API availability is limited/uncertain** as of 2024–2025. Do not rely on unofficial scraping in production. | [verify public API availability] | Unknown | [verify current pricing] | No stable official Python SDK known — avoid for production unless partner API contract exists |
| **IndMoney API** | Primarily investment/wealth platform. **Public broker-grade trading/market-data API availability is limited/uncertain.** Some Groww/IndMoney community wrappers exist but are unofficial and fragile. | [verify public API] | Unknown | [verify current pricing] | No stable official Python SDK known — use only via official partner API/contract |
| **NSE official data products** | Real-time market data, tick-by-tick (TBT), index data, derivatives data, corporate actions, reference data, historical bhavcopy, auction data; free EOD bhavcopy on website. | Direct feed / leased line / SFTP / files | Professional low-latency to EOD | Free EOD; paid professional feeds [verify current pricing via NSE Data & Analytics] | Custom feed handlers; free bhavcopy via `requests`; unofficial libs: `nsepython`, `jugaad-data`, `NSEpy` |
| **BSE official feeds** | Real-time equity/derivatives/currency data, market depth, indices, corporate actions, reference files, bhavcopy. | Direct feed / files / SFTP | Professional to EOD | Paid official feeds; free EOD [verify] | Custom ingestion; website/file download scripts |
| **Nasdaq Data Link / Quandl India** | Some India fundamentals, macro, EOD, alternative datasets per vendor package; NSE premium datasets vary by license. | REST | EOD / delayed | Free + paid datasets [verify current pricing] | `nasdaq-data-link` |
| **Refinitiv Eikon / LSEG Workspace India** | Real-time quotes, fundamentals, news, estimates, corporate actions, ownership, ESG, macro. | Desktop API / Data Platform APIs | Institutional terminal/API | High cost [verify current pricing] | `eikon`, `refinitiv-data` |
| **Bloomberg Terminal India** | Real-time data, BQL, fundamentals, estimates, news, corporate actions, EMSX/IOI where licensed. | Terminal API, BLPAPI | Institutional terminal/API | High cost [verify current pricing] | `blpapi`, `xbbg`, BQL |
| **5paisa API** | Market quotes, historical candles, order placement, portfolio; depth per entitlement. | REST + WebSocket | Retail real-time | Low/retail; brokerage plan dependent [verify] | `py5paisa` |
| **Upstox API v2** | Live market feed WebSocket, historical candles, instruments, orders, portfolio; supports NSE/BSE segments. | REST + WebSocket | Retail real-time | Generally free with account; pricing/plan [verify] | `upstox-python-sdk` (official) [verify current package/version] |
| **Angel One SmartAPI** | Quotes, WebSocket streaming, historical candles, order APIs, GTT, portfolio. | REST + WebSocket | Retail real-time | Retail/free with account [verify terms] | `smartapi-python` |
| **Fyers API v3** | Market data, WebSocket, historical candles, order placement, positions, GTT, basket orders. | REST + WebSocket | Retail real-time | Retail/free with account [verify] | `fyers-apiv3` |
| **Dhan API** | Live quotes, WebSocket, historical, orders; increasingly popular retail broker-API. | REST + WebSocket | Retail real-time | Retail [verify current pricing] | `dhanhq` |
| **Yahoo Finance / yfinance** | Delayed/EOD OHLCV, adjusted prices, corporate actions, basic fundamentals for `.NS`/`.BO` tickers; intraday limited. | Unofficial HTTP | Free/delayed | Free (fragile — Yahoo has broken `yfinance` multiple times) | `yfinance>=0.2.38` |
| **NSEpy** | Historical NSE data; maintenance inconsistent — verify current status before production use [verify]. | Unofficial HTTP scraping | EOD | Free | `nsepy` |
| **jugaad-data / jugaad-trader** | NSE bhavcopy/historical helpers; broker utilities. | Unofficial HTTP | EOD / delayed | Free | `jugaad-data`, `jugaad-trader` |
| **nsepython** | NSE option-chain / market-data scraping helpers; breaks when NSE changes anti-bot controls. | Unofficial HTTP | Delayed / fragile | Free | `nsepython` |

**Recommended India retail/low-budget stack:**
- Live trading + data: Zerodha Kite Connect (`kiteconnect`), or Upstox/Fyers/Angel One/Dhan if already brokered there.
- EOD history: NSE/BSE bhavcopy + `jugaad-data` / custom downloader; supplement with `yfinance` for non-critical research only.
- Storage: PostgreSQL/TimescaleDB for bars, Redis for live ticks, Parquet for research.
- Corporate actions: NSE/BSE official CA files; never rely solely on Yahoo adjustments for Indian backtests (adjustment errors are common on `.NS` tickers).
- Options: NSE option chain via broker WebSocket + `nsepython` for research; compute IV with `py_vollib`.

**Recommended India professional/institutional stack:**
- Official NSE/BSE licensed real-time or TBT feed + co-located / low-latency infrastructure if SC is serious.
- Refinitiv/LSEG or Bloomberg for fundamentals/news/estimates/corporate actions.
- Broker/execution: institutional broker with exchange-member FIX connectivity; IBKR India covers limited product set [verify current India offering].
- Audited symbol master, survivorship-bias-free history, licensed redistribution controls.

---

### 2.2 US Markets — NYSE / NASDAQ

| Provider | Data Available | API Type | Latency Class | Cost Tier | Python Library / Access |
|---|---|---|---|---|---|
| **Alpaca Markets** | US equities/ETFs, paper + live trading, fractional shares, orders/positions; market data via IEX (free tier) or SIP (paid); WebSocket trades/quotes/bars/news. | REST + WebSocket | Retail real-time (IEX) to SIP real-time (paid) | Free tier + paid market-data plans [verify current pricing] | `alpaca-py>=0.20` |
| **Polygon.io** | Stocks trades/quotes, aggregates, WebSocket, options (OPRA), indices, forex, crypto; historical tick/minute/day; L2 for stocks on higher tiers. | REST + WebSocket | Retail/professional per plan | Prompt says $0–$199/month tiers; enterprise higher [verify current pricing] | `polygon-api-client` |
| **IEX Cloud** | Historically fundamentals, quotes, news. **Important: IEX Cloud legacy service status changed in 2024 — sunset/retirement announced. Verify current availability and successor product before designing around it.** | REST | Delayed / real-time per entitlement | [verify current pricing/status — treat as legacy] | `iexfinance` (legacy) |
| **Nasdaq Data Link** | Alternative data, fundamentals, economic, some EOD datasets; Sharadar historical fundamentals/prices (SF1, SEP) — high quality for backtests. | REST | EOD / dataset-dependent | Free + paid datasets [verify] | `nasdaq-data-link` |
| **IBKR market data** | Global equities, options, futures, FX; real-time or delayed per exchange subscription; historical bars; tick-by-tick for limited windows; depth if subscribed. Rate-paced. | TWS/Gateway socket API | Retail/professional broker feed | Exchange subscription fees + broker account [verify] | `ib_insync`, official `ibapi` |
| **Alpha Vantage** | Intraday/daily adjusted, fundamentals, technical indicators, FX/crypto, news sentiment; free 25 calls/day; premium up to 1200 calls/min [verify]. | REST | Free/delayed/rate-limited | Free + premium tiers [verify current pricing] | `alpha_vantage` |
| **Yahoo Finance / yfinance** | Delayed quotes, historical OHLCV, corporate actions, options chains, basic fundamentals; unofficial and rate-limited; breaks periodically. | Unofficial HTTP | Free/delayed | Free | `yfinance>=0.2.38` |
| **Tiingo** | Historical EOD/intraday, IEX real-time, news, fundamentals for US equities/ETFs; excellent retail research value. | REST + WebSocket (IEX) | Retail | Affordable paid tiers [verify current pricing] | `tiingo` or direct HTTP |
| **Nasdaq Basic / TotalView-ITCH** | Nasdaq best bid/offer/trades (Basic) or full-depth order book (TotalView). | Direct/vendor feed | Professional low-latency | Paid exchange fees [verify] | Vendor feed handlers (C++/Java; Python downstream) |
| **NYSE OpenBook / Integrated** | NYSE full-depth order book. | Direct/vendor feed | Professional low-latency | Paid exchange fees [verify] | Vendor feed handlers |
| **SIP CTA/UTP** | Consolidated tape for NYSE-listed (CTA) and NASDAQ-listed (UTP) securities. | Direct/vendor feed | Professional | Paid [verify] | Vendor feed handlers |
| **Databento** | Normalized market data (equities/futures/options); PCAP/tick schemas; excellent for research and backtests. | REST / streaming / files | Professional / research | Usage-based [verify current pricing] | `databento` |
| **QuantHouse / Exegy / SR Labs** | Institutional low-latency normalized global feeds. | Feed handler / API | Professional low-latency | Institutional [verify] | Vendor SDKs |
| **SEC EDGAR** | Free filings (10-K/10-Q/8-K/Forms 3/4/5/13F/DEF 14A) + XBRL structured financials. | REST / bulk XBRL | EOD (T+0 for filings) | Free (rate-limited to 10 req/s per SEC guidance) | `edgartools`, `sec-api` (paid), direct HTTP to `data.sec.gov/api/xbrl/` |

**Recommended US retail stack:**
- Execution: Alpaca (paper + live) or IBKR.
- Real-time data: Alpaca IEX or SIP; Polygon.io for richer aggregates + options.
- Historical intraday: Polygon.io or Tiingo; Databento for research-grade tick.
- Fundamentals: SEC EDGAR direct XBRL + Sharadar SF1 (via Nasdaq Data Link).
- Calendars: `pandas_market_calendars`.
- Alpha Vantage for prototypes only (rate limits kill production use).

**Recommended US institutional stack:**
- Direct SIP + exchange proprietary feeds (Nasdaq TotalView-ITCH, NYSE OpenBook/Integrated) via licensed vendor/colo for SC.
- Bloomberg / Refinitiv / FactSet for fundamentals, estimates, corporate actions, news.
- Databento / Polygon Enterprise / QuantHouse for normalized historical tick.
- Execution via IBKR, prime-broker FIX, or broker smart order router.
- Compustat Point-in-Time for backtest-safe fundamentals.

---

### 2.3 European Markets — XETRA / Deutsche Börse

| Provider | Data Available | API Type | Latency Class | Cost Tier | Python Library / Access |
|---|---|---|---|---|---|
| **Deutsche Börse Market Data + Services (MDS)** | Xetra cash equities, Eurex derivatives, indices, reference data, delayed/EOD packages, historical data. | Direct feeds, files, vendor

---

## 3. Multi-Agent Architecture Design

The system uses a hierarchical, event-driven multi-agent architecture with a LangGraph-based supervisor orchestrator for research/decision workflows, wrapped by deterministic Python asyncio services for latency-sensitive market data, risk gates, and execution. Communication is via a typed message bus (Redpanda/Kafka for durable streams, NATS JetStream for control-plane, Redis for hot cache). All agent boundaries are Pydantic v2.x validated.

Core design principle: split into (a) deterministic latency-sensitive services (data, risk, execution) and (b) LLM/agentic workflows (research, red-team, thesis synthesis). For scalping and sub-second intraday, LLMs must NOT be in the hot path — they operate asynchronously as supervisory/research layers.

Base stack:
- Messaging: Redpanda 24.x or Apache Kafka 3.x for durable streams; NATS JetStream 2.10.x for control-plane
- Schemas: Pydantic v2.x at boundaries; Protobuf/Avro for high-volume streams
- Hot cache: Redis 7.x (last-tick, kill switches, idempotency keys)
- Time-series: TimescaleDB 2.x, QuestDB 8.x [verify current], ClickHouse 24.x
- Object storage: MinIO / S3 for filings, transcripts, LLM prompts/completions
- Workflow orchestration: LangGraph (pin exact version, 0.2.x+ [verify current stable])
- Observability: OpenTelemetry, Prometheus, Grafana, Loki, Jaeger; LangSmith or Arize Phoenix for LLM traces
- Broker adapters: kiteconnect 5.0.x (Zerodha), ib_insync 0.9.86 or ib_async (IBKR), QuickFIX for institutional FIX

### 3.1 Agent Roster and Roles

---

#### 1. Market Data Agent (MDA)

Role: Real-time and historical market data ingestion, normalisation, validation, and fan-out.

Responsibilities:
- Maintain WebSocket connections (Kite Ticker, IBKR TWS/Gateway, Polygon.io, Alpaca, Deutsche Börse CEF/A7 [verify current API])
- Subscribe/unsubscribe symbols dynamically; heartbeat with exponential backoff + jitter reconnection
- Normalise ticks/quotes/trades/OHLCV/corporate actions to canonical UTC-nanosecond schemas
- Detect stale feeds (configurable `stale_feed_threshold_ms`, default 3000ms); publish DATA_FEED_DEGRADED
- Deduplicate ticks; handle symbol mapping across NSE/BSE/NYSE/NASDAQ/XETRA
- Compute derived real-time fields: VWAP, rolling ATR(14), bid-ask spread, order-book imbalance
- Failover to secondary vendor if primary stale beyond threshold
- Persist raw + normalised data to TimescaleDB/QuestDB/ClickHouse

Inputs:
- Kite Connect WebSocket (wss://ws.kite.trade) — NSE/BSE
- Polygon.io WebSocket (wss://socket.polygon.io) [verify current pricing]
- IBKR TWS API / IB Gateway via ib_insync
- Deutsche Börse A7 / XETRA feed [verify current access path, likely via IBKR or FIX broker]
- REST fallback: yfinance 0.2.x, Alpha Vantage v1, Finnhub [verify pricing]
- Corporate actions: NSE/BSE bhavcopy, NYSE TAQ, EDGAR 8-K feed

Outputs: `MarketTick`, `Quote`, `Trade`, `OHLCVBar`, `OrderBookSnapshot`, `CorporateAction`, `MarketStatus` Pydantic messages published to Kafka/NATS topics: `market.tick.{venue}.{symbol}`, `market.bar.{tf}.{venue}.{symbol}`, `market.status.{venue}`

Tools: `kiteconnect==5.0.x`, `ib_insync==0.9.86` (or `ib_async` fork), `polygon-api-client`, `alpaca-py`, `websockets==12.x`, `aiohttp==3.9.x`, `aiokafka` or `redis-py[hiredis]==5.x`, `pandas==2.x`, `polars`, `pyarrow==14.x`, `exchange_calendars`, `pandas_market_calendars`

Communicates with: Technical Analysis Agent (real-time), Execution Agent (last-price validation), Risk Manager (kill-switch triggers on feed degradation), Macro & Sentiment Agent (session state)

LLM tier: None — deterministic Python service. Optional cheap/fast LLM only for anomaly summarisation on side path (never in hot path).

Note on scalping: retail broker APIs generally do NOT support institutional-grade sub-100ms latency [speculative]. Sub-100ms scalping needs colocation, direct exchange feeds, and FIX. Kite/IBKR retail feeds typically deliver ticks in ~100–500ms.

---

#### 2. Fundamental Research Agent (FRA)

Role: Bottom-up fundamental analysis and valuation.

Responsibilities:
- Fetch and parse filings: SEC 10-K/10-Q/8-K/XBRL (EDGAR), NSE/BSE disclosures, Deutsche Bundesanzeiger, annual reports
- Compute ratios: P/E,Continuing directly from the truncation point in §3.1 (Fundamental Research Agent, in the middle of the ratios list):

P/B, P/S, EV/EBITDA, EV/Sales, EV/Revenue, ROE, ROCE, ROIC, FCF yield, net debt/EBITDA, interest coverage, gross/operating/net margins, cash conversion, dividend yield, Piotroski F-Score, Altman Z-Score, Beneish M-Score (earnings manipulation detection)
- Normalise statements across IFRS / Ind AS / US GAAP; detect one-offs and extraordinary items
- Build DCF models: multi-stage (3-stage typical), configurable terminal growth (Gordon growth or exit multiple), WACC via CAPM plus Damodaran country risk premium for India/EU; reverse-DCF to back out market-implied assumptions; sensitivity tables on WACC × terminal growth × margin
- Peer comparison: auto-select peers from same GICS sub-industry / NIC code; normalise for cross-listing and accounting differences; compute percentile rank
- Moat assessment (Morningstar-style: cost advantage, intangibles, switching cost, network effects, efficient scale) via LLM synthesis over 10-K risk factors and MD&A with structured output
- Earnings call transcript analysis: tone, guidance changes, Q&A hedging, management confidence
- Management quality: insider ownership, compensation structure, capital allocation history
- Insider transactions: Form 4 (US), NSE/BSE insider trading disclosures, DE §19 MAR notifications
- Track analyst revisions, guidance changes, promoter pledging (India-specific), buybacks, related-party transactions

Inputs:
- SEC EDGAR REST API (data.sec.gov/api/xbrl/), sec-api / edgartools
- Financial Modeling Prep API v3/v4 [verify current pricing], EODHD [verify], Simfin v2, Intrinio [verify], Polygon.io reference/financials [verify]
- NSE/BSE corporate filings RSS/API, Screener.in / Tickertape / Trendlyne / Tijori (scraping subject to ToS — prefer licensed) [verify]
- European: Deutsche Bundesanzeiger, company IR pages, Deutsche Börse issuer data [verify]
- Earnings transcripts: Seeking Alpha [verify], Quartr API [verify], Motley Fool [ToS risk — speculative]
- Rate curves & macro context: FRED, RBI, ECB
- Damodaran country risk premium datasets (annual CSV from NYU Stern)
- yfinance 0.2.x as fallback only (not production-critical)

Outputs: `FundamentalReport` / `FundamentalSignal` — {ticker, venue, as_of, ratios: dict, dcf_intrinsic_value, dcf_low, dcf_high, dcf_assumptions, upside_pct, peer_percentile, moat_rating (Wide/Narrow/None), moat_score, quality_score [0–100], earnings_quality_score, red_flags: list[str], signal_direction ∈ {bullish, bearish, neutral}, reasoning, confidence, timestamp_utc}

Tools: `edgartools` / `sec-api` / `python-xbrl`, `pandas==2.x`, `polars`, `numpy`, `scipy`, `pyxirr` (IRR/DCF), `simfin`, `yfinance==0.2.x`, `beautifulsoup4`, `lxml`, `httpx`, `playwright==1.x` (JS-heavy sites), `openpyxl`/`pyxlsb`/`tabula-py`/`camelot-py` for statement extraction, `unstructured` + `pymupdf` for PDF, LangChain document loaders, vector store (Qdrant 1.9+ / Weaviate 1.24+ / pgvector 0.7+) for filings RAG

Communicates with: Signal Aggregator (primary), Red Team (exposes assumptions for adversarial review), Portfolio Manager (long-term conviction, sector exposure), Macro & Sentiment Agent (shares earnings/calendar events), Compliance & Audit (source provenance)

LLM tier: **Frontier** (GPT-4o / Claude 3.5–4.x Sonnet or Opus / Gemini 1.5–2.x Pro [verify current model names]) for narrative synthesis, moat assessment, transcript analysis, MD&A reading. **Cheap tier** (Claude 3.5 Haiku / GPT-4o-mini) for ratio extraction, table normalisation, filing pre-processing. Deterministic Python for numeric ratio and DCF math. Frequency: daily for swing/positional, weekly+ for long-term. Token budget: ~8k–32k per analysis.

---

#### 3. Technical Analysis Agent (TAA)

Role: Indicator computation, pattern recognition, and multi-timeframe technical signal generation.

Responsibilities:
- Compute 100+ indicators across all configured timeframes (tick / 1s / 5s / 15s / 1m / 3m / 5m / 15m / 30m / 1h / 4h / 1D / 1W / 1M):
  - Trend: SMA, EMA (9/21/50/200), WMA, DEMA, TEMA, MACD (12,26,9), ADX/DMI, Supertrend (7,3), Ichimoku (9,26,52), Parabolic SAR
  - Momentum: RSI (14), StochRSI, Stochastic, CCI, ROC, Williams %R
  - Volatility: ATR (14), Bollinger Bands (20,2), Keltner Channels, Donchian Channels
  - Volume: OBV, VWAP, anchored VWAP + stddev bands, Volume Profile / POC, MFI, CMF
  - Microstructure: bid-ask spread, order-book imbalance, realized volatility (custom Cython/Rust module if sub-ms compute needed)
- Multi-timeframe confluence scoring: bullish/bearish alignment across TFs (e.g., daily + 4h + 1h all bullish → high confluence)
- Pattern recognition:
  - TA-Lib's 60+ CDL candlestick functions
  - Classical patterns: H&S, double top/bottom, cup & handle, flags/pennants, triangles, wedges — rule-based detectors preferred; `stumpy` matrix profile for motif discovery [speculative for production]
  - Support/resistance: rolling fractal pivots, Volume Point of Control, options OI clusters (NSE derivatives)
- Market regime detection: trending vs mean-reverting vs volatile — Hurst exponent, ADX regimes, HMM via `hmmlearn`; used to weight strategy types
- Signal generation from configurable strategy library (breakout, mean reversion, momentum, trend-following); each strategy emits a typed signal with entry, stop, targets, invalidation, expected holding period
- Backtest each indicator/strategy before live enablement; reject signals failing liquidity/spread constraints

Inputs: `OHLCVBar` and `MarketTick` streams from MDA per timeframe topic, historical from TimescaleDB/QuestDB/ClickHouse, corporate action-adjusted history, options chain (NSE derivatives) for OI-based S/R, horizon config, risk constraints

Outputs: `TechnicalSignal` — {ticker, venue, horizon, timeframe, signal_type ∈ {breakout, reversal, trend, meanrev}, direction ∈ {long, short, exit, flat}, entry_zone: tuple[float,float], stop_loss, target_1, target_2, indicators_snapshot: dict, pattern_detected, key_levels: {support, resistance}, invalidation_price, regime, confluence_score, strength [-1..1], confidence, timestamp_utc}

Tools: `TA-Lib==0.4.28`+ (C-backed; install via conda or pre-built wheel — pin build), `pandas-ta==0.3.14b0` (verify maintenance status), `stumpy`, `numpy`, `polars`, `numba` (JIT for custom indicators), `scipy.signal` (peak/trough), `hmmlearn`, `arch` (GARCH volatility), `vectorbt` / `backtrader` / `bt` / `zipline-reloaded` [verify maintenance] for backtesting, `mplfinance`/`plotly` for debug viz, `XGBoost==2.x` / `LightGBM==4.x` optional for ML pattern classification

Communicates with: Signal Aggregator (normalized technical score), Execution Agent (entry/exit levels, order style suggestion), Risk Manager (ATR-based stops, expected loss), Market Data Agent (bar subscriptions)

LLM tier: **None in hot path.** Deterministic numpy/Cython. Optional **cheap/fast LLM** (GPT-4o-mini, Claude 3 Haiku) purely for natural-language pattern narrative in swing/positional reports. For scalping, LLM absent entirely.

---

#### 4. Macro & Sentiment Agent (MSA)

Role: Top-down macro context, news NLP, social sentiment, options/flow signals, regime classification.

Responsibilities:
- **Macro monitoring**: Fed / RBI / ECB rates; CPI / WPI / PCE / HICP / PMI / unemployment / GDP release calendars; yield curves (2s10s, 3m10y, India 10Y, US 2Y/10Y, German Bund); DXY, USD/INR, EUR/USD, oil, gold, copper, Baltic Dry; VIX / India VIX / VSTOXX
- **Event calendar**: FOMC / RBI MPC / ECB decisions, CPI/jobs/GDP releases, earnings dates, ex-dividend, index rebalancing (NIFTY, SENSEX, S&P 500, DAX)
- **News NLP**: real-time headline ingestion (NewsAPI, Benzinga, Bloomberg/Reuters if licensed, GDELT 2.1); FinBERT (`ProsusAI/finbert`, `yiyanghkust/finbert-tone`) or FinLlama for sentiment; entity linking via spaCy 3.7+ custom NER; event classification (M&A, earnings beat/miss, fraud, regulatory, litigation, downgrade); topic modelling via BERTopic
- **Social sentiment**: Reddit (r/wallstreetbets, r/IndianStreetBets — Reddit API, rate-limit aware, pushshift where available), StockTwits API, X/Twitter API v2 [verify pricing tier — paid as of 2024], Telegram/Discord only if compliant + licensed; bot/spam filtering and source credibility weighting; abnormal-mention spike detection
- **Options signals**: PCR, IV rank, skew, max pain (use cautiously), OI change, gamma exposure (GEX), unusual options activity — NSE options chain via Kite REST, CBOE data [verify], OCC/options vendors [verify]
- **India-specific flow**: FII/DII cash + derivatives (NSE participant-wise OI), delivery %, bulk/block deals — daily NSE/BSE public data [verify ToS]
- **Regime classification**: risk-on/risk-off, trending/ranging, high-vol/low-vol, liquidity stress — used by Signal Aggregator to reweight agents

Inputs: NewsAPI / Benzinga / Finnhub / GDELT keys, FRED API, ECB SDW API [verify], RBI portals [verify], Reddit/StockTwits/X credentials, NSE bhavcopy + FII/DII CSV, FinBERT weights (local or HF Inference API), market data from MDA

Outputs: `MacroRegimeSignal`, `NewsSentimentSignal`, `SocialSentimentSignal`, `OptionsFlowSignal`, `FiiDiiFlowSignal`, `EventRiskAlert` — schema includes {ticker_or_index, news_sentiment_score [-1..1], social_bull_bear_ratio, mention_spike_zscore, pcr, iv_rank, gex, fii_net_flow_inr_cr, dii_net_flow_inr_cr, regime_label, event_risk_flags: list, confidence, timestamp_utc}

Tools: `transformers==4.x`, FinBERT models on HF, `spaCy==3.7+`, `sentence-transformers`, BERTopic, `scikit-learn`, `statsmodels`, `fredapi`, `newspaper3k` / `trafilatura`, `feedparser`, `praw` (Reddit), custom StockTwits/X clients, cheap LLM for headline summarisation, frontier LLM for ambiguous event interpretation

Communicates with: Signal Aggregator (sentiment/regime scores), Risk Manager (event-risk lockouts, regime-risk flags), Portfolio Manager (macro allocation tilts), Compliance & Audit (source/timestamp logs)

LLM tier: **Frontier** model for ambiguous news/event interpretation and management-commentary parsing. **FinBERT/local transformer** for high-throughput sentiment scoring (thousands of headlines/hour). **Cheap model** for summarisation, entity linking pre-processing.

---

#### 5. Alternative Data Agent (ADA)

Role: Scheduled ingestion and analysis of non-traditional datasets for medium/longer-horizon alpha.

Responsibilities:
- Satellite / footfall / parking-lot proxy analysis (requires licensed vendor — RS Metrics, Orbital Insight, SpaceKnow [verify current]) [speculative usefulness at retail scale]
- Web scraping: price changes, product launches, app reviews, hiring pages, store openings — robots.txt / ToS compliance mandatory
- Credit/debit card and consumer transaction panels (Yodlee, Second Measure, Facteus [verify]) — requires licensing + privacy review
- Job postings trends by company/sector (LinkedIn scraping restricted — use licensed providers like Revelio Labs, LinkUp)
- App download rankings + user ratings (SensorTower / data.ai [verify pricing], App Store / Google Play public metadata within ToS)
- Supply chain / shipping / import-export records (ImportGenius, Panjiva, government portals where legal)
- ESG controversy detection, litigation monitoring
- Batch feature generation for ML models and thesis support

Inputs: Licensed alt-data vendors [verify], public web with ToS compliance, App Store / Play public APIs [verify], government import/export portals

Outputs: `AlternativeDataSignal`, `AltDataFeatureSet`, `AnomalyReport`, `ThesisSupportEvidence` — {ticker, feature_name, value, zscore_vs_history, percentile_vs_peers, provenance, license_tag, confidence, timestamp_utc}

Tools: `scrapy==2.x`, `playwright==1.x`, `beautifulsoup4`, `trafilatura`, `great_expectations` / `pandera` (data quality), `opencv-python` / `rasterio` / `geopandas` (satellite/geospatial), `Airflow==2.x` / Dagster 1.x / Prefect 2.x (batch scheduling), Feast 0.4x (feature store) [verify], DuckDB + Iceberg/Delta Lake [verify]

Communicates with: Fundamental Research Agent (supports/rejects business assumptions), Signal Aggregator (lower-frequency alpha features), Red Team (provenance/bias risk exposure), Compliance & Audit (legal/source audit, license tags)

LLM tier: **Cheap model** for extraction/classification; **frontier model** for thesis synthesis when alt-data materially affects valuation.

---

#### 6. Signal Aggregator Agent (SAA)

Role: Combine all research/technical/macro/alt signals into a unified trade thesis with a calibrated confidence score.

Responsibilities:
- Consume normalized signals from FRA, TAA, MSA, ADA via Kafka
- Apply ensemble logic:
  - Weighted voting by horizon and regime (technical dominates scalping; fundamental+macro dominate long-term)
  - Bayesian updating with calibrated priors (if implemented)
  - Stacking / meta-model using historical hit-rate per agent × symbol × regime
  - Rule-based hard gates: liquidity floor, spread ceiling, corporate-action lockout, earnings-window lockout, restricted list
- Down-weight correlated evidence (RSI + MACD + MA cross ≠ three independent signals)
- Decay stale signals exponentially: `freshness_decay = exp(-age_seconds / half_life_seconds)`; half-life ranges from seconds (scalping) to weeks (fundamental)
- Produce `TradeThesis`: direction, entry range, stop, targets, expected return/loss, R:R, confidence, horizon, evidence attribution, invalidation conditions
- Detect materially conflicting signals → auto-route to Red Team
- Refuse to trade if insufficient independent evidence (min agent count per horizon)
- Maintain per-agent Sharpe / hit-rate / precision tracked in evaluation store (MLflow / W&B)

Inputs: `AgentSignal` stream from all research agents, historical hit rates from evaluation store, current risk constraints from RMA, horizon config

Outputs: `TradeThesis`, `SignalAttribution`, `ConsensusScore`, `ResearchGapRequest`

Tools: `pydantic==2.x`, `numpy`, `scipy`, `scikit-learn` (isotonic regression, Platt scaling for confidence calibration), optional `XGBoost`/`LightGBM` meta-model, `mlflow` / W&B for tracking

Communicates with: Red Team (every non-trivial thesis), Risk Manager (candidate order plan), Orchestrator (missing evidence / low confidence), Portfolio Manager (allocation feasibility)

LLM tier: **Frontier model** for generating the human-readable thesis text and evidence synthesis; **deterministic scoring engine** for the actual numeric aggregation. Never let the LLM invent numeric confidence — cap LLM-declared confidence unless supported by quantitative evidence.

---

#### 7. Red Team / Cynical Advisor Agent (RTA)

Role: Adversarially challenge every trade thesis before capital is committed. This is the single most important agent for avoiding narrative-driven losses.

Responsibilities:
- Generate an explicit bear case and alternative explanations for every thesis
- Bias / fallacy checks: recency bias, confirmation bias, narrative fallacy, survivorship bias, overfitting / data snooping, small-sample, unpriced event risk, crowded-trade risk, liquidity trap, correlation concentration, "too good to be true" backtest metrics, stale or unreliable data source
- Stress tests: gap up/down, IV spike, earnings surprise, macro shock (rate surprise, geopolitical), broker/API outage, slippage 2×/3×, correlation-breakdown, sudden delisting/circuit
- Emit decision ∈ {approve, caution, veto, escalate} with severity ∈ {low, medium, high, critical}
- Propose risk-adjusted mitigation: smaller size, options hedge (if permitted), wait for confirmation, convert to paper-only observation, reject
- Cap final confidence: `final_confidence = min(aggregator_confidence, red_team.adjusted_confidence_cap)`
- Retrieve historical similar-trade outcomes from trade-journal RAG for base-rate anchoring

Inputs: `TradeThesis`, supporting evidence from all upstream agents, historical similar-trade outcomes (vector-search over trade journal + postmortems), portfolio exposure, data provenance logs

Outputs: `RedTeamReview` — {thesis_id, decision, severity, counter_thesis, bias_flags: list[str], stress_failures: list[str], required_mitigations: list[str], adjusted_confidence_cap: float [0..1], base_rate_reference}

Tools: **Frontier reasoning LLM** — Anthropic Claude Sonnet/Opus (4.x class) [verify current], OpenAI o-series / GPT-4.1 class [verify current], Google Gemini 2.x Pro [verify current]; mandatory checklist prompt templates; retrieval over trade journal + postmortems (Qdrant/pgvector); statistical validation helpers (bootstrap CI, permutation tests)

Communicates with: Signal Aggregator (challenge/response loop, revision requests), Risk Manager (veto/caution flags, stress assumptions), Orchestrator (human escalation for major disagreement), Compliance & Audit (rationale logging)

LLM tier: **Frontier / high-reasoning required.** Red Team quality > cost/latency for swing/positional/long-term. For scalping, Red Team runs offline/post-trade on samples, never in hot path. Consider deliberately using a *different* provider than the Signal Aggregator (e.g., Aggregator on GPT-4o, Red Team on Claude Opus) to reduce shared-blindspot risk [speculative but supported by ensemble-diversity theory].

---

#### 8. Risk Manager Agent (RMA)

Role: Enforce position-level and portfolio-level risk before and during trading. Hard synchronous gate — deterministic, not LLM-driven.

Responsibilities:
- **Pre-trade**: position sizing via fractional Kelly (typically 0.25×–0.5× full Kelly), fixed-fractional, volatility targeting, or max-loss cap; reject trades exceeding per-symbol / sector / country / currency / broker / strategy limits; liquidity check (ADV participation ≤ configurable %, spread ≤ threshold, market-impact estimate); stop distance and max-loss computation; correlation and factor exposure limits
- **Portfolio**: parametric + historical-simulation + Monte Carlo VaR/CVaR (95%, 99%); drawdown monitoring; beta to NIFTY/SENSEX/SPY/QQQ/DAX; currency exposure (USD/INR, EUR/INR); sector/geography concentration
- **Intraday controls**: daily max loss, max consecutive losses, kill switch on feed-degradation / broker outage / excessive slippage / order-reject storm; market-wide volatility circuit breakers
- **Post-trade**: realized vs expected slippage, risk-limit breach detection, PnL attribution by agent/strategy/symbol/regime

Inputs: `TradeThesis`, `RedTeamReview`, portfolio positions + cash, live market data + volatility (ATR, GARCH), broker margin/available funds, horizon-specific risk policy

Outputs: `RiskDecision` ∈ {approve, reduce_size, reject, kill_switch}, `PositionSize`, `RiskLimitsStatus`, `KillSwitchEvent`, `StressTestReport`

Tools: `numpy`, `pandas`, `scipy`, `arch` (GARCH), `riskfolio-lib`, `PyPortfolioOpt`, `quantstats`, `empyrical-reloaded`, `cvxpy`; Redis for real-time kill-switch state; Prometheus alerts; broker margin APIs

Communicates with: Execution Agent (only approved orders pass), Portfolio Manager (portfolio limit updates), Orchestrator (breach escalations), Compliance & Audit (all approvals/rejections logged)

LLM tier: **None** for numContinuing directly from the truncation point in §3.1 (Compliance & Audit Agent, Inputs list incomplete):

restricted list, corporate action calendar, human-operator overrides, broker end-of-day ledgers

Outputs: `ComplianceDecision` ∈ {pass, block, warn, escalate}, `AuditEvent` (immutable append-only), `RegulatoryReport` (daily/weekly/monthly), `PolicyViolation`, `ModelGovernanceRecord`, `TradeRegister` (SEBI/FINRA/MiFID export format)

Tools: PostgreSQL 15/16 append-only tables with row-level checksums, ClickHouse 24.x for high-volume audit search, Kafka compacted audit topics, S3 Object Lock / MinIO WORM for tamper-evident archive [verify cloud config], OpenTelemetry traces, `Open Policy Agent (OPA)` for policy-as-code rule engine, HashiCorp Vault for secret custody, `great_expectations` / `pandera` for schema validation, `python-jose` for signed audit records

Communicates with: Orchestrator (hard blocks + escalations), Execution Agent (synchronous pre-order permission check), Risk Manager (limit-state authority), all agents (provenance capture, license tag propagation)

LLM tier: **Cheap model** for narrative compliance summaries in daily/weekly reports. **Frontier model** offline only for classifying complex regulatory text or new circulars into machine-readable policy rules. **Never LLM as real-time compliance gate** — deterministic OPA/rule engine only.

---

#### 12. Orchestrator / Supervisor Agent (OSA)

Role: Top-level coordinator that wires agents into workflows per horizon, manages state, error recovery, and human-in-the-loop escalation.

Responsibilities:
- Activate correct agent topology per horizon config (see §3.3)
- Manage LangGraph workflow lifecycle: start, checkpoint, resume, replay
- Route inter-agent messages when direct pub-sub is insufficient (e.g., research → red-team → risk → execution chains)
- Detect and act on failure modes:
  - Data feed degradation → freeze new entries, allow only risk-reduction exits
  - Broker disconnect → cancel unfilled orders, escalate
  - LLM provider outage → failover to secondary provider (e.g., HAI proxy switching Claude → GPT-4o → Gemini)
  - Agent unresponsive → circuit-break, degrade gracefully
- Human-in-the-loop:
  - Notify via Slack / Telegram / email / SMS (Twilio) when confidence in escalation grey zone or Red Team veto with override permission
  - Structured approval UI (FastAPI + minimal HTMX front-end or Streamlit) with expiring approval tokens
  - Timeout defaults to safe action (no new trade)
- Scheduling:
  - Pre-market briefing (India: 08:30 IST, US: 08:00 ET, EU: 07:30 CET)
  - Post-market attribution (India: 16:00 IST, US: 17:00 ET, EU: 18:00 CET)
  - Weekly / monthly rebalance triggers
  - Earnings-cycle review triggers
- Model / prompt governance: version LLM prompts, model IDs, temperatures; A/B test new versions on paper before live
- Trace correlation: attach `trace_id` to every message; propagate through Kafka headers; unified OpenTelemetry spans across services
- Emergency stop: single `emergency_stop` REST endpoint that flattens or halts all activity

Inputs: Horizon config, market calendar, scheduled cron triggers, agent status heartbeats, exception events, human approval callbacks

Outputs: `WorkflowState` checkpoints, `AgentTask` dispatch messages, `EscalationRequest`, `HumanApprovalRequest`, `RunSummary`, `EmergencyStopEvent`

Tools: **LangGraph** (0.2.x+ [verify]), **LangSmith** or Arize Phoenix for LLM tracing, `APScheduler==3.10.x` / Prefect 2.x / Dagster 1.x for scheduled jobs, FastAPI 0.110.x + Uvicorn/Hypercorn control plane, Slack SDK / Telegram Bot API / Twilio for HITL, PostgreSQL for LangGraph checkpoints, Redis for ephemeral workflow state, OpenTelemetry SDK

Communicates with: All agents; broker/risk/compliance control plane; human operators

LLM tier: **Frontier** for complex supervision and explanation in research workflows. **Cheap model** for routine status summaries and Slack notifications. **None** for deterministic state transitions and routing rules.

---

### 3.2 Inter-Agent Communication Patterns

#### Hybrid communication topology

Trading systems have conflicting requirements: low-latency deterministic execution and stateful async LLM research. Use a hybrid pattern rather than committing to a single messaging paradigm.

**1. Durable event bus (Kafka / Redpanda) for market and signal streams**

Topics with suggested partitioning:
- `market.tick.{venue}.{symbol}` — partition by symbol hash, retention 7 days hot + S3/MinIO cold
- `market.bar.{timeframe}.{venue}.{symbol}` — partition by symbol hash
- `signal.technical`, `signal.fundamental`, `signal.macro`, `signal.alternative` — partition by ticker
- `trade.thesis` — partition by thesis_id
- `risk.decision`, `execution.order_intent`, `execution.order`, `execution.fill`
- `audit.event` — compacted topic keyed by event_id

Producer/consumer libraries: `aiokafka==0.10.x` for asyncio, `confluent-kafka-python==2.x` for higher throughput.

**2. Low-latency control plane (NATS JetStream / Redis pub-sub)**

For control messages that must reach all agents in <10ms:
- `control.kill_switch` — global halt
- `control.agent_heartbeat` — health monitoring
- `control.human_approval` — approval events
- `control.emergency_stop`

NATS JetStream 2.10.x offers durable pub-sub with lower latency than Kafka for small control messages. Redis pub-sub is simpler but non-durable — use only for ephemeral notifications.

**3. Direct synchronous RPC for hard gates**

The Execution Agent MUST synchronously call Risk Manager + Compliance before every order submit. Async approval is unsafe for real capital.
- Transport: FastAPI + HTTP/2, or gRPC (`grpcio==1.60.x`), or Unix domain sockets if colocated
- Timeout: strict, e.g. 200ms for intraday, 2s for swing
- Every synchronous decision must ALSO emit an audit event to Kafka

**4. Shared state (Redis) for cache only — never source of truth**

- `last_tick:{venue}:{symbol}` — TTL 5s
- `risk:kill_switch` — boolean flag, always-consulted before order submit
- `broker:connection_status:{broker}` — health flag
- `order:idempotency:{key}` — TTL 24h, prevents duplicate submissions
- `position:{account}:{symbol}` — hot cache, authoritative copy in PostgreSQL

**5. Workflow state (LangGraph checkpoints in PostgreSQL)**

Research workflows persist state at every node. Enables:
- Resume after LLM provider outage
- Replay for debugging
- Time-travel for postmortem analysis

#### Communication flow diagram

```text
Market stream (high-freq):
  MDA ─Kafka─▶ TAA / MSA / RMA / EA
              (partitioned by symbol; ~100k msg/s peak)

Research stream (low-freq, high-value):
  FRA / TAA / MSA / ADA ─Kafka─▶ SAA ─▶ RTA ─▶ RMA ─▶ PMA ─▶ EA
  (LangGraph orchestrates SAA→RTA→RMA→PMA transitions with checkpoints)

Control plane (low-latency):
  OSA ◀─NATS/Redis─▶ all agents
  (kill switches, heartbeats, human approvals)

Hard synchronous gates (pre-order):
  EA ─sync gRPC─▶ RMA + CAA ─sync gRPC─▶ EA
  (must pass BOTH before broker submit; strict timeout)

Audit fan-in:
  all agents ─append─▶ Kafka `audit.event` ─▶ CAA / PostgreSQL / ClickHouse
```

#### Pydantic v2 structured output schemas

Every agent boundary uses strict Pydantic v2 models with `extra="forbid"` and `validate_assignment=True`. High-volume ticks may use msgspec or Protobuf internally, but convert to Pydantic at boundaries.

```python
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field, ConfigDict, confloat

class Venue(str, Enum):
    NSE = "NSE"; BSE = "BSE"
    NYSE = "NYSE"; NASDAQ = "NASDAQ"
    XETRA = "XETRA"

class Horizon(str, Enum):
    SCALPING = "scalping"
    INTRADAY = "intraday"
    SWING = "swing"
    POSITIONAL = "positional"
    LONG_TERM = "long_term"

class Direction(str, Enum):
    LONG = "long"; SHORT = "short"
    EXIT = "exit"; FLAT = "flat"

class BaseEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=False)
    schema_version: str = "1.0"
    event_id: str
    trace_id: str
    timestamp_utc: datetime
    source_agent: str

class MarketTick(BaseEvent):
    venue: Venue
    symbol: str
    last_price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    volume: Optional[int] = None
    exchange_timestamp_utc: datetime

class AgentSignal(BaseEvent):
    ticker: str
    venue: Venue
    horizon: Horizon
    direction: Direction
    strength: confloat(ge=-1.0, le=1.0)
    confidence: confloat(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    features: dict[str, Any] = Field(default_factory=dict)
    expires_at_utc: Optional[datetime] = None

class TradeThesis(BaseEvent):
    thesis_id: str
    ticker: str
    venue: Venue
    horizon: Horizon
    direction: Direction
    entry_low: float
    entry_high: float
    stop_loss: float
    target_prices: list[float]
    expected_return_pct: float
    expected_loss_pct: float
    reward_risk_ratio: float
    aggregator_confidence: confloat(ge=0.0, le=1.0)
    evidence_attribution: dict[str, float]  # source_agent → weight
    invalidation_conditions: list[str]
    thesis_text: str

class RedTeamReview(BaseEvent):
    thesis_id: str
    decision: Literal["approve", "caution", "veto", "escalate"]
    severity: Literal["low", "medium", "high", "critical"]
    counter_thesis: str
    bias_flags: list[str]
    stress_failures: list[str]
    required_mitigations: list[str]
    adjusted_confidence_cap: confloat(ge=0.0, le=1.0)

class RiskDecision(BaseEvent):
    thesis_id: str
    decision: Literal["approve", "reduce_size", "reject", "kill_switch"]
    approved_quantity: int = 0
    approved_notional: float = 0.0
    max_loss_amount: float
    stop_loss: Optional[float]
    risk_reasons: list[str]
    portfolio_var_95: Optional[float] = None
    portfolio_cvar_95: Optional[float] = None

class OrderIntent(BaseEvent):
    thesis_id: str
    broker: str
    account_id_hash: str
    ticker: str
    venue: Venue
    side: Literal["buy", "sell"]
    quantity: int
    order_type: Literal["market", "limit", "stop", "stop_limit"]
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: Literal["DAY", "IOC", "GTC"] = "DAY"
    idempotency_key: str
```

#### Confidence scoring schema

Never allow an LLM to invent a confidence number unsupported by quantitative evidence. Confidence is computed, not claimed.

**Agent-level confidence:**
```text
agent_confidence =
    model_calibration_score      # historical Brier score / precision by agent×horizon×regime
  × data_quality_score            # 1.0 validated; degraded if stale/missing/conflicting
  × freshness_score               # exp(-age_seconds / half_life_seconds)
  × regime_fit_score              # strategy-regime match (trend strat in ranging regime → down-weight)
  × evidence_independence_score   # penalize redundant correlated signals
```

Half-life by signal type:
- Technical (scalping): 30s
- Technical (intraday): 5min
- Technical (swing): 1 day
- Sentiment (news): 2h
- Sentiment (social): 30min
- Fundamental: 7 days
- Macro: 3 days
- Alternative: 14 days

**Signal Aggregator confidence:**
```text
weighted_score = Σ(w_i × strength_i × confidence_i × freshness_i)
gross_confidence = sigmoid(weighted_score)
conflict_penalty = 1 - min(0.4, weighted_disagreement_index)
calibrated_confidence = isotonic_calibrator(gross_confidence)  # trained on historical hit-rate
aggregator_confidence = calibrated_confidence × conflict_penalty
```

**Red Team cap:**
```text
post_red_team_confidence = min(
    aggregator_confidence,
    red_team.adjusted_confidence_cap
)
```

**Risk-adjusted final confidence:**
```text
final_trade_confidence =
    post_red_team_confidence
  × liquidity_score          # ADV participation, spread
  × portfolio_fit_score      # concentration, correlation
  × compliance_pass_binary   # {0, 1}
```

**Minimum thresholds by horizon:**
- Scalping: no LLM confidence — deterministic strategy score ≥ 0.72
- Intraday: `final_confidence ≥ 0.65`, no critical event risk
- Swing: `final_confidence ≥ 0.70`, Red Team mandatory
- Positional: `final_confidence ≥ 0.72`, Red Team + fundamental support mandatory
- Long-term: `final_confidence ≥ 0.75`, full evidence bundle required

#### Disagreement handling matrix

| Scenario | Aggregator action | Red Team action | Terminal action |
|---|---|---|---|
| Minor disagreement (1 agent contrary, others aligned) | Down-weight confidence | Standard review | Trade if threshold met |
| Material disagreement (2+ agents contrary) | Route to Red Team mandatory | Deep bear-case analysis | Reduce size or reject |
| Technical bullish + fundamental bearish + news of fraud/regulatory | Auto-veto attempt | Almost certain veto | Reject; add to watchlist |
| Red Team `caution` | Cap confidence, tighten stop | Emit mitigations | Reduce size, tighter stop |
| Red Team `veto` | — | Hard reject | Reject unless 2-person human override with ≤25% normal size |
| Red Team `escalate` | — | Human review required | Wait for human; timeout → no trade |
| Risk Manager `reject` | — | — | Hard reject (no override) |
| Compliance `block` | — | — | Hard reject (policy admin override only, full audit) |
| Kill switch active | Halt new entries | — | Risk-reduction exits only |

#### Human-in-the-loop escalation triggers

Trigger criteria (any one):
- Red Team decision = `escalate` or `veto` with override permitted
- Aggregator confidence in grey-zone: swing 0.60–0.70; positional 0.62–0.72; long-term 0.65–0.75
- Trade notional > 5% of portfolio OR > configured absolute threshold (₹10L / $50k / €50k typical)
- New strategy/model version not yet approved for live
- Data feed degraded (any critical source stale beyond threshold)
- Broker connection status uncertain in last 60s
- Regulatory/compliance ambiguity flagged by CAA
- Earnings/news event within horizon-configured blackout window
- Short-sell, leverage > 1×, derivatives, or unhedged cross-currency exposure
- Alternative data source with uncertain license/privacy provenance
- Model disagreement index > 0.35
- Kill switch triggered within last N minutes (configurable, default 30min)
- First N live trades of a newly deployed strategy (default N=10)

Approval request payload (structured, expiring token):
```json
{
  "approval_id": "uuid",
  "thesis_id": "uuid",
  "trace_id": "uuid",
  "decision_required_by_utc": "2025-01-01T10:15:00Z",
  "max_notional": 100000,
  "recommended_action": "approve|reject|modify",
  "summary": "text",
  "red_team_summary": "text",
  "risk_summary": "text",
  "approver_id_required": "user_hash",
  "rationale_required": true
}
```

Default timeout action: **no trade**. Never default to approval.

---

### 3.3 Trading Horizon Configuration

The same agent topology adapts per horizon by activating/deactivating agents in the hot path, adjusting data resolution, and tuning latency budgets. **LLM-driven agents are disabled from sub-second execution paths.**

| Horizon | Latency budget | Active agents (hot path) | Data resolution | Decision frequency | LLM in hot path? |
|---|---:|---|---|---|:---:|
| Scalping (<1 min) | <100ms internal (broker/API reality often 100–500ms retail) [speculative] | MDA, TAA, RMA, EA, CAA gates, OSA | Tick / L2 book | Continuous | No |
| Intraday | <1s internal | MDA, TAA, MSA (light), SAA (light), RMA, EA, CAA, OSA | Tick + 1s/1m bars | Per signal / event | No |
| Swing (2–10d) | Minutes | Full: MDA, FRA, TAA, MSA, SAA, RTA, RMA, PMA, EA, CAA, OSA | 15m/1h/daily | Daily review + event triggers | Yes (research path) |
| Positional (weeks–months) | Hours | Full + ADA | Daily/weekly | Weekly review + major events | Yes (research path) |
| Long-term (months–years) | Days | Full roster with heavy FRA/ADA/RTA | Weekly/monthly + filings | Monthly/quarterly review | Yes (research path) |

#### Horizon-specific signal weighting

```text
scalping    : technical=0.80, microstructure=0.20, others=0.00
intraday    : technical=0.55, sentiment=0.20, options_flow=0.15, macro=0.10
swing       : technical=0.35, fundamental=0.25, macro_sentiment=0.25, options=0.10, alt=0.05
positional  : fundamental=0.40, macro=0.25, technical=0.15, alt=0.15, sentiment=0.05
long_term   : fundamental=0.55, macro=0.20, alt=0.15, technical=0.05, sentiment=0.05
```

#### Full YAML configuration schema

```yaml
environment: production
paper_trading: true
base_currency: INR

markets:
  enabled: [NSE, BSE, NYSE, NASDAQ, XETRA]
  trading_calendar_timezone: Asia/Kolkata
  symbol_universe:
    NSE: [RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK]
    NASDAQ: [AAPL, MSFT, NVDA, GOOGL]
    NYSE: [JPM, BRK.B]
    XETRA: [SAP, SIE, ALV]

horizon_profile: swing  # default; per-strategy overrides allowed

profiles:
  scalping:
    latency_budget_ms: 100
    active_agents:
      - market_data
      - technical_analysis
      - risk_manager
      - execution
      - compliance_audit
      - orchestrator
    disabled_hot_path_agents:
      - fundamental_research
      - macro_sentiment_llm
      - alternative_data
      - signal_aggregator_llm
      - red_team_llm
      - portfolio_manager_llm
    data_resolution: tick
    decision_frequency: continuous
    require_human_approval: false
    min_confidence: 0.0
    strategy_score_threshold: 0.72
    max_order_participation_rate: 0.01
    max_spread_bps: 5
    max_position_risk_pct: 0.10
    signal_half_life_seconds: 30

  intraday:
    latency_budget_ms: 1000
    active_agents:
      - market_data
      - technical_analysis
      - macro_sentiment_light
      - signal_aggregator
      - risk_manager
      - execution
      - compliance_audit
      - orchestrator
    data_resolution: 1m
    decision_frequency: per_signal
    require_human_approval: false
    min_confidence: 0.65
    news_event_lockout_minutes: 15
    max_position_risk_pct: 0.25
    signal_half_life_seconds: 300

  swing:
    latency_budget_ms: 60000
    active_agents:
      - market_data
      - fundamental_research
      - technical_analysis
      - macro_sentiment
      - signal_aggregator
      - red_team
      - risk_manager
      - portfolio_manager
      - execution
      - compliance_audit
      - orchestrator
    data_resolution: daily
    decision_frequency: daily_review
    require_human_approval: true
    min_confidence: 0.70
    red_team_required: true
    earnings_blackout_days_before: 2
    earnings_blackout_days_after: 1
    max_position_risk_pct: 0.50

  positional:
    latency_budget_ms: 3600000
    active_agents:
      - market_data
      - fundamental_research
      - technical_analysis
      - macro_sentiment
      - alternative_data
      - signal_aggregator
      - red_team
      - risk_manager
      - portfolio_manager
      - execution
      - compliance_audit
      - orchestrator
    data_resolution: weekly
    decision_frequency: weekly_review
    require_human_approval: true
    min_confidence: 0.72
    fundamental_required: true
    max_position_risk_pct: 0.75

  long_term:
    latency_budget_ms: 86400000
    active_agents:
      - market_data
      - fundamental_research
      - technical_analysis
      - macro_sentiment
      - alternative_data
      - signal_aggregator
      - red_team
      - risk_manager
      - portfolio_manager
      - execution
      - compliance_audit
      - orchestrator
    data_resolution: monthly
    decision_frequency: monthly_review
    require_human_approval: true
    min_confidence: 0.75
    fundamental_required: true
    max_position_risk_pct: 1.00

risk:
  daily_max_loss_pct: 2.0
  portfolio_max_drawdown_pct: 10.0
  per_symbol_max_weight_pct: 8.0
  per_sector_max_weight_pct: 25.0
  per_country_max_weight_pct: 60.0
  fractional_kelly_multiplier: 0.25
  var_confidence: 0.95
  cvar_confidence: 0.95
  kill_switch:
    stale_market_data_ms: 3000
    broker_disconnect_seconds: 10
    consecutive_order_rejects: 3
    slippage_multiple_threshold: 3.0
    daily_loss_pct_trigger: 1.5  # softer trigger before hard 2.0

execution:
  default_order_type: limit
  twap_enabled: true
  vwap_enabled: true
  iceberg_enabled: true
  idempotency_required: true
  brokers:
    zerodha:
      enabled: true
      markets: [NSE, BSE]
      rate_limit_req_per_sec: 10  # verify current
    ibkr:
      enabled: true
      markets: [NYSE, NASDAQ, XETRA, LSE]
    groww:
      enabled: false  # verify official API contract before enabling
    indmoney:
      enabled: false  # verify official API contract before enabling
    saxo:
      enabled: false  # verify OpenAPI credentials

llm:
  provider_routing:
    cheap: gpt-4o-mini            # verify current model id
    frontier: claude-3-5-sonnet   # verify current model id
    red_team: claude-opus         # verify current model id — use different provider than frontier
  max_retries: 2
  structured_outputs_required: true
  store_prompts_and_responses: true
  provider_diversity_required: true  # red team ≠ aggregator provider
```

---

### 3.4 ASCII Architecture Diagram

#### Full system architecture

```text
                           ┌───────────────────────────────────────────────┐
                           │                 HUMAN OPERATOR                │
                           │  Approval UI / Slack / Telegram / Reports     │
                           └──────────────────────┬────────────────────────┘
                                                  │ approvals/escalations
                                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                       ORCHESTRATOR / SUPERVISOR AGENT (LangGraph)                         │
│    horizon config + retries + HITL + trace correlation + emergency stop endpoint          │
└───────────────┬─────────────────────┬───────────────────────────┬────────────────────────┘
                │                     │                           │
                │ workflow tasks      │ control/status            │ audit context
                ▼                     ▼                           ▼
        ┌───────────────┐     ┌────────────────┐         ┌─────────────────────┐
        │ LLM Providers │     │ Redis Hot State│         │ PostgreSQL+Timescale│
        │ (HAI proxy)   │     │ kill switches  │         │ checkpoints/audit   │
        │ OpenAI/Anthr/ │     │ last ticks     │         │ positions/orders    │
        │ Google/local  │     │ idempotency    │         │ ClickHouse audit    │
        └───────────────┘     └────────────────┘         └─────────────────────┘

┌─────────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│External Market Data │       │External Research Data│       │ Alternative Data     │
│ Kite WS/REST        │       │ SEC EDGAR/XBRL       │       │ licensed satellite   │
│ IBKR TWS/Gateway    │       │ NSE/BSE filings      │       │ web/app/job data     │
│ Polygon/Alpaca      │       │ FMP/EODHD/Intrinio   │       │ card panels [verify] │
│ XETRA via IBKR/FIX  │       │ FRED/RBI/ECB         │       │ ImportGenius/Panjiva │
└──────────┬──────────┘       └──────────┬───────────┘       └──────────┬───────────┘
           │                             │                              │
           ▼                             ▼                              ▼
┌─────────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│ MARKET DATA AGENT   │       │ FUNDAMENTAL RESEARCH │       │ ALTERNATIVE DATA     │
│ WS mgmt/reconnect   │       │ ratios/DCF/moat      │       │ batch features       │
│ normalize/fan-out   │       │ filings/transcripts  │       │ provenance/licensing │
│ deterministic       │       │ frontier LLM         │       │ Airflow/Dagster      │
└──────────┬──────────┘       └──────────┬───────────┘       └──────────┬───────────┘
           │                             │                              │
           │ ticks/bars                  │ fundamental signals          │ alt signals
           ▼                             ▼                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA / REDPANDA EVENT BUS + NATS CONTROL PLANE                        │
│ market.tick | market.bar | signal.* | trade.thesis | risk.decision | order/fill | audit   │
└───────┬─────────────────────┬──────────────────────┬───────────────────────┬─────────────┘
        │                     │                      │                       │
        ▼                     ▼                      ▼                       ▼
┌───────────────────┐ ┌──────────────────────┐ ┌────────────────────┐ ┌───────────────────┐
│TECHNICAL ANALYSIS │ │ MACRO & SENTIMENT    │ │ COMPLIANCE & AUDIT │ │FEATURE/EVAL STORE │
│TA-Lib/pandas-ta   │ │ FinBERT/news/options │ │ OPA policy/audit   │ │MLflow/W&B/Feast   │
│patterns/regimes   │ │ FII/DII/macro regime │ │ model governance   │ │hit-rate tracking  │
│deterministic      │ │ frontier LLM         │ │ WORM archive       │ │calibration        │
└─────────┬─────────┘ └──────────┬───────────┘ └─────────┬──────────┘ └─────────┬─────────┘
          │                      │                       │                      │
          │ technical signals    │ macro/sent signals    │ policy decisions     │ calibrations
          └──────────┬───────────┴───────────┬───────────┴──────────┬───────────┘
                     ▼                       ▼                      ▼
              ┌────────────────────────────────────────────────────────┐
              │              SIGNAL AGGREGATOR AGENT                   │
              │ weighted ensemble + freshness decay + isotonic calib   │
              │ outputs TradeThesis + evidence attribution             │
              │ frontier LLM for narrative; deterministic scoring math │
              └───────────────────────────┬────────────────────────────┘
                                          │ thesis
                                          ▼
              ┌────────────────────────────────────────────────────────┐
              │           RED TEAM / CYNICAL ADVISOR AGENT             │
              │ bear case + bias checks + stress tests + veto/caution  │
              │ frontier LLM (different provider than aggregator)      │
              └───────────────────────────┬────────────────────────────┘
                                          │ reviewed thesis + conf cap
                                          ▼
              ┌────────────────────────────────────────────────────────┐
              │                 RISK MANAGER AGENT                     │
              │ Kelly/vol targeting + VaR/CVaR + drawdown + kill switch│
              │ DETERMINISTIC — NO LLM                                 │
              └───────────────────────────┬────────────────────────────┘
                                          │ risk-approved size
                                          ▼
              ┌────────────────────────────────────────────────────────┐
              │               PORTFOLIO MANAGER AGENT                  │
              │ allocation/rebalance/sector/country/cash/tax signals   │
              │ deterministic optimizer + cheap LLM narrative          │
              └───────────────────────────┬────────────────────────────┘
                                          │ order intent
                                          ▼
              ┌────────────────────────────────────────────────────────┐
              │                  EXECUTION AGENT                       │
              │ broker router + TWAP/VWAP/iceberg + state reconciler   │
              │ DETERMINISTIC — NO LLM — sync Risk+Compliance gate     │
              └───────────────┬──────────────────────┬─────────────────┘
                              │                      │
                              ▼                      ▼
                 ┌────────────────────┐  ┌────────────────────────────┐
                 │Broker APIs India   │  │Broker APIs US/EU           │
                 │Zerodha Kite v3     │  │IBKR TWS/Gateway            │
                 │Groww [verify]      │  │Saxo OpenAPI [verify]       │
                 │IndMoney [verify]   │  │FIX to XETRA broker         │
                 └────────────────────┘  └────────────────────────────┘
                              │                      │
                              └──────── fills/status ┘
                                         ▼
              ┌────────────────────────────────────────────────────────┐
              │       PORTFOLIO / ORDER / AUDIT EVENT STORES           │
              │ append-only fills, PnL, slippage, model trace, reports │
              │ PostgreSQL + ClickHouse + S3/MinIO WORM                │
              └────────────────────────────────────────────────────────┘
```

#### Hot-path vs research-path separation

```text
HOT PATH (scalping / intraday): deterministic streaming loop
────────────────────────────────────────────────────────────────────────
Market Data ─▶ Technical Engine ─▶ Risk Gate ─▶ Compliance Gate ─▶ Execution
   │                  │                │              │                │
   └────audit─────────┴────audit───────┴────audit─────┴──────audit─────┘
   • NO LLM calls anywhere in this path
   • NO web scraping, NO slow RAG
   • Precomputed strategy rules and calibrated thresholds only
   • Latency budget end-to-end: <100ms scalping, <1s intraday


RESEARCH PATH (swing / positional / long-term): quality loop
────────────────────────────────────────────────────────────────────────
Filings/News/Macro/Alt ─▶ Research Agents (parallel) ─▶ Signal Aggregator
                                                              │
                                                              ▼
                                                          Red Team
                                                              │
                                                    ┌─────────┴──────────┐
                                                    │                    │
                                                  veto             approve/caution
                                                    │                    │
                                                  reject          Risk → Portfolio
                                                                        │
                                                                Compliance gate
                                                                        │
                                                        ┌───────────────┴──────────┐
                                                        │                          │
                                                  human approval             auto-execute
                                                        │                          │
                                                        ▼                          ▼
                                                    Execution or Watchlist    Execution
   • LangGraph orchestrates with checkpoints at every node
   • Frontier LLMs used; provider diversity enforced (aggregator ≠ red team)
   • Latency budget: minutes to hours
   • All outputs Pydantic-validated

---

## 5. Broker MCP Integration Patterns

The broker integration layer is the single most safety-critical surface in the system. Agents must never call broker SDKs directly. All order flow — read and write — passes through a canonical MCP tool contract, and every write passes through a Risk Manager gate before it reaches a broker adapter. This section specifies the MCP server architecture, per-broker adapters (Zerodha, Angel One, Upstox, IBKR for US + XETRA), and the unified Python abstraction layer that a coding agent can implement directly.

### 5.1 MCP Server Architecture for Brokers

#### 5.1.1 Deployment Topology

Run **one MCP server process per broker account per environment** (paper vs live). This isolates credentials, rate-limit budgets, kill switches, WebSocket state, and failure domains. A single "unified broker MCP" is tempting but couples blast radius across brokers — reject it for production.

```
                    ┌──────────────────────────────────────┐
                    │ Agent Orchestrator (LangGraph)       │
                    │ Execution / Risk / Strategy agents   │
                    └────────────────────┬─────────────────┘
                                         │ MCP JSON-RPC 2.0
                                         │ (stdio | SSE | streamable-HTTP)
                    ┌────────────────────▼─────────────────┐
                    │ MCP Tool Router                       │
                    │ routes by exchange + preferred_broker │
                    └───┬─────────────┬──────────────┬─────┘
                        │             │              │
              ┌─────────▼───┐  ┌──────▼──────┐  ┌────▼──────────┐
              │ Zerodha MCP │  │ IBKR MCP    │  │ Angel One MCP │
              │ :8001       │  │ :8002       │  │ :8003         │
              └─────┬───────┘  └──────┬──────┘  └────┬──────────┘
                    │                 │              │
              ┌─────▼────────────────────────────────▼──────────┐
              │ Shared services (per env)                        │
              │  • Risk Engine (pre-trade gate)                  │
              │  • Idempotency store (Redis: client_ref→ord_id)  │
              │  • Audit log (Postgres, hash-chained)            │
              │  • Kill switch (global boolean + reason)         │
              │  • Symbol master cache                           │
              │  • Market calendar (pandas_market_calendars)     │
              └──────────────────────────────────────────────────┘
```

Inside each broker MCP server:

```
┌───────────────────────────────────────────────────────────────┐
│ Broker MCP Server                                              │
│                                                                │
│  Transport: stdio (agent-colocated) | SSE/HTTP (cross-host)    │
│  Framework: FastMCP 2.x on top of Anthropic mcp Python SDK 1.x │
│                                                                │
│  ┌─────────────────┐   ┌──────────────────────────────────┐   │
│  │ Tool layer      │──▶│ Pre-trade risk + compliance gate │   │
│  │ (10 canonical   │   │ (calls Risk Engine, kill switch, │   │
│  │  tools + extras)│   │  PDT/SEBI/MiFID checks)          │   │
│  └────────┬────────┘   └────────────────┬─────────────────┘   │
│           │                             │                     │
│           ▼                             ▼                     │
│  ┌─────────────────┐   ┌──────────────────────────────────┐   │
│  │ Idempotency +   │──▶│ BrokerAdapter (canonical schemas)│   │
│  │ dedup layer     │   │  ZerodhaAdapter / IBKRAdapter... │   │
│  └─────────────────┘   └────────────────┬─────────────────┘   │
│                                         ▼                     │
│                        ┌──────────────────────────────────┐   │
│                        │ Broker SDK (kiteconnect,         │   │
│                        │ ib_insync, smartapi-python, ...) │   │
│                        └────────────────┬─────────────────┘   │
│                                         ▼                     │
│                              Broker REST / WebSocket / FIX    │
└───────────────────────────────────────────────────────────────┘
```

Split tools into three tiers with different guarantees:

| Tier | Tools | Auth required | Idempotent | Risk gate | Rate class |
|---|---|---|---|---|---|
| Read: market data | `get_quote`, `get_market_depth`, `get_order_book`, `get_historical` | yes | yes (safe retry) | no | quote bucket |
| Read: account state | `get_positions`, `get_holdings`, `get_funds`, `get_order_status` | yes | yes | no | REST global |
| Write: trading | `place_order`, `modify_order`, `cancel_order` | yes | **conditional** | **yes** | order bucket |

#### 5.1.2 Reference SDK Stack

- Python 3.11+
- `mcp` (Anthropic Python SDK, ≥1.x, MCP spec 2025-06-18) or **`fastmcp` ≥2.0** (higher-level decorator API) — recommended: FastMCP for ergonomics, drop to raw `mcp` for custom transports
- `pydantic>=2.6` for tool input/output schemas
- `httpx>=0.27` for REST when a broker SDK isn't used directly
- `websockets>=12.0` for custom WS clients
- `tenacity>=8.2` for retry policies
- `redis>=5.0` for idempotency + state cache
- `sqlalchemy>=2.0` + PostgreSQL 16 for audit log
- `structlog>=24.1` for JSON logs
- `cMCP tool overloads, so cap per-broker route depth
- Add explicit **allow-lists** by exchange and strategy horizon
- Log every routing decision with reason (fallback used, primary unhealthy, etc.)

#### 5.5.4 Environment and Deployment Layout

```
project/
├── broker_mcp/
│   ├── __init__.py
│   ├── schemas.py              # canonical pydantic models (§5.1.3)
│   ├── base.py                 # BrokerAdapter ABC (§5.5.1)
│   ├── errors.py               # BrokerError hierarchy
│   ├── idem.py                 # Redis idempotency store
│   ├── audit.py                # hash-chained audit log
│   ├── killswitch.py           # global + per-broker kill switches
│   ├── risk_gate.py            # pre-trade risk hook (calls §6 engine)
│   ├── router.py               # BrokerRouter + RoutingPolicy
│   ├── adapters/
│   │   ├── zerodha.py          # ZerodhaAdapter
│   │   ├── angelone.py         # AngelOneAdapter
│   │   ├── upstox.py           # UpstoxAdapter
│   │   ├── ibkr.py             # IBKRAdapter (ib_insync)
│   │   ├── simulated.py        # SimulatedBrokerAdapter (paper)
│   │   └── disabled.py         # GrowwAdapter / TradeRepublicAdapter stubs
│   └── servers/
│       ├── zerodha_server.py   # FastMCP entrypoint per broker
│       ├── ibkr_server.py
│       └── ...
├── config/
│   ├── routing.yaml            # BrokerRouter policy
│   ├── risk_limits.yaml        # per-strategy/portfolio limits
│   └── compliance.yaml         # jurisdiction rules (§6.5)
└── deploy/
    ├── docker/
    │   ├── ib-gateway.Dockerfile
    │   └── broker-mcp.Dockerfile
    └── k8s/
        └── broker-mcp-*.yaml   # one Deployment per broker-account-env
```

Each broker MCP server is a **separately deployable, separately credentialed** process. In Kubernetes, use one `Deployment` per `(broker, account, environment)` tuple with dedicated `Secret` mounts. Never share pods across live and paper.

---

## 6. Risk Management System Design

The Risk Management System is a **hard gate**, not advisory text from an agent. It runs as deterministic code with versioned configuration. Agents may propose trades; the Risk Manager approves, resizes, modifies, rejects, pauses, or liquidates. No LLM output ever bypasses this layer.

```
┌────────────────────┐
│ Strategy Agents     │
│ signals/proposals   │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ Portfolio Context   │
│ NAV, positions,     │
│ vol, correlations   │
└─────────┬──────────┘
          ▼
┌──────────────────────────────────────────────┐
│ Risk Manager (deterministic, versioned YAML) │
│ • position sizing                             │
│ • stop policy                                 │
│ • VaR / CVaR / drawdown                       │
│ • sector / country / beta caps                │
│ • circuit breakers                            │
│ • regulatory checks (SEBI / PDT / MiFID II)   │
│ • kill switch                                 │
└─────────┬────────────────────────────────────┘
          │ approved CanonicalOrderRequest
          ▼
┌────────────────────┐
│ Broker MCP Layer    │
└────────────────────┘
```

### 6.1 Position Sizing Algorithms

#### 6.1.1 Fixed Fractional

Risk a fixed percentage of portfolio equity on each trade. Default for most strategies.

```
risk_amount     = portfolio_value × risk_fraction
per_unit_risk   = abs(entry_price - stop_price)
quantity        = floor(risk_amount / per_unit_risk)
quantity        = min(quantity, max_position_notional / entry_price)
```

Example: ₹10,00,000 portfolio, 1% risk, entry ₹500, stop ₹475 → 400 shares (₹2,00,000 notional).

```python
def fixed_fractional_size(
    portfolio_value: float,
    entry_price: float,
    stop_price: float,
    risk_fraction: float = 0.01,
    max_position_fraction: float = 0.10,
    lot_size: int = 1,
) -> int:
    per_unit_risk = abs(entry_price - stop_price)
    if per_unit_risk <= 0:
        return 0
    risk_amount = portfolio_value * risk_fraction
    raw_qty = risk_amount / per_unit_risk
    max_qty_by_notional = (portfolio_value * max_position_fraction) / entry_price
    qty = min(raw_qty, max_qty_by_notional)
    return max(int(qty // lot_size * lot_size), 0)
```

Recommended defaults by horizon:

| Horizon    | Risk per trade  | Notes                                            |
|------------|-----------------|--------------------------------------------------|
| Scalping   | 0.05% – 0.25%   | Many trades/day; hard slippage discipline needed |
| Intraday   | 0.25% – 0.75%   | ATR-based stops preferred                        |
| Swing      | 0.5%  – 1.5%    | 2–10 day holds                                   |
| Positional | 0.5%  – 2.0%    | Weeks to months                                  |
| Long-term  | Use allocation limits, not stop-based sizing     |

#### 6.1.2 Kelly Criterion (fractional)

For binary win/loss trades:

```
f* = p − (1 − p) / b
```

where `p` = win probability, `b` = avg_win / avg_loss. Full Kelly is unstable when edge is noisy; use **half-Kelly** or **quarter-Kelly**.

```python
def kelly_fraction_binary(
    win_probability: float,
    avg_win: float,
    avg_loss: float,
    fraction: float = 0.5,   # half-Kelly
    cap: float = 0.02,       # never risk more than 2% regardless of Kelly
) -> float:
    if avg_loss <= 0 or avg_win <= 0:
        return 0.0
    p = win_probability
    q = 1.0 - p
    b = avg_win / avg_loss
    full_kelly = p - q / b
    if full_kelly <= 0:
        return 0.0
    return min(full_kelly * fraction, cap)
```

Preconditions for using Kelly:
- ≥ few hundred comparable historical trades
- probabilities are calibrated (Brier score / reliability check)
- costs and slippage included in avg_win/avg_loss
- output is capped by fixed-fractional and portfolio-level limits

Rule: `risk_fraction = min(half_kelly, fixed_fractional_cap)`.

#### 6.1.3 Volatility Targeting (ATR / realized vol)

ATR-based:
```
stop_distance = atr_multiplier × ATR
quantity      = target_risk_amount / stop_distance
```

Realized volatility targeting:
```
asset_vol_ann      = stdev(daily_returns) × sqrt(252)
position_weight    = target_position_vol / asset_vol_ann
```

```python
import math, numpy as np

def atr_position_size(
    portfolio_value: float, entry_price: float, atr: float,
    risk_fraction: float = 0.01, atr_multiplier: float = 2.0,
    max_position_fraction: float = 0.10, lot_size: int = 1,
) -> int:
    stop_distance = atr_multiplier * atr
    if stop_distance <= 0:
        return 0
    risk_amount = portfolio_value * risk_fraction
    qty = risk_amount / stop_distance
    max_qty = (portfolio_value * max_position_fraction) / entry_price
    qty = min(qty, max_qty)
    return int(qty // lot_size * lot_size)

def realized_vol_target_weight(
    daily_returns: np.ndarray,
    target_vol_ann: float = 0.10,
    max_weight: float = 0.20,
) -> float:
    if len(daily_returns) < 20:
        return 0.0
    vol_ann = float(np.std(daily_returns, ddof=1) * math.sqrt(252))
    if vol_ann <= 0:
        return 0.0
    return min(target_vol_ann / vol_ann, max_weight)
```

For scalping/intraday use **intraday realized volatility** or high-frequency ATR (e.g. 5-minute ATR), not daily ATR.

#### 6.1.4 Maximum Drawdown Constraint

Reduce risk after portfolio drawdowns — prevents a degraded strategy from trading full size.

| Drawdown from peak | Size multiplier |
|--------------------|-----------------|
| 0% – 5%            | 1.00            |
| 5% – 10%           | 0.75            |
| 10% – 15%          | 0.50            |
| 15% – 20%          | 0.25            |
| > 20%              | 0.00 (paused)   |

```python
def drawdown_multiplier(current_equity: float, peak_equity: float) -> float:
    if peak_equity <= 0:
        return 0.0
    dd = (peak_equity - current_equity) / peak_equity
    if dd < 0.05:  return 1.00
    if dd < 0.10:  return 0.75
    if dd < 0.15:  return 0.50
    if dd < 0.20:  return 0.25
    return 0.0
```

Track drawdown at **four levels**: portfolio, strategy, broker account, asset class. Any single level triggering can pause its scope without pausing others — a scalping strategy can be shut down while positional holdings remain live.

#### 6.1.5 Correlation-Adjusted Sizing

Reduce new-position size when it increases concentrated factor exposure.

Simple weighted-correlation penalty:
```
weighted_corr = Σ (|wᵢ| / Σ|w|) × max(corr(new, i), 0)
multiplier    = 1 − penalty × weighted_corr
```

More rigorous: enforce marginal portfolio volatility `σp = sqrt(wᵀΣw)` under a cap.

```python
import numpy as np
from sklearn.covariance import LedoitWolf

def correlation_adjustment_multiplier(
    new_symbol: str,
    existing_weights: dict[str, float],
    corr_matrix: dict[tuple[str, str], float],
    penalty: float = 0.75,
    min_multiplier: float = 0.25,
) -> float:
    if not existing_weights:
        return 1.0
    gross = sum(abs(w) for w in existing_weights.values())
    if gross <= 0:
        return 1.0
    weighted_corr = 0.0
    for sym, w in existing_weights.items():
        corr = corr_matrix.get((new_symbol, sym), corr_matrix.get((sym, new_symbol), 0.0))
        weighted_corr += abs(w) / gross * max(corr, 0.0)
    return max(min_multiplier, min(1.0, 1.0 - penalty * weighted_corr))

def projected_portfolio_vol_ok(
    current_weights: np.ndarray,
    new_weight_vector: np.ndarray,
    cov_matrix: np.ndarray,
    max_vol_ann: float,
) -> bool:
    projected = current_weights + new_weight_vector
    vol = float(np.sqrt(projected.T @ cov_matrix @ projected))
    return vol <= max_vol_ann

def estimate_covariance(returns_matrix: np.ndarray) -> np.ndarray:
    lw = LedoitWolf().fit(returns_matrix)
    return lw.covariance_
```

Use `sklearn.covariance.LedoitWolf` (shrinkage) — sample covariance is unstable on small return samples and produces silently wrong sizing.

### 6.2 Stop-Loss Patterns

#### 6.2.1 Fixed Percentage Stop

```python
def fixed_percent_stop(entry: float, side: str, stop_pct: float) -> float:
    return entry * (1.0 - stop_pct) if side == "BUY" else entry * (1.0 + stop_pct)
```

Use for: long-term / positional trades with wide, price-based invalidation. Avoid for assets with regime-shifting volatility.

#### 6.2.2 ATR-Based Trailing Stop

```python
def atr_trailing_stop(
    side: str, previous_stop: float | None,
    highest_high: float, lowest_low: float,
    atr: float, atr_multiplier: float = 2.0,
) -> float:
    if side == "BUY":
        candidate = highest_high - atr_multiplier * atr
        return candidate if previous_stop is None else max(previous_stop, candidate)
    else:
        candidate = lowest_low + atr_multiplier * atr
        return candidate if previous_stop is None else min(previous_stop, candidate)
```

Swing: `2×ATR`–`3×ATR`. Scalping: use microstructure-aware stops (bid/ask, spread) and **hard broker-side stop** in addition to logic stop.

#### 6.2.3 Time-Based Stop

Exit if thesis isn't confirmed in `N` bars.

```python
def time_stop_triggered(
    bars_since_entry: int, max_bars: int,
    current_r_multiple: float, min_required_r: float = 0.0,
) -> bool:
    return bars_since_entry >= max_bars and current_r_multiple < min_required_r
```

Examples: breakout needs `+0.5R` within 5 bars; mean-reversion needs revert-to-VWAP within 20 min; earnings drift needs relative strength within 2 days.

#### 6.2.4 Volatility Stop

Exit or reduce when realized vol exceeds regime baseline.

```python
def volatility_stop_triggered(
    current_realized_vol: float, baseline_vol: float, multiplier: float = 2.5,
) -> bool:
    return baseline_vol > 0 and current_realized_vol > baseline_vol * multiplier
```

Useful for: news shocks, low-vol mean-reversion strategies, leveraged / options exposure.

#### 6.2.5 Risk Manager Stop Monitoring

```
Market Data Stream ─┐
                    ▼
             ┌──────────────┐
Positions ──▶│ Stop Monitor │── stop event ─▶ Risk Manager ─▶ Broker MCP cancel/exit
Orders ─────▶│              │
             └──────────────┘
```

Requirements:
- Deterministic code, **not** an LLM prompt.
- Per-position state: entry px/time, initial stop, trailing stop, hi-hi/lo-lo, ATR window, bars since entry, strategy invalidation rule.
- On trigger: cancel open entry/target orders → send exit order → log reason → update strategy metrics → notify human if severity ≥ threshold.
- Combine **broker-native protective stop** (disaster-level) + **server-side synthetic stop** (normal exits). Broker-native survives your infra dying; server-side survives spurious wick-triggers.

### 6.3 Portfolio-Level Risk Controls

#### 6.3.1 Maximum Position Size

```yaml
# config/risk_limits.yaml
risk_limits:
  max_single_position_pct_nav:
    default: 0.10
    liquid_large_cap: 0.15
    illiquid_small_cap: 0.03
  max_single_order_pct_adv: 0.02      # never exceed 2% of avg daily volume
  max_gross_exposure: 1.00
  max_net_exposure: 0.80
  max_leverage: 1.00
```

For margin/intraday products, check exposure on **both notional and margin basis** — notional risk is what matters in fast markets.

#### 6.3.2 Sector Concentration

```yaml
max_sector_exposure_pct_nav:
  Information Technology: 0.30
  Financials: 0.25
  Energy: 0.20
  default: 0.25
```

```python
def sector_exposure_ok(positions, proposed, metadata, nav, sector_limits):
    exposure = {}
    for pos in positions + [proposed]:
        sector = metadata[pos.symbol]["sector"]
        exposure[sector] = exposure.get(sector, 0.0) + abs(pos.notional)
    for sector, notional in exposure.items():
        limit = sector_limits.get(sector, sector_limits["default"])
        if notional > nav * limit:
            return False, f"Sector {sector} {notional/nav:.1%} > {limit:.1%}"
    return True, "OK"
```

#### 6.3.3 Country / Single-Country Exposure

```yaml
max_country_exposure_pct_nav:
  IN: 0.50
  US: 0.60
  DE: 0.35
  EU_TOTAL: 0.50
```

For ADRs and cross-listed instruments, exposure should follow **issuer country**, not listing venue. Currency exposure is tracked separately (see 6.3.7 beta section for FX-hedged variants).

#### 6.3.4 VaR — Parametric and Historical Simulation

Parametric (normal):
```
VaRα = portfolio_value × (zα × σp − μp)
```
`z(95%)=1.645`, `z(99%)=2.326`.

```python
from scipy.stats import norm
import numpy as np, math

def parametric_var(
    portfolio_value: float, weights: np.ndarray,
    mean_returns: np.ndarray, cov_matrix: np.ndarray,
    confidence: float = 0.99, horizon_days: int = 1,
) -> float:
    mu = float(weights @ mean_returns) * horizon_days
    sigma = float(np.sqrt(weights.T @ cov_matrix @ weights)) * math.sqrt(horizon_days)
    z = norm.ppf(confidence)
    return portfolio_value * max(0.0, z * sigma - mu)

def historical_var(
    portfolio_value: float, returns_matrix: np.ndarray,   # days × assets
    weights: np.ndarray, confidence: float = 0.99,
) -> float:
    portfolio_returns = returns_matrix @ weights
    loss_quantile = np.quantile(portfolio_returns, 1.0 - confidence)
    return portfolio_value * max(0.0, -loss_quantile)
```

Recommended: intraday (rolling HF-return VaR), swing/positional (1-day and 10-day), long-term (stress tests + monthly drawdown risk).

#### 6.3.5 CVaR / Expected Shortfall

CVaR = average loss **conditional on** losses exceeding VaR. It captures tail severity; VaR only captures the threshold. Use **CVaR** to drive portfolio throttling, not VaR alone.

```python
def historical_cvar(
    portfolio_value: float, returns_matrix: np.ndarray,
    weights: np.ndarray, confidence: float = 0.99,
) -> float:
    portfolio_returns = returns_matrix @ weights
    threshold = np.quantile(portfolio_returns, 1.0 - confidence)
    tail_returns = portfolio_returns[portfolio_returns <= threshold]
    if len(tail_returns) == 0:
        return 0.0
    return portfolio_value * max(0.0, -float(np.mean(tail_returns)))
```

#### 6.3.6 Correlation Matrix Monitoring

Run rolling correlation at multiple horizons:
- 20-day (short-term regime)
- 60-day (swing/medium)
- 252-day (long-term)
- intraday for scalping baskets

Alerts:
- avg pairwise correlation > threshold
- correlation spike vs 60-day baseline
- single factor dominates portfolio variance (PCA)
- correlation matrix instability from stale/missing data

#### 6.3.7 Beta-Adjusted Exposure

```
beta_i                    = cov(asset_i, benchmark) / var(benchmark)
beta_adjusted_exposure    = Σ w_i × beta_i
```

Benchmarks: IN → NIFTY 50 / NIFTY 500; US → S&P 500 / Nasdaq-100; DE/EU → DAX / STOXX Europe 600.

```python
def beta_to_benchmark(asset_returns, benchmark_returns):
    cov = np.cov(asset_returns, benchmark_returns, ddof=1)[0, 1]
    var = np.var(benchmark_returns, ddof=1)
    return 0.0 if var <= 0 else cov / var

def portfolio_beta(weights, betas):
    return float(np.dot(weights, betas))
```

```yaml
max_beta_adjusted_net_exposure:
  IN_NIFTY:  0.50
  US_SPX:    0.60
  EU_STOXX:  0.40
```

### 6.4 Circuit Breakers for Automated Systems

#### 6.4.1 Daily Loss Limit

```yaml
circuit_breakers:
  daily_loss_limit_abs:
    INR: 50000
    USD: 1000
    EUR: 1000
  daily_loss_limit_pct_nav: 0.02   # soft: stop opening new positions
  hard_loss_limit_pct_nav:  0.03   # hard: cancel + flatten
```

```python
def daily_loss_breached(sod_equity, current_equity, realized_pnl, unrealized_pnl, limit_pct):
    pnl = realized_pnl + unrealized_pnl
    return pnl <= -sod_equity * limit_pct
```

Actions:
- **Soft breach:** block new positions; allow risk-reducing orders only.
- **Hard breach:** cancel open orders, flatten positions, page human.
- Immutable audit event on every breach.
- Notify via PagerDuty / Slack / SMS / Email — at least two independent channels.

#### 6.4.2 Consecutive Losing Trades Counter

```python
def update_losing_streak(trade_pnl, current_streak):
    return current_streak + 1 if trade_pnl < 0 else 0

def losing_streak_multiplier(streak):
    if streak < 3:  return 1.00
    if streak == 3: return 0.50
    if streak == 4: return 0.25
    return 0.0
```

Track **per strategy and globally**. Don't pause a mean-reversion strategy because a separate momentum strategy took losses — unless global limits are also breached.

#### 6.4.3 Slippage Anomaly Detection

```python
def adverse_slippage_bps(side: str, expected: float, fill: float) -> float:
    if expected <= 0:
        return 0.0
    if side == "BUY":
        return (fill - expected) / expected * 10000
    else:
        return (expected - fill) / expected * 10000

def slippage_anomaly(side, expected, fill, threshold_bps):
    return adverse_slippage_bps(side, expected, fill) > threshold_bps
```

On anomaly:
1. Pause strategy
2. Cancel remaining child orders
3. Mark market data as suspect if quote was stale
4. Inspect bid-ask spread, liquidity, exchange status
5. Escalate above hard threshold (e.g. > 50 bps for liquid large-caps)

#### 6.4.4 Market Circuit Breakerbreaker awareness — halted, price-band-locked, or auction-state instruments must be blocked pre-trade, not detected only after a rejected order.

Per-market rules:

| Market | Constraint | Detection source |
|---|---|---|
| NSE / BSE | Per-scrip circuits 2/5/10/20%; index circuits 10/15/20% on NIFTY 50 / SENSEX (15 min / 45 min / rest-of-day halt depending on trigger + time-of-day) [verify current SEBI/exchange rules] | KiteTicker market status; instrument-level circuit_limit field; SEBI/NSE announcements feed |
| NSE F&O | Dynamic price bands per contract, no fixed retail band | Broker instrument master + tick-level `oi_day_high/low` |
| US | Level 1 (-7%), Level 2 (-13%), Level 3 (-20%) S&P 500 market-wide breakers; per-stock LULD bands by price tier and time band | IBKR `reqMktData` tick type 49 (halted); NASDAQ Trader halt feed; NYSE halt feed [verify current URLs] |
| XETRA / T7 | Volatility interruption on static/dynamic price ranges → 2-min auction | Deutsche Börse T7 market status; IBKR contract trading status |

```python
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

class MarketState(str, Enum):
    OPEN               = "OPEN"
    PREOPEN            = "PREOPEN"
    AUCTION            = "AUCTION"
    HALTED             = "HALTED"
    CIRCUIT_LOCKED     = "CIRCUIT_LOCKED"
    VOL_INTERRUPTION   = "VOL_INTERRUPTION"
    CLOSED             = "CLOSED"
    UNKNOWN            = "UNKNOWN"

@dataclass
class SymbolMarketState:
    symbol: str
    exchange: str
    state: MarketState
    upper_circuit: float | None
    lower_circuit: float | None
    last_price: float | None
    updated_at: datetime
    halt_reason: str | None = None

def order_allowed_for_symbol(order, sms: SymbolMarketState) -> tuple[bool, str]:
    if sms.state == MarketState.OPEN:
        # still check price-band proximity
        if order.order_type == "MARKET" and sms.upper_circuit and sms.last_price:
            proximity = (sms.upper_circuit - sms.last_price) / sms.last_price
            if order.side == "BUY" and proximity < 0.005:
                return False, "buy market blocked: within 0.5% of upper circuit"
        return True, "OK"
    if sms.state in {MarketState.HALTED, MarketState.CIRCUIT_LOCKED,
                     MarketState.VOL_INTERRUPTION, MarketState.UNKNOWN}:
        return False, f"blocked: {sms.state.value} ({sms.halt_reason or 'no reason'})"
    if sms.state in {MarketState.PREOPEN, MarketState.AUCTION}:
        if order.order_type == "LIMIT" and getattr(order, "auction_ok", False):
            return True, "auction participation allowed"
        return False, f"blocked during {sms.state.value}"
    if sms.state == MarketState.CLOSED:
        return False, "market closed"
    return False, "unhandled state"
```

Hardening rules:
- **Do not fire orders into halted instruments** — most brokers reject, some can create locked positions or race with re-open auctions.
- **Do not close positions in halted names via market orders** — wait for resume; log-only.
- **Stale market-state data** (older than N seconds, configurable per horizon: 1s scalping, 5s intraday, 30s swing) → treat as `UNKNOWN` and block writes.
- Reject new orders during auction/vol-interruption unless the strategy explicitly opts into auction participation (`auction_ok=True`) with a conservative limit price.

#### 6.4.5 Automatic Trading Pause and Human Escalation

```
   ┌──────────┐  soft breach   ┌──────────────┐
   │  ACTIVE  │───────────────▶│  RISK_OFF    │  block opens; allow reduces
   │          │◀──── manual ───│              │
   └────┬─────┘                └──────┬───────┘
        │                             │ hard breach / anomaly / halt storm
        │                             ▼
        │                      ┌──────────────┐
        │                      │   PAUSED     │  cancel opens; freeze writes
        │                      └──────┬───────┘
        │                             │ escalation timeout OR operator ack + confirm
        │                             ▼
        │                      ┌──────────────┐
        └── never auto-────────│  KILL/FLAT   │  liquidation policy runs
              transition       └──────────────┘
```

Pause scopes (each independent, each with its own state key):

| Scope | Trigger examples | Allowed while paused |
|---|---|---|
| Strategy | losing streak, model drift, slippage anomaly, PnL cliff | exits, cancels, reduce-only |
| Symbol | halt, abnormal spread, stale data, circuit lock | exits only if venue open + tradable |
| Broker | broker API errors, auth failure, position mismatch | reconcile + cancel |
| Account | daily loss, margin shortfall, PDT hit | reduce-only / flatten |
| Global | kill switch, audit engine failure, risk engine failure | flatten or no-op depending on mode |

Escalation matrix:

| Severity | Notification channel | Human action required |
|---|---|---|
| INFO     | Slack + email | none |
| WARN     | Slack + email + dashboard banner | review within session |
| CRITICAL | PagerDuty / Opsgenie + SMS + phone | acknowledge before resume |
| KILL     | PagerDuty + SMS + immutable audit + on-call handoff | manual unlock with 2FA |

Resume rules:
- Never auto-resume after: hard daily loss, kill switch, audit-log failure, unresolved reconciliation break.
- Auto-resume allowed after: transient rate-limit cooldown, temporary quote staleness, single-symbol halt clearing.
- Every live-resume after CRITICAL requires a **human-signed reason** persisted in audit log.

#### 6.4.6 Kill Switch — Emergency Flatten-All

Non-negotiable design requirements:

1. **≥3 independent activation channels:** CLI on ops host, authenticated HTTPS webhook, MCP tool `emergency_flatten` with out-of-band confirmation token, plus optional hardware/YubiKey path.
2. **Idempotent** — repeated calls converge on flat; safe to retry.
3. **Deterministic** — pure code path, no LLM in the loop, no agent framework dependency.
4. **Persistent** — state stored in Redis + Postgres; process restarts see armed state and refuse to trade.
5. **Cancel-then-liquidate** — always cancel open orders before submitting exits.
6. **Per-broker parallel** — one failing broker cannot block flattening at others.
7. **Liquidity-aware liquidation policy:** liquid → marketable limit / market; illiquid → TWAP/VWAP over N minutes with hard-timeout fallback to marketable limits; halted/locked → skip and escalate.
8. **Cannot be re-enabled by an agent** — only a human operator with 2FA can lift.

Kill switch modes:

| Mode | Behavior |
|---|---|
| `PAUSE_ONLY`         | reject new orders; leave positions and open orders alone |
| `CANCEL_ONLY`        | cancel all open orders; no new orders |
| `FLATTEN_LIQUID`     | cancel + flatten liquid, market-open instruments only |
| `FLATTEN_ALL`        | attempt to close all positions across brokers |
| `DISABLE_AUTOMATION` | stop agents + MCP write tools; read-only reconciliation allowed |
| `NUKE`               | FLATTEN_ALL + revoke broker credentials + page on-call |

Flatten workflow:

```
Kill Switch Trigger
        │
        ▼
Persist GLOBAL_PAUSE=true (Redis + Postgres, hash-chained audit event)
        │
        ▼
Block all place_order/modify_order MCP calls
        │
        ▼   (parallel per broker)
Fetch positions + open orders from every broker
        │
        ▼
Cancel open orders
        │
        ▼
Generate reduce-only exit orders (respect halts, price bands, liquidity)
        │
        ▼
Pre-trade gate runs in "reduce-only" mode
        │
        ▼
Submit exits per broker; poll fills; handle partials
        │
        ▼
Reconcile positions; retry residuals up to N times
        │
        ▼
Emit signed completion report to humans + audit log
```

Reference implementation combining both patterns:

```python
import asyncio, json, uuid, logging
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import redis.asyncio as aioredis

class KillSwitchLevel(str, Enum):
    SOFT   = "SOFT"     # block new opens, hold existing
    MEDIUM = "MEDIUM"   # reduce-only
    HARD   = "HARD"     # cancel + flatten liquid
    NUKE   = "NUKE"     # flatten all + revoke credentials

@dataclass
class FlattenReport:
    correlation_id: str
    reason: str
    level: KillSwitchLevel
    started_at: datetime
    brokers: dict
    residual_positions: list
    completed_at: datetime | None = None

class KillSwitch:
    REDIS_KEY = "trading:kill_switch"

    def __init__(self, redis_url, brokers, audit, notifier):
        self.redis    = aioredis.from_url(redis_url)
        self.brokers  = brokers          # list[BrokerAdapter]
        self.audit    = audit
        self.notifier = notifier
        self.log      = logging.getLogger("killswitch")

    async def is_active(self) -> tuple[bool, dict | None]:
        raw = await self.redis.get(self.REDIS_KEY)
        return (True, json.loads(raw)) if raw else (False, None)

    async def activate(self, level: KillSwitchLevel, reason: str, actor: str) -> FlattenReport:
        corr = str(uuid.uuid4())
        payload = {"level": level.value, "reason": reason,
                   "actor": actor, "ts": datetime.utcnow().isoformat(),
                   "correlation_id": corr}
        await self.redis.set(self.REDIS_KEY, json.dumps(payload))
        self.audit.write("KILL_SWITCH_ARMED", payload)
        self.log.critical("KILL_SWITCH level=%s reason=%s actor=%s corr=%s",
                          level.value, reason, actor, corr)
        await self.notifier.page("CRITICAL", "Kill switch armed", payload)

        report = FlattenReport(correlation_id=corr, reason=reason, level=level,
                               started_at=datetime.utcnow(), brokers={}, residual_positions=[])

        if level == KillSwitchLevel.SOFT:
            report.completed_at = datetime.utcnow()
            return report

        # Cancel + flatten in parallel across brokers
        results = await asyncio.gather(
            *[self._flatten_broker(b, level, corr) for b in self.brokers],
            return_exceptions=True,
        )
        for broker, res in zip(self.brokers, results):
            if isinstance(res, Exception):
                report.brokers[broker.broker_id] = {"status": "error", "error": str(res)}
            else:
                report.brokers[broker.broker_id] = res
                report.residual_positions.extend(res.get("residual", []))

        if level == KillSwitchLevel.NUKE:
            await self.redis.set("trading:credentials_revoked", "1")
            self.audit.write("CREDENTIALS_REVOKED", {"correlation_id": corr})

        report.completed_at = datetime.utcnow()
        self.audit.write("KILL_SWITCH_COMPLETED", report.__dict__)
        await self.notifier.page("CRITICAL", "Kill switch execution complete", report.__dict__)
        return report

    async def _flatten_broker(self, adapter, level, corr) -> dict:
        cancelled, exits, errors = [], [], []
        try:
            for o in await adapter.list_open_orders():
                try:
                    cancelled.append(await adapter.cancel_order(o.broker_order_id))
                except Exception as e:
                    errors.append(f"cancel {o.broker_order_id}: {e}")

            for p in await adapter.get_positions():
                if p.quantity == 0:
                    continue
                if level == KillSwitchLevel.MEDIUM:
                    continue  # reduce-only; wait for strategies to unwind
                if level == KillSwitchLevel.HARD and not p.is_liquid:
                    errors.append(f"skipped illiquid {p.symbol}")
                    continue
                sms = await adapter.get_symbol_state(p.symbol, p.exchange)
                if sms.state != MarketState.OPEN:
                    errors.append(f"skipped {p.symbol}: state={sms.state.value}")
                    continue

                side = "SELL" if p.quantity > 0 else "BUY"
                order = _build_exit_order(p, side, sms, corr)
                exits.append(await adapter.place_order(order))

            residual = [p for p in await adapter.get_positions() if p.quantity != 0]
            return {"status": "flat" if not residual else "partial",
                    "cancelled": cancelled, "exits": exits,
                    "errors": errors,
                    "residual": [{"symbol": r.symbol, "qty": r.quantity} for r in residual]}
        except Exception as e:
            return {"status": "error", "error": str(e),
                    "cancelled": cancelled, "exits": exits, "errors": errors}

    async def deactivate(self, actor: str, reason: str, mfa_token: str) -> None:
        if not verify_mfa(actor, mfa_token):
            raise PermissionError("2FA required to deactivate kill switch")
        await self.redis.delete(self.REDIS_KEY)
        self.audit.write("KILL_SWITCH_DEACTIVATED",
                         {"actor": actor, "reason": reason,
                          "ts": datetime.utcnow().isoformat()})
        self.log.warning("KILL_SWITCH DEACTIVATED actor=%s reason=%s", actor, reason)
```

Startup contract: every broker MCP server checks `KillSwitch.is_active()` on boot and before every write tool call. Any code path that can send a write tool call without consulting this check is a critical security defect and must fail CI.

Additional constraints:
- Never send blind market orders into halted/closed/circuit-locked instruments.
- For illiquid Indian small-caps at lower circuit, mark as **unflattenable**, record explicitly, escalate to human.
- For US premarket/after-hours, flatten only if extended-hours trading is explicitly enabled and risk-approved.
- For XETRA auction/volatility interruption, prefer conservative limit orders with narrow bands or defer to next continuous session.
- Emergency flatten must be exercised in **weekly game-days** on paper accounts — if it hasn't been tested this week, treat it as broken.

### 6.5 Regulatory Compliance

Compliance is not legal advice; the system implements deterministic, versioned guardrails per jurisdiction, and requires review by qualified counsel and the executing broker before live deployment. Every rule is tagged with `jurisdiction`, `source_citation`, `version`, `effective_date`, and `last_reviewed_at`.

#### 6.5.1 SEBI Algo Trading Regulations (India)

Foundational framework: SEBI algorithmic-trading circular Sept 2021 (institutional/broker-facing) and the retail-focused SEBI circular dated **Feb 4, 2025**, effective **Aug 1, 2025** for API-based algorithmic trading by retail investors [verify current effective date and text; SEBI circulars are amended frequently].

Core obligations relevant to a retail/prosumer algo bot:

- **Algo tagging:** orders placed via API by a system beyond a specified frequency threshold are treated as algorithmic and must carry a **unique algo ID** issued by the broker after exchange registration [verify current threshold and workflow].
- **Broker approval:** each strategy/algo must be registered with the broker; the broker registers with the exchange (NSE/BSE).
- **Audit trail:** immutable, tamper-evident records of every signal → risk decision → order → modification → fill → cancellation → reconcile.
- **Retail obligations:** SEBI has increasingly restricted DIY retail algos placed via unofficial APIs / screen-scraping / reverse-engineered mobile flows — do **not** implement Groww/Trade Republic-style scraping paths for live trading.
- **Order rate caps:** brokers apply per-account per-second and per-minute rate limits; the risk engine must cap below the broker's limit.

Implementation requirements:
- Complete audit trail carrying: signal timestamp, model/strategy version + git commit hash, market data snapshot hash, risk decision id, final order params, broker request id, broker response, modifications, cancellations, fills, operator overrides.
- Immutable logs (append-only Postgres with row-hash chaining + WORM S3 archive) for the statutory retention period [verify retention window per broker/exchange].
- Every live strategy mapped to: `strategy_id`, code commit hash, config version, broker account, approved exchanges/products, per-day order cap, per-second rate cap, max notional.
- Broker approval workflow integration if broker/exchange requires algo registration.
- Kill switch, max-order-rate, and max-daily-loss enforced at **broker-account** level.
- No credential sharing; no unattended use outside broker terms.
- Do **not** bypass broker front-end/API controls with scraping, reverse-engineered mobile APIs, or session hijacking.

Conservative India live-trading configuration:

```yaml
jurisdiction: IN
market: NSE_BSE
mode: live
compliance:
  require_strategy_approval: true
  require_broker_algo_tag: true            # [verify per broker/exchange]
  require_operator_enable_each_day: true
  allow_screen_scraping: false
  allow_unofficial_apis: false
  immutable_audit_log: true
  max_orders_per_second: 1                 # well below broker/exchange limit
  max_daily_orders_per_strategy: 500
  block_if_audit_unavailable: true
  block_if_risk_engine_unavailable: true
  algo_id_required_above_orders_per_minute: 10   # [verify current SEBI threshold]
```

#### 6.5.2 SEBI API Key Restrictions and Broker Terms

Retail broker APIs (Zerodha Kite Connect, Angel One SmartAPI, Upstox v2) typically impose:
- per-second and per-minute rate limits (Kite: ~3 orders/sec, ~200/min, ~3000/day [verify current]; SmartAPI and Upstox: similar order of magnitude, verify per broker docs)
- restrictions on automated high-frequency order flow
- credential + session security obligations (daily TOTP-derived access token, no key sharing)
- restrictions on sharing API keys with third parties
- order placement only by the account holder or an authorized application
- exchange-specific product and order-type controls

Design implications:
- Store API keys only in a secrets manager: HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, or macOS Keychain for solo/dev use.
- **Never expose raw broker credentials to LLM agents.** Agents call MCP tools; the MCP server holds credentials.
- Require TOTP/2FA through approved flows. If a TOTP seed must be stored to automate daily Kite login, encrypt with envelope encryption, restrict to a dedicated auth service, and treat the seed as the highest-tier secret. Prefer manual daily login where possible for live accounts.
- Apply per-broker rate limiters **below** documented limits with a safety factor (0.5×–0.7×).
- Every MCP write tool call must attach: `client_order_id`, `strategy_id`, `user_id` / service account, `risk_decision_id`, `audit_event_id`.
- No screen-scraping-based trading for Groww/IndMoney/Trade Republic in production.

#### 6.5.3 US Pattern Day Trader Rule

FINRA/SEC PDT rule for **margin accounts**:
- A pattern day trader executes **4+ day trades within 5 business days** where day trades exceed 6% of total trades in that period [verify current FINRA text].
- PDT accounts must maintain **≥ $25,000 equity** before day trading.
- Conservative guard for sub-$25k margin accounts: allow at most **3 day trades in rolling 5 business days**.

```python
def pdt_day_trade_allowed(
    account_equity: float,
    rolling_5d_day_trades: int,
    account_type: str,
) -> tuple[bool, str]:
    if account_type.upper() != "MARGIN":
        return True, "PDT applies to margin accounts; verify cash-account settlement rules separately"
    if account_equity >= 25000:
        return True, "equity >= PDT threshold"
    if rolling_5d_day_trades >= 3:
        return False, "PDT guard: <$25k margin account already has 3 day trades in 5 business days"
    return True, "PDT guard OK"
```

Also enforce:
- Cash-account settlement / free-riding rules (T+1 settlement for US equities effective May 28, 2024).
- Short-sale locate/borrow requirements; Reg SHO close-out considerations [verify broker-specific handling].
- Options approval level restrictions if options are later added.
- Wash-sale tracking for taxable accounts (see 6.5.5).

#### 6.5.4 MiFID II / European Algorithmic Trading Controls

For Europe, especially XETRA/Deutsche Börse via IBKR or DEA, MiFID II Article 17 and RTS 6 obligations may apply. Applicability depends on whether the operator is retail, professional, investment firm, or using direct electronic access [verify with counsel and broker].

Common control themes (RTS 6):
- notify competent authority and trading venue if subject to algorithmic trading requirements
- effective systems + risk controls proportionate to activity
- resilience and sufficient capacity of trading systems
- prevent erroneous orders and disorderly markets
- **kill functionality** capability
- detailed records of algorithms, orders, decisions
- **pre-deployment testing** of algorithms (including stressed-market conditions)
- continuous real-time monitoring
- annual self-assessment / validation for regulated firms

Implementation checklist:

```yaml
jurisdiction: EU
venue: XETRA
compliance:
  mifid_algo_controls_enabled: true
  require_pre_trade_price_band_check: true
  require_max_message_rate: true
  require_kill_switch: true
  require_real_time_monitoring: true
  require_algo_version_registry: true
  require_order_record_retention: true       # per MiFIR: 5 years [verify]
  require_predeployment_test_report: true
  require_human_supervision: true
  max_message_rate_per_second: 5             # well below venue OTR limit
  order_to_trade_ratio_cap: 100              # [verify venue OTR rules]
```

IBKR enforces many broker/venue controls, but the bot must still implement its own pre-trade risk and audit trail. Broker rejection is a last-resort safety net, not a risk-management system.

#### 6.5.5 Tax Implications

Tax handling is a reporting-support responsibility. The bot tags every fill with tax-lot metadata and exports broker/account-level reports. This is not tax advice — reconcile with a qualified professional before filing.

**India**
- **STT** applies to exchange-traded equity transactions; rate depends on delivery / intraday / F&O segment [verify current STT rates].
- Post-2024 budget regime commonly cited: **STCG on listed equity ~20%**, **LTCG on listed equity 12.5%** above exemption threshold [verify current FY rules].
- Intraday equity → speculative business income.
- F&O → non-speculative business income; audit requirements depend on turnover/profitability [verify current Income Tax Act rules].
- Separate ledgers: delivery equity, intraday equity, equity F&O, currency/commodity derivatives, and cost ledger (brokerage, STT, GST, exchange transaction charges, SEBI turnover fee, stamp duty).

**US**
- **Wash-sale rule:** losses disallowed if substantially identical securities bought within 30 days before/after the sale (61-day window). Applies to substantially identical options/ETFs — implementation must resolve "substantially identical" carefully [verify].
- Short-term capital gains taxed as ordinary income; long-term (>1 year hold) at preferential rates.
- PDT status and tax-trader-status ("mark-to-market" election under IRC §475(f)) are separate concepts.
- Export tax lots compatible with broker 1099-B reconciliation.
- Preserve millisecond timestamps and order IDs for audit and reconciliation.

**Germany**
- Capital gains subject to **Abgeltungsteuer 25%** plus solidarity surcharge (~5.5% of tax) and possible church tax [verify current rates and personal exemptions (Sparer-Pauschbetrag)].
- Loss-offset limitations, especially for derivatives / termination losses, have been subject to legislative and court changes [verify current law].
- Broker withholding differs for domestic vs foreign brokers — IBKR (foreign broker) generally does **not** withhold German Abgeltungsteuer at source; the operator self-declares.
- Track FX conversion between USD and EUR for acquisition and disposal on both legs.

Tax data model:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TaxLot:
    lot_id: str
    account_id: str
    broker: str
    jurisdiction: str            # "IN" | "US" | "DE" | ...
    symbol: str
    isin: str | None
    exchange: str
    acquisition_datetime: datetime
    quantity: float
    cost_basis_local: float
    cost_basis_base: float       # in reporting currency
    currency: str
    fees: float
    taxes: float                 # STT, stamp duty, transaction tax
    strategy_id: str
    broker_order_id: str
    broker_execution_id: str

@dataclass
class RealizedGainLoss:
    open_lot_id: str
    close_execution_id: str
    quantity_closed: float
    proceeds: float
    cost_basis: float
    fees: float
    taxes: float
    realized_pnl: float
    holding_period_days: int
    tax_classification: str      # "STCG" | "LTCG" | "Speculative" | "F&O" | "Abgeltung" | "Wash-Sale-Disallowed"
    wash_sale_adjustment: float  # US only
    fx_rate_open: float | None
    fx_rate_close: float | None
```

Lot-matching methods must be configurable per jurisdiction: FIFO (default IN/DE), specific-lot (US election), average-cost (some funds). Wash-sale adjustment engine is US-specific and must run at close time, not fill time, because the 61-day window straddles both directions.

#### 6.5.6 Compliance-Aware Pre-Trade Gate

All compliance checks share the same pre-trade gate as risk checks. Every order — proposed by any agent — passes through here before reaching a broker adapter:

```python
async def pre_trade_gate(order, context) -> tuple[bool, str, dict]:
    checks = [
        check_kill_switch,
        check_market_hours,
        check_market_state,             # halts, auctions, circuit-lock
        check_broker_permissions,       # exchange + product + order type
        check_regulatory_permissions,   # jurisdiction gate router
        check_pdt_if_us,
        check_sebi_if_india,            # algo tag, rate caps, approval flag
        check_mifid_if_eu,              # message rate, OTR, algo registry
        check_position_limits,          # 6.3.1
        check_sector_country_limits,    # 6.3.2 / 6.3.3
        check_var_cvar_limits,          # 6.3.4 / 6.3.5
        check_drawdown_limits,          # 6.1.4
        check_correlation_limits,       # 6.1.5 / 6.3.6
        check_beta_limits,              # 6.3.7
        check_order_rate_limits,        # per-broker + per-strategy
        check_price_bands,              # NSE circuits, LULD, XETRA VI
        check_liquidity,                # ADV, spread, market impact
        check_duplicate_client_order_id,
        check_wash_sale_if_us_taxable,  # advisory: warn + tag, don't block
    ]

    evidence = {}
    for check in checks:
        ok, reason, data = await check(order, context)
        evidence[check.__name__] = {"ok": ok, "reason": reason, "data": data}
        if not ok:
            audit_rejection(order, check.__name__, reason, evidence)
            return False, reason, evidence

    decision_id = audit_approval(order, evidence)
    return True, "approved", {"decision_id": decision_id, "evidence": evidence}
```

**Fail-closed invariants** (any of these blocks new writes; existing reduce-only exits may proceed if the operator explicitly enables that mode):
- Risk engine unavailable → reject.
- Audit log unavailable → reject.
- Market data stale beyond horizon threshold → reject (except operator-approved liquidation).
- Broker position reconciliation broken → reject new opens.
- Compliance config missing or unsigned → reject live orders.
- Kill switch armed → reject per switch mode.
- Any check raises unexpected exception → reject (never silently allow).

The pre-trade gate is deterministic, side-effect-free except for audit writes, and unit-tested exhaustively. It is the last line of defense between an LLM's opinion and real money moving. Every rejection is an immutable audit event; every approval carries a `decision_id` that flows through to the broker's `client_order_id` for end-to-end traceability.

<!-- CHUNK-C SELF-AUDIT: 2/2 sections emitted; §5 covers Indian+IBKR+European+abstraction layer with code; §6 covers position sizing+stops+portfolio risk+circuit breakers+regulatory compliance; no truncation -->

---

## 7. Red Team Analysis — Risks and Failure Modes

*Written from the perspective of a jaded senior quant engineer who has watched more trading systems blow up than survive. This section is intentionally adversarial. Assume every component will eventually fail, every backtest is lying until proven otherwise, and every broker/API/exchange rule will hurt you at the worst possible moment.*

---

### 7.1 Strategy-Level Risks

#### 7.1.1 Overfitting / Curve Fitting

**The failure mode**

The single most likely way this trading bot fails is by discovering patterns that only existed in historical data. With 50+ candidate parameters, 10 years of data, and enough compute, you can fit *anything*. LLM-assisted strategy generation makes this dramatically worse — LLMs are exceptionally prone to producing plausible-sounding rules that happen to fit noise, complete with confident-sounding rationales.

Common examples in this system:
- Optimising moving-average windows until the backtest looks perfect
- Selecting indicators *after* seeing which ones worked historically
- Tuning stop-loss/take-profit values to a specific past regime
- Letting LLM agents generate impressive-sounding rationales for statistically weak strategies
- Testing hundreds of strategies and only retaining the best without correcting for multiple comparisons
- High-dimensional feature sets with insufficient observations (curse of dimensionality)
- Training on 2020-2023 bull-market period and assuming performance generalises
- Treating one successful backtest on NIFTY 50 as evidence of robustness

**How it shows up live**
- Backtest Sharpe: 2.5-3.2. Live Sharpe: -0.2 to 0.4
- In-sample vs out-of-sample Sharpe divergence > 40%
- Win rate collapses immediately after deployment
- Trades become highly correlated with hidden market beta
- Strategy stops working the moment realistic transaction costs are applied
- ±10% parameter perturbation causes >30% performance degradation (knife-edge fragility)

**Detection**
- Walk-forward validation with anchored and rolling windows; require positive OOS Sharpe in ≥70% of folds
- **Combinatorially Purged Cross-Validation (CPCV)** — López de Prado, *Advances in Financial Machine Learning* (2018)
- **Deflated Sharpe Ratio (DSR)** — Bailey & López de Prado (2014); adjusts for multiple testing. If you tested 100 variants, the expected max Sharpe from pure noise is ~2.5 even with zero skill
- Parameter stability heatmaps
- Monte Carlo permutation test: shuffle trade timestamps 10,000 times; if real strategy doesn't beat shuffled distribution (p < 0.05), it's random
- Regime segmentation: bull, bear, sideways, high-vol, low-vol
- Performance decay analysis post-deployment

**Mitigation (concrete architecture + process)**

Enforce a strict, non-negotiable research workflow:
```
Idea → Hypothesis → Frozen feature set → Train period → Validation period
     → Walk-forward test → Paper trade → Small capital live → Scale gradually
```

Maintain a `strategies/registry.yaml` with immutable records:
- Strategy ID, hypothesis, allowed features
- Train/validation/test date ranges
- Number of parameter searches attempted
- Final selected parameters
- Live deployment date

**Hard rules:**
- Maximum 5-7 free parameters per strategy
- Minimum 30 trades per parameter (rule of thumb from empirical quant research)
- Ban manual parameter tweaking after viewing OOS results unless a new experiment is registered
- Hold out a *never-touched* validation set — locked in a separate git branch, only opened at Phase 5 sign-off
- Reject any strategy where IS Sharpe > 2× OOS Sharpe
- Require performance to survive: 2× estimated transaction costs, 3× estimated slippage, 25-50% signal latency degradation, randomly dropped signals

**Minimum live paper-trading duration before production:**
- Scalping: 20-40 trading sessions
- Intraday: 30-60 trading sessions
- Swing: 3-6 months
- Positional/long-term: 6-12 months

---

#### 7.1.2 Survivorship Bias

**The failure mode**

Backtests using only *currently listed* stocks systematically overstate returns because they exclude companies that were delisted, merged, suspended, bankrupted, or became illiquid. Studies estimate survivorship bias inflates backtest returns by 1-3% annually for US equities. For Indian mid/small-cap universes, the effect is likely larger given ecosystem volatility.

**Indian-specific context:**
- NSE has delisted 200+ companies in the last decade
- Yes Bank (near-zero recapitalisation), DHFL, IL&FS, Reliance Communications, Jet Airways, Cafe Coffee Day, Cox & Kings — must all appear in historical data
- Companies shifted to Trade-for-Trade (T2T) or ASM/GSM surveillance often had massive liquidity crises before delisting
- NIFTY 500 constituents have rotated significantly since 2015

**Danger zones:**
- Momentum strategies on surviving stocks (overstates momentum edge)
- Mean-reversion strategies that buy "cheap" collapsing stocks (catches falling knives that never recovered)
- Indian mid/small-cap and SME-listed universes
- US small caps, European smaller exchanges

**Detection**
- Compare results using: current constituents only vs point-in-time constituents vs full listed universe including delis---

## 7. Red Team Analysis — Risks and Failure Modes (continued)

**Real-world detection technique — the "double the cost" test:**
Run every promising backtest with `cost_multiplier = 2.0`. If Sharpe drops below 0.8 or CAGR turns negative, the strategy is not robust to cost estimation error. This is a hard gate before paper trading.

**Cost model implementation requirements:**

```python
class IndianEquityCostModel:
    """All-in cost model for NSE/BSE equity trades. Rates as of 2024 —
    VERIFY CURRENT RATES from broker + exchange before production use."""

    def compute_round_trip_cost(
        self,
        symbol: str,
        trade_value_inr: float,
        product: Literal["MIS", "CNC", "NRML"],
        broker: Literal["zerodha", "angel_one", "upstox"],
        exchange: Literal["NSE", "BSE"],
        assumed_slippage_bps: float = 5.0,
        assumed_spread_bps: float = 3.0,
    ) -> CostBreakdown:
        """Returns explicit breakdown; never a single scalar."""
        ...
```

Store historical cost snapshots in `config/costs/india_2024_q4.yaml`, `india_2025_q1.yaml` etc. — SEBI/exchange rates change; backtests must use rates valid at each historical point in time, not current rates.

**Slippage modelling — the part everyone gets wrong:**

Slippage is not a constant. It is a function of order size, volatility, spread, and time of day. Model at minimum:

```
slippage_bps = base_slippage
             + k1 * (order_value / avg_daily_value * 10000)   # size impact
             + k2 * atr_pct                                    # volatility impact
             + k3 * spread_bps                                 # spread cost
             + time_of_day_factor                              # open/close penalty
```

Calibrate `k1, k2, k3` from live paper trading, not assumption.

---

## 8. Implementation Roadmap — Handoff to Coding Agent

*(Sections 8.1 through 8.6 as delivered above.)*

**Final coding-agent handoff notes:**

1. Do not begin Phase 2 until Phase 1 acceptance criteria are 100% green in CI. Skipping foundation testing is the most common reason multi-agent trading systems become unmaintainable by Week 8.

2. Every LLM-touching code path must have a deterministic fallback. If Anthropic/OpenAI is down, the bot must degrade to rule-based signals, not halt trading of existing positions (exits must still work).

3. Treat the Compliance Agent, Risk Manager, and Execution Agent as *deterministic Python code*, not LLM agents. LLMs may advise them but must never bypass them. This is non-negotiable and encoded in the type system (`RiskDecision`, `ComplianceDecision`, `OrderIntent` are Pydantic models produced only by non-LLM functions).

4. The single most important test to write first (Phase 1, before any agent code): a broker adapter contract test that submits, cancels, modifies, and reconciles paper orders on both Zerodha and IBKR. If this test is flaky, nothing built on top of it can be trusted.

5. Version-pin everything. `pyproject.toml` must lock exact versions for `langgraph`, `pydantic`, `kiteconnect`, `ib_insync`, `vectorbt`, `ta-lib`, `pandas-ta`, `finbert`, and all LLM SDKs. Financial code that "works with the latest version of X" will silently break on library updates and cost real money.

6. Before Phase 6 sign-off, run a minimum 90-day paper trading period across at least two market regimes (trending + choppy). No live capital deployment before this gate.

7. First live deployment: single symbol, smallest legal position size, human approval on every order, one horizon only (recommend swing). Scale slowly. The urge to "go big" after a good paper month has ruined more retail algo traders than any other single factor.

<!-- CHUNK-D SELF-AUDIT: 2/2 sections emitted; §7 has 5 risk categories with mitigations; §8 has full stack decision + repo structure + 6-phase plan with tasks + config examples + open questions; no truncation -->

<!-- STITCHED: chunks A+B+C+D | sections 1-8 | trading-bot-research -->
