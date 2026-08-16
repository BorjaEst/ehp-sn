---
title: EHP-SN documentation
authority: descriptive
document_status: specified
---

# EHP-SN documentation

EHP-SN is a specification-first framework and research programme for spatial navigation, relational memory, and structural reasoning.

The documentation is organized by semantic responsibility.

## Start here

### Framework

[`framework/`](framework/index.md) defines reusable `ehp_sn` contracts such as generated data artifacts and task corpora.

### Interfaces

[`interfaces/`](interfaces/index.md) defines public operational interfaces:

- CLI;
- configuration;
- Python.

### Research

[`research/`](research/index.md) defines reusable `ehp_research` scientific building blocks:

- substrates;
- tasks;
- models, and objectives/controllers/metrics/analyses as their specifications are added.

### Development

[`development/`](development/index.md) contains repository/development contracts such as data layout.

## Core architecture

```text
ehp_research → ehp_sn
```

The framework owns reusable contracts and services.

The research package owns reusable scientific building blocks.

Repository-level `experiments/` owns concrete experiment compositions and Bindings (ARCH-005/006).

## Data lifecycle

```text
task-neutral substrates
        ↓
task-owned corpus generation
        ↓
self-contained TaskCorpus
        ↓
training / evaluation
        ↓
analysis / reporting
```

The CLI exposes this as:

```text
data → tasks → train → evaluate → analyze → report
```

## Configuration and resources

Scientific definitions declare resource requirements.

Configuration resolves them to exact resources before execution planning.

This keeps scientific meaning separate from workspace/deployment selection while preserving reproducibility.

## Specification status

EHP-SN is under specification-first development.

A specification marked `specified` defines intended semantics; it does not by itself imply complete implementation or scientific validation.

Consult each authoritative specification for its current status.
