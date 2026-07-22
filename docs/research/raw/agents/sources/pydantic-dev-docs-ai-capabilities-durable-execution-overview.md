---
url: https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/
title: "Overview | Pydantic Docs"
fetched_at: 2026-07-22T17:55:50.496348+00:00
source_id: domain-agent-harness
method: static
status: FETCHED
word_count: 134
---

Overview
Pydantic AI allows you to build durable agents that can preserve their progress across transient API failures and application errors or restarts, and handle long-running, asynchronous, and human-in-the-loop workflows with production-grade reliability. Durable agents have full support for
streaming
and
MCP
, with the added benefit of fault tolerance.
Pydantic AI officially supports four durable execution solutions:
Temporal
DBOS
Prefect
Restate
These integrations are co-maintained by the Pydantic and vendor teams. The Temporal, DBOS, and Prefect integrations ship with Pydantic AI as
capabilities
you attach to an agent; the
Restate
integration lives in the Restate SDK and builds only on Pydantic AI’s public interface, so it can also serve as a reference for integrating with other durable systems.
Additional external SDK integrations:
Kitaru
Apache Airflow
Was this page helpful?
Thanks for your feedback!
