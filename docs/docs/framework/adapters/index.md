---
title: Adapters
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Adapters

This document defines the generic adapter concepts used by `ehp_sn`: `InputAdapter`, `OutputAdapter`, their responsibility boundaries, the ownership rules for adapter configuration, and the principles used to resolve representational compatibility inside an experiment.

Adapters connect task-domain representations to model-native representations without redefining either side.

```text
TaskData
    ↓
InputAdapter
    ↓
ModelInput
    ↓
Model
    ↓
ModelOutput
    ↓
OutputAdapter
    ↓
TaskPrediction
```

Tasks remain authoritative for task-data and prediction semantics. Models remain authoritative for model-input and model-output semantics. Concrete adapter specifications are authoritative only for the representation transformations they define.

## InputAdapter

An `InputAdapter` transforms authorized task data into a representation accepted by a model-input interface.

Its source is a task-data interface declared by a task. Its target is a model-input interface declared by a model.

An input adapter may perform deterministic representational operations such as canonical ordering, flattening, categorical translation, representation padding, mask construction required by the target interface, or equivalent transformations needed to satisfy the declared model-input representation.

An input adapter must not introduce new scientific information, consume privileged or target-only task channels, or branch on concrete task or model identity.

The adapter stops at the earliest representation satisfying the model's declared native input interface. If the model owns a trainable embedding layer and accepts categorical IDs, the adapter produces categorical IDs rather than embeddings.

## OutputAdapter

An `OutputAdapter` transforms a model-native output into the prediction representation required by a task.

Its source is a model-output interface declared by a model. Its target is a task-prediction interface declared by a task.

An output adapter may perform deterministic representational operations such as domain correspondence, reshaping, removal of representation-only outputs, categorical translation, score-axis reindexing, or task-domain reconstruction when required by the declared target interface.

Selection of which declared model output role an experiment uses is a binding/experiment choice, not an adapter-owned scientific decision. The selected role must already satisfy the source requirements of the chosen output adapter.

An output adapter must not perform task-level scoring, oracle-assisted repair, scientific validity correction, calibration, threshold tuning, or any transformation that changes the scientific meaning of the model result.

## Responsibility boundary

| Concern | Authority |
|---|---|
| Task-data semantics and information boundary | Task |
| Task-prediction semantics | Task |
| Model-native input semantics | Model |
| Model-native output semantics | Model |
| Source-to-target representation transformation | Adapter |
| Adapter-specific compatibility constraints | Adapter |
| Genuine adapter transformation choices | Adapter |
| Task/model/adapter and model-output-role selection | Experiment / binding composition |
| Objectives, metrics, traces, scientific protocols | Their respective scientific owners |
| Device, workers, caching, execution policy | Request / runtime |

An adapter must not duplicate authority already owned by a task or model.

## Genericity

A framework adapter must be expressible entirely in terms of:

- declared source-interface requirements;
- declared target-interface requirements;
- authored adapter-owned configuration; and
- composition state derived during resolution.

A framework adapter must not branch on concrete task or model identity.

This is generic:

```text
read the declared source domain
translate declared categorical identities
adapt to declared target capacity
```

This is not generic:

```python
if task.ref == "maze-hard/v1":
    ...
if model.ref == "hrm/v1":
    ...
```

Logic that inherently depends on a concrete scientific task or model remains research-specific.

## Configuration authority

Every semantic fact has one authoritative owner. An adapter may own a value, consume a value owned by an endpoint, or derive a value from composition, but it must not independently redefine an endpoint-owned fact.

### Endpoint-owned values

Endpoint-owned values are authoritative properties of the selected task or model, for example:

- task domain extent or step count;
- task vocabulary identity;
- model sequence capacity;
- model-native input or output representation;
- model-owned embedding width;
- model-output timing or conditioning semantics.

They are consumed from the resolved endpoint interfaces and are not independently authored as adapter configuration.

### Adapter-owned configuration

Adapter-owned configuration contains genuine transformation choices not determined by either endpoint, for example:

- an explicit categorical correspondence when endpoint vocabulary identities do not determine one uniquely;
- an adapter-specific representation policy when the adapter contract intentionally admits more than one compatible choice.

Only these genuine transformation choices are authored as adapter configuration.

### Derived composition state

Derived composition state is computed during resolution from endpoint-owned values and authored adapter choices.

Examples include:

- position-to-slot correspondence;
- task-step-to-model-step correspondence;
- padding count;
- represented span;
- a category mapping uniquely implied by endpoint declarations.

Derived composition state is not authored configuration and is not an independent precedence source. It is recorded for reproducibility and validation.

Runtime concerns such as device placement, worker count, caching, or data-loader execution policy are not adapter semantic configuration.

## Resolution and compatibility

An adapter specification declares the source and target conditions under which its transformation is valid.

Resolution uses:

```text
declared source interface
+
declared target interface
+
adapter specification
+
authored adapter-owned configuration
        ↓
compatibility checks
        ↓
derived composition state
        ↓
resolved adapter state
```

Adapter resolution checks representational compatibility only. It does not establish that a task-model combination is scientifically meaningful, validated, supported, or mature.

Any incompatibility decidable from endpoint interfaces and adapter configuration must be rejected during resolution rather than discovered during scientific execution.

Input-side resolution may establish composition facts that an output adapter later validates and reuses, such as position-slot or task-step/model-step correspondence. Such facts are derived once and must not be independently re-authored in the reverse direction.

The complete representation and lifecycle of a task-model binding are defined by the framework component responsible for bindings; this document defines only the adapter contribution to that composition.

## Adapter specifications

Concrete adapter specifications use a common section structure:

```text
1. Purpose and scope
2. Interface contract
3. Transformation semantics
4. Configuration and derivation
5. Compatibility and resolution
6. Runtime behavior
7. Information and semantic boundaries
8. Invariants and validation
9. Identity and reproducibility
10. Failure semantics
11. Evolution
12. Examples
```

Current adapter specifications:

| File | Contract | Role | Source | Target |
|---|---|---|---|---|
| `raster-input-v1.md` | `raster-categorical-to-sequence/v1` | InputAdapter | categorical rectangular position domain | categorical sequence |
| `raster-output-v1.md` | `categorical-sequence-to-raster/v1` | OutputAdapter | categorical sequence | categorical rectangular prediction |
| `sequence-input-v1.md` | `observation-relation-sequence-to-sensory-relation-sequence/v1` | InputAdapter | observation/relation task sequence | sensory/relation model sequence |
| `sequence-output-v1.md` | `sensory-prediction-sequence-to-observation-sequence/v1` | OutputAdapter | sensory-prediction model sequence | observation-prediction task sequence |

Filenames are intentionally concise. Canonical contract identities describe the full source-to-target transformation.
