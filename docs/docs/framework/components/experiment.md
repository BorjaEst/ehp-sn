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
The concrete Binding is embedded in the declaration and is not an independently registered or discoverable component (`ARCH-006`).
The exhaustive `v1` field catalogue for each endpoint is specified in the following subsection, "Full declaration field catalogue (v1)"; per-endpoint configuration sets that belong to a referenced contract (for example the exhaustive per-adapter `config` field set) remain owned by that contract and are referenced, not reproduced.

### Full declaration field catalogue (v1)

This subsection specifies the exhaustive `v1` field catalogue for `experiment.toml`.
It is the framework-owned declaration shape exercised against the authored concrete declarations (`ARCH-016`); those declarations evidence the variance the schema must accommodate but are not normative content here (`ARCH-002`).
The declaration references declared interfaces and reusable components by canonical reference; it must not redefine their semantics.

#### Top-level scalar keys

The top of the declaration holds four scalar keys.

| Key      | Type                     | Meaning                        |
| -------- | ------------------------ | ------------------------------ |
| `schema` | `"ehp-sn/experiment/v1"` | declaration-schema identifier  |
| `ref`    | `ExperimentRef`          | canonical experiment reference |
| `task`   | component reference      | canonical task reference       |
| `model`  | component reference      | canonical model reference      |

`schema` is the declaration-schema identifier this declaration conforms to, `ehp-sn/experiment/v1`.
`ref` is the `ExperimentRef` identifying the concrete experiment, of the form `experiment:<name>/vN`.
`task` and `model` are canonical component references to the task and model the experiment selects, of the forms `task:<task>/vN` and `model:<model>/vN`; they are resolved through the installed component registry during resolution.

#### `[binding.input]` and `[binding.output]`

A concrete Binding embeds one configured `InputAdapter` and one configured `OutputAdapter` in the declaration (`ARCH-006`; `BIND-001`).

```toml
[binding.input]
adapter = "adapter:<kind>/v1"

[binding.input.config]
# adapter-owned transformation choices only

[binding.output]
adapter = "adapter:<kind>/v1"

[binding.output.config]
# adapter-owned transformation choices only
```

`adapter` is a canonical adapter reference to the selected `InputAdapter` or `OutputAdapter`.
The `config` block carries **only** genuine adapter-owned transformation choices, per the adapter configuration authority (`ADAPT-003`).
Endpoint-owned values (task domain extent, task vocabulary identity, model sequence capacity, model-native input/output representation, and similar) are consumed from the resolved endpoint interfaces and are **not** authored here.
Derived composition state (position-to-slot correspondence, task-step-to-model-step correspondence, padding, a category mapping uniquely implied by endpoint declarations, and similar) is computed during resolution and is **not** authored configuration.
Only a genuine transformation choice not determined by either endpoint — for example an explicit categorical correspondence, or an adapter-specific representation policy the adapter contract intentionally leaves open — is authored in `config`.
Runtime concerns such as device placement or execution policy are not adapter semantic configuration.

The exhaustive per-adapter `config` field set is owned by the referenced adapter contract, not by this experiment schema (`ARCH-014`).
This experiment schema does not invent per-adapter formats and does not re-list adapter-owned fields; a missing per-adapter field set blocks resolve-side use of that adapter until the adapter contract is completed.

#### Optional `[controller]`

A declaration may include an optional `[controller]` table that **selects by reference** a reusable deliberation controller orthogonal to the Binding.

```toml
# candidate shape (selection by reference; spec-pending)
[controller]
ref = "controller:<controller>/vN"

[controller.config]
# controller selection/configuration by reference only; spec-pending
```

`ref` is a canonical controller reference; `config` carries selection/configuration by reference.
The controller is a specification-pending reusable research building block whose canonical contract does not yet exist; this experiment schema must not invent that contract (`ARCH-014`).
The `[controller]` endpoint appears when an experiment selects a deliberation controller orthogonal to the Binding, as evidenced by the authored declarations; its framework shape — controller orthogonality relative to the Binding — remains an open framework-review point and is not over-specified here.

#### `[objective]`

The `[objective]` table selects and configures one or more objectives by reference.

```toml
[objective]
# objective selection and configuration by reference
```

Objective semantics are owned by the objective/owner specifications and are not redefined here (`ARCH-002`).
The schema leaves the table flexible: concrete authoring may be comment-only, or may reference objectives by canonical reference.

#### `[metrics]`

The `[metrics]` table maps a metric name to a task-owned metric ID.

```toml
[metrics]
NAME = "task:<task>/vN#<metric-id>"
```

Each entry references a task-owned metric ID under the selected task.
Metrics are taken from the task specification and are **not** redefined here (`BIND-001`); the experiment selects named metrics, it does not define their meaning.

#### `[corpus]`

The `[corpus]` table declares a committed corpus requirement and, where the task defines them, task-owned parent-role selections.

```toml
[corpus]
requirement = "task:<task>/vN"
```

`requirement` is the canonical task reference whose corpus is required.
Per `CONFIG-001`, the requirement binds at request time to an exact permitted resource rather than declaring a concrete artifact here.
Parents are selected through resolved build configuration or another explicitly specified reproducible binding mechanism (`DATA-003`).
Where the task defines parent roles, the table may carry task-owned parent-role keys; the exact parent-role vocabulary and its values are task-owned and are not enumerated or redefined by this framework schema.

#### `[resources]`

The `[resources]` table declares resource requirements, shaped by the resource-requirements contract (`CONFIG-001`).

```toml
[resources]
# requirement declarations: ref, resource_kind, accepted_schema_ids,
# cardinality, definition_resource_category, definition_resource_ref,
# request_policy, compatibility_validator_id, description
```

Requirement declarations follow the resource-requirements field catalog: requirement reference, resource kind, accepted schema IDs, cardinality, definition resource category and reference, request policy, optional package-owned compatibility validator, and description.
Resource categories (`fixed`, `default`, `none`) and request policies (`forbidden`, `allowed`, `required`) are owned by the resource-requirements contract and are not redefined here.

#### Binding boundary

Across `[binding.input]` and `[binding.output]`, the composition must not change public-versus-withheld information, task truth, target meaning, split meaning, or metric meaning (`BIND-001`).
Neither adapter may add privileged information or perform task-level scoring (`ADAPT-002`).

## Deferred specification

This document specifies the declaration boundary: the `experiment.toml` declaration, the deterministic discovery convention, the resolution lifecycle, the backend independence of the representation, and the full `v1` declaration field catalogue above.
The resolve-side loader internals remain a framework contract to be completed before production implementation; do not implement against a missing endpoint contract (`ARCH-014`).
The exhaustive per-adapter `config` field sets remain owned by their referenced adapter contracts, not by this experiment schema.
