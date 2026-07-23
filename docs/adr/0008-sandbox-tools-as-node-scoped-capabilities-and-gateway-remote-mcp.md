---
status: accepted
---

# Sandbox tools as node-scoped capabilities and gateway remote MCP

Source text is untrusted, agents have no execution authority, and MCP tool descriptions and annotations are not authorization. Direct model-to-tool or model-to-MCP access would let runtime discovery expand authority and bypass frozen source snapshots.

The harness will bind node-scoped, versioned, typed, pure or read-only capability proxies. Effective authority is the intersection of profile, node, capability release, applicability, snapshot, and network policy. Remote MCP is supported only behind `MCPCapabilityAdapter`, with pinned server identity and schema, audience-bound credentials, local validation, result limits, fixture replay, and no runtime authority expansion from discovery or `listChanged`.

This prevents arbitrary MCP integration and requires a local adapter for every approved remote tool. We accept that operational cost because transport interoperability cannot replace project authorization, provenance, cutoff, or replay rules.
