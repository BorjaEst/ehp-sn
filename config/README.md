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

### `config/data/` — reusable substrate build configurations

Reusable concrete substrate build configurations, selected by the generic `ehp-sn data` lifecycle:

```console
ehp-sn data plan substrate:dungeongen/v1 --config config/data/dungeongen-general.toml
```

These select concrete values only; they do not define what a substrate means (that is `ehp_research`), nor generic configuration/runtime behavior (that is `ehp_sn`).

Filenames describe the **data condition**, not a consumer: a substrate configuration names a concrete reusable realization of that producer (e.g. the `general` DungeonGen variant) and must not encode which experiment/task consumes it.
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
