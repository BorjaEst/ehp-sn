---
applyTo: "packages/ehp-research/src/**/*.py,packages/ehp-research/tests/**/*.py,docs/docs/research/**/*.md"
---

# Research instructions

These paths contain concrete scientific definitions owned by `ehp_research`.

`ehp_research` may depend on framework contracts from `ehp_sn`.

It must not redefine generic framework semantics locally.

## Research-owned concerns

Research-owned concerns include:

- concrete substrates;
- shared research substrate schemas;
- tasks;
- models;
- bindings;
- objectives;
- research metrics;
- analyses;
- experiment families;
- research-specific study definitions.

Put semantics at the narrowest reusable research owner.

Examples:

- common task-facing topology semantics shared by DungeonGen and Maze-ND belong in a shared research topology contract;
- Arena semantics belong to Arena;
- Arena-to-TEM representation belongs to the Arena–TEM binding;
- experiment-specific scientific protocol choices belong to the experiment.

## Registration and discovery

Research definitions are exposed through the framework-owned registration/discovery interface.

Research registration may depend on `ehp_sn`.

`ehp_sn` must not hard-code imports of `ehp_research`.

Registration must:

- use canonical references;
- be deterministic;
- avoid import-order-dependent semantics;
- reject conflicting duplicate canonical registrations;
- avoid expensive scientific execution during registration.

Import-time convenience registration may exist only if the authoritative discovery contract explicitly permits it; automatic CLI discovery must not rely on a framework import of `ehp_research` by name.

## Framework relationship

Prefer:

```text
research definition
    implements or specializes
framework contract
```

Do not copy a generic framework contract into research code or documentation and modify it locally.
