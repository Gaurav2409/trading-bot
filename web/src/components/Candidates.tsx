import type { Candidate } from "../api";

// Shows each candidate and, in plain language, why it is eligible or blocked.
export function Candidates({ candidates }: { candidates: Candidate[] }) {
  return (
    <section aria-label="Candidates">
      <h2>Opportunity candidates</h2>
      {candidates.map((c) => (
        <div key={c.candidateId} data-testid={`candidate-${c.symbol}`}>
          <strong>{c.symbol}</strong> — {c.setup}{" "}
          {c.eligible ? (
            <span data-testid="eligible">eligible</span>
          ) : (
            <span data-testid="blocked">blocked: {c.blockedReasons.join(", ")}</span>
          )}
        </div>
      ))}
    </section>
  );
}
