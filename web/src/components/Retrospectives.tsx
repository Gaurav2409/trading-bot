interface Retrospective {
  decisionId: string;
  rootCause: string;
  summary: string;
}

export function Retrospectives({ items }: { items: Retrospective[] }) {
  return (
    <section aria-label="Retrospectives">
      <h2>Retrospective findings</h2>
      {items.map((r) => (
        <div key={r.decisionId} data-testid={`retro-${r.decisionId}`}>
          <strong>{r.rootCause}</strong>: {r.summary}
        </div>
      ))}
    </section>
  );
}
