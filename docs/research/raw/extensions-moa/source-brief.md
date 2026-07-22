# Extension research source brief

Date: 2026-07-22

## User decisions that control the review

- The system targets Indian cash equities through Zerodha and US cash equities through Alpaca in V1.
- It is long-only, cash-only, deterministic for eligibility, quantity, price, risk, and execution.
- Research agents may discover and interpret opportunities but may not directly size or execute them.
- Initial live capital envelopes are INR 50,000 in Zerodha and USD 200 in Alpaca, fully expendable before broker-scoped stopping. Policy gates are immutable, configurable releases rather than hard-coded 30-day waits.
- The target is a complete end-to-end first live vertical slice in nine days, not evidence of mature alpha in nine days.
- Current portfolio analysis is now a mandatory V1 capability.
- Future extensions must include additional asset classes, with FX as the first example, and user/profile support so the Trading OS can cover a family.

## Existing-design observations

- The current Trading OS design has a global versioned portfolio snapshot and already mentions an `own + immediate-family` account allowlist, but it does not yet define household, legal owner, user, permission, mandate, account, sleeve, or consolidated-view boundaries.
- The current design explicitly rejects FX, derivatives, leverage, and margin. Any FX support is future scope and must not weaken the V1 cash-equity invariants.
- The ontology already has portfolio-context evidence and a stable instrument belief boundary, but its identity model is primarily issuer/security/instrument oriented.
- The live-domain audit separates broad opportunity discovery from the stricter tradable allowlist and requires a mandatory `TradabilityRiskPacket` before deterministic decisioning.

## Primary-source anchors

### Zerodha portfolio capability

Kite Connect documents `/portfolio/holdings` for long-term equity holdings and `/portfolio/positions` for current net/day positions. Holdings include ISIN, quantity, T1 quantity, pledged/collateral quantities, average price, last price, and P&L. Positions include quantities, product, multiplier, average and last price, realized/unrealized P&L and day activity. Selling delivery holdings may require the account owner's depository authorisation.

Source: https://kite.trade/docs/connect/v3/portfolio/

Kite's holdings API does not identify the originating external strategy or product; order/position provenance must be maintained by the Trading OS. Kite Connect also does not provide a complete back-office historical P&L API through the portfolio endpoint, so current snapshots alone are insufficient to reconstruct authoritative lifetime tax lots and historical performance.

Supporting broker forum discussions:
- https://kite.trade/forum/discussion/13438/get-only-kite-holdings-not-smallcase-and-others
- https://kite.trade/forum/discussion/14821/pnl-calculation

### Alpaca portfolio capability

Alpaca's positions endpoint returns current open positions with cost basis, quantity, and live market value. Closed positions stop being queryable through that endpoint, so activity/fill history and the Trading OS ledger are required for durable history. Alpaca also exposes account portfolio history and account activities such as fills, dividends and transfers.

Sources:
- https://docs.alpaca.markets/us/reference/getallopenpositions
- https://docs.alpaca.markets/us/reference/portfolio-history
- https://docs.alpaca.markets/us/docs/alpaca-mcp-server

### Family and account isolation

Kite Connect is account-scoped. Broker guidance says separate client accounts require separately mapped apps/credentials; one account's API key cannot place an order in another account. Current broker guidance for the 2026 static-IP regime describes limited sharing arrangements for specified immediate-family relationships through separate apps, but this is broker/exchange policy and must be reverified before activation.

Sources:
- https://kite.trade/forum/discussion/13510/can-we-connect-multiple-account-using-single-api
- https://kite.trade/forum/discussion/12072/multiple-family-account
- https://kite.trade/forum/discussion/15873/regarding-market-protection-and-static-ip

Design consequence: a household may aggregate analysis, but every account must retain its own legal owner, credentials, consent/mandate, capital envelope, orders, positions, broker reconciliation, compliance state and kill switch. A household aggregate is a derived view, not a custody account.

### India-resident FX constraints

RBI's forex FAQ says resident persons may undertake forex transactions only with authorised persons and for permitted purposes. Electronic transactions must use RBI-authorised ETPs or recognised Indian exchanges. It also says LRS remittance cannot be used for margin or margin calls for overseas online forex trading.

Source: https://www.rbi.org.in/scripts/FS_FAQs.aspx?Id=146

NSE currency-derivative specifications demonstrate that FX is not just another equity symbol: contracts have a base/quote pair, contract unit, tick size, trading session, expiry cycle, settlement reference, and margin framework.

Sources:
- https://www.nseindia.com/static/products-services/currency-derivatives-contract-specification-inr
- https://www.nseindia.com/static/products-services/currency-derivatives-parameters

Design consequence: do not implement future FX by switching on generic overseas spot/CFD brokers. Use an asset-class capability and jurisdiction policy that admits only a currently verified, legal venue/product/account combination. FX also introduces margin, expiry/roll, settlement, pair exposures, multi-currency P&L and 24x5/event-clock concerns.

## Required research posture

- Distinguish observations supported by the anchors from architectural inferences.
- Treat broker forums as implementation clues, not immutable law.
- Never assume that family membership grants trading authority.
- Never let household consolidation blur legal ownership or cross-subsidise loss budgets.
- Prefer deep, stable domain seams over V1 shortcuts that force data migration or safety redesign.
- Preserve the relational deterministic hot path and the ontology as a versioned research/retrieval layer.
