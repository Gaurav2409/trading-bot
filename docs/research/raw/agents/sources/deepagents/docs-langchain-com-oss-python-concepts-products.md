---
url: https://docs.langchain.com/oss/python/concepts/products
title: "Frameworks, runtimes, and harnesses - Docs by LangChain"
fetched_at: 2026-07-22T18:45:56.726383+00:00
source_id: deepagents-harness
method: static
status: FETCHED
word_count: 739
---

LangChain maintains several open source packages to help you build agents. Each serves a different purpose in the agent development stack. Understanding the distinctions between
agent frameworks
,
agent runtimes
, and
agent harnesses
helps you choose the right tool for your needs.
Framework
Runtime
Harness
Value add
Abstractions
Integrations
Durable execution
Streaming
HITL
Persistence
Predefined tools
Prompts
Subagents
When to use
Getting started quickly
Standardizing how a team builds
Low-level control
Long running, stateful workflows and agents
More autonomous agents
Agents faced with complex, non-deterministic tasks
Options
LangChain
Vercel’s AI SDK
CrewAI
OpenAI Agents SDK
Google ADK
LlamaIndex
LangGraph
Temporal
Inngest
Deep Agents SDK
Claude Agent SDK
Manus
​
Agent frameworks (like LangChain)
Agent frameworks provide abstractions that make it easier to get started when building with LLMs.
LangChain
is an agent framework that provides abstractions like structured content blocks, the agent loop, and middleware.
LangChain’s abstractions are designed to be easy to get started with while still providing the flexibility needed for advanced use cases.
While LangChain is built on top of
LangGraph
, you don’t need to know LangGraph to use LangChain.
Other examples of agent frameworks include
Vercel’s AI SDK
,
CrewAI
,
OpenAI Agents SDK
,
Google ADK
,
LlamaIndex
, and many more.
​
When to use LangChain
Use LangChain when:
You want to quickly build agents and autonomous applications.
You need standard abstractions for models, tools, and agent loops.
You want an easy-to-use framework that still provides flexibility.
You’re building straightforward agent applications without complex orchestration needs.
​
Agent runtimes (like LangGraph)
Agent runtimes provide the tooling for running agents in production.
Supported tools may include:
Durable execution
: Agents persist through failures and can run for extended periods, resuming from where they left off.
Streaming
: Support for streaming workflows and responses.
Human-in-the-loop
: Incorporate human oversight by inspecting and modifying agent state.
Persistence
: Thread-level and cross-thread persistence for state management.
Low-level control
: Direct control over agent orchestration without high-level abstractions.
LangGraph
is a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents.
Agent frameworks are generally higher level and run on agent runtimes.
For example, LangChain 1.0 is built on top of LangGraph.
Other examples of agent runtimes include
Temporal
,
Inngest
, and other durable execution engines.
​
When to use LangGraph
Use LangGraph when:
You need fine-grained, low-level control over agent orchestration.
You need durable execution for long-running, stateful agents.
You’re building complex workflows that combine deterministic and agentic steps.
You need production-ready infrastructure for agent deployment.
​
Agent harnesses (like the Deep Agents SDK)
Agent harnesses are opinionated, batteries-included frameworks with built-in tools and capabilities for building sophisticated, long-running agents.
Supported tools may include:
Planning capabilities
: Track multiple tasks with a to-do list.
Task delegation
: Delegate work and keep context clean with subagents.
File system
: Read and write access to files on different pluggable storage backends.
Token management
: Conversation history summarization and large tool result eviction.
The
Deep Agents SDK
builds on top of LangGraph and adds planning capabilities, file systems for context management, the ability to spawn subagents, and more.
Deep Agents is designed for complex, multi-step tasks that require planning and decomposition.
Example tasks include working with search results, scripts, and other artifacts in state.
Other examples of agent harnesses include
Claude Agent SDK
,
Manus
, and other coding CLIs.
​
When to use the Deep Agents SDK
Use the
Deep Agents SDK
when:
You are building agents that run over long time periods.
You are building agents that need to handle complex, multi-step tasks.
You want to use predefined tools, such as filesystem operations, bash execution, and automated context engineering.
You want to use predefined prompts and subagents.
​
Feature comparison
While you can accomplish similar tasks with LangChain, LangGraph, and Deep Agents, the level at which you integrate them differ:
Feature
LangChain
LangGraph
Deep Agents
Short-term memory
Short-term memory
Short-term memory
StateBackend
Long-term memory
Long-term memory
Long-term memory
Long-term memory
Skills
Multi-agent skills
-
Skills
Subagents
Multi-agent subagents
Subgraphs
Subagents
Human-in-the-loop
Human-in-the-loop middleware
Interrupts
interrupt_on
parameter
Streaming
Agent Streaming
Streaming
Streaming
​
Learn more
LangChain overview
LangGraph overview
Deep Agents overview
Connect these docs
to Claude, VSCode, and more via MCP for real-time answers.
Edit this page on GitHub
or
file an issue
.
Was this page helpful?
Yes
No
Build a custom SQL agent
Previous
Providers and models
Next
⌘
I
