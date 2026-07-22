# Domain-Agent Shadow-Run Runbook (P0 corporate-event tracer)

**Status:** Shadow-only. P0 output is observational. It **cannot** activate a
`DecisionFeatureActivation`, size a position, or create an order. The relational
retrieval champion remains the permanent decision authority for every outcome
below, including catastrophic ones.

This runbook is the operator-readable companion to the P0 corporate-event
tracer. It explains how to read a shadow run's outcome without opening code,
raw JSON, framework traces, or provider logs.

## What the tracer does

For one `ResearchQuestion` (an instrument, a decision cutoff, a frozen
`data_snapshot_id`, and a fixed set of `source_record_ids`), the tracer:

1. resolves the effective immutable `corporate_event` profile and its compiled
   trajectory closure;
2. gathers the sealed official `SourceRecord`s in scope (SEC 8-K, NSE, BSE);
3. deterministically normalizes issuer identity, cutoff, and channel family;
4. judges materiality, support, contradiction, and missing channels;
5. deterministically reconciles channel coverage;
6. validates the categorical seam (no executable number may cross);
7. admits an `EvidencePacket` via the existing `admit_packet()`.

Every terminal path that is not a catastrophe crosses admission and returns a
packet. The packet carries a categorical `assessment` and an
`eligibility_effect` — never a price, quantity, target, expected return,
position weight, conviction multiplier, or order intent.

## Reading the outcome

Each shadow run resolves to exactly one coverage interpretation. The
`eligibility_effect` tells the operator whether the evidence may exert positive
influence (in a future, separately-gated activation) or is `neutral`.

```text
complete       all applicable mandatory official channels captured
degraded       at least one applicable official channel captured and at least one missing
contradictory  material official statements conflict; no positive influence
insufficient   all applicable mandatory official channels missing; no positive influence
catastrophic   release closure or canonical ledger unavailable; port returns None
inapplicable   source is not expected for this issuer/listing at the cutoff
```

### Interpretation rules (constitutional, spec §15–§16)

- **Single-listing is not a deficiency.** An NSE-only security is `complete`
  when NSE is captured; BSE is `inapplicable`, not missing. The same holds for a
  BSE-only security. SEC is mandatory only when the issuer/security/filing
  relationship makes it applicable at the cutoff.
- **Dual-listed, one channel missing** is `degraded`: usable context, but the
  packet's `eligibility_effect` is `neutral` — degraded evidence has no positive
  influence.
- **Conflicting official records** are `contradictory`. All citations are
  preserved; `eligibility_effect` is `neutral` until deterministic resolution or
  a source correction.
- **All mandatory applicable channels missing** is `insufficient`
  (`missing_applicable_official_sources`), `eligibility_effect` `neutral`.
- **A record whose `available_at` is after the cutoff is not captured.** Cutoff
  and snapshot are frozen per run; resume and replay never resolve newer state.
  A late record therefore reads as `insufficient`, not as new evidence.
- **Duplicate/same-origin deliveries** improve delivery coverage but are **not**
  independent corroboration.

### Expected agent failures are admitted, never `None`

Provider timeout, refusal, unsupported capability, malformed output, tool
failure, MCP drift, and budget exhaustion each become an **admitted explicit-
missing packet** with `eligibility_effect` `neutral`:

```text
agent_provider_timeout       provider timed out
agent_malformed_output       provider returned output that failed the output schema
agent_budget_exhausted       run or node budget was exhausted
```

A categorical-seam violation (an attempt to smuggle an executable number, or a
citation outside `source_record_ids`, or an instrument change) becomes an
admitted `categorical_seam_violation` packet **plus** a safety ledger event; its
`source_record_ids` are emptied and its effect is `neutral`.

### Only catastrophe returns `None`

`None` is reserved for a corrupt/unavailable canonical ledger or an unresolved
immutable release closure (e.g. no effective profile for the domain at the
cutoff). `None` still leaves the relational champion fully operational.

## Verifying a shadow run is reproducible

P0 is offline and deterministic. The acceptance suite runs the entire recorded
fixture matrix through the unchanged `ResearchAgentPort`, twice (production and
replay wirings), and asserts byte-identical packets and identical canonical
ledger event hashes. No test requires provider credentials or network access.

Exact offline command:

```bash
pytest tests/integration/agents/test_p0_acceptance.py -v
```

Full P0 regression (all non-database suites):

```bash
pytest tests/unit tests/contract tests/integration/agents \
  tests/integration/research tests/integration/ontology/test_relational_fallback.py -v
```

Both must pass with no network, no credentials, and no live database.

## Enabling / disabling shadow mode

Shadow mode is **disabled by default** (`Settings().agent_shadow_enabled is
False`). The application container constructs neither a harness nor a provider
client unless shadow mode is explicitly enabled *and* provider credentials are
present; absent credentials, the container declines rather than reaching for the
network. Offline replay wiring is a separate, explicit composition
(`build_shadow_domain_agent`) used by tests and dry-runs.

Because P0 is shadow-only, enabling it changes nothing downstream: no decision
activates and no order is created from tracer output.
