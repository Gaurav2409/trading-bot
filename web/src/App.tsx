import { useState } from "react";
import type { AccountBudget, Candidate, PortfolioHealth } from "./api";
import { Portfolio } from "./components/Portfolio";
import { Candidates } from "./components/Candidates";
import { DecisionTrace } from "./components/DecisionTrace";
import { RiskControls } from "./components/RiskControls";
import { Retrospectives } from "./components/Retrospectives";

const SEED_BUDGETS: AccountBudget[] = [
  {
    accountId: "kite-1",
    broker: "kite",
    currency: "INR",
    envelopeMinor: 5_000_000,
    deployedMinor: 1_000_000,
    tier: "T0",
    cumulativeLossMinor: 0,
  },
  {
    accountId: "alpaca-1",
    broker: "alpaca",
    currency: "USD",
    envelopeMinor: 20_000,
    deployedMinor: 0,
    tier: "T0",
    cumulativeLossMinor: 0,
  },
];

const SEED_HEALTH: PortfolioHealth[] = [
  {
    accountId: "kite-1",
    freshness: "COMPLETE",
    externalPositions: [{ symbol: "TESTCO", quantity: 10, provenance: "manual_matched_broker" }],
  },
  { accountId: "alpaca-1", freshness: "COMPLETE", externalPositions: [] },
];

const SEED_CANDIDATES: Candidate[] = [
  { candidateId: "c1", symbol: "CROPSTER", setup: "momentum_acceleration", eligible: true, blockedReasons: [] },
  {
    candidateId: "c2",
    symbol: "ILLIQ",
    setup: "momentum_acceleration",
    eligible: false,
    blockedReasons: ["circuit_locked", "insufficient_liquidity"],
  },
];

export function App() {
  const [killModes, setKillModes] = useState<Record<string, string>>({
    "kite-1": "active",
    "alpaca-1": "active",
  });

  const disableEntries = (accountId: string) =>
    setKillModes((prev) => ({ ...prev, [accountId]: "entry_disabled" }));

  return (
    <main>
      <h1>Trading OS — Operator Console</h1>
      <Portfolio budgets={SEED_BUDGETS} health={SEED_HEALTH} />
      <Candidates candidates={SEED_CANDIDATES} />
      <DecisionTrace
        steps={[
          { label: "Candidate", detail: "CROPSTER momentum_acceleration" },
          { label: "Tradability", detail: "eligible on kite-1" },
          { label: "Sizing", detail: "5 shares (fixed-fractional)" },
          { label: "Risk", detail: "sector overlay 1.0" },
          { label: "Reservation", detail: "held @ CAS v7" },
        ]}
      />
      {SEED_BUDGETS.map((b) => (
        <RiskControls
          key={b.accountId}
          accountId={b.accountId}
          killMode={killModes[b.accountId]}
          onEntryDisable={disableEntries}
        />
      ))}
      <Retrospectives
        items={[
          { decisionId: "d1", rootCause: "discovery_coverage", summary: "BSE-only name now covered" },
        ]}
      />
    </main>
  );
}
