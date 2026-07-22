# Current Portfolio, Family, and Multi-Asset Extension — Controlling MoA Synthesis

**Date:** 2026-07-22
**Status:** Controlling research synthesis
**Build target:** nine-day, two-broker, direct-live cash-equity vertical slice
**Future target:** separately authorised family accounts and capability-gated additional assets

## Executive conclusion

Current portfolio analysis is a mandatory V1 safety and decision dependency. Family support and
additional asset classes are valid long-term extensions, but V1 should install only their stable
identity, authority, isolation, currency, clock, and capability seams. It must not ship family
execution or FX execution.

The requested Hermes Mixture-of-Agents review produced useful ideas but failed independent
verification as a specification. The corrected architecture below adopts the strong findings while
rejecting unsafe normalization, authority, activation, and derivative-accounting proposals.

The controlling position is:

1. both Zerodha and Alpaca enter separately capped live Tier 0 after bounded static, replay,
   contract, and protocol checks; there is no fixed 90-day campaign;
2. the broad discovery and mandatory tradability architecture in
   `13-live-domain-opportunity-audit.md` is adopted;
3. every exposure-increasing decision consumes fresh, reconciled current portfolio state;
4. household aggregation preserves account partitions and may only tighten an opted-in account;
5. asset capability, account authority, compliance, data entitlement, broker readiness, semantic
   feature activation, and kill state are independent AND-gates; and
6. FX remains research-only until a later, separately reviewed product and accounting design is
   proven against then-current legal, venue, broker, and data conditions.

## Research method and evidence

The external MoA service received a sanitized hypothetical brief plus public facts. No source code,
private repository documents, credentials, account identifiers, or personal financial amounts were
sent. The two raw results are retained as non-controlling evidence:

- `raw/extensions-moa/chunk-1.out.md` — current portfolio and household foundation;
- `raw/extensions-moa/chunk-2.out.md` — multi-asset and FX foundation.

Three distinct verification lenses then reviewed the raw output against the private specifications:

- `raw/extensions-moa/verifier-portfolio.md` — **FAIL**;
- `raw/extensions-moa/verifier-fx.md` — **FAIL**;
- `raw/extensions-moa/verifier-scope.md` — **REVIEW**.

The joint judge therefore returned **NO-GO for the raw proposals as specifications**, while accepting
the extension direction after the corrections in `raw/extensions-moa/judge.md`. Both raw self-audits
were independently found unreliable, including false output-size claims.

## 1. Current portfolio analysis is part of V1

The system cannot evaluate a new trade using only positions created by the Trading OS. Existing
broker holdings, manual trades, external strategies, unsettled quantities, open orders, and cash
reservations already change the portfolio that will bear the new risk.

Every exposure-increasing decision therefore binds:

```text
immutable broker observations
      + append-only OS intention/history
      + current prices, FX, identity and policy cuts
      -> partitioned PortfolioSnapshot
      -> CurrentPortfolioAnalysis
      -> deterministic provisional sizing
      -> post-trade risk/compliance tightening or veto
      -> CAS reservation and immediate revalidation
      -> broker submission
```

Research agents may read the resulting portfolio context and reduce candidate rank. They cannot
create quantity, price, target weight, or an executable order.

### 1.1 Truth and authority matrix

There is no single fused source of truth. Immutable observations and OS history retain separate
authority and reconciliation makes disagreements explicit.

| Field family | Primary authority | Secondary evidence | Derived rule |
|---|---|---|---|
| Broker custody quantity and broker-reported saleability | Latest accepted broker observation | Previous broker observations and OS fills | Never overwrite the observation; unexplained differences become reconciliation facts |
| Settlement, pledge, lien, depository authorisation and broker restriction | Broker observation | Exchange/corporate-action evidence | Missing or ambiguous restrictions reduce availability and block affected new exposure |
| Broker order status and broker-side protection | Broker order/trade observation or postback | OS intent and last known state | Broker state controls custody effects; missing open-order state blocks new orders |
| OS order intent, reservation, strategy/sleeve origin and approval | Append-only OS ledger | Broker identifiers and fills | Broker data may confirm execution but cannot invent OS provenance |
| Cash, buying power and broker debits/credits | Broker observation | OS cash ledger and reservations | Available cash is the conservative reconciled result, never a comparison of unlike values |
| Historical cost basis and lifetime performance | Proven OS fills or explicit imported lot evidence | Broker current average cost | Unproven history remains `PARTIAL` or `UNKNOWN`; streams are never silently blended |
| Market price and FX mark | Validated, entitled price/FX snapshot | Broker display mark | Decisioning uses policy-approved marks; broker marks remain comparison evidence |
| Classification, relationships and research evidence | Validated data and semantic snapshot | Broker metadata | Never custody truth; may only inform features or tighten/veto risk through approved seams |

### 1.2 Non-overlapping quantity and cash buckets

