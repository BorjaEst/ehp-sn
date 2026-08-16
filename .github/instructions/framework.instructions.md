---
description: "Use when working on the ehp_sn framework: contracts, adapters, orchestration, or framework docs."
applyTo: "packages/ehp-sn/**, docs/docs/framework/**"
---

# Framework instructions

## Preserve

- No `ehp_research` dependency (`ARCH-001`); `ehp_sn` must not import or declare `ehp_research`.
- Generic semantics only.
  `ehp_sn` holds reusable framework abstractions, contracts, and orchestration, not concrete EHP research instances.
- Generic adapters only.
  Adapters in `ehp_sn` are reusable transformation primitives expressed in terms of declared source/target interfaces and resolved configuration (`ADAPT-001`).
  No experiment-specific adapters (`ARCH-007`).
- No concrete Arena/TEM/HRM/Routebind etc.
  under `ehp_sn`.

## Authority

The framework contracts and services are specified under `docs/docs/framework/`.
The authority map is `docs/authority.md`; the cross-cutting rules are `docs/invariants.md`.
This file is procedural and never defines semantics.
