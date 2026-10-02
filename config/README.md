---
title: Configuration
authority: descriptive
---

# Configuration

This directory holds **operational and workspace configuration** — invocation-specific and local deployment settings, not scientific composition.
Scientific composition lives in [`experiments/`](../experiments/); reusable component defaults live in their `ehp_research` component definitions.

## Layout

```text
config/
├── resources/
├── data/
├── tasks/
├── train/
├── evaluate/
├── analyze/
├── report/
└── workspace.toml
```

Each operation subdirectory holds the operation-specific configuration consumed by the corresponding [`ehp-sn` CLI](../docs/docs/interfaces/cli/index.md) command.
`workspace.toml` holds workspace-level defaults and resource bindings.

### `config/resources/` — reusable named resource configurations

Reusable named configurations for things that substrate and task configurations depend on, named by the **resource integration being configured** rather than by framework lifecycle semantics:

```text
config/resources/dungeongen/classic-medium.toml
config/resources/flaitenberger/maze-hard-augmented.toml
```

```text
config/resources/<namespace>/<profile>.toml
    ↔ resource:<namespace>/<profile>/v1
```

```toml
[resource]
    schema = "dungeongen/generator-resource/v1"

[generator]
    protocol = "dungeongen/generation/v1"
    profile  = "dungeongen/profile/general/v1"

[generator.params]
    ...
```

Not every file here is a resource: a file that declares `[source]` instead is an **external source declaration**, identified as `external-source:<authority>/<name>/v1`.
It supplies upstream data rather than binding a resource requirement, so it is not a resource and no `ResourceRequirement` is satisfied by it.

Data and task configurations reference these by logical reference, never by relative path.
The `[resource]` header is the framework-owned part; every section after it is owned by the declared schema.
See [`docs/docs/interfaces/configuration/resources.md`](../docs/docs/interfaces/configuration/resources.md).

### Common configuration envelope

Every substrate profile shares one small framework-owned envelope and keeps a producer-owned body:

```text
config/data/<family>/<profile>.toml

[substrate]              required common substrate header
[sources.<role>]         optional upstream DATA selection
[resources.<role>]       optional non-data resource binding
<other top-level>        producer-owned scientific configuration
```

```text
[sources.<role>]     one block per declared source role, naming its mechanism
                     with an explicit `kind`
[resources.<role>]   one block per declared resource role, binding exactly one
                     logical resource reference
```

A source selection states its mechanism explicitly:

```toml
[sources.authoritative_source]
    kind = "external"
    ref  = "external-source:flaitenberger/maze-hard-augmented/v1"
```

`kind` is one of `external`, `artifact`, or `build`; it is never inferred from which keys are present.
A resource selection names an exact logical resource:

```toml
[resources.generator]
    ref = "resource:dungeongen/classic-medium/v1"
```

The profile never restates whether a role is data or a capability: `Definition.sources` and `Definition.resources` already say so.

Empty blocks are omitted entirely.
A producer section must not collide with the reserved framework names `[substrate]`, `[sources]`, or `[resources]`.
There is deliberately no universal `parameters` wrapper: the framework cannot interpret producer fields anyway, and hiding them adds a level that carries no semantics.
See [`docs/docs/interfaces/configuration/envelope.md`](../docs/docs/interfaces/configuration/envelope.md).

### `config/data/` — reusable substrate build configurations

Reusable concrete substrate build configurations, selected by the generic `ehp-sn data` lifecycle:

```console
ehp-sn data plan substrate:dungeon/v1 --config config/data/dungeon/unique-topologies.toml
```

These select concrete values only; they do not define what a substrate means (that is `ehp_research`), nor generic configuration/runtime behavior (that is `ehp_sn`).

Filenames describe the **data condition**, not a consumer: a substrate configuration names a concrete reusable realization of that producer (e.g. the `general` Dungeon variant) and must not encode which experiment/task consumes it.
Actual experiment-to- substrate coupling lives in `experiment.toml` (the composition authority), which selects and couples these reusable files; `ehp_sn` validates compatibility during resolution.

## Ownership boundary

Configuration must not become a second semantic home for scientific meaning owned elsewhere (`ARCH-002`).
It supplies:

- **workspace defaults and exact resource bindings** (`config/workspace.toml`, schema `ehp-sn/workspace/v1`); e.g. `request.runtime.device`, `request.runtime.precision`, artifact store root, and requirement-to-artifact bindings;
- **operation-specific overrides** (`config/<op>/…`) that configure one operation over an already-defined experiment, without redefining task, model, or binding (`ARCH-013`).

Canonical public semantics are owned by [`docs/docs/interfaces/configuration/`](../docs/docs/interfaces/configuration/index.md).
Hydra is an internal composition backend only, not the public configuration language (`CONFIG-002`).

## Invocation

```console
ehp-sn train run experiment:arena-tem/v1 --config config/train/arena-tem.toml
```

This directory is descriptive; the normative configuration model is [`docs/docs/interfaces/configuration/model.md`](../docs/docs/interfaces/configuration/model.md).
