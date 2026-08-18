---
description: "Use when working on concrete repository-level experiments, experiment plans, or experiment composition under experiments/."
applyTo: "experiments/**"
---

# Experiments instructions

## Ownership

`experiments/<experiment>/vN/` owns the concrete scientific composition as a **declaration** (`experiment.toml`) over reusable component specifications:

- concrete Binding selection/configuration for the selected task–model pair;
- the concrete `ExperimentDefinition` it instantiates;
- adapter selection and configuration;
- protocol composition (training, evaluation, analysis);
- objective/controller/metric selection;
- traces and resource requirements.

`experiments/<name>/vN/experiment.toml` is the canonical concrete declaration.
It references reusable component specifications but does not redefine them; it adds no semantics of its own.
An optional `README.md` in the same directory is explanatory only (motivation, rationale, reproducibility).
Informal, disposable design reasoning lives in a `design/` subdirectory while designing and is not a permanent authority.

## Do not

- Duplicate the resolved scientific composition into `run.py` or operation configuration (`train.toml`, `evaluate.toml`, `analyze.toml`) (`ARCH-013`).
- Invent serialization or loader formats if the framework contract is unspecified (`ARCH-014`); report the missing contract instead.
- Register concrete workspace experiments through `ehp_research.registration`.

## Authority

Component semantics are owned by the specifications `docs/authority.md` maps.
The experiment selects and connects them. This file is procedural and never defines semantics.
