---
description: "Use when working on concrete repository-level experiments, experiment plans, or experiment composition under experiments/."
applyTo: "experiments/**"
---

# Experiments instructions

## Ownership

`experiments/<experiment>/vN/` owns concrete scientific composition:

- concrete Binding semantics for the selected task–model pair;
- concrete `ExperimentDefinition`;
- adapter selection and configuration;
- protocol composition (training, evaluation, analysis);
- objective/controller/metric selection;
- traces and resource requirements.

`plan.md` is the normative human-readable scientific authority for the experiment (`authority: normative`).
It references reusable component specifications but does not redefine them.
A `README.md` in the same directory is explanatory only.

## Do not

- Duplicate the resolved scientific composition into `run.py` or operation configuration (`train.toml`, `evaluate.toml`, `analyze.toml`) (`ARCH-013`).
- Invent serialization or loader formats if the framework contract is unspecified (`ARCH-014`); report the missing contract instead.
- Register concrete workspace experiments through `ehp_research.registration`.

## Authority

Component semantics are owned by the specifications `docs/authority.md` maps.
The experiment selects and connects them. This file is procedural and never defines semantics.
