# Trading World

The shared language for representing tradable instruments, market evidence, hypotheses, and reasoning outputs without confusing semantic knowledge with trading decisions.

## Identity and tradability

**Legal Entity**:
A legally recognized organization or person that may own assets, incur obligations, or control other entities.
_Avoid_: Company, stock

**Issuer**:
A Legal Entity responsible for issuing a Security.
_Avoid_: Company, ticker

**Security**:
A fungible financial instrument issued under a defined set of rights and terms.
_Avoid_: Stock symbol, company

**Listing**:
A venue-specific admission of a Security for trading, identified independently from the Security and its Issuer.
_Avoid_: Ticker, stock

**Ticker**:
A time-bounded venue alias for a Listing; it is not a stable identity.
_Avoid_: Instrument ID, company ID

## Evidence and world state

**Source Record**:
An immutable captured item supplied by a publisher or vendor, including its origin and availability times.
_Avoid_: Fact

**Evidence Span**:
The exact portion of a Source Record that supports or refutes a Claim.
_Avoid_: Citation

**Observation**:
A method-produced measurement or classification about a defined target, time, and context.
_Avoid_: Fact, signal

**Claim**:
A source-attributed assertion that may be supported, contradicted, stale, or unresolved.
_Avoid_: Fact, edge

**Admitted Assertion**:
A Claim that has passed the applicable validation and review policy for use in governed reasoning.
_Avoid_: Truth

**World Event**:
A market-relevant occurrence outside the Trading OS, such as an earnings release, policy decision, corporate action, or supply disruption.
_Avoid_: Operational event

**Operational Event**:
An immutable record of a Trading OS state transition, such as a snapshot build, approval, order, fill, or reconciliation outcome.
_Avoid_: Market event, world event

## Reasoning

**Instrument Hypothesis**:
A falsifiable proposition about a Security or Listing with an explicit direction, horizon, assumptions, and invalidation conditions.
_Avoid_: Trade, prediction

**Instrument Belief State**:
A snapshot-bound representation of supported, contested, insufficient, and inapplicable Instrument Hypotheses with their evidence, contradictions, uncertainty, freshness, and missingness.
_Avoid_: Trade signal, recommendation

**Semantic Snapshot**:
An immutable, content-addressed view binding an Ontology Release, admitted assertions, inference policy, decision cutoff, and build version.
_Avoid_: Latest graph, database state

**Ontology Release**:
An immutable version of the Trading World vocabulary, constraints, mappings, and approved inference rules.
_Avoid_: Graph version, schema latest

**Relational Retrieval Baseline**:
The permanent champion reasoning path that answers the same competency questions using ordinary snapshot-scoped structured records and joins.
_Avoid_: Legacy path, temporary baseline

**Ontology Challenger**:
A candidate Ontology Release and reasoning configuration evaluated against the Relational Retrieval Baseline before promotion.
_Avoid_: Upgrade

**Ontology Improvement Loop**:
The offline, governed cycle that records reasoning failures, diagnoses causes, proposes changes, evaluates challengers, and promotes or rejects releases.
_Avoid_: Self-modifying agent, live learning loop
