import type { AccountBudget, PortfolioHealth } from "../api";

interface Props {
  budgets: AccountBudget[];
  health: PortfolioHealth[];
}

// Shows Zerodha and Alpaca separately; account partitions are preserved and
// resources are never pooled.
export function Portfolio({ budgets, health }: Props) {
  return (
    <section aria-label="Portfolio">
      <h2>Portfolio (per account)</h2>
      {budgets.map((b) => {
        const h = health.find((x) => x.accountId === b.accountId);
        return (
          <div key={b.accountId} data-testid={`account-${b.accountId}`} data-broker={b.broker}>
            <h3>{b.broker.toUpperCase()} — {b.accountId}</h3>
            <p>
              Sleeve budget: {b.currency} {(b.envelopeMinor - b.deployedMinor) / 100} available
              of {b.envelopeMinor / 100} (tier {b.tier})
            </p>
            <p>Cumulative loss: {b.currency} {b.cumulativeLossMinor / 100}</p>
            <p>Freshness: {h?.freshness ?? "UNKNOWN"}</p>
            <ul>
              {(h?.externalPositions ?? []).map((p) => (
                <li key={p.symbol} data-testid={`external-${p.symbol}`}>
                  {p.symbol}: {p.quantity} ({p.provenance})
                </li>
              ))}
            </ul>
          </div>
        );
      })}
    </section>
  );
}
