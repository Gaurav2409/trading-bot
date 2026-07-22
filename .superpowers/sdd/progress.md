# Nine-Day Two-Broker Live V1 — SDD Progress Ledger

**Branch:** `codex/live-v1`
**Worktree:** `.worktrees/codex-live-v1` (branched from `50f2ba2`)
**Controlling plan:** `docs/superpowers/plans/2026-07-22-nine-day-live-v1-implementation.md`
**Controlling spec:** `docs/superpowers/specs/2026-07-22-live-v1-architecture-amendment.md`
**ADRs:** 0001 evidence-gated two-broker live; 0002 custody vs OS intention; 0003 product vs semantic activation

> The `2026-07-21` plans (paper-first, EOD-only, ontology-sequenced) are SUPERSEDED.
> The raw MoA drafts returned NO-GO and are not specifications.

## Alembic chain (single head required)

`0001_event_ledger` → (later migrations appended per task, never reset)

## Nine-day delivery map

| Day | Tasks | Exit evidence | Status |
|---|---|---|---|
| 1 | 1–3 | Clean toolchain; kernel, identity, immutable policy contracts pass | ✅ merged (PR #1) |
| 2 | 4–6 | Event ledger, broker contract suite, read-only adapters pass | ✅ done |
| 3 | 7–8 | Portfolio normalization, completeness, analysis gate pass | ✅ done |
| 4 | 9–10 | Validated market snapshots, discovery coverage, tradability packets | ✅ done |
| 5 | 11 | Relational champion, ontology kernel, typed agent seam pass | ✅ done |
| 6 | 12–13 | Deterministic sizing/risk + India/US compliance pass replay | ✅ done |
| 7 | 14–15 | Durable execution, protection, kill states, broker write adapters | ⬜ |
| 8 | 16–17 | Reconciliation, retrospective, API, operator console e2e | ⬜ |
| 9 | 18 | Both broker T0 readiness receipts + reversible activation runbook | ⬜ |

## Task progress

| Task | Title | Status | Commit | Review |
|------|-------|--------|--------|--------|
| 1 | Repository baseline + one-command verification | ✅ done | d96ba9b | day-1 boundary |
| 2 | Typed kernel + immutable event envelope | ✅ done | 66cede5 | day-1 boundary |
| 3 | Legal parties, account authority, policy releases | ✅ done | fecdc83 | day-1 boundary |
| 4 | Append-only Postgres event store + replay | ✅ done | a88e919 | day-2 boundary |
| 5 | Normalized broker observation/execution ports | ✅ done | 44a1672 | day-2 boundary |
| 6 | Read-only Kite + Alpaca adapters | ✅ done | cc2eb73 | day-2 boundary |
| 7 | Portfolio field authority + normalization | ✅ done | 3dcdd2e | day-3 boundary |
| 8 | Portfolio snapshots, completeness, analysis gate | ✅ done | 80991df | day-3 boundary |
| 9 | Validated multi-clock market-data snapshots | ✅ done | cef617d | day-4 boundary |
| 10 | Broad discovery, CoverageReceipts, tradability packets | ✅ done | c1828ad | day-4 boundary |
| 11 | Typed research evidence, relational champion, ontology kernel | ✅ done | a2b7888 | day-5 boundary |
| 12 | Deterministic sizing, risk, CAS reservations | ✅ done | a12fc35 | day-6 boundary |
| 13 | India + US compliance gates | ✅ done | 832388a | day-6 boundary |
| 14 | Durable execution, kill states, protection | ✅ done | cd0735d | day-7 boundary |
| 15 | Capability-gated Kite + Alpaca writes | ✅ done | 0eba3c4 | day-7 boundary |
| 16 | Reconciliation + retrospective loop | ✅ done | ebca19a | day-8 boundary |
| 17 | Scheduler, API, operator console | ✅ done | 7470542 | day-8 boundary |
| 18 | Two-broker replay, readiness, scoped T0 authority | ⬜ not started | — | — |

## Non-negotiable invariants (guardrails for every task)

- Research emits no quantity/price/target weight/order/executable command.
- Every exposure-increasing decision binds fresh, partitioned, current portfolio state.
- Broker custody observations and OS intention/history stay distinct; reconciliation never silently picks a winner.
- Each order belongs to one account, capital envelope, policy set, kill generation.
- Household views never pool custody/cash/buying power/collateral/loss/orders.
- Policy changes create immutable releases; never reset loss/drawdown/history.
- Relational retrieval is the permanent champion; RDF/Neo4j are rebuildable projections.
- Semantic activation and product/account execution capability are independent AND-gates.
- Operational safety faults fence new exposure regardless of remaining loss budget.
- India: never assume algo market orders are permitted; limit/protected order types only.
- No live write without a broker-scoped, current `LiveAuthorityReceipt`.
- Family + non-equity execution deny-by-default in V1.

## Log

- 2026-07-22: New controlling plan (nine-day live V1) supersedes 2026-07-21 plans. Stale
  `codex/trading-world-ontology` worktree/branch removed (was empty, clean, no unique commits).
  Fresh worktree `.worktrees/codex-live-v1` created from `50f2ba2` on branch `codex/live-v1`.
  All 9 controlling documents read in full. Ledger reset to the 18-task nine-day plan.
