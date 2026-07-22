# Verifier V3 — structural integrity, scope, and nine-day realism

## Verdict

**REVIEW.** Both MoA chunks contain useful architecture, complete requested sections, and strong
adversarial coverage. They are not controlling without correction because each self-audit falsely
claims compliance with its 8–15 KB size contract, and several recommendations conflict with
already approved direct-live, two-broker, configurable-gate, and ontology-boundary decisions.

## Structural checks

- Chunk 1 contains headings 1–6 and 20 adversarial cases, but is 25,113 bytes rather than 8–15 KB.
- Chunk 2 contains headings 7–12 and 21 red-team cases, but is 21,229 bytes rather than 8–15 KB.
- Both end markers say size compliance passed. Treat their content checks as useful and their
  overall PASS as untrusted.
- The output is divisible into a concise controlling synthesis; the raw chunks should remain
  evidence, not become specifications verbatim.

## Controlling corrections

1. **Both brokers, not one account, on Day 9.** Chunk 1's Day-9 acceptance says one account. The
   approved target has Zerodha and Alpaca live concurrently under independent broker/account
   envelopes and kill switches.
2. **No fixed paper campaign or calendar-count gate.** Chunk 1's Day-8 protocol exercise is valid
   as bounded preflight, but Chunk 2's fixed five-day and ten-session evidence gates conflict with
   configurable, evidence-gated expansion. Counts, windows, and promotion requirements belong in
   immutable policy releases. Safety invariants and protocol tests remain mandatory.
3. **Use the approved semantic seam.** Chunk 1 revives `ExposureVector`; the ontology design
   replaced it with a tighten-or-veto-only `RiskOverlaySet`. Portfolio analysis should emit a
   typed `PortfolioRiskOverlaySet` or inputs to it, not restore the legacy contract.
4. **Portfolio analysis is a hard gate.** The strongest MoA recommendation is controlling:
   every exposure-increasing decision must bind an account-scoped, freshness-checked snapshot
   containing broker holdings/positions, open orders, cash, settlement restrictions, OS ledger
   provenance, and manual/external positions. Missing broker segments or open orders block new
   exposure for that account while reconciliation and permitted risk reduction continue.
5. **Do not overstate the broker snapshot.** Current holdings/positions are custody observations,
   not complete lifetime history. Cost basis, strategy attribution, and historical P&L carry
   per-line provenance/completeness and never get silently blended.
6. **Household analytics may tighten, never loosen or net.** Chunk 2 says household analytics may
   never affect account risk. That is too strong. With explicit owner consent and a versioned
   policy assignment, a `HouseholdRiskOverlay` may reduce an account's allowed exposure. It may
   never increase limits, net positions/cash/margin across owners, or create cross-account funding.
7. **Safe capability deactivation uses `DRAINING`.** Chunk 2's human override prerequisite can
   delay an emergency stop. Deactivation must immediately reject exposure-increasing orders,
   keep valuation/reconciliation/protection active, and permit only policy-valid risk reduction
   until positions are flat. Human review is recorded but is not a prerequisite for stopping new
   exposure.
8. **Capability policy and account assignment are separate.** A reusable
   `AssetClassCapabilityRelease` should define jurisdiction/venue/broker/instrument/data/risk/
   execution requirements. An `AccountCapabilityAssignment` binds an account, mandate, limits,
   capital envelope, and effective time. Do not embed a single `account_id` in the reusable release.
9. **The stable kernel still needs typed amounts.** The kernel should not know asset-specific lot,
   pip, expiry, or margin rules, but it must own precise `Money`, `CurrencyCode`, typed quantity
   wrappers, event identity, clocks, and policy references. Saying it contains no quantity or P&L
   semantics at all is too absolute for a coherent ledger and order state machine.
10. **Family-ready V1 is schema and isolation, not family execution.** Install Party/Person,
    UserProfile, Household, Membership, LegalOwner, BrokerConnection, BrokerageAccount, mandate,
    permission, policy assignment, and derived view boundaries now. The V1 UI can expose one
    principal. Multi-owner read aggregation and execution remain separately gated.
11. **Legal ownership must allow more than natural persons.** Prefer `LegalParty` (Person or future
    legal entity such as HUF/trust/company) as account owner. `Household` remains an analytical/
    consent group and does not itself imply ownership.
12. **Kill/close paths cannot assume a fresh pull succeeds.** They should attempt unconditional
    broker refresh, but if custody cannot be observed, keep broker-native protection active,
    freeze new exposure, alert the owner, and reconcile until authoritative state returns.

## Nine-day acceptance interpretation

The nine-day target is credible only as a complete first vertical slice with shallow breadth:

- both broker connections, current-state import, reconciliation and independent kill switches;
- broad discovery plus tradable allowlists and mandatory tradability packets;
- current portfolio analysis as a pre-trade dependency;
- deterministic eligibility, sizing, protection and execution;
- versioned configurable exposure/promotion/completeness policies;
- ontology kernel and relational baseline, with graph projections non-authoritative;
- family and multi-asset domain seams present but disabled;
- direct T0 live activation only after bounded static, replay, contract and protocol checks.

It does not include mature causal inference, proven adaptive allocation, automated family
execution, or FX execution.

VERDICT: REVIEW
