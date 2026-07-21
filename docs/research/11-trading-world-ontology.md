# Trading-world ontology: evidence review, plan fit, and adversarial assessment

**Date:** 2026-07-21

**Question:** Would a trading-world ontology help agents understand relationships among market entities, events, observations, sentiment, and evidence, and then make decisions from queried data? Does the current Trading OS plan already provide for it, and what would make the idea useful rather than ornamental?
**Source policy:** External claims below use primary sources only: standards bodies, regulators, official project specifications, authors' papers, or peer-reviewed proceedings. Repository conclusions come from the approved design and implementation plan. No existing plan file was modified for this report.

## Executive verdict

**Yes, with a narrower claim and a staged scope.** A trading-world ontology can materially improve the system's semantic correctness, entity resolution, point-in-time data integration, provenance, retrieval, exposure analysis, and explanations. It can help an agent answer questions such as “which listed securities were exposed to this supplier at the decision cutoff, through what asserted paths, based on which sources?” more reliably than free-form document search or ticker-keyed tables.

It is **not, by itself, evidence of trading alpha**. An ontology standardizes what things mean; a knowledge graph records assertions about those things; a causal model identifies effects; and a decision policy converts evidence into action. Collapsing those four layers creates false confidence. Economic-network research does show that real firm relationships transmit shocks, and several machine-learning papers report gains from relational or knowledge-graph features. But the gains are mostly historical backtests, often do not model realistic costs, and do not demonstrate that an OWL/RDF ontology causes durable out-of-sample performance.

The approved plan already contains roughly the **operational core of a minimal semantic evidence graph**: a causal KG, provenance-gated and time-scoped edges, deterministic motifs, snapshot-bound data, a security-master port, immutable source records, historical event replay, and a permanent non-KG benchmark. What it does **not** yet specify is a broader ontology contract: stable distinctions among legal entity, issuer, instrument, security, listing, ticker, event, observation, claim, source, and inference; identifier crosswalk and identity history; vocabulary governance and external-standard mappings; contradiction/uncertainty semantics; or semantic-quality evaluation.

The recommendation is therefore **not** a big-bang “world ontology” or a rewrite of Neo4j into a semantic-web stack. Treat the ontology as a small, versioned semantic contract over the existing property graph and data plane; reuse selected industry definitions and identifiers; make every query snapshot-bound and provenance-returning; and require it to beat simpler joins and sector/supply-chain baselines on factual, operational, and economic tests before expanding it.

## 1. What the current plan already covers

The idea is not new to the plan. It is already present under the narrower name **causal-KG plane**.

| Capability | Current-plan coverage | Assessment |
|---|---|---|
| Relational market model | Design §3 and plan Tasks 15–16 define Company, Sector, MacroDriver/Commodity, Geography, typed edges, deterministic motifs, decay, confidence, and anti-hub penalties. | Strong for macro-to-company exposure; not a complete trading-world vocabulary. |
| Provenance and admission | Task 15 requires citations, source metadata, human approval, corroboration, author-precision measurement, `valid_from`, `last_confirmed`, and deprecation. | Strong and directionally aligned with PROV-O. |
| Point-in-time correctness | Task 13 seals a content-addressed snapshot containing news cutoff and KG edge-set version; Task 35 rejects post-event edges and source material in historical replay. | Strong; this is more important for honest trading evaluation than adopting RDF. |
| Queried data integration | Task 5 defines typed data/security-master/graph ports; Task 29 persists immutable, snapshot-scoped source records and forbids unscoped `latest()`. | Strong boundary discipline, but no explicit semantic query contract or competency-query suite. |
| Entity resolution | A `SecurityMasterPort` and security classifications are planned. | Partial. No issuer/security/listing split, identifier crosswalk policy, temporal aliases, merge/split lineage, or match-quality measurement is specified. |
| Event modeling | `MacroEventLabel` and an append-only operational event log exist. | Partial. Market-world events, observations, claims, and internal operational events are distinct concepts but are not governed by one explicit semantic model. |
| Evaluation | Tasks 34–35 require CPCV/DSR, a permanent rule-null, KG rank correlation, costs, and 2020/2022 event replay. | Strong economic discipline; missing ontology-specific factual and retrieval evaluations. |

### The important gaps

