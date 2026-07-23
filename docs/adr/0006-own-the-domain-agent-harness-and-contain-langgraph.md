---
status: accepted
---

# Own the domain-agent harness and contain LangGraph behind typed trajectory releases

The Trading OS needs deterministic and agentic nodes, bounded loops, fan-out/join, recovery, and a graphical trajectory definition while preserving the existing `ResearchAgentPort`. Adopting a general-purpose framework as the public harness would let framework objects, state, and semantics leak into research callers and policy.

We will own one `DomainAgentHarness`, one typed `TrajectoryRelease` model, and one `TrajectoryEngine` interface. A project-owned compiler validates immutable definitions and privately targets LangGraph. The existing `investigate(question) -> EvidencePacket | None` method remains the only caller seam. Ten evidence domains use profiles, not separate harness implementations.

This adds compiler and adapter work. We accept that cost because it keeps the definition graph, compatibility behavior, admission path, and framework replacement under project control while still using LangGraph for durable execution.