A scalar settlement state is insufficient. Account projections must preserve distinct quantities
such as settled, unsettled, pledged, liened, depository-authorisation-blocked, broker-reserved,
locally reserved, pending buy, pending sell, and short-delivery/exception quantities. Merge rules
must prove whether a broker field already includes a restriction before subtracting it again.

Zerodha holdings and positions may represent different lifecycle views of the same instrument.
Canonicalization must use account, venue, product, instrument identity, trade date, direction, and
settlement status to prevent double counting. A manual record that matches broker custody becomes
provenance attached to that line; it is not added as extra quantity.

### 1.3 Completeness is a vector, not one confidence label

Each snapshot independently records at least:

- custody segments;
- cash and broker debits/credits;
- open orders and protection orders;
- instrument identity;
- quantity restrictions and settlement;
- price and FX marks;
- corporate-action state;
- OS provenance and historical cost basis; and
- policy, data and semantic versions.

Each dimension is `COMPLETE`, `DEGRADED`, `MISSING`, `STALE`, or `CONFLICT`. A deterministic policy
maps the worst relevant state to `ALLOW`, `REDUCE_ONLY`, or `BLOCK_NEW_EXPOSURE`. Missing custody,
cash, open orders, identity, price, FX where required, or an unresolved corporate action cannot be
replaced by a discretionary haircut in the Day-9 opening-risk path.

### 1.4 Account and aggregate cuts

Each Brokerage Account has its own sealed snapshot, reservations, reconciliation, capital envelope,
policy assignment, and kill generation. A principal-level or later household-level aggregate is a
partition-preserving view over compatible account cuts. It may calculate gross and net analytical
exposure, but it cannot net cash, collateral, margin, loss budgets, protection, orders, or custody.

For the initial owner, the aggregate view includes both Zerodha INR and Alpaca USD partitions. It
provides concentration and economic-exposure context while execution remains broker-account scoped.

### 1.5 Protective failure behavior

An emergency or capability stop atomically fences exposure-increasing actions first. State then
resolves to `NO_POSITION`, `REDUCE_ONLY`, or `MANAGEMENT_ONLY` while broker-native protection,
valuation, market/reference data, expiry management where applicable, and reconciliation remain
active.

The OS attempts an unconditional broker refresh before calculating a reduction. If custody cannot
be observed, it does not infer a liquidation quantity from stale state: it preserves existing
broker-native protection, blocks new exposure, alerts the owner, and keeps reconciling.

## 2. Family-ready identity and authority

Family support is not credential sharing and a Household is not a brokerage account. V1 installs
the stable model while exposing only the initial principal in the product interface.

```text
LegalParty ──ownership──> BrokerageAccount <──authorisation── AccountAccessGrant
    │                             │                                │
 Person or legal entity      BrokerConnection              read / propose /
    │                             │                         approve / execute
UserProfile                 AccountCapabilityAssignment
    │
HouseholdMembership ──> Household ──derives──> HouseholdPortfolioView
```

Required distinctions:

- `LegalParty` may be a Person or a future legal entity; joint ownership is an explicit relation.
- `UserProfile` is a login and preference identity, never proof of ownership.
- `BrokerConnection` holds scoped credentials/sessions and references only explicitly authorised
  accounts and operations.
- `AccountAccessGrant` covers read, reconciliation, proposal, approval, execution, or reporting
  scopes with effective time, evidence and revocation.
- `TradingMandate` is an explicit trading-capable grant, not an implication of family membership.
- `HouseholdMembership` grants only its recorded visibility or participation scope.
- all grants and revocations are append-only and bitemporal; current projections are rebuildable.

A consented `HouseholdRiskOverlay` may tighten an account's limit because of aggregate family
exposure. It can never loosen an account limit, offset another account's loss, transfer buying power,
or create a household order.

The staged extension is:

1. V1 domain schema and single-principal operation;
2. permission-filtered, read-only household portfolio analysis;
3. separately authenticated family broker connections and explicit mandates;
4. proposal/approval workflows per account; and
5. discretionary account execution only after broker and regulatory verification for that owner.

## 3. Multi-asset and FX extension boundary

The cross-asset kernel owns precise common envelopes: Money, CurrencyCode, typed quantity
descriptors, signed economic direction, clocks, event identity, policy references, order lifecycle,
cash-flow records, valuations, and reconciliation differences. It does not own product-specific
quotation, lot, pip/tick, session, margin, settlement, expiry, roll, or financing rules.

Those product semantics live in capability-gated modules. Cash equity is the only executable product
in V1. Future currency research needs separate identities for CurrencyPair, derivative product or
series, listed contract, venue segment/listing, temporal alias, deal, position, and contract-term
observations. A mutable contract specification is never part of a stable identity.

