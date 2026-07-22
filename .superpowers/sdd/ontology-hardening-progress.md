# Ontology Hardening — SDD Progress Ledger

**Branch:** `codex/ontology-hardening` (from `df1c2a2`, merged nine-day V1)
**Trigger:** `docs/research/16-core-ttl-schema-audit.md`
**Plan:** `docs/superpowers/plans/2026-07-22-ontology-hardening-implementation.md`
**ADRs:** 0004 (split schema vs instance validation), 0005 (time-scoped IssuerRole)

## Task progress

| Task | Tier | Title | Status | Commit |
|------|------|-------|--------|--------|
| H1 | P0 | Split ontology-schema vs instance-snapshot validation | ✅ done | 7f28ee3 |
| H2 | P0 | Model EvidencePacket links; remove no-op shape | ✅ done | 7f28ee3 |
| H3 | P0 | Field rules: tz, cardinality, payload_hash, name alignment | ✅ done | 7f28ee3 |
| H4 | P0 | Ontology/version metadata + release manifest | ✅ done | 7f28ee3 |
| H5 | P0 | Negative safety tests | ✅ done | 7f28ee3 |
| H6 | P1 | Identity/tradability module | ⬜ planned |
| H7 | P1 | Time/provenance module | ⬜ planned |
| H8 | P1 | Evidence/reasoning module | ⬜ planned |
| H9 | P1 | Events/relationships module | ⬜ planned |
| H10 | P1 | Technical/fundamental/sentiment markers | ⬜ planned |
| H11 | P1 | Portfolio-context module | ⬜ planned |
| H12 | P2 | Competency-query pack | ⬜ planned |
| H13 | P2 | Projection parity + challenger evaluation | ⬜ planned |
| H14 | P2 | Governed promotion | ⬜ planned |

## Verification (P0)

`make verify` green: ruff ✓, mypy --strict ✓ (79 files), pytest ✓ (131 passed).

## Log

- 2026-07-22: P0 (H1–H5) implemented from audit 16 with ADR-0004/0005. Relational
  champion unchanged; RDF/Neo4j remain rebuildable projections. P1/P2 are specified
  as future tasks in the plan and not executed in this PR.
