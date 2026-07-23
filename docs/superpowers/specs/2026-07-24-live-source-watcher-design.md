# Live NSE/BSE SourceWatcher + Early-Signal Tier — Design

**Status:** Approved (design)

**Date:** 2026-07-24

**Scope:** Implementation-ready design for the live source-ingestion control plane the P0 tracer left as a gap. Adds live official NSE/BSE announcement capture (evidence-bearing) and an early-signal calendar tier (attention-only), plus a committed catalog of credible India-market event sources. Does not change the analysis seam, the decision hot path, or the ontology promotion path.

**Motivation:** The P0 corporate-event tracer proved the analysis → evidence → decision flow, but the only `SourceWatcher` implementation is `FixtureSourceWatcher` (offline). A real corporate event — e.g. *Tanla Platforms announces quarterly results; the stock re-rates the next session* — would only be seen if the record were hand-fed. For an event-reactive swing OS this is table stakes. This design wires live ingestion within the governed control plane of spec §14.

**Architecture basis:** [Domain-agent architecture spec §14](2026-07-23-domain-agent-architecture.md), [ADR-0008 (tool/network containment)](../../adr/0008-sandbox-tools-as-node-scoped-capabilities-and-gateway-remote-mcp.md). Consumes existing types: `SourceRecord`, `SourceCoveragePolicyRelease`, `reconcile_coverage`, the `filing_watcher` scheduled job, and the recorded NSE/BSE adapters.

---

## 1. Decision summary

Add live ingestion in **two clearly-ranked epistemic tiers**, both behind one transport abstraction and both governed by effective-dated source-policy releases:

- **Tier 1 — Official (evidence-bearing).** A `LiveSourceWatcher` polls the exchange-wide NSE + BSE "latest corporate announcements" feeds on the existing 5-minute `filing_watcher` cadence, normalizes via the same logic as the recorded adapters, seals immutable `SourceRecord`s, deduplicates, and appends them to the store. These records carry positive evidentiary weight.
- **Tier 2 — Early-signal (never evidence).** A `CalendarWatcher` polls the NSE/BSE board-meeting / results calendar and emits `WatchScheduled` intents that arm a tighter watch and may raise an alert. A `WatchScheduled` is structurally incapable of becoming an `EvidencePacket`.

Transport is abstracted behind a `SourceFetchPort` with a real integration-tagged HTTP fetcher and a deterministic fixture fetcher, so all watcher logic is tested offline. A committed catalog ranks all credible India-market event sources; only the two official announcement channels and the board-meeting calendar are wired live in this phase. Everything else in the catalog is a ranked candidate for governed onboarding (spec §14.3).

**Constitutional invariant preserved:** agents never fetch; the watcher seals records before any analysis run; no early-signal source can carry positive evidentiary weight; no executable number is introduced anywhere (the price move is market data on the deterministic side, never an input the LLM asserts).

## 2. Goals and non-goals

### Goals
1. Capture real NSE/BSE official corporate announcements on a schedule, sealed into immutable `SourceRecord`s identical in shape to the recorded adapters' output.
2. Poll exchange-wide (all listed issuers); let applicability + the account tradable allowlist decide relevance downstream.
3. Emit early-signal `WatchScheduled` intents from the board-meeting/results calendar that schedule attention but never become evidence.
4. Keep all watcher logic transport-agnostic and offline-deterministic; isolate live HTTP behind an integration-tagged fetcher.
5. Deliver a committed, ranked catalog of credible India-market event sources (official, aggregator, wire tiers) with endpoint, authority, latency, entitlement/legal, and parser-difficulty metadata.
6. Preserve cutoff integrity, fail-safe degradation, and idempotent re-polling.

### Non-goals
- The `fundamental` domain profile (analysis of the *numbers* inside a results filing). Deferred — see the P1 gap note in the P0 plan.
- Wiring aggregator/wire early-signal sources live (catalog only; governed onboarding later).
- Any change to the analysis seam, `admit_packet`, decision sizing/risk, live-authority, or the ontology promotion path.
- Intraday/tick ingestion. This is EOD/event-cadence swing scope.
- Auto-promotion of a captured event into a position. Position formation remains the existing gated path (eligibility gates/ranks; deterministic code sizes; owner-approved feature activation governs any learned behaviour).

## 3. The two tiers

