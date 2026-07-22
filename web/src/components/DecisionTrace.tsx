interface TraceStep {
  label: string;
  detail: string;
}

// Human-readable decision trace: candidate -> coverage -> evidence -> portfolio
// -> sizing -> risk/compliance -> reservation -> execution -> reconciliation.
export function DecisionTrace({ steps }: { steps: TraceStep[] }) {
  return (
    <section aria-label="Decision trace">
      <h2>Decision trace</h2>
      <ol>
        {steps.map((s, i) => (
          <li key={i}>
            <strong>{s.label}:</strong> {s.detail}
          </li>
        ))}
      </ol>
    </section>
  );
}
