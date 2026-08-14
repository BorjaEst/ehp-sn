---
title: TEM
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# TEM

## Normative summary

TEM is the Tolman–Eichenbaum Machine used in EHP-SN as a recurrent relational-memory model.

It separates:

- sensory/content representation `x`;
- structural/relational representation `g`;
- conjunctive representation `p`;
- environment-specific associative memory `M`.

TEM owns the computation that constructs and updates these representations, the model state that stores their associations, and the model-native prediction and trace outputs.

Task semantics, task-to-model conversion, task targets, experiment protocols, and runtime configuration are outside the model.

## 1. Model definition

TEM combines reusable relational structure with environment-specific sensory associations.

```text
relation / transition
        ↓
structural state g
        │
        ├──────────┐
        │          │
sensory state x    │
        │          │
        └────→ conjunctive state p
                     │
                     ↓
              associative memory M
```

Core variables are:

| Symbol | Meaning                                                    |
| ------ | ---------------------------------------------------------- |
| `x_t`  | model-internal sensory/content representation              |
| `g_t`  | model-internal structural/relational representation        |
| `p_t`  | conjunctive representation combining `g_t` and `x_t`       |
| `M_t`  | environment-specific associative-memory state              |
| `a_t`  | relation/transition input associated with the current step |

`g_t` is a latent structural representation. It is not a decoded physical position supplied by a task.

The model follows the TEM architecture introduced by Whittington et al. (2020). Any EHP-SN deviation that changes the model computation must be documented at the affected rule rather than in a separate compatibility/versioning layer.

## 2. Architecture

```text
sensory_id
    ↓
sensory pathway
    ↓
x_t ────────────────┐
                    │
relation_id         │
    ↓               │
structural pathway  │
    ↓               │
g_t ────────────────┤
                    ↓
              conjunctive p_t
                    │
                    ↕
              associative M_t
                    │
                    ↓
          sensory prediction pathway
```

### Sensory pathway

The sensory pathway maps the native sensory identity to `x_t`.

If the native interface accepts categorical sensory identifiers, their trainable embedding belongs to TEM.

### Structural pathway

The structural pathway updates `g_t` from prior structural state and the incoming relation:

```text
g_(t-1), a_t
    ↓
structural transition
    ↓
g_t
```

The task or binding must not provide `g_t` directly.

### Conjunctive pathway

The model combines `g_t` and `x_t` to construct `p_t`.

The conjunction is model-owned because it defines how structural and sensory information are bound before memory storage or retrieval.

### Associative memory

TEM maintains environment-specific associative memory over its internal representations.

The memory supports retrieval of previously associated information from the current model state. Its representation and update rule are part of the TEM implementation and must preserve the adopted TEM semantics.

## 3. Native interface

### Inputs

TEM consumes an ordered sequence with these semantic roles:

| Role            | Meaning                                                           |
| --------------- | ----------------------------------------------------------------- |
| `sensory_id`    | current categorical sensory/content identity                      |
| `relation_id`   | relation producing the current step from the preceding valid step |
| `reset`         | initializes environment/sequence-specific model state             |
| `sequence_mask` | optional validity mask when padded storage is used                |

At the first valid step after reset, no ordinary relation from a preceding task step exists.

### Outputs

The stable task-facing model output is the declared sensory-prediction role.

The following are model-native observables rather than task predictions:

- `x_t`;
- `g_t`;
- `p_t`;
- associative-memory diagnostics.

Every sensory-prediction role must state its temporal meaning explicitly, for example whether it predicts the current sensory identity or another declared step.

## 4. State and computation

TEM distinguishes:

```text
learned parameters
    persist across checkpoints/runs

recurrent structural state
    persists across valid sequence steps

environment-specific associative memory
    persists until reset

transient activations
    exist only during one model computation
```

A reset initializes all environment/sequence-specific recurrent and memory state.

A model step follows the adopted TEM inference schedule:

1. apply reset when required;
2. use `relation_id` and prior structural state to update the structural pathway;
3. encode the current sensory identity;
4. compute conjunctive representations;
5. perform the TEM memory/inference operation;
6. emit the declared sensory prediction;
7. update environment-specific associative memory;
8. retain recurrent state for the next valid step.

The precise read/inference/write equations are implementation-level details only to the extent that alternative implementations preserve this adopted TEM computation. A binding must never own or reorder these operations.

## 5. Model parameters

Model-owned parameters are architectural or computational parameters such as:

- sensory vocabulary capacity;
- relation vocabulary capacity;
- structural representation dimensions;
- sensory representation dimensions;
- conjunctive representation dimensions;
- associative-memory dimensions;
- structural-transition architecture;
- intrinsic TEM regularization parameters required by the adopted model.

Optimizer settings, learning rate, batch size, training duration, corpus selection, device, precision, and output paths are not model parameters.

## 6. Observables

Stable model-native observables are:

- sensory representation `x_t`;
- structural representation `g_t`;
- conjunctive representation `p_t`;
- declared sensory prediction;
- explicitly supported associative-memory diagnostics.

Each observable must define its step timing and semantic axes.

Recording an observational trace must not alter model computation.

## 7. Conformance

A conforming TEM implementation must satisfy:

- sensory and structural representations are distinct model-owned pathways;
- `g_t` is derived from prior model state and relational input rather than copied from task coordinates;
- `p_t` binds structural and sensory information;
- associative memory is environment-specific model state;
- embeddings, structural transition, conjunction, memory retrieval, and memory update remain inside TEM;
- reset clears every sequence/environment-specific state declared by the model;
- the model emits the declared sensory-prediction role without privileged task information.

## 8. Boundaries and related specifications

Bindings own transformation between task semantics and the TEM native interface.

They may map task categorical identities to the model's declared categorical domains and preserve sequence/reset alignment. They must not implement TEM embeddings, structural-state updates, conjunctive computation, memory retrieval, or memory updates.

Experiments own training/evaluation composition, objective weighting, resource selection, and protocol choices.

Relevant neighboring documents include:

- Arena task specification;
- Arena–TEM binding;
- TEM experiments and analyses.

## References

- Whittington, J. C. R. et al. (2020). _The Tolman–Eichenbaum Machine: Unifying Space and Relational Memory through Generalization in the Hippocampal Formation_. Cell 183, 1249–1263.e23.
