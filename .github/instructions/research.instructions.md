---
description: "Use when working on ehp_research: reusable scientific building blocks, registration/discovery, or research docs."
applyTo: "packages/ehp-research/**, docs/docs/research/**"
---

# Research instructions

## Preserve

- Reusable scientific building blocks only: substrates, tasks, models, objectives, controllers,
  metrics, analyses, configuration, registration (`ARCH-004`).
- No `experiments/` under `ehp_research` (`ARCH-005`).
- No concrete task-model `bindings/` under `ehp_research` (`ARCH-006`).
- Tasks stay independent of concrete models (`ARCH-009`); models stay independent of concrete
  tasks (`ARCH-010`).
- Concrete substrate producers belong here and consume framework-owned logical contracts
  (`ARCH-012`).

## Registration and discovery

ARCH-001 and ARCH-003 govern this.

Research definitions are exposed through the framework-owned registration/discovery interface.
Research registration may depend on `ehp_sn`.
ARCH-003 requires registration to use canonical references, not make catalogue semantics depend on registration/import order, and reject conflicting duplicate canonical references; consult it rather than re-stating that requirement here.
Python-engineering hygiene (avoiding expensive work at import time, keeping imports lightweight) is implementation practice, not an architectural invariant.

Import-time convenience registration may exist only if the authoritative discovery contract explicitly permits it; automatic CLI discovery must not rely on a framework import of `ehp_research` by name.

Concrete workspace experiments under `experiments/` are discovered through workspace experiment discovery, not through `ehp_research.registration`.

## Authority

Reusable scientific semantics live in the corresponding `docs/docs/research/` specifications.
Concrete experiment composition belongs to repository-level `experiments/`, declared canonically in `experiments/<experiment>/vN/experiment.toml` over those reusable specifications.
This file is procedural and never defines semantics.
