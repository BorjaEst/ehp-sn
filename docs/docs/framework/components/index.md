---
title: Framework components
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Framework components

The framework defines generic component abstractions (contracts) that concrete scientific definitions implement.
Generic `Task` and `Model` contracts, the `ModelIOSpec` abstraction, and the `ExperimentDefinition` abstraction are framework-owned; their concrete scientific definitions and compositions are research- or experiment-owned (`docs/authority.md`).

## Documents

- [ModelIOSpec](model-io.md) — the model IO specification abstraction; what it contains and validates.
- [Experiment](experiment.md) — the `ExperimentDefinition` abstraction and its resolution.

Concrete adapters are specified under the framework [Adapters](../adapters/index.md) reference.
Concrete task and model definitions live under `docs/docs/research/`.