```
                    ┌─ Tier 1  LiveSourceWatcher ─→ normalize ─→ seal SourceRecord ─→ dedup ─→ store
 filing_watcher ────┤                                                                     │
   (5m job)         │                                                                     └─→ reconcile_coverage → analysis (cutoff-safe, unchanged)
                    └─ Tier 2  CalendarWatcher ───→ WatchScheduled intent ─→ scheduler (arm watch) / alert
                                                    (NEVER a SourceRecord, NEVER evidence)
```

- Tier 1 records are the only tier that can reach `reconcile_coverage` and the analysis harness.
- Tier 2 intents are a distinct type with no path to `EvidencePacket` construction. They can (a) cause the scheduler to poll a given issuer more tightly around the expected date, and (b) raise an operator alert for a high-signal upcoming event. Nothing more.
- A `WatchScheduled` is a *hypothesis about the future*; the official filing is the *fact*. Only the fact is admissible.

## 4. Components and boundaries

| Unit | Responsibility | Depends on |
|---|---|---|
| `SourceFetchPort` (Protocol) | `fetch(endpoint, since) -> RawFetchResult` — transport only, no normalization | — |
| `RawFetchResult` (frozen model) | raw bytes/payload + fetch metadata (status, fetched_at, endpoint) | — |
| `HttpSourceFetcher` | Real NSE/BSE fetch: session/cookie handshake, retry with backoff, rate-limit, result-size cap, timeout. **Integration-tagged.** | httpx |
| `FixtureSourceFetcher` | Replays recorded raw payloads keyed by endpoint. Deterministic, offline. | recorded fixtures |
| `_normalize` core (in `corporate_event_sources`) | Shared normalizer extracted from the recorded adapters: issuer/category/dissem-time/content → `_NormalizedRecord`. Live + recorded seal identically. | — |
| `LiveSourceWatcher` | Poll official feed via port → normalize → seal → dedup → return new `SourceRecord`s; emit an attempted/omitted signal on fetch/parse failure | fetch port, normalize core, `SeenRecordStore`, clock |
| `CalendarWatcher` | Poll calendar via port → parse upcoming events → emit `WatchScheduled` intents | fetch port, clock |
| `WatchScheduled` (frozen model) | issuer, event kind, expected window, source authority tier, provenance. No evidentiary fields. | — |
| `SeenRecordStore` (Protocol + in-memory impl) | Idempotent dedup by `(channel, record_id)` and `payload_hash` | — |
| Source catalog | Ranked credible-resource catalog (doc) | — |

**Targeted refactor (in scope):** extract a shared `_normalize` core so `RecordedNseAnnouncementAdapter`/`RecordedBseAnnouncementAdapter` and the live path produce byte-identical `SourceRecord`s from the same fields. This is what makes the live path verifiable offline against recorded fixtures. No behavioural change to the recorded adapters (their existing tests must stay green).

## 5. Data flow — the Tanla results case, concretely

1. **T-3 days:** `CalendarWatcher` reads "Tanla board meeting on Jul 21 to consider financial results" → emits `WatchScheduled(issuer=Tanla, event=results, expected≈2026-07-21, tier=official_calendar)`. The scheduler arms a tighter announcement watch for that issuer around the window; an operator alert may fire. **No evidence exists yet.**
2. **T0 (results filed):** Tanla files results on NSE and BSE. On the next `filing_watcher` cycle (≤5 min), `LiveSourceWatcher` pulls the exchange-wide latest-announcements feed via `SourceFetchPort`, finds the two new announcements, runs the shared normalizer, seals two `SourceRecord`s (`channel=nse`/`bse`, `kind=results`, shared `source_family_id`, `available_at=`dissemination time, `received_at=`now), dedups against the seen-store, and appends to the record store.
3. **Decision run:** unchanged path. `reconcile_coverage` finds both applicable official channels captured and in-cutoff → `COMPLETE`; the `corporate_event` harness produces `EvidencePacket(assessment="material_event_supported")`; that evidence *gates and ranks* Tanla as a candidate; deterministic code sizes; compliance + live-authority gate the order. **No number crossed the seam; the price move was never an input.**

The sole new capability is that step 2 now runs for real instead of requiring a hand-fed fixture.

## 6. Error handling, entitlement, and safety

