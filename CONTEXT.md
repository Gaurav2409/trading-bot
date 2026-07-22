# Trading World

The shared language for representing tradable instruments, market evidence, hypotheses, and reasoning outputs without confusing semantic knowledge with trading decisions.

## Identity and tradability

**Legal Party**:
A person or legally recognized organization that can own a Brokerage Account or grant authority over it.
_Avoid_: User, household, profile

**Person**:
A natural person whose legal identity is distinct from every software profile, household membership, and brokerage credential.
_Avoid_: User, account

**Legal Entity**:
A legally recognized organization that may own assets, incur obligations, issue securities, or control other entities.
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

**Discovery Universe**:
The broad set of Listings inspected for opportunities, independent of whether they are currently eligible for trading.
_Avoid_: Tradable universe, portfolio

**Tradable Allowlist**:
The narrower set of Listings that currently satisfy account, broker, venue, compliance, data, and risk requirements for decisioning.
_Avoid_: Discovery universe, watchlist

**Coverage Receipt**:
An immutable account of what a detector inspected, over which time range, with which data and policy versions, including omissions and failures.
_Avoid_: Scan completed flag

**Opportunity Candidate**:
A discovered market setup that requires tradability, evidence, portfolio, and deterministic risk evaluation before it can influence an order.
_Avoid_: Trade, buy signal

**Tradability Risk Packet**:
A snapshot-bound assessment of whether a candidate is legally, operationally, and economically executable for a particular Brokerage Account.
_Avoid_: Research report, recommendation

## Ownership, access, and portfolios

**User Profile**:
A software identity for interaction preferences and permissions; it is not a Legal Party, owner, or brokerage credential.
_Avoid_: Owner, account

**Household**:
A consent-scoped grouping of Legal Parties and User Profiles for derived views and tighten-only policies; it owns no account by implication.
_Avoid_: Joint account, trading account

**Household Membership**:
A time-bounded relationship granting specified household visibility or participation without granting brokerage authority.
_Avoid_: Trading mandate

**Brokerage Account**:
A broker-maintained custody and execution partition owned by one or more Legal Parties, with its own capital, positions, orders, compliance state, reconciliation, and kill state.
_Avoid_: User, portfolio, household

**Broker Connection**:
A scoped credential and session relationship that may access only explicitly authorized Brokerage Accounts and operations.
_Avoid_: Broker, account owner

**Account Access Grant**:
A revocable, time-bounded authority to read or operate a Brokerage Account within a precisely stated scope.
_Avoid_: Household membership, role

**Trading Mandate**:
An Account Access Grant that explicitly authorizes proposing, approving, or executing specified trades for a Brokerage Account.
_Avoid_: Consent, family membership

**Portfolio Snapshot**:
An immutable, partition-preserving cut of account custody observations, OS ledger state, reservations, prices, policies, and completeness at a decision time.
_Avoid_: Current holdings response, household total

**Current Portfolio Analysis**:
A snapshot-bound assessment of cash, positions, orders, availability, provenance, concentration, liquidity, event exposure, and protection that gates exposure-increasing decisions.
_Avoid_: Dashboard, performance report

**Household Portfolio View**:
A derived, permission-filtered view that preserves Brokerage Account partitions and never becomes custody or execution authority.
_Avoid_: Household account, pooled portfolio

**Capital Envelope Release**:
An immutable, effective-dated statement of the capital and cumulative loss authorized for a Brokerage Account or sleeve.
_Avoid_: Balance, buying power

## Capability and policy

**Asset Class Capability Release**:
An immutable statement of the verified jurisdiction, product, venue, broker, data, valuation, risk, execution, protection, and reconciliation capabilities required for an asset class.
_Avoid_: Feature flag, broker support

**Account Capability Assignment**:
A revocable, effective-dated binding of a Brokerage Account and mandate to an Asset Class Capability Release; absence means denied.
_Avoid_: Account default, inherited permission

**Promotion Policy Release**:
An immutable definition of the evidence thresholds and review windows required to expand or reduce live authority.
_Avoid_: Fixed waiting period

**Source Coverage Policy Release**:
An immutable, effective-dated definition of which source channels are applicable, mandatory, optional, entitled, fresh enough, and correctly parsed for a governed research purpose.
_Avoid_: URL list, watcher configuration

**Tool Capability Release**:
An immutable definition of a typed, bounded, pure or read-only operation that a specific Agent Profile Release may expose within a frozen snapshot scope.
_Avoid_: Function list, plugin permission

**LLM Routing Policy Release**:
An immutable definition of eligible model capabilities, provider routes, fallbacks, budgets, and fail-closed behavior for one or more LLM Roles.
_Avoid_: Model name, provider config

## Evidence and world state

**Source Record**:
An immutable captured item supplied by a publisher or vendor, including its origin and availability times.
_Avoid_: Fact

**Source Coverage Receipt**:
An immutable observation of which applicable source channels a watcher intended, attempted, captured, omitted, delayed, or rejected for a time range and frozen snapshot.
_Avoid_: Poll succeeded, coverage flag

**Source Coverage Status**:
A deterministic reconciliation of a Source Coverage Policy Release with Source Coverage Receipts, classifying coverage as complete, degraded, contradictory, insufficient, suspended, or inapplicable.
_Avoid_: Agent opinion, source score

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

**Domain Agent Harness**:
The single governed Research Agent Port implementation that resolves immutable profiles, executes bounded typed trajectories, records canonical run events, and returns admitted categorical Evidence Packets.
_Avoid_: Domain-specific agent, autonomous research bot

**Agent Profile Release**:
An immutable manifest for one evidence-domain purpose that references its trajectory, prompts, tool capabilities, source coverage, output schema, LLM routing, budgets, failure policy, and evaluation policy.
_Avoid_: Agent instance, mutable configuration

**Trajectory Release**:
An immutable typed graph of registered deterministic and agentic nodes, bounded transitions, capability grants, and terminal outcomes used as the source of truth for execution and workbench rendering.
_Avoid_: Python workflow, LangGraph object

**LLM Role**:
A provider-neutral structured invocation responsibility, selected by immutable routing policy and unable to fetch sources, execute tools directly, persist memory, or activate policy.
_Avoid_: Model, agent persona

**Agent Run Ledger**:
The canonical append-only record of an agent run's immutable release closure, snapshot scope, node transitions, model and capability boundaries, budgets, admission result, and terminal compatibility outcome.
_Avoid_: LangGraph checkpoint, provider trace

**Definition Proposal**:
An immutable candidate change to a prompt, profile, trajectory, capability, source policy, routing policy, or evaluation definition, with provenance and evaluation results but no activation authority.
_Avoid_: Live config update, self-improvement

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
