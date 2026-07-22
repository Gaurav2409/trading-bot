---
status: accepted
---

# Model issuer as a time-scoped role, not an essential subclass of legal party

`core.ttl` declared `Issuer rdfs:subClassOf LegalParty`, making "issuer" an essential kind: every
issuer is permanently a legal party and nothing else. That is too coarse for the trading world. A
legal entity acts as issuer for a specific security over a specific interval, and the same entity may
simultaneously be a counterparty, a supplier, an index constituent, or an acquirer. Under RDFS,
`rdfs:domain` on `issuedBy` also silently infers any subject to be an Issuer, so the subclass choice
compounds an inference hazard.

We model a stable `LegalEntity` separately from a time-scoped `IssuerRole` that binds an entity to an
issued security over a validity interval. Roles carry their own temporal validity and provenance; the
convenient `Issuer` view, if kept, is an explicitly governed inferred class rather than an asserted
essence. This mirrors the approved architecture's separation of identity from role and lets one entity
hold many concurrent, independently-dated roles.

The trade-off is more classes and one indirection (entity → role → security) instead of a flat
subclass. We accept that because collapsing role into essence cannot represent role changes, dual
listings, or an entity's non-issuer relationships, and would leak incorrect type inferences into any
graph projection. Existing V1 relational decisioning is unaffected — this governs the semantic
projection only, which is never the execution truth.
