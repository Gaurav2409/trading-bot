---
status: accepted
---

# Use LLM Role as the only provider boundary

OpenAI, Anthropic, Pydantic AI, and future providers differ in structured output, tool calling, retry safety, usage reporting, tracing, and hosted capabilities. Allowing those differences into profiles or trajectory code would create provider lock-in and inconsistent safety behavior.

All model invocation will cross one `LLMRole.invoke(structured_request)` interface. Immutable routing policy chooses eligible providers and models. Adapters return typed results or typed expected failures, normalize usage, and fail closed when a required capability is unavailable. Hosted web, fetch, code, memory, and provider-agent tools are excluded from domain runs.

The common interface cannot expose every provider feature. We accept that constraint: a provider-only feature must first earn an owned typed representation and pass the common contract suite.
