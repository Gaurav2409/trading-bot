# Trading OS Live V1 — Operator Runbook

> Live activation is a **policy/readiness operation**, never a base-URL or
> `ALPACA_PAPER=false` edit. Every live write requires a current, broker-scoped
> `LiveAuthorityReceipt`.

## 1. Bring up services

```bash
make services-up          # Postgres/TimescaleDB, Valkey, Fuseki, Neo4j (localhost only)
# If host port 5432 is taken, set POSTGRES_HOST_PORT (e.g. 5442) and align DATABASE_URL.
```

## 2. Apply migrations

```bash
DATABASE_URL=postgresql+asyncpg://trading:trading@localhost:5432/trading uv run alembic upgrade head
```

## 3. Read-only observation and reconciliation

```bash
uv run python -m trading_os.app.cli observe --account-id kite-1
uv run python -m trading_os.app.cli observe --account-id alpaca-1
uv run python -m trading_os.app.cli reconcile --account-id kite-1
uv run python -m trading_os.app.cli reconcile --account-id alpaca-1
```

## 4. Dry-effect cycle (no broker writes)

```bash
uv run python -m trading_os.app.cli run-cycle --account-id kite-1
```

## 5. Readiness issuance (per broker)

```bash
uv run python -m trading_os.app.cli readiness --all-accounts --read-only
```

A broker receives a receipt only when its readiness report shows every required
item true: correct live account/endpoint, credential/session, broker + data
entitlements, static-IP/tag where applicable, current account flags, fresh
compliance profile, current portfolio completeness, reconciliation,
capital/exposure/promotion releases, kill-switch exercise, protection-protocol
exercise, code commit + schema version, and operator approval.

## 6. Issue and verify T0 authority (per broker)

```bash
uv run python -m trading_os.app.cli issue-live-authority --account-id kite-1
uv run python -m trading_os.app.cli verify-live-authority --account-id kite-1
```

Issue independently for each broker. Zerodha uses the INR 50,000 T0 envelope;
Alpaca uses the USD 200 T0 envelope. If only one broker passes, activate it and
keep the other **entry-disabled** — never weaken the failing broker's gate.

## 7. Shutdown

```bash
uv run python -m trading_os.app.cli halt --account-id kite-1
uv run python -m trading_os.app.cli halt --account-id alpaca-1
make services-down
```
