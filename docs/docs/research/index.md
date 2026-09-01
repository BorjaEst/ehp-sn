---
title: Research
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Research

This section contains the `ehp_research` specifications: reusable scientific building blocks — substrates, tasks, models, and (as they are added) objectives, controllers, metrics, analyses, and figures.
It mirrors the scientific ownership model of the `ehp_research` package.

```text
substrate
    reusable task-neutral domain structure

task
    scientific problem and truth semantics
```

- [`substrates/`](substrates/index.md) — reusable, task-neutral domain structure.
- [`tasks/`](tasks/index.md) — scientific problem, information regime, and truth semantics.
- [`models/`](models/index.md) — reusable computational architectures and their grounding.
- `objectives/` — reusable scientific objectives (not yet authored; no research page exists).
- `controllers/` — reusable control mechanisms (not yet authored; no research page exists).
- `metrics/` — reusable scientific metrics (not yet authored; no research page exists).
- `analyses/` — reusable analyses (not yet authored; no research page exists).
- [`figures/`](figures/index.md) — reusable scientific visualization capabilities (as written).

A resolved binding — one task, one model, and their configured `InputAdapter`/`OutputAdapter` pair — is not an independent research artifact.
The framework owns the [`Binding`](../framework/components/binding.md) abstraction; a concrete binding is assembled by an experiment definition from the generic adapter contracts in [Adapters](../framework/adapters/index.md) and belongs to a repository-level experiment under `experiments/`, not to `ehp_research`.

Substrate and task specifications conform to and require producer-agnostic, consumer-agnostic shared data schemas owned by the framework; see [Framework contracts](../framework/contracts/index.md).

## Related specifications

- [Framework](../framework/index.md)
- [Interfaces](../interfaces/index.md)
