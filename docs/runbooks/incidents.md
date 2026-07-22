# Incident Runbook

All incidents share one rule: **a safety fault fences new exposure immediately**
(ENTRY_DISABLED / MANAGEMENT_ONLY / HALTED) while reconciliation and
broker-native protection keep running. The OS never guesses a liquidation
quantity when custody is unavailable.

| Incident | Immediate state | Action |
|---|---|---|
| Stale custody | `ENTRY_DISABLED` | `cli observe` to refresh; if custody still unobservable, keep broker-native protection, alert owner, keep reconciling. Do not infer a close quantity. |
| Reconciliation conflict | `ENTRY_DISABLED` | Inspect the typed `ReconciliationDifference`; resolve the underlying broker/OS divergence; never patch ledger history. |
| Protection failure | `MANAGEMENT_ONLY` | Protection is not confirmed for the reconciled quantity. Repair broker-native stop; do not submit a guessed close. |
| Credential / session expiry (Kite) | `ENTRY_DISABLED` | Operator re-does Kite interactive login; refresh access token into the secret store (no TOTP automation). |
| Data entitlement loss (Alpaca SIP) | `REDUCE_ONLY` for affected discovery | Constrain US discovery to delayed-SIP/EOD; do not treat IEX as whole-market. |
| Broker outage | `ENTRY_DISABLED` | Pause submissions; keep reconciling; resume only after read-only readiness re-passes. |
| Unknown order effect | `ENTRY_DISABLED` for the symbol | `OUTCOME_UNKNOWN` blocks new exposure on that symbol until reconciled. |
| Full-envelope loss (100%) | Sleeve `HALTED` | Sleeve stops until a new funded, owner-approved envelope release exists. Loss/drawdown/history are never reset. |

## Loss-response ladder (per sleeve, from policy)

- 5% daily sleeve loss → no-new-entry cooldown + retrospective
- 20% cumulative drawdown → mandatory retrospective
- 40% → promotion disabled
- 60% → demote at least one tier
- 80% → return to T0 + explicit owner restart
- 100% → sleeve stop until new funded envelope

## Emergency stop

```bash
uv run python -m trading_os.app.cli halt --account-id <account>
```

This fences new exposure before any acknowledgement; open positions retain
broker-native protection and continue to reconcile.