An `AssetClassCapabilityRelease` defines reusable verified requirements for a jurisdiction,
resident context, product, venue/segment, broker, data entitlement, valuation, risk, execution,
protection, and reconciliation combination. A deny-by-default `AccountCapabilityAssignment` binds
one account, mandate, limits, capital envelope, and effective time to that release. One account may
have several assignments; there is no permission-bearing default.

Live authority is the intersection of:

```text
AssetClassCapabilityRelease
AND AccountCapabilityAssignment + active mandate
AND ComplianceProfileRelease
AND data entitlement and permitted-use policy
AND broker/account readiness
AND fresh reconciled portfolio state
AND effective capital/exposure/promotion policies
AND current kill-switch generation
AND DecisionFeatureActivation for any semantic feature that influences economics
```

No authority implies another. In particular, semantic promotion cannot grant product execution,
and product capability cannot promote ontology-derived features.

For an India-resident user, current RBI guidance requires forex transactions to use authorised
persons for permitted purposes and permitted electronic routes, and states that LRS cannot fund
overseas online-forex margin. This supports blocking unverified and offshore leveraged retail FX/CFD
routes, not a claim that every authorised spot conversion is unlawful. Any later FX scope requires
fresh human legal/compliance verification. [RBI forex FAQ](https://www.rbi.org.in/scripts/FS_FAQs.aspx?Id=146)

NSE currency contracts demonstrate the additional product lifecycle: pair, contract unit, tick,
session, expiry, settlement reference and margin. Before execution, the design must specify
side-aware daily MTM cash events, collateral and broker margin, fees/taxes, corrections, expiry/final
settlement, roll legs, and deterministic reconciliation fail directions. [NSE contract specifications](https://www.nseindia.com/static/products-services/currency-derivatives-contract-specification-inr), [NSE parameters](https://www.nseindia.com/static/products-services/currency-derivatives-parameters)

## 4. Configurable releases and Day-10 changes

Capital, exposure, research completeness, decision windows, and promotion evidence are immutable,
effective-dated releases rather than fixed waits. A change on Day 10 creates a new release, binds it
to an account at a safe activation boundary, and preserves every prior decision's original versions.

Configurable releases include:

- `CapitalEnvelopeRelease`;
- `ExposurePolicyRelease`;
- `PromotionPolicyRelease`;
- `ResearchCompletenessPolicyRelease`;
- `DecisionWindowPolicyRelease`;
- `ComplianceProfileRelease`; and
- future `AssetClassCapabilityRelease` plus `AccountCapabilityAssignment`.

Reducing a ceiling below current exposure enters `REDUCE_ONLY` until compliant. Increasing a ceiling
requires reconciled funding and does not reset loss, drawdown, evidence, or historical receipts.
Agents may propose a change but cannot activate it.

Constitutional invariants remain non-configurable: account identity and authority, deterministic
price/quantity, append-only history, idempotency, reconciliation, protection, kill switches,
temporal validity, long-only cash-equity V1, and denial of unverified products/routes.

## 5. Nine-day interpretation

Day 9 delivers the complete first vertical slice with deliberately shallow intelligence breadth:

- live Zerodha and Alpaca account partitions with independent envelopes and kill switches;
- current portfolio import, authority-aware normalization, analysis and reconciliation;
- broad discovery, multi-clock detectors, CoverageReceipts, strict tradable allowlists and
  mandatory TradabilityRiskPackets;
- shallow but typed multi-domain EvidencePackets and official filing/event watchers;
- deterministic provisional sizing, risk/compliance tightening, reservations, protected execution,
  reconciliation and retrospective records;
- immutable configurable policy releases and Day-10-safe changes;
- relational champion plus ontology kernel and rebuildable research projections; and
- family and multi-asset schema/capability seams disabled beyond the initial owner and cash equities.

Direct Tier-0 activation remains conditional on external Day-1 readiness: funded and legally usable
accounts, Zerodha API/static-IP/tagging readiness, Alpaca credentials/account flags/data entitlement,
required data and LLM credentials, and deployable infrastructure. Code completion cannot waive an
unmet external dependency.

Day 9 does not claim mature alpha, family execution, FX execution, full tax-lot history, licensed
broad sentiment, mature causal graphs, or proven automatic strategy/ontology promotion.

## Primary operational sources

- [Kite portfolio API](https://kite.trade/docs/connect/v3/portfolio/) — holdings, positions,
  settlement/authorisation fields and portfolio semantics.
- [Alpaca current positions](https://docs.alpaca.markets/us/reference/getallopenpositions) — open
  positions and current cost/market values.
- [Alpaca portfolio history](https://docs.alpaca.markets/us/reference/portfolio-history) — account
  equity/P&L history interface.
- [RBI forex FAQ](https://www.rbi.org.in/scripts/FS_FAQs.aspx?Id=146) — authorised persons/routes
  and overseas online-forex margin restriction under LRS.
- [NSE currency contract specifications](https://www.nseindia.com/static/products-services/currency-derivatives-contract-specification-inr)
  — pair, unit, tick, session and expiry examples.
