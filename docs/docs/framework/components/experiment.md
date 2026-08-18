---
title: ExperimentDefinition
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# ExperimentDefinition

This document defines the framework abstraction for an **experiment definition**.

An `ExperimentDefinition` is the generic framework contract stating what a resolved scientific experiment composition contains and how it is resolved.
It defines no concrete experiment.

## What an ExperimentDefinition contains

A resolved experiment composition selects and combines:

- a task;
- a model;
- a concrete Binding (task + model + configured adapters);
- adapters;
- objectives;
- controllers;
- metrics;
- analyses;
- a training protocol;
- an evaluation protocol;
- traces;
- resource requirements.

## Resolution lifecycle

The framework owns the resolution mechanism.
Resolution conceptually proceeds from an experiment reference through a workspace experiment catalogue to the experiment definition, which carries component references resolved against the installed component registry, and finally to a resolved `ExperimentDefinition` and constructed concrete Binding.

The resolution mechanism is framework-owned; the repository owns the concrete experiment definition.

## Executable representation

A concrete experiment is workspace-owned and identified by a canonical `ExperimentRef` of the form `experiment:<name>/vN`.
Its executable declaration is an EHP-SN-defined TOML document at a deterministic, convention-based location:

```text
experiment:<name>/vN
    ↔
experiments/<name>/vN/experiment.toml
```

Discovery is this fixed convention: `experiment:<name>/vN` locates `experiments/<name>/vN/experiment.toml` under the workspace.
There is no arbitrary recursive scanning, no Python package import, and no `ehp_research.registration` for experiments.

`experiment.toml` is a **concrete declaration**: it instantiates this `ExperimentDefinition` specification for one concrete experiment, exactly as a `TaskCorpus` manifest instantiates a task contract.
It is canonical for the experiment it declares without being a semantic specification: the framework specification defines what the fields and constraints mean, and `experiment.toml` declares one instance.

A concrete experiment directory may contain:

```text
experiments/<name>/vN/
    experiment.toml    canonical concrete declaration
    README.md          optional, descriptive (motivation, rationale, reproducibility)
    design/            optional, informal and disposable design notes while designing
```

`README.md` is explanatory only (`DOC-001`) and introduces no new semantics.
`design/` content is temporary design reasoning, not a permanent authority.

## Resolution and construction

`ehp_sn` owns workspace experiment discovery, schema validation, reusable-component resolution, Binding construction, and `resolve_experiment()`, which returns a validated `ExperimentDefinition`.
Resolution proceeds along this lifecycle:

```text
parse ExperimentRef
    ↓
locate workspace experiment declaration
    ↓
validate TOML schema
    ↓
resolve task/model/etc. through installed component registry
    ↓
resolve configured generic adapters
    ↓
resolve parameter configuration
    ↓
construct/validate Binding
    ↓
construct/validate ExperimentDefinition
```

It stops there.
Resource binding, `TrainingRequest`, `EvaluationRequest`, `ExecutionPlan`, and actual execution remain downstream.

The concrete Binding is embedded in the experiment declaration and is not an independently registered or discoverable research component (`ARCH-006`).
There is no separately discoverable `binding:<experiment>/vN` installed component.
A resolved Binding may carry an internal/scoped identity for provenance, but that identity is subordinate to the experiment.

## Parameter composition backend

Hydra/OmegaConf may be used internally for parameter composition, using YAML where appropriate (for example model hyperparameters, objective presets, or runtime presets).
Hydra syntax is not the experiment representation and not the semantic authority (`CONFIG-002`).
Experiment identity and scientific composition are expressed through the EHP-SN TOML contract; Hydra sits below that layer as an implementation backend.

## Concrete ExperimentDefinition authority

The framework defines what a resolved experiment composition contains and how it is assembled.
Which components a particular experiment selects is the concrete `ExperimentDefinition`, declared in `experiments/<experiment>/vN/experiment.toml` and validated against this specification.
There is no separate normative per-experiment markdown: the declaration conforms to this framework specification, and any experimental narrative (motivation, rationale, reproducibility) is carried by an optional descriptive `README.md`.

## Experiment declaration schema (`experiment.toml`)

This section specifies the minimal `experiment.toml` declaration schema, version `v1`.
It is the framework-owned representation of a concrete experiment composition; a concrete `experiment.toml` declares one instance and adds no semantics of its own.

```toml
schema = "ehp-sn/experiment/v1"

ref = "experiment:<name>/vN"

task  = "task:<task>/vN"
model = "model:<model>/vN"

[binding.input]
adapter = "adapter:<adapter>/vN"
# adapter-specific configuration

[binding.output]
adapter = "adapter:<adapter>/vN"
# adapter-specific configuration

[objective]
# objective selection and configuration

[metrics]
# selected metrics

[corpus]
# committed corpus requirement

[resources]
# resource requirements
```

The declaration references declared interfaces and reusable components by canonical reference; it must not redefine their semantics.
Specific endpoint schema (adapter configuration, objective/metric/resource tables) is elaborated in the corresponding framework contract specifications as they are completed; until then this section specifies the top-level shape and the convention that the concrete Binding is embedded in the declaration (`ARCH-006`).

## Deferred specification

This document specifies the declaration boundary: the `experiment.toml` declaration, the deterministic discovery convention, the resolution lifecycle, and the backend independence of the representation.
The resolve-side loader internals and the exhaustive per-endpoint field catalogue remain framework contracts to be completed before production implementation; do not implement against a missing endpoint contract (`ARCH-014`).
