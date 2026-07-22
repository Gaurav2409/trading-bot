# Live Domain Opportunity Audit

**Date:** 2026-07-22
**Scope:** First live iteration of the approved India/US long-only cash-equity Trading OS
**Question:** What Cropster-like opportunities or traps exist across the targeted evidence domains,
and what must change for a nine-day end-to-end live build?

## Executive conclusion

The current design needs a broader opportunity-discovery mesh, not only a price-momentum scanner.
The permanent pattern should be:

```text
broad discovery universe
  -> domain detectors + CoverageReceipts
  -> OpportunityCandidate
  -> mandatory TradabilityRiskPacket
  -> multi-domain research EvidencePackets
  -> deterministic eligibility/rank/size/execution
```

The broad discovery universe must be separate from the tradable allowlist. The system should detect
and research all exchange-listed cash equities for which adequate data exists, while capital remains
restricted by liquidity, surveillance, corporate-action, market-mechanics, evidence-completeness,
and broker-orderability gates. An index-only India universe such as NIFTY 500 would miss BSE-only
momentum episodes such as Cropster Agro.

The nine-day target can credibly be a complete, end-to-end **first live vertical slice** with every
architectural plane represented. It cannot honestly be the final, deeply populated and adaptively
trained semantic Trading OS. In the first live iteration, relational EvidencePackets should be the
decision champion; OWL/SHACL, RDF and Neo4j should be versioned, rebuildable research/audit paths
until equivalence and temporal-correctness evidence permits greater influence.

## Cross-domain opportunity and failure matrix

| Domain | Cropster-equivalent opportunity | Primary failure/trap | Nine-day detector and gate | Final-state extension |
|---|---|---|---|---|
| Technical | Breakout, reversal, trend acceleration, relative-strength leadership | Corporate-action-distorted bars, circuit-only prints, stale/missing bars | Multi-timeframe price/volume detector; adjustment lineage; 15m/1h/day coverage receipts | Learned pattern families and cross-market propagation |
| Fundamental | Earnings or cash-flow inflection before broad repricing; post-result drift | Restatement, period/unit mismatch, low-quality accruals, one-off gains | Official filing watcher; point-in-time XBRL/filing packet; deterministic surprise and quality checks | Broader normalized PIT panels and estimate revisions |
| Corporate event | Buyback, order win, approval, capital allocation, management change | Rumour, effective-date error, already-priced event, adverse fine print | Exchange/SEC filing trigger; event type, publication/effective time, terms, expiry | Rich event lifecycle and comparable-event retrieval |
| Sentiment/narrative | Attention acceleration or credible narrative change | Promotional SMS/social campaign, syndicated-copy overcounting, bot amplification | Source clustering; primary-source corroboration; sentiment is risk-only when uncorroborated | Licensed broad sentiment, author history and propagation graph |
| Macro/cross-asset | Rate, FX, commodity or policy surprise creates beneficiaries/losers | Wrong exposure sign, revised macro vintage, narrative mistaken for causality | Official release/vintage watcher; closed event taxonomy; approved exposure rules | Vintage database, deeper cross-asset graph and fitted structural weights |
| Economic relationships | Supplier/customer/competitor/geography transmission | Stale relationship, hub overreach, unsupported causal edge | Small approved relationship set with provenance and expiry; depth-bounded lookup | Wider supply-chain/ownership/regulatory graph with challenger evaluation |
| Governance/surveillance | Governance repair or credible ownership change | Auditor/director exit, pledge/encumbrance, ASM/GSM/ESM, concentrated activity | Mandatory governance and current-surveillance packet before a small-cap trade | Longitudinal governance and ownership anomaly models |
| Liquidity/microstructure | Tradable volume expansion confirms a move | Upper/lower circuit lock, false displayed depth, spread/impact, inability to exit | Depth/turnover/spread/circuit checks at submission and revalidation | Fill-probability and market-impact models |
| Identity/corporate action | Correctly mapped rename, split, bonus, merger or dual listing | False momentum and wrong order caused by ticker reuse or unadjusted history | Typed Security/Listing identity; raw and adjusted bars; corporate-action receipt | Full temporal crosswalk and multi-venue equivalence |
| Portfolio context | Several independent opportunities diversify the book | Candidates are one hidden sector/factor/commodity bet | Correlation/sector/currency/relationship cluster caps | Adaptive multi-strategy and regime allocation |
| Market mechanics | Fast opportunity remains legally and operationally executable | India algo-order restrictions; US day-trade/account restrictions | Versioned broker/exchange compliance profile; limit-order and order-rate gates | Automatic rule-source monitoring with reviewed policy releases |

