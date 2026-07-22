# Domain Agent Source, Tool, and Skill Profiles

**Date:** 2026-07-23

## Purpose

This document defines the research-backed starting profile for all ten `EvidenceDomain`s. It specifies source classes, typed capability families, domain reasoning skills, expected categorical evidence, and fail-closed traps. It does not activate a source or grant a tool; effective `SourceCoveragePolicyRelease`s and `ToolCapabilityRelease`s do that.

“Skill” here means a versioned domain reasoning instruction/evaluation package referenced by an `AgentProfileRelease`, not executable code and not permission.

## Cross-domain source policy

1. Prefer the original regulator, exchange, statistical agency, issuer filing, or internal custody record.
2. Preserve origin and delivery channel separately. The same issuer disclosure delivered by SEC, NSE, BSE, a newswire, and a vendor is one source family unless independent content exists.
3. Bind every observation to publisher time, availability time, ingestion time, decision cutoff, parser release, and frozen snapshot.
4. Treat derived APIs and XBRL as structured access paths, not replacements for the original official filing when the two disagree. The SEC specifically cautions users to refer to the official filing for what was filed. See [About EDGAR](https://www.sec.gov/edgar/searchedgar/aboutedgar.htm).
5. Encode entitlement and feed scope in policy. NSE documents separate real-time levels and historical products, while Alpaca's free US feed covers IEX rather than the full SIP. See [NSE real-time data](https://www.nseindia.com/static/market-data/real-time-data-subscription), [NSE data policy](https://www.nseindia.com/static/market-data/nse-data-policy), and [Alpaca market-data FAQ](https://docs.alpaca.markets/us/docs/market-data-faq).
6. Agents read sealed `SourceRecord`s only. New fetching is `SourceWatcher` work.
7. A source class starts experimental and shadow-only until provenance, entitlement, freshness, parser, independence, failure, and replay gates pass.

## Common evidence shape

Every domain packet must:

- state a categorical assessment in domain language;
- cite support only from the question's source-record set;
- preserve material counterevidence in `contradictions`;
- state missing applicable evidence in `missing`;
- distinguish inapplicable sources from missing sources;
- use only the existing categorical eligibility effect;
- emit no price, quantity, target, expected return, position weight, conviction multiplier, or order.

Positive influence is permitted only when that domain allows it, applicable primary coverage is sufficient, evidence is within cutoff, and no material contradiction is unresolved. Degraded evidence may remain informational but cannot be silently treated as complete. Insufficient or contradictory evidence has no positive influence. Sentiment is always risk-only.

## 1. Technical profile

### Authoritative source classes

- Exchange-licensed trades, quotes, depth, end-of-day, historical, security-master, and corporate-action data. NSE offers Level 1, Level 2, Level 3, tick-by-tick, snapshot, delayed, and historical products with distinct delivery and licensing. [NSE real-time data](https://www.nseindia.com/static/market-data/real-time-data-subscription)
- BSE licensed real-time, delayed, historical, index, and corporate data. [BSE market data](https://marketdata.bseindia.com/)
- The exact broker/vendor feed used by execution, with its scope recorded. Alpaca's free feed is IEX-only; SIP is a different entitlement. [Alpaca market-data FAQ](https://docs.alpaca.markets/us/docs/market-data-faq)
- Official corporate-action and symbol/master records for adjustment boundaries.

### Typed capability families

- `AdjustedBarWindowQuery`
- `QuoteAndDepthWindowQuery`
- `CorporateActionAdjustmentCheck`
- `FeedEntitlementAndCompletenessCheck`
- pure `TrendRegime`, `VolatilityRegime`, `Gap`, and `Participation` calculators

### Domain skills

- separate observation from interpretation;
- detect corporate-action, session, symbol, and feed discontinuities before calculating;
- compare indicator conclusions across raw and correctly adjusted series;
- reason categorically about regime and data quality.

### Good packet

The assessment names a categorical regime such as persistent trend, range, transition, dislocation, or indeterminate. Support cites the exact adjusted-bar or quote records. Contradictions preserve incompatible horizons or feed views. Missing identifies absent depth, incomplete venue coverage, adjustment uncertainty, or stale bars. Positive support is allowed only with complete applicable data; data-quality uncertainty tightens or removes positive influence.

### Traps and guards

- split/dividend-distorted bars → mandatory corporate-action adjustment check;
- IEX or single-venue activity treated as whole-market activity → entitlement-aware coverage status;
- after-hours and auction prints mixed with continuous trading → session classifier;
- indicator proliferation → approved calculator set and held-out evaluation;
- technical output becoming an entry, target, or stop → categorical seam rejection.

## 2. Fundamental profile

### Authoritative source classes

- Original SEC annual, quarterly, current, and foreign-issuer filings plus EDGAR submission history. EDGAR APIs expose submissions and XBRL company facts and are updated as filings disseminate. [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- NSE/BSE filed financial results, corporate data, and XBRL where applicable. NSE's corporate data includes fundamentals, announcements, and shareholding patterns. [NSE corporate data](https://www.nseindia.com/static/market-data/corporate-data-subscription), [NSE XBRL filing information](https://www.nseindia.com/static/companies-listing/xbrl-information), [BSE market/corporate data](https://marketdata.bseindia.com/)
- Issuer annual reports only when identity, publication time, and filing relationship are sealed.

### Typed capability families

- `FilingSectionQuery`
- `XBRLFactQueryAsFiled`
- `FactContextAndUnitValidator`
- `PeriodAndRestatementComparator`
- pure accounting ratio, bridge, and consistency calculators
- `OriginalFilingCrossCheck`

### Domain skills

- distinguish reported, derived, management-adjusted, and agent-inferred values;
- normalize units, periods, consolidations, currencies, and fiscal calendars;
- recognize restatements, taxonomy extensions, and changed definitions;
- explain categorical quality, direction, and uncertainty without valuation targets.

### Good packet

The assessment states categorical operating, balance-sheet, cash-flow, or reporting quality. Support cites official filing spans and structured facts with context. Contradictions capture filing-versus-XBRL differences, restatements, or inconsistent definitions. Missing lists required statements, periods, segments, or units. Positive influence requires direct official support and consistent periods; unresolved accounting inconsistency blocks it.

### Traps and guards

- treating XBRL as more authoritative than the filing → original-filing cross-check;
- mixing quarterly, year-to-date, annual, consolidated, and standalone periods → context validator;
- using later restatements before the cutoff → as-filed version binding;
- comparing issuer extensions as standard concepts → taxonomy mapping policy;
- turning ratios into expected return → categorical seam rejection.

## 3. Corporate-event profile

### Authoritative source classes

- SEC 8-K and, when applicable, 6-K or related filed disclosures through EDGAR. [SEC filing search and feeds](https://www.sec.gov/search-filings)
- NSE corporate announcements, actions, board meetings, and filed attachments. The exchange displays received and dissemination times and notes that issuer uploads are disseminated on receipt. [NSE announcements](https://www.nseindia.com/companies-listing/corporate-filings-announcements?tabIndex=equity)
- BSE corporate announcements, actions, results, board meetings, and governance data. [BSE market/corporate data](https://marketdata.bseindia.com/)
- Specialized official sources only when an effective-dated product or regulatory relationship makes them applicable.

### Typed capability families

- `OfficialAnnouncementQuery`
- `FilingItemAndAttachmentQuery`
- `IssuerSecurityListingApplicabilityResolve`
- `DisclosureSourceFamilyDeduplicate`
- `CorporateEventNormalize`
- `OfficialChannelReconcile`
- `CutoffAndAvailabilityValidate`

### Domain skills

- classify event type, subject, effective date, stated scope, and conditionality;
- separate issuer statement from regulatory disposition and agent inference;
- distinguish delivery corroboration from independent corroboration;
- preserve corrections, withdrawals, amendments, and official conflict.

### Good packet

The assessment names a categorical event and materiality class, not an expected price move. Support cites the exact official disclosures. Contradictions preserve incompatible official descriptions or effective dates. Missing names applicable official channels or required attachments. One missing applicable exchange channel is degraded but usable; all mandatory channels absent is insufficient; material conflict blocks positive influence.

### Traps and guards

- requiring BSE for an NSE-only listing or vice versa → effective-dated applicability;
- treating SEC, NSE, and BSE copies of the same issuer disclosure as independent → source-family graph;
- future leakage from amended filings → cutoff-bound filing version;
- attachment omitted while headline is present → attachment completeness requirement;
- acquisition, award, approval, or litigation language over-interpreted → conditionality and authority classifier.

## 4. Sentiment profile

### Source classes

- Official issuer, exchange, regulator, and statistical releases as the anchor for claims.
- Approved licensed news or transcript vendors as secondary channels with explicit entitlement, publisher identity, and availability time.
- Social or crowd sources only as experimental shadow inputs unless a separate policy release passes provenance, manipulation, deduplication, and replay gates.

### Typed capability families

- `NarrativeItemQuery`
- `PublisherAndSourceFamilyResolve`
- `SyndicatedCopyCluster`
- `ClaimAnchorToOfficialSource`
- `NarrativeRiskThemeClassify`
- `ManipulationAndBotRiskFlag`

### Domain skills

- distinguish attention, tone, claim, rumor, and verified event;
- collapse syndicated and copied stories into one source family;
- anchor material claims to official evidence where available;
- identify narrative risk without producing a bullish recommendation.

### Good packet

The assessment is categorical narrative risk: elevated, concentrated, contested, rapidly changing, stale, or indeterminate. Support cites approved narrative records and their official anchors. Contradictions preserve materially opposing narratives or official denials. Missing identifies provenance, independence, entitlement, or official confirmation. `eligibility_effect` is neutral, tighten, or veto only; sentiment can never create positive influence.

### Traps and guards

- syndicated-copy overcounting → source-family clustering;
- social manipulation or bot amplification → experimental-only policy and risk flags;
- post-cutoff articles summarizing pre-cutoff events → availability-time enforcement;
- model mistaking tone for fact → claim/observation separation;
- absence of negative news interpreted positively → prohibited inference.

## 5. Macro profile

### Authoritative source classes

- RBI statistical releases and DBIE series for India, with release-calendar and revision metadata.
- MoSPI official national accounts, inflation, production, labor, and release notices.
- Original statistical agencies such as BEA/BLS for US data; BEA publishes a release schedule that can change when source data are unavailable. [BEA release schedule](https://www.bea.gov/news/schedule)
- FRED as an access layer and ALFRED for historical vintages. ALFRED records when values were originally released and later revised. [FRED API](https://fred.stlouisfed.org/docs/api/fred/overview.html), [ALFRED](https://fred.stlouisfed.org/docs/api/fred/alfred.html)

### Typed capability families

- `MacroSeriesAsOfQuery`
- `MacroVintageAndRevisionQuery`
- `OfficialReleaseCalendarQuery`
- `ReleaseExpectationSnapshotQuery`
- pure growth, inflation, diffusion, and surprise classifiers
- `SeriesDefinitionAndBaseYearCheck`

### Domain skills

- reason using the vintage available at the decision cutoff;
- distinguish level, rate, annualized rate, seasonal adjustment, base year, and revision;
- treat release schedules as mutable observed facts, not timeless calendars;
- map macro evidence to categorical regime or risk, not expected market return.

### Good packet

The assessment identifies a categorical macro regime, transition, or surprise with vintage. Support cites official releases and as-of series. Contradictions capture cross-series divergence or later revision only when relevant to retrospective evaluation. Missing identifies unavailable vintage, expectation snapshot, release delay, or definition. Positive influence requires the intended vintage and applicable geography; otherwise neutral or tighten.

### Traps and guards

- using latest revised data in historical decisions → ALFRED/as-of query;
- stale or rescheduled calendars → watcher receipt and release-status check;
- base-year or methodology change treated as growth → definition release;
- mixing seasonally adjusted and unadjusted data → schema validation;
- using FRED observation time as original publication time → original-source and vintage metadata.

## 6. Economic-relationship profile

### Authoritative source classes

- Issuer filings for segments, customers, suppliers, subsidiaries, geographic exposure, commodities, and currency risks.
- Official trade and industry statistics. UN Comtrade aggregates official country-reported trade data by product and partner, with availability and licensing limits. [UN Comtrade](https://comtradeplus.un.org/)
- Effective-dated internal issuer/security/listing, sector, index, product, supplier, customer, currency, and commodity relationships with provenance.

### Typed capability families

- `TemporalRelationshipGraphQuery`
- `FilingExposureSpanQuery`
- `TradeFlowAsOfQuery`
- `RelationshipProvenanceAndValidityCheck`
- pure exposure direction and transmission-path classifiers

### Domain skills

- separate asserted relationship from inferred relationship;
- preserve direction, scope, validity interval, and provenance;
- recognize that trade statistics are country/product aggregates, not issuer exposure;
- explain transmission uncertainty and missing links.

### Good packet

The assessment names a categorical relationship and possible transmission channel. Support cites issuer disclosure or official aggregate evidence plus the effective relationship record. Contradictions preserve conflicting segment or counterparty evidence. Missing lists relationship validity, issuer mapping, geography, product code, or cutoff data. Positive influence requires a direct, current, supported relationship; broad sector analogies remain neutral.

### Traps and guards

- converting country trade into issuer revenue → explicit aggregation-level check;
- stale supplier/customer relationships → effective intervals;
- ticker joins mistaken for entity identity → Issuer/Security/Listing model;
- causal certainty from correlation → transmission uncertainty;
- double-counting exposure through multiple graph paths → path-family deduplication.

## 7. Governance profile

### Authoritative source classes

- SEC periodic/current filings, proxy materials, and ownership Forms 3, 4, and 5. [SEC filing search](https://www.sec.gov/search-filings)
- NSE/BSE governance, shareholding, voting, pledge, board, and related-party filings. NSE provides shareholding-pattern detail and XBRL governance filing formats. [NSE shareholding patterns](https://www.nseindia.com/companies-listing/corporate-filings-shareholding-pattern), [NSE XBRL information](https://www.nseindia.com/static/companies-listing/xbrl-information)
- SEBI LODR requirements and regulatory orders for Indian listed entities. [SEBI LODR regulations](https://www.sebi.gov.in/legal/regulations/jan-2026/securities-and-exchange-board-of-india-listing-obligations-and-disclosure-requirements-regulations-2015-last-amended-on-january-22-2026-_100004.html)

### Typed capability families

- `BoardAndCommitteeCompositionQuery`
- `OwnershipAndPledgeAsOfQuery`
- `RelatedPartyDisclosureQuery`
- `InsiderOwnershipChangeQuery`
- `GovernanceFilingConsistencyCheck`
- `RegulatoryActionAndStatusQuery`

### Domain skills

- distinguish allegation, investigation, order, appeal, remediation, and final disposition;
- track role and ownership changes by effective date;
- compare governance disclosures across periods and official channels;
- treat missing required disclosure as risk, not proof of misconduct.

### Good packet

The assessment names categorical governance quality or risk with legal status. Support cites filings, ownership records, or final regulatory text. Contradictions preserve issuer responses, appeals, or inconsistent official records. Missing lists required governance reports, ownership periods, related-party detail, or disposition. Positive influence requires complete routine evidence; unresolved adverse matters tighten or veto.

### Traps and guards

- allegation presented as adjudicated fact → legal-status taxonomy;
- director name collision → legal-entity/person identity resolution;
- later board composition used before cutoff → effective dating;
- absence of disclosure interpreted as absence of risk → required-disclosure applicability;
- shareholding percentage crossing the seam → internal numeric analysis, categorical external result.

## 8. Liquidity profile

### Authoritative source classes

- Licensed exchange quote, depth, order, and trade data at the entitlement actually held. NSE distinguishes best bid/ask, 5-level, 20-level, and full tick-by-tick products. [NSE real-time data](https://www.nseindia.com/static/market-data/real-time-data-subscription)
- BSE exchange feeds and historical trade data. [BSE market data](https://marketdata.bseindia.com/)
- FINRA transparency datasets for applicable US OTC/short-interest contexts. [FINRA Developer Center](https://developer.finra.org/docs)
- Broker/vendor data only with feed and venue completeness recorded; Alpaca IEX and SIP are not interchangeable. [Alpaca market-data FAQ](https://docs.alpaca.markets/us/docs/market-data-faq)

### Typed capability families

- `SpreadDepthAndTurnoverWindowQuery`
- `VenueCoverageAndEntitlementCheck`
- `StaleQuoteAndLockedCrossedMarketCheck`
- `AuctionAndSessionLiquiditySeparate`
- pure categorical depth, spread, participation, and discontinuity classifiers

### Domain skills

- interpret liquidity relative to feed scope, venue, session, and horizon;
- distinguish displayed depth from executable certainty;
- detect stale, locked, crossed, auction, and halt conditions;
- emit risk category only, never position size.

### Good packet

The assessment states categorical liquidity and execution-environment risk. Support cites exact quote/depth/trade windows and entitlement. Contradictions preserve venue or horizon divergence. Missing lists depth level, venue coverage, session, or stale data. The domain may only tighten or veto execution eligibility; it cannot prescribe quantity or order type.

### Traps and guards

- single-venue feed treated as consolidated market → entitlement check;
- displayed depth treated as guaranteed liquidity → categorical uncertainty;
- open/close auction mixed with continuous session → session segmentation;
- stale quote creates false tight spread → freshness check;
- internal impact estimate crossing the seam → categorical projection.

## 9. Portfolio profile

### Authoritative source classes

- Internal immutable `PortfolioSnapshot`, preserving Brokerage Account partitions.
- Broker custody observations, OS ledger, reservations, open orders, prices, policies, and completeness captured in that snapshot.
- Admitted semantic relationships and risk classifications bound to the same cutoff; no unfrozen external fetch is permitted.

### Typed capability families

- `PortfolioSnapshotPartitionQuery`
- `ExposureOverlapAndConcentrationCompute`
- `LiquidityAndEventExposureJoin`
- `ScenarioAggregationCompute`
- `SnapshotCompletenessAndProvenanceCheck`

### Domain skills

- preserve account and mandate partitions;
- distinguish custody observation, OS intention, reservation, and available capital;
- aggregate numeric exposures internally while emitting categorical concentration, correlation, liquidity, event, and protection risk;
- treat incomplete custody or pricing as a veto for exposure increase.

### Good packet

The assessment names categorical portfolio interaction risk. Support cites the immutable portfolio and admitted evidence records. Contradictions preserve broker/ledger or price-source inconsistencies. Missing names incomplete accounts, stale prices, unknown reservations, or absent relationship evidence. `eligibility_effect` is neutral, tighten, or veto; the packet never emits target weights, position sizes, or orders.

### Traps and guards

- household aggregation erases account authority → partition-preserving query;
- broker observation confused with OS intention → ADR-0002 model;
- stale price or missing account treated as zero exposure → completeness gate;
- correlation estimate over-trusted → categorical uncertainty and regime sensitivity;
- recommendation disguised as allocation analysis → seam rejection.

## 10. Market-mechanics profile

### Authoritative source classes

- Exchange security masters, calendars, session definitions, auction rules, halts, bands, corporate actions, settlement schedules, and status messages.
- NSE/BSE market and corporate data products with their applicable licenses. [NSE data products](https://www.nseindia.com/static/nse-data-and-analytics), [BSE market data](https://marketdata.bseindia.com/)
- SEC/FINRA regulatory and transparency records for applicable US mechanics. [SEC filing/data resources](https://www.sec.gov/about/developer-resources), [FINRA Developer Center](https://developer.finra.org/docs)
- Broker capability observations only as broker-specific operational evidence.

### Typed capability families

- `ExchangeSessionAndCalendarQuery`
- `SecurityMasterAndSymbolHistoryResolve`
- `HaltBandAuctionStatusQuery`
- `CorporateActionMechanicsQuery`
- `SettlementAndVenueRuleQuery`
- `BrokerVenueCapabilityCheck`

### Domain skills

- distinguish Security, Listing, Ticker, venue, segment, and session;
- apply effective-dated rules and symbol history;
- separate market-state restriction from trading recommendation;
- explain when bars, quotes, or candidate events are mechanically invalid.

### Good packet

The assessment states categorical market-state constraints: normal, auction, halted, band-limited, special session, settlement-constrained, symbol-transition, or indeterminate. Support cites official status/rule/master records. Contradictions preserve exchange-versus-broker state disagreement. Missing lists calendar, segment, symbol mapping, corporate action, or venue status. Mechanics evidence may tighten or veto; ordinary state is neutral rather than positive alpha.

### Traps and guards

- ticker treated as stable identity → effective symbol resolver;
- halt or auction print treated as continuous price discovery → market-state query;
- current rule applied historically → rule-release binding;
- corporate action produces false gap/volume event → mechanics join before technical analysis;
- broker support treated as exchange permission → separate product capability from semantic activation per ADR-0003.

## Source-coverage starting priorities

### P0 mandatory

- recorded SEC 8-K fixtures for applicable issuers;
- recorded NSE and BSE corporate-announcement/action fixtures according to listing applicability;
- identity, listing, filing-status, cutoff, and source-family records needed to determine applicability and contradiction.

### P1 source-policy workstreams

- official financial/XBRL coverage for fundamental and governance profiles;
- licensed quote/depth and corporate-action coverage for technical, liquidity, and market mechanics;
- RBI/MoSPI and ALFRED-vintage macro coverage;
- issuer-disclosed and official aggregate relationship evidence;
- partition-preserving portfolio snapshot capabilities;
- approved licensed narrative sources for risk-only sentiment.

## Evaluation requirements across all profiles

Every profile fixture suite must cover complete, degraded, insufficient, contradictory, inapplicable, stale, late, malformed, and entitlement-denied states. Held-out cases must differ by issuer and event family. No aggregate quality score may compensate for a failure in cutoff safety, citation scope, contradiction preservation, sentiment risk-only behavior, executable-field rejection, or relational-champion availability.
