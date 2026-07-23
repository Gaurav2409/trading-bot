# India-Based Retail Algo Trader: Broker Landscape Research Report

> Research stream 1 of 3 (Sonnet web-research gather). Compiled 2026-07-18.
> Raw sources: `/tmp/trading-os-research/broker-landscape/`
> NOTE: pending MoA adversarial verification pass. Items flagged in "Key Gaps" section need verbatim verification.

---

## 1. Zerodha Kite Connect (India — NSE/BSE)

### API Capabilities
Kite Connect is a REST + WebSocket API suite exposing order execution, portfolio management, market quotes, and historical data. Primary programmatic trading interface for Indian retail algo traders.

- **Protocol:** REST HTTP (form-encoded requests, JSON responses) + WebSocket for streaming quotes
- **Auth model:** OAuth-style — `api_key` + `api_secret` per developer app; login redirects to Kite web returning `request_token`; token exchange via POST to `/session/token` yields per-session `access_token` (valid one trading day). SHA-256 checksum (`api_key + request_token + api_secret`) required. Source: https://kite.trade/docs/connect/v3/user/
- **Order types:** MARKET, LIMIT, SL (stop-loss limit), SL-M (stop-loss market). Varieties: `regular`, `amo`, `co`, `iceberg`, `auction`. Products: CNC (delivery), NRML (F&O overnight), MIS (intraday), MTF. Validity: DAY, IOC, TTL. Source: https://kite.trade/docs/connect/v3/orders/
- **Exchanges:** NSE, BSE, NFO, BFO, CDS, BCD, MCX, MF. Source: https://kite.trade/docs/connect/v3/user/
- **WebSocket:** Binary over `wss://ws.kite.trade`. Up to 3,000 instruments/connection, 3 connections/API key. Modes: ltp/quote/full. Source: https://kite.trade/docs/connect/v3/websocket/
- **Postbacks:** Async order status to registered webhook.
- **SDKs:** Python, Go, Java, JavaScript, PHP, R. Source: https://kite.trade/docs/connect/v3/

### Cost
**~₹2,000/month** per API application (community-confirmed; pricing page JS-rendered, returned thin content). URL: https://kite.trade/connect/pricing/

### Rate Limits
Not explicitly published in fetched docs. Community figure: **~3 API calls/second** for order placement; data APIs have own limits. WebSocket: 3 connections, 3,000 subscriptions/connection.

### Paper / Sandbox
**No true paper trading or sandbox — LIVE ONLY.** No simulated environment. Testing must be against live exchange (real money) or manual Kite web. Known limitation. → **This makes SimulatedBrokerAdapter mandatory for India paper trading.**

### Fractional Shares
No. Indian exchanges don't support fractional shares.

---

## 2. SEBI February 2025 Retail Algo Trading Circular

**Circular:** SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013
**Title:** "Safer participation of retail investors in Algorithmic trading"
**Date:** February 4, 2025
**Source:** https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html

Page fetched (title/number/date confirmed) but body is JavaScript-rendered; PDF attachment returned 404. SEBI homepage ticker references "Settlement Scheme for Association with Algo Platforms, 2025 (SSAAP-2025)" — indicating enforcement against non-compliant retail algo channels.

**Requirements as reported in Indian financial press (consistent with circular title, NOT verbatim-verified):**
1. All retail algo orders must be tagged as algo orders at exchange level.
2. Each algo strategy must be registered/approved with the broker before use — broker vets the algo.
3. Retail investor does NOT need separate SEBI registration but must use a SEBI-registered broker's approved algo platform; **broker is the gatekeeper**.
4. Brokers must identify/monitor/halt retail algo activity.
5. APIs allowing order placement (Kite Connect) are the primary channel; unregistered third-party auto-placement was the gap this addressed.

**CAVEAT:** Circular body not directly fetched. MoA pass should verify exact text.

---

## 3. Alpaca Markets (US Stocks — India Accessibility)

### India Accessibility: YES (confirmed)
- Alpaca "How to Open a Live Trading Account as a Non-US Resident" (Mar 2026): "We support the services to 195+ countries." Source: https://alpaca.markets/learn/live-trading-account-non-us
- BrokerChooser (Nov 2025, fact-checked): "Yes, you can open an account at Alpaca Trading if you're an Indian resident." Source: https://brokerchooser.com/broker-reviews/alpaca-trading-review/alpaca-trading-india
- **No US SSN required.** W-8BEN form, passport, PAN (local Tax ID), selfie/KYC. Source: https://alpaca.markets/learn/live-trading-account-non-us
- **Minimum deposit:** $1 after approval.
- **Funding:** LRS wire (no ACH for Indian residents); wire withdrawals $50; USD-only.

### Paper Trading (Sandbox)
**Yes — full paper trading, free, no live account or US residency needed.** Separate API key + base URL (`https://paper-api.alpaca.markets`). Identical API spec paper vs live. $100k virtual, resettable. Real-time IEX data. Full WebSocket. Source: https://docs.alpaca.markets/docs/paper-trading

### API
- REST (HTTPS) + WebSocket. Auth: API key + secret headers.
- Order types: Market, Limit, Stop, Stop-Limit, Trailing Stop; OCO; Bracket. Source: https://alpaca.markets/support/which-apis-does-alpaca-offer
- **Fractional shares: Yes** ($1 min notional). Source: https://alpaca.markets/support/fractional-shares
- Markets: US stocks/ETFs (~7,000/~4,000), options, crypto. No Indian markets.
- Extended hours: Yes. Rate limits: increasable on request. Commission: $0.

### PDT
Applies regardless of residency. Use **cash account** (PDT-exempt) to swing trade freely (tradeoff: T+1 settlement). Source: https://alpaca.markets/support/alpaca-cash-accounts

