---
status: accepted
---

# Govern agent evolution through proposals, not runtime self-modification

Source monitors, DSPy optimizers, model evaluations, and agent observations can identify better sources, prompts, tools, models, or trajectories. Allowing any of them to change active definitions would collapse evaluation, approval, and production authority into the system being evaluated.

Every change is an immutable `DefinitionProposal` evaluated against recorded and held-out fixtures. DSPy is an offline proposal engine. Deep Agents may serve as a bounded loop strategy only after passing capability, budget, child-isolation, typed-output, and replay gates. Neither component can activate releases, mutate policy, persist uncontrolled memory, or bypass the one generic harness.

This slows adaptation compared with a self-modifying agent. We accept that latency because the research layer may influence live economics later and must remain reproducible, reversible, and owner-governed.
