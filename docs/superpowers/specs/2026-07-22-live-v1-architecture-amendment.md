# Trading OS Live V1 Architecture Amendment

**Date:** 2026-07-22
**Status:** Accepted design amendment
**Research basis:** `docs/research/13-live-domain-opportunity-audit.md` and
`docs/research/14-portfolio-family-multi-asset-moa-synthesis.md`

## 1. Precedence

This amendment controls where it conflicts with:

- `2026-07-20-trading-os-design.md`;
- `2026-07-21-trading-world-ontology-design.md`;
- `2026-07-21-trading-os-v1-implementation.md`; and
- `2026-07-21-trading-world-ontology-implementation.md`.

Specifically, it replaces the fixed 90-day paper-first campaign, EOD-only discovery, one-account
canary implications, fixed promotion windows, NIFTY-500-like discovery assumptions, and the older
`ExposureVector` seam. The ontology specification remains controlling for semantic release,
snapshot, validation, retrospective, and `DecisionFeatureActivation` requirements before
ontology-derived features can gain economic influence.

## 2. Outcome and scope

Build a complete end-to-end first live vertical slice in nine days for:

- Zerodha cash equities on NSE/BSE with an INR strategy sleeve;
- Alpaca cash equities on supported US venues with a USD strategy sleeve;
- broad opportunity discovery and strict account-specific tradability;
- multi-domain research agents behind typed non-executable boundaries;
- deterministic eligibility, sizing, risk, compliance, protection and execution;
- current portfolio analysis across all observed holdings and positions; and
- versioned policies, audit, reconciliation, retrospective diagnosis and safe improvement.

The initial product is swing/positional trading with intraday opportunity discovery. Intraday data
does not create an unrestricted day-trading mandate.

V1 is long-only and cash-funded. No shorting, leverage, derivatives, options, futures, crypto, or FX
execution is enabled. The schema is family-ready and multi-asset-ready, but V1 execution is limited
to the initial legal principal's separately reconciled cash-equity accounts.

## 3. Non-negotiable boundaries

1. Research agents never emit quantity, price, target weight, broker order, or executable command.
2. Every exposure-increasing decision binds fresh, partitioned, current portfolio state.
3. Broker custody observations and OS intention/history remain distinct; reconciliation never
   silently chooses a winner.
4. Every order belongs to one Brokerage Account, capital envelope, policy set and kill generation.
5. Household views never pool custody, cash, buying power, collateral, loss budgets or orders.
6. Policy changes create immutable releases and never rewrite prior decisions or reset losses.
7. Relational state is the production decision baseline; RDF and Neo4j are rebuildable research
   projections.
8. Semantic feature activation and product/account execution capability are independent AND-gates.
9. Operational safety faults halt new exposure regardless of remaining loss budget.
10. External broker, exchange, legal and data constraints cannot be configured away.

## 4. System shape

```text
Broad discovery universe
  -> OpportunityDetectorRegistry
  -> CoverageReceipts
  -> OpportunityCandidate
  -> account-specific TradabilityRiskPacket
  -> multi-domain EvidencePackets + InstrumentBeliefState
  -> DecisionFeatureSet
  -> fresh AccountPortfolioSnapshot + partitioned OwnerPortfolioCut
  -> deterministic provisional sizing
  -> RiskOverlaySet + compliance tightening/veto
  -> CAS reservation + immediate revalidation
  -> broker-scoped protected execution
  -> reconciliation + retrospective outcome
  -> offline diagnosis, challenger evaluation and governed policy/ontology proposals
```

The broad discovery universe answers “what might matter?” The tradable allowlist answers “what may
this account act on now?” They are never the same collection by accident.

## 5. Domain ownership and account model

V1 installs the following stable distinctions:

- `LegalParty`: a Person or future legal entity capable of account ownership;
- `UserProfile`: interaction identity, not proof of ownership or authority;
- `OwnershipRelation`: one or more Legal Parties owning a Brokerage Account;
- `BrokerConnection`: scoped credentials and sessions;
- `BrokerageAccount`: custody/execution/risk/reconciliation partition;
- `AccountAccessGrant`: effective-dated read or operational access;
- `TradingMandate`: explicit proposal, approval or execution authority;
- `Portfolio`: all observed positions and orders in one Brokerage Account;
- `Sleeve`: attribution and budget boundary inside one account;
- `Household` and `HouseholdMembership`: consent grouping, not ownership;
- `HouseholdPortfolioView`: rebuildable, permission-filtered derived view; and
- `PolicyAssignment`: binding of immutable policies to an account or sleeve.

