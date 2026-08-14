---
title: HRM
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# HRM

## Normative summary

HRM is the Hierarchical Reasoning Model used in EHP-SN as a latent recurrent reasoning core.

Its defining structure is a slow high-level recurrent process and a faster low-level recurrent process:

```text
model-native problem representation
        ↓
high-level recurrent state z_H
        ↕
low-level recurrent state z_L
        ↓
theta_summary / schema_slots
        ↓
supervised ACT halt/continue control
```

The EHP-SN HRM realization includes RoPE positional encoding and a schema-slot workspace.

HRM owns the hierarchical recurrent computation and its native reasoning state. Task-specific problem encoding and task-specific prediction decoding remain binding-owned.

## 1. Model definition

Core model variables are:

| Symbol          | Meaning                                                |
| --------------- | ------------------------------------------------------ |
| `z_H`           | slow/high-level recurrent reasoning state              |
| `z_L`           | fast/low-level recurrent reasoning state               |
| `theta_summary` | summary representation of the current reasoning state  |
| `schema_slots`  | model-native workspace slots                           |
| `halt_logits`   | supervised ACT-style scores over `halt` and `continue` |

The high- and low-level states operate at different update frequencies.

```text
H_0
 ├─ L update
 ├─ L update
 ├─ ...
 └─ H update
       ↓
H_1
 ├─ L update
 ├─ ...
```

This is a hierarchy of recurrent computation, not a requirement that `z_H` or `z_L` encode particular symbolic concepts.

HRM performs latent reasoning and does not expose textual chain-of-thought as part of its interface.

## 2. Architecture

```text
native slot sequence
        ↓
model-owned embedding/projection
        ↓
RoPE
        ↓
schema-slot workspace
        ↓
┌──────────────────────┐
│ H recurrent module   │
│ layers_h / cycles_h  │
└──────────┬───────────┘
           ↕
┌──────────┴───────────┐
│ L recurrent module   │
│ layers_l / cycles_l  │
└──────────┬───────────┘
           ↓
theta_summary / schema_slots
           ↓
halt_logits
```

### H/L recurrence

`z_L` is updated on the faster timescale under the current high-level context.

`z_H` is updated according to the declared slower schedule.

The exact H/L nesting and cycle counts are model-owned.

### Positional encoding

RoPE is part of the HRM architecture and must not be performed by a task adapter.

### Schema workspace

Schema slots are model-native working representations used by downstream bindings/decoders.

A task may determine what information is encoded into the input slots, but it does not assign intrinsic symbolic meaning to the latent schema slots.

## 3. Native interface

### Inputs

HRM consumes an ordered sequence of model-native slots.

Each slot contains a representation in the model input feature domain. The binding is responsible for constructing those slot values from task data.

The model interface declares:

| Property            | Meaning                                                                            |
| ------------------- | ---------------------------------------------------------------------------------- |
| `sequence_capacity` | maximum number of native slots                                                     |
| `input_width`       | feature width consumed by the HRM core after any model-owned categorical embedding |
| `slot_order`        | ordered slot identity used by RoPE                                                 |
| `sequence_mask`     | optional validity mask for padded slots                                            |
| `reset`             | initializes problem-scoped recurrent state                                         |

If the endpoint accepts categorical IDs rather than ready feature vectors, the categorical vocabulary and embedding are model-owned.

### Outputs

HRM's stable native outputs are:

| Role            | Meaning                                                  |
| --------------- | -------------------------------------------------------- |
| `theta_summary` | summary representation for downstream prediction/control |
| `schema_slots`  | final model-native workspace representations             |
| `halt_logits`   | supervised ACT-style scores for `halt`, `continue`       |

`z_H` and `z_L` are optional model traces.

HRM itself does not define a task-specific answer vocabulary or task-specific decoder. A binding may attach a decoder to `theta_summary`, `schema_slots`, or another explicitly supported native representation.

`halt_logits` are not reinforcement-learning Q-values.

## 4. State and computation

HRM state contains:

- `z_H`;
- `z_L`;
- schema-slot/workspace state;
- ACT deliberation state required by the model.

Independent problems reset all problem-scoped reasoning state.

One reasoning cycle:

1. initialize or restore the native slot representation and recurrent state;
2. perform the declared low-level recurrent updates;
3. update high-level state according to the H/L schedule;
4. update `theta_summary` and `schema_slots`;
5. produce `halt_logits`;
6. apply the HRM supervised ACT halt/continue rule;
7. terminate or perform another reasoning cycle.

The H/L schedule, RoPE, workspace update, and ACT control are model-owned and must not be reproduced by a binding.

## 5. Model parameters

Model-owned parameters include:

- model width;
- `sequence_capacity`;
- native input width and model-owned categorical embedding sizes where applicable;
- schema-slot count;
- `layers_h`;
- `cycles_h`;
- `layers_l`;
- `cycles_l`;
- attention/MLP dimensions;
- RoPE parameters;
- maximum model deliberation capacity where intrinsic.

Task decoder dimensions, task label mappings, corpus choice, optimizer, learning rate, training duration, batch size, device, and output paths are outside HRM.

## 6. Observables

Stable model-native observables are:

- `theta_summary`;
- `schema_slots`;
- `halt_logits`.

Optional diagnostic traces may expose:

- `z_H`;
- `z_L`;
- the evolution of `theta_summary` or schema slots across reasoning cycles.

Each observable must define its cycle timing.

## 7. Conformance

A conforming HRM implementation must satisfy:

- distinct H and L recurrent states exist;
- H and L follow the declared nested update schedule;
- RoPE is model-owned;
- schema slots are model-owned workspace state;
- the stable model endpoint is `theta_summary` / `schema_slots`, not a task-specific prediction vocabulary;
- `halt_logits` have supervised ACT-style semantics;
- independent problems do not inherit undeclared recurrent state;
- task bindings do not implement model-owned recurrence or ACT control.

## 8. Boundaries and related specifications

Bindings own:

- task-to-HRM slot construction;
- padding and task-category mapping;
- any task-specific decoder from HRM native representations to task predictions.

Bindings must not perform RoPE, model-owned embeddings, H/L recurrence, schema-workspace updates, or ACT control.

Experiments own training/evaluation protocols and objective composition.

Relevant neighboring documents include:

- HRM-rl;
- MazeHard–HRM binding;
- Routebind–HRM binding;
- HRM reproduction experiments.

## References

- Wang, G. et al. (2025). _Hierarchical Reasoning Model_. arXiv:2506.21734.