1. **“Company” is overloaded.** A legal entity can issue several instruments; one instrument may have several listings; a ticker can change or be reused; an ADR is not the operating company; and a parent, issuer, brand, and listed security are not interchangeable. Without these distinctions, the graph can propagate a correct relationship to the wrong tradable object.
2. **No explicit assertion model.** “Company A supplies Company B” should not be stored as if it were timeless truth. The system needs to distinguish the world relationship, the source's claim, the extraction activity, the evidence span, and the system's admitted inference.
3. **Time is not yet fully decomposed.** `valid_from` and snapshot cutoff are good, but event occurrence, source publication, vendor arrival, system retrieval, correction time, and world-valid interval answer different questions. Using the wrong one creates look-ahead.
4. **No ontology/vocabulary governance.** The plan defines edge types locally but not term ownership, definitions, deprecation, mappings to external standards, competency questions, or migration rules.
5. **No contradiction or absence semantics.** Missing facts, unverified facts, refuted claims, expired relationships, and true negatives must not collapse to the same state.
6. **No semantic utility gate.** The KG has an economic gate, but the broader ontology should also prove that it improves entity-link accuracy, query answer accuracy, citation coverage, and analyst time/cost over a simpler relational implementation.

## 2. What the evidence actually supports

### 2.1 Economic relationships can carry real information