V1 creates the family-ready records but exposes one principal. No family member can be traded for
without their separately verified ownership, broker connection, active mandate, account capability,
capital envelope, reconciliation and kill switch.

## 6. Current portfolio analysis contract

### 6.1 Immutable observations

Each broker refresh appends raw, hashed observations for holdings, positions, open orders,
protection orders, cash/buying power, restrictions and account state. Every record carries the
broker/account/environment identity, broker-reported time where available, OS receipt time, request
identity, and adapter version.

The OS ledger separately owns order intentions, approvals, reservations, strategy/sleeve provenance,
submitted client order IDs, fills observed by the OS, fees/taxes recorded by the OS, policy versions,
and operational state transitions.

### 6.2 Authority and reconciliation

- Broker observations are authoritative evidence of broker-reported custody, cash, restrictions,
  current broker orders and fills.
- The OS ledger is authoritative for what the OS intended, reserved, approved and attributed.
- Validated market-data snapshots are authoritative for decision prices and approved FX marks.
- Semantic projections are never custody, cash, order or fill truth.
- Differences append typed reconciliation outcomes; no input is mutated to hide a difference.

Canonicalization includes explicit broker-specific overlap rules. Zerodha holdings and positions,
Alpaca positions, manual imports and OS fills cannot be summed without proving their lifecycle and
identity relationship.

### 6.3 Quantity, cash and provenance

Position state uses non-overlapping buckets for settled, unsettled, pledged, liened,
authorisation-blocked, broker-reserved, locally reserved, pending-buy, pending-sell and exception
quantities. Cash uses native-currency buckets for settled, unsettled, broker-available,
OS-reserved, pending debits/credits and reconciled availability.

Every position/cost/history line carries provenance such as OS-confirmed, reconciled broker
observation, imported evidence, broker-snapshot-only, manual-unmatched, or unknown. Broker P&L,
OS-ledger P&L and unknown/partial performance remain separately labelled.

### 6.4 Completeness and fail direction

`PortfolioCompletenessVector` independently evaluates custody, cash, open/protection orders,
identity, settlement restrictions, prices, FX, corporate actions, provenance and policy versions.
Each dimension is `COMPLETE`, `DEGRADED`, `MISSING`, `STALE` or `CONFLICT`.

The effective `ResearchCompletenessPolicyRelease` deterministically maps the vector to:

- `ALLOW`;
- `REDUCE_ONLY`; or
- `BLOCK_NEW_EXPOSURE`.

Critical missing/stale/conflicting custody, cash, open orders, identity, price or required FX blocks
new exposure for the affected account. It does not block continued reconciliation or policy-valid
risk reduction.

### 6.5 Sealed cuts

`AccountPortfolioSnapshot` binds broker observation IDs, ledger cut, current reservations,
ValidatedDataSnapshotId, policy releases, clocks, CAS version and completeness vector.

`OwnerPortfolioCut` is a partition-preserving aggregation of compatible account snapshots. It may
measure global concentration and currency/economic exposure but never nets execution resources
across accounts. A later HouseholdPortfolioView follows the same partition rule with explicit read
consent.

## 7. Correct deterministic decision sequence

1. Candidate discovery and research emit typed categorical `DecisionFeatureSet` evidence only.
2. Portfolio snapshot and owner cut are sealed and freshness checked.
3. Deterministic eligibility runs without an agent-provided number.
4. Deterministic sizing produces a provisional account-scoped quantity from price, stop distance,
   capital envelope and portfolio state.
5. Risk and compliance evaluate the hypothetical post-trade portfolio and may shrink or veto.
6. Tighten-only `RiskOverlaySet`, including `PortfolioRiskOverlaySet`, may further shrink or veto.
7. The OS obtains a CAS reservation for cash, quantity and risk capacity.
8. Policy, snapshot freshness, kill generation, capability and account readiness are revalidated.
9. A durable order intent is appended before broker submission.
10. Broker acknowledgements, fills, protection and reconciliation append subsequent facts.

No step accepts raw graph queries or unrestricted LLM output.

## 8. Opportunity discovery and research coverage

`OpportunityDetectorRegistry` runs deterministic detectors across technical, fundamental,
corporate-event, sentiment/narrative, macro/cross-asset, economic-relationship,
governance/surveillance, liquidity/microstructure, identity/corporate-action, portfolio-context and
market-mechanics domains.

