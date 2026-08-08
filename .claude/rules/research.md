---
paths:
  - "packages/ehp-research/src/**/*.py"
  - "packages/ehp-research/tests/**/*.py"
  - "docs/docs/research/**/*.md"
  - "experiments/**/*.toml"
---

# Research instructions

These paths contain concrete scientific definitions owned by `ehp_research`.

`ehp_research` may depend on framework contracts from `ehp_sn`.

It must not redefine generic framework semantics locally.

## Research-owned concerns

`docs/authority.md` § "Authority map" assigns the "Research substrate semantics and shared schemas", "Research task semantics", and "Research model, binding, and experiment-family semantics" rows to `ehp_research`, with specification roots `docs/docs/research/substrates/`, `docs/docs/research/tasks/`, and `docs/docs/research/` / `experiments/`. Consult those specification roots for what is research-owned; do not re-enumerate them here.

Put semantics at the narrowest reusable research owner.

## Registration and discovery

ARCH-001 and ARCH-003 govern this.

Research definitions are exposed through the framework-owned registration/discovery interface.

Research registration may depend on `ehp_sn`.

ARCH-003 requires that conflicting duplicate canonical registrations fail rather than depend on import order; consult it rather than re-stating that requirement here.

`docs/decisions.md` DEC-006 records that broader registration properties beyond ARCH-003's duplicate-registration rule have no recorded specification owner yet; do not treat any such property as settled authority until DEC-006 is resolved.

Import-time convenience registration may exist only if the authoritative discovery contract explicitly permits it; automatic CLI discovery must not rely on a framework import of `ehp_research` by name.

## Framework relationship

Prefer:

```text
research definition
    implements or specializes
framework contract
```

Do not copy a generic framework contract into research code or documentation and modify it locally.
