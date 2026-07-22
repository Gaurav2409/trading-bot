# Day-10 Policy Change Runbook

Policy is immutable and effective-dated. A change **never** edits a prior
release, and **never** resets cumulative loss, drawdown, evidence, trades or
historical receipts. It appends a new release with `supersedes` set and a safe
activation boundary.

## Increase a ceiling (requires real funding)

1. Fund the broker account and reconcile: `cli observe` + `cli reconcile`.
2. Author a new `CapitalEnvelopeRelease` with a new `release_id`,
   `supersedes = <prior release_id>`, and `effective_from` at the activation
   boundary.
3. Activate (owner-authenticated): `cli activate-policy --account-id <acct>`.
4. Prior decisions remain bound to the old release id; the loss meter is
   unchanged.

## Reduce a ceiling below current exposure

1. Author the reduced release (new id, `supersedes` set).
2. On activation the account enters `REDUCE_ONLY` until exposure is compliant.
3. No position is force-closed by the policy change itself; reduction happens
   through normal risk-reducing flow.

## Worked example (Kite capital v1 → v2)

```text
kite-capital-v1: capital INR 50,000, effective_from D0
kite-capital-v2: capital INR 75,000, supersedes kite-capital-v1,
                 effective_from D10 (after funding + reconciliation)
```

- The Day-0..Day-9 decisions still reference `kite-capital-v1`.
- Cumulative loss carried into Day 10 is preserved, not reset.
- Agents may *propose* v2 but can never activate it; activation is
  owner-authenticated.

## Invariants that are never configurable

Account identity/authority, deterministic price/quantity, append-only history,
idempotency, reconciliation, protection, kill switches, temporal validity,
long-only cash-equity V1, and denial of unverified products/routes.
