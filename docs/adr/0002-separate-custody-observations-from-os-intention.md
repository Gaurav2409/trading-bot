---
status: accepted
---

# Keep broker custody observations separate from OS intention and history

Current portfolio analysis stores immutable broker observations and append-only OS intention/history
under an explicit field-authority and reconciliation contract. They are not fused into one mutable
truth because broker snapshots cannot prove OS provenance or complete lifetime history, while the OS
ledger cannot overrule current broker-reported custody, restrictions, orders or cash.
