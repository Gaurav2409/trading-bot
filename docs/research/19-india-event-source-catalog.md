# India Event Source Catalog — Ranked Credible Sources

**Version:** 1.0  
**Date:** 2026-07-23  
**Status:** Committed (governs which sources may be onboarded to the live NSE/BSE SourceWatcher)

---

## Tiering Rule

> **Only official exchange/regulator records carry evidentiary weight.**
>
> A `SourceRecord` sealed from a Tier-1 Official source may enter `reconcile_coverage`, produce an
> `EvidencePacket`, and influence the deterministic hot path.
>
> Early-signal sources (Tier-2 Aggregators and Tier-3 Wires) **schedule attention only**. They emit
> `WatchScheduled` intents — a hypothesis about a future event. A `WatchScheduled` is structurally
> incapable of becoming an `EvidencePacket` and can never carry positive evidentiary weight,
> regardless of how reliable the underlying source has proven to be in practice.
>
> This split is a **type boundary**, not a convention. Mixing tiers — treating an aggregator
> calendar entry as confirmation of a corporate action — is a constitutional violation of the
> architecture.

---

## Tier 1 — Official (Evidence-Bearing)

Sources in this tier are the authoritative primary disclosures mandated under SEBI Listing
Obligations and Disclosure Requirements (LODR) Regulations. An announcement on these channels
is the legally recognised act of disclosure.

| Source | Channel / Endpoint | Access Method | Authority Tier | Typical Latency vs Event | Entitlement / Legal | Parser Difficulty | `source_family` Mapping |
|---|---|---|---|---|---|---|---|
| **NSE Corporate Announcements** | `https://www.nseindia.com/companies-listing/corporate-filings-announcements` (JSON API: `https://www.nseindia.com/api/corp-info?symbol=<SYM>&corpType=announcement` and the exchange-wide listing `https://www.nseindia.com/api/liveEquity-derivatives?index=nse500`) | HTTP GET with session cookie (`nsit`, `nseappid`) acquired via browser-like handshake on `www.nseindia.com`. Rotating cookie; must be refreshed periodically. No OAuth. No official public API — scraping under NSE's Terms of Use. Rate-limit: informal; honour ≥5 s between polls; production bulk-feed use requires an NSE data subscription agreement. | Official — primary exchange disclosure (SEBI LODR) | 0–5 min post-filing (NSE stamp time is the disclosure moment) | NSE Terms of Use prohibit redistribution; production exchange-feed use may require a data subscription. No credentials/tokens stored in this repo. | Medium — JSON; field layout changes without notice; cookie handshake brittle; need to handle anti-bot 403 and retry with exponential backoff | `nse_announcement` |
| **BSE Corporate Announcements** | `https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w` (query params: `pageno`, `strCat`, `strPrevDate`, `strScrip`, `strSearch`, `strtodate`, `strType`) | HTTP GET; no auth header required for the public API endpoint. Pagination via `pageno`. Returns JSON with announcement metadata + PDF attachment URL. Rate-limit: informal; honour ≥5 s between polls; bulk/automated production use may require a BSE data subscription. | Official — primary exchange disclosure (SEBI LODR) | 0–5 min post-filing (BSE stamp time is the disclosure moment) | BSE Terms of Use prohibit redistribution; production exchange-feed use may require a data subscription. No credentials/tokens stored in this repo. | Low-Medium — JSON; stable schema; PDF attachment requires separate fetch for full text | `bse_announcement` |
| **NSE Board-Meeting & Results Calendar** | `https://www.nseindia.com/api/event-calendar` (query params: `index`, `from`, `to`) | HTTP GET with the same session cookie as the NSE announcements endpoint. Returns upcoming board meetings, record dates, dividend events across all listed companies. | Official — exchange-published forward calendar (SEBI LODR-mandated board-meeting notice) | 2–10 days before event (companies must notify exchange ≥2 working days ahead of board meeting; results notice typically 5–7 days prior) | NSE Terms of Use; no redistribution; production use may require subscription. No credentials/tokens stored. | Medium — JSON; same cookie-rotation challenge as announcements endpoint | `nse_calendar` |
| **BSE Corporate Actions & Board-Meeting Calendar** | `https://api.bseindia.com/BseIndiaAPI/api/DefaultData/w` with `scripcode` and `Scode`; event calendar at `https://api.bseindia.com/BseIndiaAPI/api/CorporateAction/w` | HTTP GET; no auth header. Returns corporate actions (dividend, bonus, rights, split) and upcoming board meetings. | Official — exchange-published forward calendar | 2–10 days before event | BSE Terms of Use; no redistribution; production use may require subscription. No credentials/tokens stored. | Low-Medium — JSON; relatively stable schema | `bse_calendar` |
| **NSE / BSE Exchange RSS Feeds** | NSE: `https://www.nseindia.com/content/equities/security_announcements.xml`; BSE: `https://www.bseindia.com/Msource/RSSFeeds/BSECorporateAnnouncements.aspx` | Standard HTTP GET; no auth; RSS/Atom XML. NSE feed is intermittently maintained; BSE feed is more reliable. Treat as a low-cost heartbeat, not a primary source. | Official — exchange-vended RSS (secondary delivery of the same LODR filings) | 0–15 min post-filing (RSS refresh lag variable) | Same NSE/BSE Terms of Use as the API endpoints. No credentials/tokens stored. Rate-limit: honour ≥60 s between fetches per feed. | Low — standard RSS/Atom XML; strip HTML from `<description>` | `nse_rss` / `bse_rss` |
| **SEBI SCORES (Complaints / Adjudication)** | `https://scores.sebi.gov.in/` — no public machine-readable API; orders and adjudication notices published as PDFs under `https://www.sebi.gov.in/enforcement/orders/` | Web scrape of SEBI website; PDF download for full text. Session-less public access. No rate-limit documentation; honour ≥30 s between fetches. | Official — regulator primary source (enforcement / adjudication) | Days to weeks after the underlying event (enforcement orders are retrospective) | Public domain government records; no redistribution restriction on SEBI orders as official regulatory instruments. No credentials/tokens stored. | High — PDF; unstructured text; inconsistent layout across order types | `sebi_scores` |
| **SEBI UDiFF / Intermediary Filings** | UDiFF portal: `https://udiff.sebi.gov.in/` (Uniform Document Interface for Filings). Accepts filings from depositories, RTA, listed entities. No public bulk-download API documented as of 2026. | Manual or portal-based access; no documented public API. Monitor SEBI circular `SEBI/HO/CFD/CMD1/CIR/P/2023` and successor circulars for API availability. | Official — SEBI-mandated structured filing (emerging standard) | Variable; filings submitted per SEBI timelines (same-day to T+1 for material events) | Subject to SEBI access terms; public filings are public record. No credentials/tokens stored. | High — evolving schema; no stable public API | `sebi_udiff` |

