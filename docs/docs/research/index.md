---
title: Research
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Research

This section contains the `ehp_research` specifications: concrete scientific substrates, tasks, and (as they are added) models and experiment families.

```text
substrate
    reusable task-neutral domain structure

task
    scientific problem and truth semantics
```

- [`substrates/`](substrates/index.md) — reusable, task-neutral domain structure.
- [`tasks/`](tasks/index.md) — scientific problem, information regime, and truth semantics.
- [`models/`](models/index.md) — reusable computational architectures and their grounding.

A resolved binding — one task, one model, and their configured `InputAdapter`/`OutputAdapter`
pair — is not an independent research artifact; it is assembled by an experiment definition from
the generic adapter contracts in [Adapters](../framework/adapters/index.md).

Experiment-family specifications live under `experiments/` at the repository root and will be added as they are written.

Substrate and task specifications conform to and require producer-agnostic, consumer-agnostic shared data schemas owned by the framework; see [Framework contracts](../framework/contracts/index.md).

## Related specifications

- [Framework](../framework/index.md)
- [Interfaces](../interfaces/index.md)