---

## 4. Interactive Brokers (IBKR) — India to US

### India Accessibility: YES — Standard Legal Route
- India entity: Interactive Brokers India Pvt. Ltd. — https://www.interactivebrokers.co.in/
- **LRS:** Up to **USD 250,000/financial year** for overseas investment.
- **TCS:** Budget 2025 raised TCS-free threshold ₹7L→₹10L/yr; beyond ₹10L, 20% TCS (creditable against income tax). Source: https://www.winvesta.in/blog/investors/how-to-open-a-us-brokerage-account-from-india-step-by-step-guide
- Docs: PAN (Foreign Tax ID on W-8BEN), Aadhaar, passport, bank statements, W-8BEN.
- Standard route for experienced traders wanting global markets. Groww's latest
  help centre says new US-stocks activation is **paused**; it is therefore not a
  current US API alternative. See `10-groww-broker-evaluation.md`.

### IBKR Paper Account
**Yes — supports both TWS API and Client Portal API.** "We recommend using the paper account for initial testing." Source: https://interactivebrokers.github.io/cpwebapi/

### API Options
1. **TWS API** (socket, Python/Java/.NET/C++) — connects to TWS desktop; `ib_insync` popular Python wrapper. https://interactivebrokers.github.io/tws-api/
2. **Client Portal Web API** (REST + WebSocket) — local headless gateway. https://interactivebrokers.github.io/cpwebapi/ (now IBKR Campus docs)
3. No API fee; market-data subs may cost.
- **ib_insync works with live+paper for any IBKR holder regardless of country.**

---

## 5. Domestic India→US Brokers
- **INDmoney:** No programmatic API. App-only (DriveWealth backend). Not suitable for algo.
- **Vested:** No public API. App-only (DriveWealth). Not suitable for algo.
- **Groww US:** New-account activation is paused. Groww India now has a public
  trading API; see the targeted evaluation in
  `docs/research/10-groww-broker-evaluation.md`.

---

## 6. Angel One SmartAPI (India — NSE/BSE)
- Root: `https://apiconnect.angelone.in`. REST (CORS-enabled, unlike Kite) + WebSocket.
- Auth: TOTP-based (2FA mandatory).
- Features: login/token, funds/margins, GTT rules, orders (place/modify/cancel/book), portfolio (holdings/positions/EDIS), market data (option Greeks, gainers/losers, historical, WebSocket Streaming 2.0), instruments. Source: https://smartapi.angelbroking.com/docs
- SEBI: INZ000161534.
- **Cost:** Generally free for Angel One holders (no ₹2,000/mo like Kite) — community-sourced, not verbatim-confirmed.
- **Sandbox:** Not advertised. Likely live-only.
- Fractional: No.

---

## 7. US PDT Rule — Swing/Positional Impact
**PDT triggers only on intraday round-trips (same-day buy+sell), NOT swing/positional held overnight.**
- PDT = 4+ day trades in 5 rolling business days AND >6% of total trades → must maintain $25,000 equity.
- Overnight-held trade is NOT a day trade. <$25k accounts can hold overnight indefinitely.
- **Cash accounts are entirely PDT-exempt** (tradeoff: T+1 settlement).
- FINRA/SEC rule for US margin accounts. Source: Alpaca FAQ, BrokerChooser.
- (Unverified: a TradeStation FB post headline suggested SEC eliminated PDT — cookie-walled, treat as unconfirmed.)

---

## India-Accessibility Verdict Per Broker

| Broker | Markets | API | India Live | Paper/Sandbox | Cost (API) | Fractional | Key Constraint |
|--------|---------|-----|-----------|---------------|-----------|-----------|----------------|
| **Zerodha Kite** | NSE,BSE,MCX,CDS | REST+WS | Yes (demat) | **None — live only** | ~₹2,000/mo | No | No sandbox; SEBI algo reg via broker |
| **Alpaca** | US stk/ETF/opt/crypto | REST+WS | **Yes** (195+ ctry, W-8BEN, no SSN) | **Yes — free, no live acct needed** | $0 comm | Yes ($1) | PDT (use cash acct); LRS wire only |
| **IBKR** | US+global | TWS + CP REST | Yes (India entity, LRS) | **Yes — full API** | No API fee | Limited | LRS $250k/yr; TCS >₹10L |
| **Angel One** | NSE,BSE,MCX,CDS | REST+WS | Yes (demat) | Likely none | Free | No | TOTP 2FA; SEBI algo reg via broker |
| **INDmoney** | US | None (app) | Yes | No | — | Yes | No API — unsuitable |
| **Vested** | US | None (app) | Yes | No | — | Yes | No API — unsuitable |
| **Groww (India)** | CASH,F&O (MCX unverified) | REST + NATS WS | Yes | None documented | ₹499/mo* | No | Shadow-only: prove CNC protection and acknowledgement-loss recovery; US activation paused |

---

## Key Gaps / Verification Flags for MoA Pass
1. **SEBI Feb 2025 circular body** — not fetched (JS-rendered/PDF 404). Requirements need verbatim verification.
2. **Kite pricing** — ₹2,000/mo community-known, page failed. Verify at kite.trade/connect/pricing/.
3. **PDT elimination** — TradeStation FB headline unverified (cookie wall).
4. **Angel One pricing/rate limits** — pages thin.
5. **IBKR India entity specifics** — page returned only cookie policy (JS). Whether India-entity accounts trade US directly needs verification.
6. **Groww Trade API** — **resolved by targeted primary-source/MoA pass:** live
   routing remains blocked on CNC GTT protection and acknowledgement-loss
   idempotency tests; see `10-groww-broker-evaluation.md`.

\* Pricing checked 2026-07-21; recheck before purchase.