- **Fail-safe, not fail-open.** A fetch failure, anti-bot block, timeout, or parse error produces an *attempted-but-omitted* signal for the channel, never a fabricated or partial record. Downstream, missing applicable official coverage is already handled as degraded/insufficient evidence with no positive influence.
- **Cutoff integrity.** `received_at` is stamped at seal time from an injected clock; `available_at` is the disclosure's dissemination time. No look-ahead is introduced.
- **Idempotency.** Re-polling re-seals identically (content-addressed `payload_hash`); the `SeenRecordStore` drops duplicates. Safe to run every 5 minutes indefinitely.
- **Entitlement / legal.** The catalog records each source's terms (NSE/BSE market-data policy, rate limits, subscription requirements). `HttpSourceFetcher` honours a configurable cadence and per-source rate limit. The design explicitly surfaces that production use of exchange feeds may require a data subscription rather than hiding it. No credentials or tokens are committed.
- **Governed onboarding.** New catalog sources enter `EXPERIMENTAL` → shadow → owner-approved `SourceCoveragePolicyRelease` before going live (spec §14.3). This phase wires only official-announcements + board-meeting calendar.
- **Plane separation.** This is the ingestion control plane, distinct from the agent tool-capability plane (ADR-0008). Agents still never fetch; they read only sealed records.

## 7. Testing strategy

- **Offline-first, deterministic.** All watcher logic — normalize, seal, dedup, cutoff stamping, coverage interaction, calendar → `WatchScheduled` — is tested against `FixtureSourceFetcher` with recorded NSE/BSE payloads. No network, no credentials, CI-green.
- **Shared-normalizer parity.** A test asserts the live path and the recorded adapter seal byte-identical `SourceRecord`s from the same source fields (the refactor's safety net).
- **Idempotency & fail-safe.** Re-poll yields no duplicate; a failing fetch yields an attempted-omitted signal, not a record.
- **Live fetcher.** Thin, `@pytest.mark.integration`, excluded from the default gate (as the existing Postgres integration tests are). Exercises the real session handshake against the live endpoints; run on demand, not in the offline gate.
- **Tier separation.** A test asserts a `WatchScheduled` intent has no path to `EvidencePacket` (type-level and flow-level).

## 8. The credible-resource catalog

`docs/research/19-india-event-source-catalog.md` — every credible India-market event source, tiered and ranked, each row carrying: endpoint/access method, authority tier, typical latency vs. the event, entitlement/legal note, parser difficulty, and dedup `source_family` mapping.

- **Official (evidence-bearing):** NSE corporate-announcements endpoint; BSE corporate-announcements endpoint; NSE/BSE board-meeting & results calendar; exchange RSS; SEBI (SCORES / UDiFF / intermediary filings) where applicable.
- **Aggregators (early-signal, catalog-only this phase):** Trendlyne, Screener.in, Tickertape, MoneyControl earnings/board-meeting calendars.
- **Wires (early-signal, catalog-only):** PTI, Reuters, Bloomberg corporate-action feeds.

Wired live now: NSE official announcements, BSE official announcements, NSE/BSE board-meeting calendar. All others are ranked candidates for later governed onboarding.

## 9. Hard-to-reverse decisions

- `SourceFetchPort` as the single transport seam (real HTTP vs. fixture never leaks above it). Consistent with ADR-0008's insistence on a local adapter per external access.
- The evidence/early-signal tier split as a **type boundary**, not a convention — `WatchScheduled` cannot be constructed into an `EvidencePacket`.
- Exchange-wide polling (not watchlist-scoped) as the official-tier universe, so events on not-yet-tracked names are still captured.

## 10. Acceptance criteria

- Live official NSE/BSE announcements are captured on the `filing_watcher` cadence and sealed identically to the recorded adapters (parity test green).
- Exchange-wide polling; applicability + allowlist decide relevance downstream; no analysis-seam change.
- `CalendarWatcher` emits `WatchScheduled` intents with no path to evidence (tier-separation test green).
- All watcher logic offline-deterministic; live HTTP integration-tagged and out of the default gate.
- Fetch/parse failure degrades safely (attempted-omitted), never fabricates a record; cutoff integrity preserved; re-poll idempotent.
- The committed catalog ranks all credible sources with the required metadata; only official-announcements + calendar are wired live.
- No secrets/tokens committed; entitlement requirements surfaced.
