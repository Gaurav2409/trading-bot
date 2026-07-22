// Typed operator-console API client. Read-only views plus narrowly-scoped
// control actions; the console never submits a natural-language order.

export interface AccountBudget {
  accountId: string;
  broker: "kite" | "alpaca";
  currency: string;
  envelopeMinor: number;
  deployedMinor: number;
  tier: string;
  cumulativeLossMinor: number;
}

export interface PortfolioHealth {
  accountId: string;
  freshness: "COMPLETE" | "DEGRADED" | "MISSING" | "STALE" | "CONFLICT";
  externalPositions: { symbol: string; quantity: number; provenance: string }[];
}

export interface Candidate {
  candidateId: string;
  symbol: string;
  setup: string;
  eligible: boolean;
  blockedReasons: string[];
}

const BASE = import.meta.env?.VITE_API_BASE ?? "http://127.0.0.1:8000";

export async function fetchBudgets(): Promise<AccountBudget[]> {
  const res = await fetch(`${BASE}/budgets`);
  return res.json();
}
