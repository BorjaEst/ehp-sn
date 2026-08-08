---
paths:
  - "packages/ehp-sn/src/**/*.py"
  - "packages/ehp-sn/tests/**/*.py"
  - "docs/docs/framework/**/*.md"
  - "tests/architecture/**/*.py"
  - "pyproject.toml"
  - "packages/*/pyproject.toml"
---

# Framework instructions

These paths participate in the reusable `ehp_sn` framework.

## Framework ownership

`ehp_sn` owns reusable contracts and services that are independent of the concrete EHP research programme.

`docs/authority.md` § "Authority map" assigns "Generic framework contracts and services" to `ehp_sn`, with specification root `docs/docs/framework/`. These paths implement the framework contracts specified there; do not restate or re-enumerate what is framework-owned here — consult the specification root.

## Dependency invariant

ARCH-001 and ARCH-003 govern this. The direction is:

```text
ehp_research → ehp_sn
```

Framework discovery of research definitions must occur through a framework-owned registration/discovery contract.

## Generalization rule

Do not move a concept into the framework merely because multiple current research components share it.

A framework abstraction requires a demonstrated reusable requirement independent of those concrete research components.

Consult `docs/authority.md` § "Authority map" and the specification frontmatter of the concept in question — do not classify a component as framework- or research-owned by listing it here.

Research examples may illustrate framework contracts without becoming framework requirements.

## Specification and implementation

Framework implementation must conform to the normative framework/interface specifications.

Do not silently change public semantics in code because another implementation would be easier.

When code reveals a specification gap, surface the gap and update the appropriate authority.

## Infrastructure boundary

PyTorch, Lightning Fabric, Hydra, Pydantic, MLflow, TorchMetrics, Optuna, Typer, and similar tools are implementation dependencies.

They must not become the semantic authority for EHP-SN public contracts.