This is the strongest foundation for the idea. Cohen and Frazzini used disclosed material customer-supplier links and found delayed price incorporation across linked firms and a historically profitable “customer momentum” strategy. The mechanism is relational: news about one firm can matter for another because the link affects cash flows. The paper also makes a crucial point for this project—links must have been publicly available before the predicted move. [Cohen & Frazzini, *Economic Links and Predictable Returns*](https://users.nber.org/~confer/2006/bfs06/frazzini.pdf)

Network propagation is not merely a machine-learning artifact. Using narrow windows around Federal Reserve announcements, Ozdagli and Weber decomposed monetary-policy effects through production networks and attributed 50–85% of the overall stock-return response to indirect network effects; they also found corresponding effects in cash-flow fundamentals. That is evidence that a well-specified graph can improve **exposure reasoning**, but it is not evidence that a retail EOD strategy can capture the response after costs. [NBER: *Monetary Policy through Production Networks*](https://www.nber.org/papers/w23424)

Economic theory likewise shows that endogenous supply-network structure can amplify shocks and be inefficiently fragile. This supports modeling concentration, substitutes, and network topology for risk analysis, while also warning that relationships change endogenously rather than remaining static ontology facts. [American Economic Review: *Supply Network Formation and Fragility*](https://www.aeaweb.org/articles?id=10.1257/aer.20210220)

### 2.2 Relational and knowledge features often improve historical prediction

Several primary studies report incremental predictive value from structured relationships:

- A COLING study jointly learned event and knowledge-graph embeddings and improved its S&P 500 direction accuracy from 64.21% for the event-only baseline to 66.93%, with improvements on its selected individual stocks. This supports the claim that entity/relation context can disambiguate news events; it does not establish live tradability, robustness across regimes, or ontology value as distinct from feature engineering. [Ding et al., *Knowledge-Driven Event Embedding for Stock Prediction*](https://aclanthology.org/C16-1201/)
- Relational Stock Ranking combined time series with sector and Wikidata company relations and reported improved NYSE/NASDAQ backtests. The paper itself notes volatile curves, high risk from selecting one stock, and settings where industry relations were less effective. This is evidence for testing relation-aware ranking, not for accepting every available relation. [Feng et al., *Temporal Relational Ranking for Stock Prediction*](https://arxiv.org/abs/1809.09441)
- A spatiotemporal hypergraph model reported improvements over neural forecasting baselines across three markets and over six years. Again, this supports relational inductive bias, but the learned hypergraph is not the same thing as an auditable ontology and the publication does not prove durable net-of-cost alpha. [AAAI 2021: *Stock Selection via Spatiotemporal Hypergraph Attention Network*](https://ojs.aaai.org/index.php/AAAI/article/view/16127)

Recent LLM/KG results are promising but should be treated as early evidence. FinKario constructs an event-enhanced financial KG and reports higher backtested trend accuracy than financial LLM and institutional-strategy baselines; its own motivation acknowledges that fast market evolution outpaces static knowledge bases, and the paper does not validate live trading or eliminate regime/distribution-shift risk. [ACL 2026: *FinKario*](https://aclanthology.org/2026.acl-long.446/) A separate causal-temporal KG/RAG system reports better zero-shot post-earnings shock prediction, but this remains a paper benchmark rather than forward-paper evidence for this system. [EACL 2026: *Decoding the Market's Pulse*](https://aclanthology.org/2026.eacl-long.141/)

### 2.3 What these studies do not prove

No reviewed primary source establishes that adopting FIBO, RDF, OWL, SHACL, or a particular graph database produces investment alpha. The evidence supports three weaker propositions:

1. real economic relationships affect fundamentals and prices;
2. relational features can improve some historical prediction or retrieval tasks; and
3. structured, provenance-bearing retrieval can constrain an LLM better than relying on model memory alone.

The last proposition also has limits. A 2026 KG-RAG benchmark found current systems had limited reasoning ability when knowledge was missing and often fell back to internal memorization. A systematic GraphRAG analysis similarly found that extraction quality and KG coverage can bottleneck downstream reasoning. In finance specifically, an automatic news-to-KG system produced 342,000 extractions but only 78% precision among its top 100 results—far below the reliability needed for unreviewed decision edges. In other words, a graph can ground the model only to the extent that the graph is correct, complete, current, and retrieved properly. [EACL 2026 BRINK benchmark](https://aclanthology.org/2026.eacl-long.114/), [TACL 2026 GraphRAG analysis](https://aclanthology.org/2026.tacl-1.29/), [COLING 2020 financial KG extraction](https://aclanthology.org/2020.coling-main.84/)

## 3. Standards: what to reuse, and what not to confuse

### 3.1 FIBO: reference vocabulary, not turnkey trading intelligence

The Financial Industry Business Ontology is the most relevant semantic standard. It is an OWL ontology standardized by OMG and maintained by EDM Council to provide a common vocabulary for financial contracts and related concepts. Its official repository covers business entities, corporate actions and events, financial instruments, indicators, market data, securities, derivatives, and temporal market data; it is MIT-licensed and updated continuously with quarterly formal releases. [Official FIBO specification](https://spec.edmcouncil.org/fibo/index.html), [official FIBO repository and domain map](https://github.com/edmcouncil/fibo/blob/master/README.md)

FIBO is valuable here for definitions and mappings around legal entities, issuers, instruments, listings, securities, corporate actions, indicators, prices, and identifiers. It is not a ready-made ontology of geopolitical shocks, sentiment, supply-chain causality, market narratives, or trading decisions. Importing its full dependency closure would add vocabulary and reasoning complexity far beyond the v1 need. The defensible path is to reuse or map selected terms while keeping a small local application vocabulary.

### 3.2 RDF, OWL, SPARQL, and SHACL solve different problems

- **RDF** is a graph data model of subject-predicate-object statements with globally scoped identifiers. It is useful as an exchange representation and for linking disparate sources. The standard explicitly says the RDF model itself is atemporal; temporal behavior must be represented through vocabulary and/or immutable graph snapshots. [W3C RDF 1.1 Concepts](https://www.w3.org/TR/rdf11-concepts/)
- **OWL 2** formalizes shared vocabularies and supports logical inference. Its profiles explicitly trade expressive power for computational properties; OWL 2 QL targets query answering over large relational data, and OWL 2 RL supports rule-based operation on triples. This makes a lightweight profile more plausible than unrestricted reasoning for an operational trading system. [W3C OWL 2 overview](https://www.w3.org/TR/owl2-overview/)
- **SPARQL** queries RDF graphs and supports property paths, including inverse and arbitrary-length paths. It is useful for semantic interoperability and analyst queries, but unrestricted paths are exactly what the current anti-hub and depth-cap rules correctly avoid for decision arithmetic. [W3C SPARQL 1.1 Query](https://www.w3.org/TR/sparql11-query/)
- **SHACL** validates graph structure and supports closed shapes, cardinalities, datatypes, enumerations, and validation reports. It is the closest semantic-web analogue to the plan's strict Pydantic models and six-gate edge admission. [W3C SHACL Recommendation](https://www.w3.org/TR/shacl/)

The standards do **not** require replacing Neo4j. The ontology can remain a technology-neutral contract; a property graph can enforce equivalent constraints and expose a standards-aligned export only if interoperability justifies it.

### 3.3 Provenance and time

PROV-O/PROV-DM provide a useful minimal distinction among **Entity**, **Activity**, and **Agent**, plus generation, usage, derivation, attribution, invalidation, and provenance bundles. This is exactly the separation needed to represent “a filing is a source entity; an extraction run used it; a model/analyst performed the activity; an admitted claim was derived from it.” [W3C PROV-O](https://www.w3.org/TR/prov-o/), [W3C PROV-DM](https://www.w3.org/TR/prov-dm/Overview.html)

OWL-Time represents instants, intervals, duration, beginnings/endings, and interval relations. It is appropriate for event occurrence and world-valid intervals, but it does not replace the trading-specific need to record publication, receipt, and decision-cutoff times. Bitemporal database research formalizes the same core distinction as valid time (when a fact is true in the modeled world) and transaction time (when it is stored/known by the system). [W3C OWL-Time](https://www.w3.org/TR/owl-time/), [Jensen & Snodgrass, *Effective Timestamping in Databases*](https://www2.cs.arizona.edu/~rts/pubs/VLDBJ99.pdf)

For market data, the minimum semantic distinction is:

| Time | Meaning | Failure if omitted |
|---|---|---|
| `occurred_at` | When the world event happened | Misorders causal chains. |
| `announced_at` / `published_at` | When the source made it public | Creates event-study leakage if replaced by event date. |
| `received_at` | When this system/vendor actually had it | Hides vendor and ingestion latency. |
| `valid_from` / `valid_to` | When a relationship was true in the world | Treats stale supply/ownership links as current. |
| `recorded_at` / supersession time | When this system stored or corrected the assertion | Makes historical reconstruction impossible. |
| `decision_cutoff` | Latest information admissible to a decision | Allows silent look-ahead. |

The approved snapshot boundary already supplies the most important enforcement mechanism. An ontology should clarify these meanings, not replace content-addressed snapshots.

### 3.4 schema.org Event and FINOS CDM

`schema.org/Event` is useful for ingesting public-web event markup with dates, status, place, organizer, and participants. It is designed around general scheduled events and has no financial causal semantics, impact sign, evidence confidence, or market-availability model. It is therefore an ingestion vocabulary, not the core event model. [schema.org Event](https://schema.org/Event)

The FINOS Common Domain Model is a standardized, machine-readable and executable blueprint for products and transaction lifecycles. Its event model treats events as composable before/after trade-state transitions and supports reconstruction of trade lineage. That is highly relevant to execution and post-trade state, but FINOS explicitly scopes the reference model to what is required for in-scope products and lifecycle events; it is not an ontology of macro news or causal exposure. [FINOS CDM overview](https://cdm.finos.org/docs/cdm-overview/), [FINOS CDM event model](https://cdm.finos.org/docs/event-model/), [FINOS reference-data scope](https://cdm.finos.org/docs/reference-data-model/)

The plan's append-only operational event log is already conceptually aligned with CDM's lineage principle. It should remain separate from the evidence graph: an `OrderFilled` state transition and an `OilSupplyDisruption` world event have different truth and governance rules.

### 3.5 Identifiers, LEI, and regulatory direction

Entity resolution should start with authoritative identifiers, not names or tickers. GLEIF's Legal Entity Identifier data supplies Level 1 “who is who” identity and Level 2 “who owns whom” relationships for direct and ultimate accounting-consolidating parents. GLEIF also publishes daily ISIN-to-LEI mappings intended to connect securities exposure to issuers and related entities. [GLEIF Level 1/2 data](https://www.gleif.org/en/lei-data/access-and-use-lei-data), [GLEIF ISIN-to-LEI files](https://www.gleif.org/en/lei-data/lei-mapping/download-isin-to-lei-relationship-files)

The coverage is not complete. GLEIF's 2026-07-18 files contained 3.38 million LEI records, about 659,000 relationship records, and 6.08 million parent-reporting exception records; the ISIN-to-LEI program itself says its current files cover participating “early mover” national numbering agencies and plans longer-term legacy-ISIN expansion. These limitations make LEI a strong anchor, not a universal resolver. [GLEIF concatenated-file statistics](https://www.gleif.org/en/lei-data/gleif-concatenated-file/download-the-concatenated-file), [GLEIF ISIN mapping scope](https://www.gleif.org/en/lei-data/lei-mapping/download-isin-to-lei-relationship-files)

The U.S. Financial Data Transparency Act standards reinforce this direction. The 2026 final joint rule selected LEI for legal entities, UPI for swaps, CFI for instrument classification, ISO 8601 for dates, ISO 4217 for currencies, and machine-readable schemas with ontology/taxonomy metadata; it deliberately did **not** select FIGI as a common instrument identifier pending more analysis. The rule is aimed at regulatory-data interoperability, not trading alpha, but it is strong evidence for using open, standard identifiers and explicit machine-readable semantics. [Federal Reserve board memo on the final rule](https://www.federalreserve.gov/newsevents/pressreleases/files/bcreg20260611a2.pdf), [SEC final-rule page](https://www.sec.gov/rules-regulations/2026/05/s7-2024-05)

## 4. A conservative semantic architecture

This is a research-level architecture recommendation, not an implementation design.

### 4.1 Separate four layers

1. **Vocabulary/ontology:** definitions and allowed relationship meanings; versioned and reviewed.
2. **Evidence graph:** snapshot-scoped assertions, identity links, events, observations, claims, provenance, validity, and contradiction state.
3. **Causal/exposure model:** a reviewed subset of graph relations plus identified or conservatively fitted weights; this is where motifs and effect signs live.
4. **Decision policy:** deterministic gating, ranking, sizing, risk, compliance, and execution. It consumes typed query results, never free graph walks or LLM-authored numbers.

This separation preserves the plan's strongest invariant: **LLMs propose, deterministic code disposes.** The agent may translate a question into an approved query template, summarize returned evidence, classify a closed event type, or propose an edge. It should not decide that graph proximity is causality or turn a narrative path into size.

### 4.2 Minimal domain distinctions

A useful v1 ontology would prioritize identity and evidence over breadth:

- **Identity/tradability:** LegalEntity, Issuer, Instrument/Security, Listing, Venue, Identifier, Fund, Index, Sector/Industry, Geography.
- **World state:** Product/Service, Commodity, Facility/Asset, Supply/Customer/Ownership/Competition relation, Regulation, Jurisdiction.
- **Evidence:** SourceDocument, SourceRecord, Observation, Claim, EvidenceSpan, Extraction/Review Activity, Agent, admitted/refuted/deprecated status.
- **Events:** CorporateAction, Earnings/Guidance, MacroRelease, PolicyDecision, Supply/Demand/Uncertainty Shock, GeopoliticalEvent, and the plan's closed `MacroEventLabel`.
- **Decision artifacts:** Snapshot, Query, RetrievedPath, ExposureVector, Thesis, Decision—linked for audit but not treated as external-world facts.

The ontology should explicitly avoid treating **sentiment as an entity-level truth**. Sentiment is an observation produced by a method about a document, entity, or event, with a label set, model version, language, source, and as-of time. Domain context matters: Loughran and McDonald found that nearly three-quarters of words marked “negative” by a general dictionary were not negative in financial usage. [Loughran & McDonald, *When Is a Liability Not a Liability?*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1331573)

### 4.3 Identity-resolution rules

- Use canonical, type-specific IDs and preserve all source identifiers as temporal aliases.
- Anchor legal entities with LEI where available; map instruments/listings with ISIN and venue-specific IDs; never use ticker alone as identity.
- Record the match method, source, confidence class, review state, and validity interval.
- Treat mergers, name changes, spin-offs, delistings, share-class changes, and ADR/underlying relationships as events that create or terminate identity relationships.
- Fuzzy name/address matches should produce candidates, not silent merges. A wrong merge can contaminate every downstream relation and is more dangerous than a missing link.

### 4.4 Query contract

An agent-facing query should always bind:

1. a `ValidatedDataSnapshotId` and decision cutoff;
2. a bounded question or approved motif;
3. entity types and canonical identifiers;
4. minimum evidence/admission state;
5. depth, relation allowlist, and freshness limits; and
6. a response containing both result and provenance: paths, source records, validity, confidence class, contradictions, and missingness.

Natural-language-to-graph translation should not be trusted as the policy boundary. In NatureKG, the best reported Text2Cypher execution accuracy was 0.21 on paraphrases and 0.14 on generalization. Although that benchmark is outside finance, it demonstrates why an agent should select among reviewed query templates and typed parameters rather than author unrestricted Cypher for decisioning. [NatureKG Text2Cypher evaluation](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1693843/full)

The system should maintain **competency questions** as executable acceptance tests, for example:

- Which tradable listings represented securities issued by entities directly or ultimately exposed to a named supplier on date *t*?
- Which admitted facts supporting that answer were public and received before the decision cutoff?
- Which relationships were stale, contradicted, inferred, or missing?
- What changed between graph versions *g1* and *g2*, and would the historical answer change?

If the ontology cannot answer a competency question more reliably than ordinary snapshot-scoped joins, its extra complexity is not justified.

## 5. Evaluation: prove semantic value before economic value

The existing Task 34/35 promotion gates should remain. Add a separate evaluation ladder for the broader ontology.

### 5.1 Semantic and data-quality tests

- **Entity resolution:** precision/recall by entity type on a manually labeled, time-stratified set; report catastrophic false merges separately.
- **Relationship quality:** edge precision, recall where measurable, evidence coverage, contradiction rate, staleness, and deprecation latency.
- **Temporal integrity:** planted future facts, late vendor arrivals, corrections, renamed tickers, mergers, and stale ownership/supply links.
- **Constraint integrity:** invalid cardinality, wrong endpoint types, missing source, impossible date order, and unknown enum values must fail admission.
- **Reproducibility:** the same snapshot and query must return byte-equivalent facts and paths.

### 5.2 Agent-reasoning tests

Run blinded questions in at least three conditions:

1. raw document retrieval;
2. flat structured records/search; and
3. ontology/evidence-graph retrieval.

Measure factual precision, completeness, source entailment, citation correctness, abstention on missing knowledge, latency, and cost. Include false-premise questions and delete required graph facts deliberately. KG-RAG research shows that missing knowledge can cause models to rely on memorization rather than the graph, so graceful “unknown” behavior is a core metric, not an edge case. [EACL 2026 BRINK](https://aclanthology.org/2026.eacl-long.114/)

### 5.3 Exposure and economic tests

- Compare the KG overlay against simpler baselines: sector lookup, direct-only supply links, static ownership, factor-only null, and no ontology.
- Use event-time historical snapshots built only from evidence available at the time; audit `published_at` and `received_at`, not just event date.
- Evaluate cross-sectional Spearman rank correlation, top-minus-bottom spread, turnover, costs, drawdown, risk reduction, and calibration by independent shock event.
- Separate **risk utility** (loss avoided, concentration discovered, exposure explanation) from **alpha utility** (net excess return). A system can be valuable even if only the first clears.
- Pre-register all ontology variants and relation families. The Deflated Sharpe Ratio literature shows that testing many alternatives inflates backtest performance; DSR corrects for multiple testing and non-normal returns. [Bailey & López de Prado, *The Deflated Sharpe Ratio*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551)
- Require forward paper evidence. In a dataset of 888 Quantopian algorithms, ordinary backtest Sharpe had less than 0.025 R² for subsequent out-of-sample performance, and more backtesting was associated with a larger backtest/OOS gap. [Wiecki et al., *All That Glitters Is Not Gold*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2745220)

## 6. Adversarial review

### 6.1 The best case

The ontology becomes the system's semantic memory and evidence control plane. It prevents ticker/issuer confusion, makes point-in-time joins reproducible, gives agents bounded multi-hop context, exposes uncertainty and provenance, lets humans audit why an exposure was inferred, and reuses standards rather than inventing every financial term. Those benefits can reduce operational and reasoning errors even if incremental return is zero.

### 6.2 The strongest objections

**1. Semantic compression is not information creation.** A beautifully modeled graph cannot recover missing or late source data. It can make an unsupported story look more coherent.

**2. A “causal” edge is not an identified causal effect.** Pearl's framework separates causal assumptions, intervention semantics, identification, and estimation. An asserted `depends_on` path is a hypothesis or mechanism unless an identification strategy supports the effect. [Pearl, *Causal Inference in Statistics: An Overview*](https://projecteuclid.org/journals/statistics-surveys/volume-3/issue-none/Causal-inference-in-statistics-An-overview/10.1214/09-SS057.pdf)

**3. Graph errors propagate nonlocally.** A wrong entity merge or hub edge can contaminate hundreds of paths. The current plan's endpoint typing, anti-hub penalty, confidence decay, depth cap, and human admission are not optional hardening; they are preconditions.

**4. The graph can launder LLM guesses into apparent facts.** The agent should never write admitted edges directly. Extraction, claim, review, and admission must remain separate, and answers must expose the source evidence—not merely cite a graph node.

**5. Sentiment is noisy, contextual, and easy to double-count.** Multiple outlets may repeat one wire story; managerial optimism can be narrative bias; and a general sentiment lexicon can misclassify financial vocabulary. Event clustering and source lineage are necessary to avoid treating syndication volume as independent corroboration.

**6. Markets are nonstationary and reflexive.** The Adaptive Markets Hypothesis argues that efficiency varies with market ecology, competition, opportunity, and participant adaptation. More generally, performative-prediction theory formalizes that predictions can change the outcomes they target; the paper explicitly lists stock predictions affecting trading activity and prices. Static edge weights and historical effects therefore need ongoing regime and decay checks. [Andrew Lo, *The Adaptive Markets Hypothesis*](https://www.mit.edu/~alo/Papers/JPM2004.pdf), [ICML 2020: *Performative Prediction*](https://proceedings.mlr.press/v119/perdomo20a.html)

**7. The alpha may disappear precisely because the ontology works.** If many participants encode the same public relationships, delayed reaction shrinks. Ontology-based reasoning can still improve risk and auditability after the return anomaly is competed away.

**8. Complexity can dominate value.** Vocabulary governance, mappings, temporal identity, edge review, source licensing, graph migration, and replay are ongoing data products. A universal ontology can become an expensive taxonomy project that delays the deterministic v1.

**9. Standards can create false safety.** FIBO describes meaning; it does not guarantee source truth, identifier coverage, causal validity, freshness, or correct local mapping. GLEIF relationship exceptions and partial ISIN mapping show that even high-quality standards have coverage boundaries.

**10. Query freedom can bypass decision controls.** Arbitrary graph traversal encourages post-hoc narratives and hub-driven answers. Decisioning should use reviewed query templates/motifs and snapshot-bound results, while broad exploratory querying remains research-only.

### 6.3 Kill or pause criteria

Pause expansion beyond the current causal KG if any of these persist after a bounded pilot:

- entity-link false merges cannot be held below a pre-registered safety threshold;
- provenance coverage or point-in-time reconstruction is materially incomplete;
- agents cite graph assertions without source entailment or fail to abstain when facts are deleted;
- the graph does not outperform flat structured retrieval on factual/citation quality;
- exposure ranking does not beat direct-link and sector baselines in pre-registered replays;
- ongoing data/ontology maintenance cost exceeds measured risk or research-time benefit; or
- the project delays the plan's deterministic paper-trading foundation.

## 7. Recommended decision

**Accept the idea as a bounded semantic-evidence layer, not as a new autonomous decision engine.** The approved plan already contains the right substrate and safety posture. The next planning revision should explicitly recognize the broader ontology concerns, but v1 should remain centered on:

1. canonical identity and issuer/security/listing separation;
2. claim/evidence/provenance separation;
3. full point-in-time semantics and correction history;
4. a small versioned vocabulary mapped selectively to FIBO, LEI/ISIN/MIC, PROV-O, and OWL-Time concepts;
5. bounded, snapshot-scoped, provenance-returning agent queries; and
6. semantic A/B tests plus the already planned economic nulls and forward-paper gates.

Do **not** make full FIBO import, RDF storage, unrestricted OWL reasoning, SPARQL federation, automatic LLM edge authoring, or graph-derived sizing prerequisites for v1. Those are optional interoperability or research choices whose value must be demonstrated independently.

The ontology is useful if it makes the system **less wrong, more reproducible, and more auditable**. It should be credited with alpha only after it also survives the current plan's much harder net-of-cost, post-cutoff, forward-paper test.
