# Research models

## Purpose

This directory contains the scientific specifications of the models used by `ehp_research`.

A model document defines the task-independent computational system owned by that model:

```text
model-native input
        ↓
model computation
        ↓
model-native output / state / observables
```

The model specification stops at the model boundary.

## What belongs in a model specification

A model document owns:

- the model's native input and output semantics;
- defining architecture and computation;
- recurrent state, memory, and workspace;
- model-owned embeddings and projections;
- architectural parameters;
- stable model-native observables;
- model-defining conformance invariants.

It does not define:

- task semantics, targets, or oracle truth;
- task-to-model or model-to-task representation;
- task-specific decoders that are not intrinsic to the reusable model;
- controller, reward, or return semantics;
- training or evaluation protocols;
- optimizer or runtime configuration.

A useful diagnostic is:

> If a statement is needed to distinguish, implement, or connect this model correctly, it probably belongs here. If it remains true for almost every model in the repository, it probably belongs elsewhere.

## Native model boundary

```text
TaskData
    ↓
InputAdapter
    ↓
ModelInput        ← model begins
    ↓
Model
    ↓
ModelOutput       ← model ends
    ↓
OutputAdapter
    ↓
TaskPrediction
```

The model document is authoritative from the earliest model-native input through the latest model-native output.

Model-owned embeddings, recurrence, memory, attention, workspace updates, and intrinsic control remain inside this boundary.

## Document structure

Model documents use the following compact structure:

| Section                                  | Include                                                                       | Do not include                                              |
| ---------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Normative summary                        | shortest complete definition of the model and its role                        | training recipe, results, implementation detail             |
| 1. Model definition                      | defining scientific idea, local notation, model-specific concepts             | literature review, shared/common math documents             |
| 2. Architecture                          | model-owned components, information flow, defining equations                  | Python class layout unless semantically normative           |
| 3. Native interface                      | model-native inputs/outputs, ordering, capacity, masks, reset, timing         | task-specific mappings                                      |
| 4. State and computation                 | recurrent state, memory/workspace, persistence, reset, update/inference order | generic runtime lifecycle                                   |
| 5. Model parameters                      | architecture-affecting parameters                                             | optimizer, learning rate, batch size, corpus, device, paths |
| 6. Observables                           | stable scientifically meaningful model-native states/traces                   | arbitrary internal tensors                                  |
| 7. Conformance                           | small set of model-defining invariants                                        | benchmark thresholds                                        |
| 8. Boundaries and related specifications | model-specific ownership edge and links                                       | duplicated neighboring specifications                       |

Sections should remain concise. Do not add material merely to fill the structure.

## Authoring rules

- Keep each model mathematically self-contained for the notation and equations it actually uses.
- Do not introduce shared model-mathematics documents merely to avoid small amounts of repetition.
- Describe scientific/computational semantics, not repository class organization.
- Do not repeat generic framework rules unless a model-specific consequence must be stated.
- Do not include training recipes, reproduction settings, benchmark results, or runtime policy.
- Expose only observables that are stable and scientifically meaningful.
- Put task-specific encodings and decoders in bindings rather than model documents.

## Naming

Model names identify distinct scientific/computational designs, for example:

```text
TEM
TEM-t
HRM
HRM-rl
```

Implementation versions do not version the scientific model document. A materially different model design receives a different model name.

## Model catalogue

### TEM

[TEM](tem.md)

Recurrent relational-memory model separating sensory state `x`, structural state `g`, conjunctive state `p`, and environment-specific associative memory.

### TEM-t

[TEM-t](tem-t.md)

Transformer reformulation of TEM using relation-dependent structural state and attention over prior experience for associative retrieval.

### HRM

[HRM](hrm.md)

Hierarchical recurrent reasoning core with slow `H` and fast `L` processes, RoPE, schema-slot workspace, and supervised ACT-style halting.

### HRM-rl

[HRM-rl](hrm-rl.md)

HRM reasoning core with reinforcement-learned deliberation control, a halt/continue action-value head, and a separate STR state-value critic.