Default clocks are policy-owned:

- broad discovery: daily, hourly and 15-minute where feeds support it;
- active shortlist: 1-minute and 5-minute observations;
- entry evaluation: configured decision windows;
- risk/protection: event driven and second-level where required; and
- event/fundamental research: filing and calendar driven.

Every run emits a `CoverageReceipt` including the intended universe, actually scanned instruments,
time range, data sources, missing instruments, errors, detector/policy versions and latency.

Every candidate must obtain a current account-specific `TradabilityRiskPacket` containing listing
and broker orderability, circuits/bands, surveillance/restrictions, spread/depth/turnover,
raw/adjusted lineage, stop feasibility, account constraints, data freshness and policy versions.

Sentiment is risk-only in the nine-day V1 unless corroborated by primary evidence. Official NSE/BSE
and SEC filing/event watchers are preferred over unverified narratives.

## 9. Market data and charting

- India research and execution data uses Kite historical candles, quotes/depth and WebSocket data,
  plus exchange/source records required for coverage and compliance.
- US live intraday breadth requires the Alpaca SIP entitlement. Without it, the US policy limits
  discovery to delayed-SIP/EOD-compatible decisions; IEX-only data cannot silently represent the
  whole US market.
- Human chart inspection uses TradingView Lightweight Charts fed by the OS's validated data.
- Agents consume numeric bars, features and evidence packets, not chart screenshots.

## 10. Configurable live authority

Policy is stored as immutable content-addressed releases:

- `CapitalEnvelopeRelease`;
- `ExposurePolicyRelease`;
- `PromotionPolicyRelease`;
- `ResearchCompletenessPolicyRelease`;
- `DecisionWindowPolicyRelease`;
- `ComplianceProfileRelease`;
- `DecisionFeatureActivation`; and
- future `AssetClassCapabilityRelease` with `AccountCapabilityAssignment`.

Every release has owner, approval evidence, effective interval, supersession reference and safe
activation boundary. A Day-10 change creates a new release. It never resets cumulative loss,
drawdown, evidence, trades or historical receipts.

Reducing a ceiling below current exposure enters `REDUCE_ONLY`. Increasing it requires actual
funding plus broker reconciliation. Agents may propose releases but cannot activate them.

### 10.1 Initial broker-scoped releases

| Setting | Zerodha sleeve | Alpaca sleeve |
|---|---:|---:|
| Capital envelope | INR 50,000 | USD 200 |
| Maximum cumulative loss | INR 50,000 | USD 200 |
| Automatic reload | Disabled | Disabled |
| Initial live tier | T0 | T0 |
| T0 maximum deployed | 25% of sleeve envelope | 25% of sleeve envelope |
| T0 per-symbol exposure | 10% of sleeve envelope | 10% of sleeve envelope |

These are initial policy values, not code constants. Existing external positions influence risk and
concentration but do not enter the OS sleeve's loss attribution unless explicitly adopted through a
versioned provenance action.

Default promotion policy:

- T1: maximum deployed 50%, per symbol 15%, after at least 3 reconciled protected entries and one
  reconciled exit, unless a superseding policy changes the evidence requirement;
- T2: maximum deployed 90%, per symbol 20%, after at least 10 clean lifecycles and cost evidence,
  unless superseded; and
- no tier grants permission beyond the capital envelope or maximum cumulative loss.

Default loss response:

- 5% sleeve loss in a trading day: no-new-entry cooldown and retrospective;
- 20% cumulative drawdown: mandatory retrospective;
- 40%: promotion disabled;
- 60%: step down at least one tier;
- 80%: T0 plus explicit owner restart; and
- 100%: broker sleeve stops until a new owner-approved funded envelope is created.

Evidence counts and windows are configurable through later immutable releases. Protection,
reconciliation, idempotency, account authority and kill behavior are not optional.

## 11. Execution, protection and stops

Each account has a kill generation and scoped state:

- `ACTIVE`;
- `ENTRY_DISABLED`;
- `REDUCE_ONLY`;
- `MANAGEMENT_ONLY`; or
- `HALTED`.

A safety/compliance/data stop fences new exposure before any human acknowledgement. Open positions
keep broker-native protection, observations and reconciliation. If broker custody is unavailable,
the OS does not guess a close quantity; it alerts and reconciles while preserving existing
broker-native orders.

India order logic must obey the active broker/exchange compliance profile, including current
order-type, static-IP, tagging and rate restrictions. Alpaca account flags, data entitlement and
day-trade protections are read dynamically, not assumed.