---

## Tier 2 — Aggregators (Early-Signal, Catalog-Only This Phase)

These sources aggregate or reprocess official exchange data, adding structured calendars,
formatted tables, and search UIs. They are often faster or easier to parse than the raw exchange
endpoints but are **derivative**: their data originates from the same NSE/BSE filings.

Because they are not the authoritative act of disclosure, they can never serve as evidence. They
are cataloged here as ranked candidates for `CalendarWatcher` integration in a later governed
onboarding phase (spec §14.3).

| Source | Channel / Endpoint | Access Method | Authority Tier | Typical Latency vs Event | Entitlement / Legal | Parser Difficulty | `source_family` Mapping |
|---|---|---|---|---|---|---|---|
| **Trendlyne** | `https://trendlyne.com/equities/upcoming-announcements/` and `https://trendlyne.com/equities/quarterly-results-calendar/` | Web scrape; no documented public API. HTML tables. Bot-protection present (Cloudflare). | Aggregator — derived from NSE/BSE disclosures | 0–30 min reprocessing lag after official filing | Trendlyne ToS prohibit automated scraping without a commercial data agreement. Personal/research use ambiguous. No credentials/tokens stored. | Medium-High — HTML scrape; anti-bot; layout changes | `trendlyne_calendar` |
| **Screener.in** | `https://www.screener.in/company/<NSE_SYMBOL>/` (company page with quarterly results, annual reports); no public bulk-events API | Web scrape or login-based session. HTML. Screener.in has unofficial JSON endpoints (e.g. `https://www.screener.in/api/company/<id>/`) that are undocumented and may break. | Aggregator — derived from BSE/NSE and company filings | 1–60 min lag after official filing | Screener.in ToS: personal use permitted; automated bulk use requires explicit approval. No credentials/tokens stored. | Medium — relatively clean HTML; unofficial JSON brittle | `screener_in` |
| **Tickertape** | `https://www.tickertape.in/stocks/<symbol>/events` and earnings calendar at `https://api.tickertape.in/corporate/events` (undocumented) | Web scrape or undocumented API. Session-based. ET Money / Morningstar India ecosystem. | Aggregator — derived from exchange data | 1–60 min lag after official filing | Tickertape ToS prohibit automated scraping; data is licensed from exchange/intermediaries. No credentials/tokens stored. | Medium — JSON via undocumented API; may require auth headers | `tickertape_calendar` |
| **MoneyControl Earnings / Board-Meeting Calendar** | `https://www.moneycontrol.com/stocks/marketstats/earnings/` and `https://mc.moneycontrol.com/mccode/common/autosuggesion.php` for symbol resolution; event calendar endpoint not publicly documented | Web scrape; heavy anti-bot (CAPTCHA, JS challenge). MoneyControl is part of the Network18 / Reliance group — strong enforcement of ToS against scrapers. | Aggregator — derived from exchange data + editorial | 0–30 min lag for calendar events; editorial content may precede official filing | MoneyControl ToS explicitly prohibit automated scraping. Commercial data licensing available. No credentials/tokens stored. | High — heavy anti-bot; JS rendering required; layout changes frequently | `moneycontrol_calendar` |