## Required design changes

### 1. OpportunityDetectorRegistry

Add deterministic detectors for technical momentum, fundamental inflection, official events,
attention/narrative anomalies, macro shocks, relationship exposure, governance/surveillance, and
tradeability. Every detector returns the same typed `OpportunityCandidate` and a `CoverageReceipt`.
The receipt records the expected universe, evaluated instruments, missing/stale instruments,
triggered candidates, rejection reasons, data snapshot, detector release, and cutoff.

The scanner—not an LLM—owns exhaustive universe coverage. Research agents investigate the
shortlist and may propose `BUY_CANDIDATE`, `WAIT`, `REJECT`, or `INSUFFICIENT_EVIDENCE`; they do
not emit price, size, quantity, or executable orders.

### 2. Mandatory TradabilityRiskPacket

No technical or research score can bypass a packet containing:

- broker orderability and listing status;
- current upper/lower price bands, halt state, and surveillance state;
- spread, depth, turnover, volume persistence, and estimated impact;
- raw-versus-adjusted price lineage and pending corporate actions;
- protection feasibility, including the possibility that a stop cannot fill during a circuit;
- applicable broker/account constraints and same-day round-trip budget; and
- data completeness/freshness at the decision cutoff.

Kite supplies an instrument master, historical candles, OHLC/quotes, depth and circuit limits.
Its documentation now also exposes a sandbox; use that for brief protocol smoke tests, not a
calendar paper campaign. [Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/),
[historical candles](https://kite.trade/docs/connect/v3/historical/),
[sandbox](https://kite.trade/docs/connect/v3/sandbox/).

### 3. Official event and fundamental watchers

For India, ingest NSE/BSE corporate announcements, financial results, shareholding, encumbrance,
corporate-action, board/auditor and surveillance disclosures. Exchange dissemination is primary
evidence but remains an issuer submission rather than exchange verification; preserve that
epistemic distinction. [NSE corporate filings](https://www.nseindia.com/companies-listing/corporate-filings-application?id=allAnnouncements).

For the US, use SEC EDGAR submissions and XBRL APIs for filings and financial facts, including
8-K/10-Q/10-K/6-K, Forms 3/4/5 and Schedules 13D/13G where applicable. SEC states that submissions
and XBRL JSON APIs update throughout the day. [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces),
[SEC technical specifications](https://www.sec.gov/submit-filings/technical-specifications).

### 4. Sentiment is not a standalone buy signal in the nine-day build

The first iteration may detect attention acceleration and cluster narratives, but social/news
sentiment is supportive or adverse evidence only. Uncorroborated promotional attention is a risk
flag. Syndicated copies share one origin and cannot be counted as independent evidence. Broad,
licensed, source-complete sentiment coverage is a later capability.

### 5. Data-feed limitations are explicit policy inputs

Alpaca exposes historical and real-time stock bars, but the IEX feed represents one venue while
SIP consolidates US exchanges. Production US intraday discovery therefore requires SIP readiness;
without it, constrain US opportunity discovery to delayed-SIP/EOD swing use and do not pretend IEX
volume is whole-market volume. [Alpaca real-time feeds](https://docs.alpaca.markets/us/v1.4.2/docs/real-time-stock-pricing-data),
[historical API](https://docs.alpaca.markets/us/docs/historical-api),
[historical feed guidance](https://docs.alpaca.markets/us/docs/historical-stock-data-1).

Alpaca also documents PDT protection behavior for sub-$25,000 accounts. The $200 sleeve must read
the broker account flags and maintain a same-day-round-trip budget rather than assume unrestricted
intraday exits. Protective risk exits remain higher priority than strategy entry cadence.
[Alpaca user protection](https://docs.alpaca.markets/us/v1.4.2/docs/user-protection).

For India, the current retail client-algo standard uses a 10-orders-per-second threshold and static
IP controls; NSE's current FAQ also says algo market orders are not permitted. These are external
compliance ceilings, not owner-editable exposure settings. Keep them in a separately versioned
`ComplianceProfileRelease` and fail closed if freshness is unknown.
[NSE implementation standards](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf),
[NSE retail-algo FAQ](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail%20Algo_03112025_NSE.pdf).

### 6. Multi-clock swing architecture

The existing EOD/weekly-monthly design is insufficient for the approved opportunity requirement.
Split the clocks while keeping the mandate swing/positional:

- broad discovery: daily, hourly and 15-minute snapshots;
- active shortlist monitoring: 1-minute and 5-minute bars;
- entry decisions: configured, liquidity-aware windows rather than unrestricted tick reactions;
- protection/reconciliation: independent second-level risk clock; and
- research refresh: event-triggered plus expiry-based.

This adds intraday discovery, not an unrestricted day-trading mandate.

## Configurable gates without mutable history

All tunable values belong to immutable, content-addressed policy releases:

- `CapitalEnvelopeRelease` — broker budget, currency, maximum cumulative loss, review/expiry;
- `ExposurePolicyRelease` — tier, gross, symbol, sector, correlation and liquidity caps;
- `PromotionPolicyRelease` — required clean lifecycle counts and evidence bounds;
- `ResearchCompletenessPolicyRelease` — required domains by risk class;
- `DecisionWindowPolicyRelease` — scan and entry clocks; and
- `ComplianceProfileRelease` — externally owned broker/exchange constraints.

A day-10 budget or exposure change creates a new release with `effective_from`, `supersedes`, owner
approval, and a safe activation boundary. Before activation, reconcile broker cash, positions,
orders, protection and cumulative loss. A reduction below current exposure enters `REDUCING`; an
increase becomes available only after funding and account reconciliation. Past decisions remain
bound to the old release, and no policy change retroactively resets losses.

Research agents may propose a change but cannot activate it. Cash-only, long-only, no leverage,
no shorting/derivatives, temporal validity, idempotency, protection, reconciliation, kill switch,
account identity and the no-LLM-size/price seam are constitutional invariants and cannot be turned
off through configuration.

## Nine-day delivery verdict

### Credible Day-9 outcome

- Zerodha and Alpaca live adapters with read-only readiness, idempotent order intents,
  reconciliation, protection and broker-scoped kill switches;
- broad discovery universe plus risk-gated tradable allowlists;
- multi-timeframe scanner, domain detectors and coverage receipts;
- official filing/event watchers and shallow EvidencePackets for all targeted domains;
- research-agent synthesis influencing candidate eligibility/ranking through the typed seam;
- deterministic capital, exposure, compliance, sizing and execution policy;
- immutable policy releases supporting a day-10 budget change;
- append-only decision/order/fill/outcome history and a first retrospective loop;
- ontology kernel and SHACL constraints, relational retrieval champion, and rebuildable RDF/Neo4j
  research projections; and
- direct-live Tier 0 after static/replay/contract/protocol-readiness checks, with no 90-day wait.

### Not honestly complete by Day 9

- deep historical and source-redundant coverage in every domain;
- broad licensed sentiment and whole-market alternative data;
- mature supply-chain/ownership/causal graph population;
- proven automatic ontology or strategy promotion;
- calibrated adaptive multi-strategy capital allocation; and
- evidence that the system has learned durable alpha across regimes.

Those are final-state intelligence and calibration, not missing architectural foundations. The
nine-day implementation should place the final contracts and versioning boundaries now so later
capability is additive rather than a rewrite.

## Go-live dependencies outside coding throughput

Day-9 live operation assumes Day-1 availability of funded live accounts, correct account/legal
status, Zerodha API access and mapped static IP, Alpaca live credentials and appropriate market-data
entitlement, LLM credentials, an allowlisted research path, and the required Postgres/Valkey/Fuseki/
Neo4j deployment. Missing external readiness can block live operation even if code is complete.