## 12. Retrospective agentic improvement loop

Every decision records candidate, coverage, research, portfolio, policies, semantic snapshots,
deterministic calculations, order lifecycle, costs and realized outcome. Retrospectives compare:

1. the permanent relational snapshot-scoped baseline;
2. ontology/RDF challenger answers; and
3. bounded Neo4j relationship challenger answers.

Diagnosis uses closed root-cause classes such as discovery coverage, identity, temporal leakage,
data quality, research extraction, ontology/query, portfolio normalization, risk, execution,
protection and regime shift.

Agents may propose detector, query, ontology, policy or strategy changes. Promotion requires frozen
evaluation manifests and immutable receipts. Live self-modification is prohibited.

## 13. Family extension path

After V1:

1. add permission-filtered read-only family views;
2. connect each family account with its own credentials and verified ownership/mandate;
3. reconcile and risk each account independently;
4. allow account-specific proposals and approvals; and
5. enable discretionary execution only under an account capability and then-current broker/legal
   verification.

With explicit consent, `HouseholdRiskOverlay` may tighten one account based on aggregate exposure.
It can never loosen or use another account's resources.

## 14. Multi-asset and FX extension path

V1 adds common typed Money, CurrencyCode, quantity descriptors, clocks, venue/segment identity,
price-source lineage and deny-by-default capability assignments. Only cash equity assignments are
active.

Future FX work proceeds independently from family execution:

1. model currency-pair, product/series, listed-contract, venue-segment, contract-term, calendar,
   margin and settlement identities with bitemporal source lineage;
2. build research-only data and evidence with live transport structurally unreachable;
3. implement side-aware daily MTM cash events, margin/collateral, fees/taxes, expiry, final
   settlement, roll and full reconciliation;
4. reverify current product-purpose-person-venue legality and broker/data entitlement;
5. evaluate semantic features under independent DecisionFeatureActivation; and
6. activate a separately capped product Tier 0 only under the intersection of all current releases.

Unsupported offshore leveraged retail FX/CFD routes remain denied. The system must not generalize
that conservative block into a claim that every authorised foreign-exchange transaction is illegal.

## 15. Nine-day acceptance boundary

Day 9 is accepted only if:

- both broker adapters authenticate against intended live accounts and reconcile current state;
- independent broker/sleeve capital envelopes and kill switches are effective;
- current portfolio analysis includes external/manual positions and blocks on critical missingness;
- discovery emits CoverageReceipts over the configured broad universe;
- every candidate receives a TradabilityRiskPacket and required domain EvidencePackets;
- deterministic provisional sizing, risk/compliance tightening, CAS reservation, durable intent,
  protection and reconciliation pass contract/replay/protocol checks;
- live Tier 0 can be enabled or disabled per broker without changing code;
- every decision is reproducible from immutable versions and snapshots;
- relational retrieval works if RDF/Neo4j/LLMs are unavailable;
- family and non-equity capability assignments remain disabled; and
- operator runbooks cover halt, reduce-only, stale state, reconciliation drift, credential expiry,
  protection failure and policy change.

External readiness is a launch dependency, not a code acceptance waiver: funded/legal accounts,
Zerodha API/static IP/tagging, Alpaca credentials/account/data entitlement, required infrastructure,
and research/data credentials must be available.

## 16. First iteration versus final state

| Dimension | Day-9 first iteration | Intended mature state |
|---|---|---|
| Architecture | Complete vertical spine; roughly 60–70% of structural shape | Scaled, redundant, multi-account and multi-asset operations |
| Intelligence | Broad but shallow typed evidence; roughly 30–40% of intended depth | Calibrated multi-domain, regime-aware and causally cautious research |
| Portfolio | Full current-state gate, conservative provenance and basic exposures | Tax lots, richer factor/liquidity/correlation and household planning |
| Ontology | Kernel, releases, SHACL, relational champion, rebuildable projections | Deeper identity/event/relationship coverage with proven challengers |
| Adaptation | Append-only outcomes and governed proposals | Statistically supported promotion/demotion and resource allocation |
| Accounts | Initial owner across Zerodha and Alpaca | Separately authorised family profiles and additional brokers |
| Assets | Cash equities only | Capability-gated additional assets after product-specific proof |

The first iteration is not disposable. It contains the permanent safety, audit, identity, policy,
portfolio and deterministic execution spine. Later work expands evidence depth and activated
capabilities rather than replacing those foundations.
