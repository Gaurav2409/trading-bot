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
| H0 | P1 | Module dependency manifest (owl:imports DAG) | ✅ done | fd2894c |
| H6a | P1 | Identity canonicalization (IdentityAssertion, no owl:sameAs) | ✅ done | 73db75a |
| H6b | P1 | Tradability / capability | ✅ done | 73db75a |
| H7a | P1 | Time module (OWL-Time; decisionCutoffAt; receipt-vs-cutoff) | ✅ done | 73db75a |
| H7b | P1 | Provenance module (PROV-O; correction/supersession lineage) | ✅ done | 73db75a |
| H9 | P1 | Events/relationships (typed RelationshipAssertion) | ✅ done | 73db75a |
| H8 | P1 | Evidence/reasoning (source-family, admission, contradiction target) | ✅ done | 73db75a |
| H8b | P1 | Belief-state + DecisionFeatureSet projection (imports H9/H10) | ✅ done | 73db75a |
| H11 | P1 | Portfolio-projection context (sh:closed allowlist) | ✅ done | 73db75a |
| H10 | P1 | Technical/fundamental/sentiment markers | ✅ done | 73db75a |
| H11b | P1 | Governance/release module | ✅ done | 73db75a |
| H12 | P2 | Competency-query pack (per-module goldens + cutoff cases) | ✅ done | 38e216b |
| H13 | P2 | Projection parity + challenger evaluation (champion null hyp.) | ✅ done | 38e216b |
| H14 | P2 | Governed promotion + demotion (DecisionFeatureDeactivation) | ✅ done | 38e216b |

## Verification (P0)

`make verify` green: ruff ✓, mypy --strict ✓ (79 files), pytest ✓ (131 passed).

## Verification (P1)

`make verify` green: ruff ✓, mypy --strict ✓ (80 files), pytest ✓ (146 passed).
11 modules; import closure OK across the real DAG.

## Log

- 2026-07-22: P0 (H1–H5) implemented from audit 16 with ADR-0004/0005. Relational
  champion unchanged; RDF/Neo4j remain rebuildable projections. P1/P2 are specified
  as future tasks in the plan and not executed in this PR.
- 2026-07-22: Hermes MoA `deep-research` improvement review of P1/P2 (3/3 reference
  models LIVE, GO). Findings folded into the plan: added H0 dependency manifest;
  reordered to H6→H7→H9→H8→H11→H10; split H6→H6a/H6b and H7→H7a/H7b; split belief-state
  into H8b; added H11b governance/release; hardened H12–H14 (champion null hypothesis,
  DecisionFeatureDeactivation, auto-demotion). Review saved at
  `docs/research/raw/ontology-hardening/17-p1p2-hermes-moa-review.md`.