---

## Tier 3 — Wires (Early-Signal, Catalog-Only This Phase)

Newswire services publish corporate announcements as they are filed, sometimes picking up
embargoed or pre-filing information (e.g. press releases distributed simultaneously with
exchange filing). They are the fastest human-readable signal but remain early-signal: a wire
story is not the exchange-filed record and cannot be treated as evidence.

All Tier-3 sources require a paid subscription for machine-readable feeds. Catalog-only this phase.

| Source | Channel / Endpoint | Access Method | Authority Tier | Typical Latency vs Event | Entitlement / Legal | Parser Difficulty | `source_family` Mapping |
|---|---|---|---|---|---|---|---|
| **PTI (Press Trust of India)** | PTI syndication feed; no public API. Machine-readable access via PTI data licensing or redistribution through financial data aggregators (Refinitiv, Bloomberg, etc.) | Licensed feed (XML/JSON) via PTI subscriber agreement or through a licensed aggregator. No free API. | Wire — independent newswire; not an official exchange disclosure | 0–10 min from press release / filing announcement; may coincide with or slightly precede NSE/BSE stamp | PTI is a paid-subscription newswire. Redistribution prohibited without license. No credentials/tokens stored. | Medium — XML/JSON feed if licensed; otherwise HTML scrape of ptinews.com (unreliable, ToS violation risk) | `pti_wire` |
| **Reuters (LSEG) Corporate Actions / Newsflow** | Reuters News API (LSEG Data & Analytics): `https://api.refinitiv.com/data/news/v1/headlines` and related endpoints; requires Refinitiv/LSEG subscription | OAuth2 via LSEG Developer Platform. Requires a Refinitiv Eikon or LSEG Workspace subscription plus API access entitlement. | Wire — international newswire with India corporate coverage | 0–5 min from filing / press release; editorial stories 5–30 min | LSEG/Reuters News API: paid subscription required; licensed for specific use cases; redistribution prohibited. Pricing: Eikon terminal (~USD 22k/yr) or API-only tier. No credentials/tokens stored. | Low (once licensed) — well-documented JSON REST API; stable schema | `reuters_wire` |
| **Bloomberg Corporate Action Feeds** | Bloomberg B-PIPE / SAPI corporate action events (`Corp Action` field mnemonics: `DVD_CASH_GROSS`, `EPS_ACTUAL`, `NEXT_EARNINGS_DATE`, etc.); Bloomberg News (`BN` monitor for India equities) | Bloomberg Terminal API (BLPAPI / B-PIPE) or Bloomberg Enterprise Access Point (EAP). Requires Bloomberg Professional Service subscription + API entitlement. | Wire — international financial data provider; India corporate action coverage | Corporate action data: T+0 to T+1 vs official filing; Bloomberg News: 0–15 min | Bloomberg Terminal (~USD 24k/yr per seat) or B-PIPE enterprise agreement. Redistribution strictly prohibited. No credentials/tokens stored. | Low (once licensed) — BLPAPI is well-documented; B-PIPE is production-grade | `bloomberg_wire` |

---

## Wired Live Now

The following sources are active in the current `LiveSourceWatcher` and `CalendarWatcher` implementation:

- **NSE official announcements** (`nse_announcement`)
- **BSE official announcements** (`bse_announcement`)
- **NSE/BSE board-meeting calendar** (`nse_calendar` / `bse_calendar`)

All other sources in this catalog are ranked candidates for later governed onboarding under the
`EXPERIMENTAL` → shadow → owner-approved `SourceCoveragePolicyRelease` process (spec §14.3).
No other source is wired live in this phase.

---

## Security and Entitlement Notice

- **No credentials, API tokens, cookies, session keys, or secrets of any kind are stored in this
  repository.** All runtime secrets (if any are required) are loaded exclusively from the macOS
  Keychain or an encrypted environment file that is never committed.
- **Production use of NSE/BSE exchange feeds may require a formal data subscription agreement**
  with the respective exchange. The endpoints listed here are used under the exchanges' implicit
  allowance for low-frequency informational access; bulk, high-frequency, or redistributed use
  is subject to the exchanges' market-data policies and may require a paid licence.
- Rate limits stated per source reflect best-known informal thresholds. The `HttpSourceFetcher`
  honours a configurable per-source cadence and applies exponential backoff on 429 / 403
  responses.
- The `CalendarWatcher` and `LiveSourceWatcher` poll on the 5-minute `filing_watcher` cadence —
  well within the informal rate boundaries for official announcement endpoints.

---

*Catalog authored 2026-07-23. Review before onboarding any new source; all additions must follow
the governed onboarding process in spec §14.3.*
