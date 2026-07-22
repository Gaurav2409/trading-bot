---
status: accepted
---

# Keep the agent run ledger canonical over framework checkpoints

LangGraph checkpoints are valuable for resuming work, but they do not by themselves record the immutable release closure, evidence snapshot, applicability, provider identity, budgets, capability boundaries, admission, and compatibility mapping required by the Trading OS. Treating checkpoints or vendor traces as audit truth would introduce a competing state authority.

The project-owned `AgentRunLedger` is the canonical append-only record. The harness emits events around every node and external boundary. LangGraph checkpoints remain disposable recovery projections and must reconcile with ledger events before resume. Any disagreement fails closed; a checkpoint cannot overwrite canonical history.

This duplicates some execution metadata. We accept the duplication because recovery convenience and governed audit truth have different responsibilities and retention requirements.
