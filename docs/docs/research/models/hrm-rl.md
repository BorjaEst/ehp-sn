---
title: HRM-rl
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# HRM-rl

## Normative summary

HRM-rl is HRM with reinforcement-learned deliberation control.

It reuses the hierarchical PFC reasoning core of HRM and changes the halt/continue mechanism from supervised ACT-style classification to action-value-based control. It also adds a separate STR critic.

```text
PFC reasoning core
    ↓
theta_summary / schema_slots
    ├──→ Q(halt), Q(continue)
    └──→ STR critic → V(s)
```

HRM-rl owns the PFC+STR model architecture and the native semantics of its Q-value and state-value outputs.

Reward design, policy sampling, TD targets, discounting, optimizer configuration, and warm-up schedules are outside the model.

## 1. Model definition

HRM-rl keeps the HRM reasoning variables:

| Symbol          | Meaning                                   |
| --------------- | ----------------------------------------- |
| `z_H`           | slow/high-level recurrent reasoning state |
| `z_L`           | fast/low-level recurrent reasoning state  |
| `theta_summary` | PFC reasoning summary                     |
| `schema_slots`  | PFC workspace                             |

It adds:

| Output        | Meaning                                                                |
| ------------- | ---------------------------------------------------------------------- |
| `q_values`    | action-value estimates for the canonical actions `halt` and `continue` |
| `state_value` | STR estimate of the current deliberation-state value                   |

The canonical action domain is:

```text
halt
continue
```

The Q and state values are interpreted under the resolved deliberation-control return specification supplied by the surrounding controller/objective composition.

The model defines the estimator roles and architecture; it does not define one fixed reward function, discount factor, or TD algorithm.

## 2. Architecture

### PFC reasoning core

HRM-rl uses the same native slot interface, RoPE, schema workspace, and H/L recurrence defined by HRM.

```text
native slot sequence
        ↓
HRM PFC reasoning core
        ↓
theta_summary / schema_slots
        ├──→ q_values
        └──→ STR
                ↓
            state_value
```

### Q-value head

The PFC Q head produces exactly two ordered values:

```text
Q(halt)
Q(continue)
```

The head belongs to HRM-rl.

Sampling or selecting an action from these values belongs to the deliberation controller.

### STR critic

STR consumes the current PFC deliberative representation and produces one scalar `state_value`.

The implementation may include `q_values` among the STR input features, but that detail is not part of the scientific model contract unless required by the adopted architecture.

STR is non-recurrent in HRM-rl and does not constitute an additional H/L reasoning level.

## 3. Native interface

### Inputs

HRM-rl uses the HRM native slot interface:

| Property                  | Meaning                                               |
| ------------------------- | ----------------------------------------------------- |
| `sequence_capacity`       | maximum number of native problem slots                |
| `input_width`             | model-native feature width                            |
| `slot_order`              | ordered slot identity                                 |
| `sequence_mask`           | optional validity mask                                |
| `reset`                   | starts a new problem                                  |
| resumable reasoning state | H/L/workspace state for the same deliberation lineage |

The binding constructs the native slot sequence. The controller may pass back resumable reasoning state after `continue`.

### Outputs

HRM-rl's stable native outputs are:

| Role            | Meaning                                  |
| --------------- | ---------------------------------------- |
| `theta_summary` | PFC reasoning summary                    |
| `schema_slots`  | PFC workspace                            |
| `q_values`      | ordered estimates for `halt`, `continue` |
| `state_value`   | scalar STR critic estimate               |

Task-specific answer prediction is binding-owned and decoded from supported HRM-rl native representations.

The action axis of `q_values` is fixed and must not depend on implementation ordering.

## 4. State and computation

PFC H/L/workspace state may persist across multiple deliberation interactions for the same problem.

Independent problems must not share problem-scoped reasoning state.

One deliberation evaluation:

1. restore or initialize the native slot representation and PFC reasoning state;
2. perform one declared unit of H/L reasoning;
3. update `theta_summary` and `schema_slots`;
4. produce `q_values`;
5. compute `state_value` through STR;
6. return the stable native outputs and resumable PFC state.

Action selection occurs outside the model:

```text
q_values
    ↓
controller
    ↓
halt / continue
```

If the controller selects `continue`, the next interaction may resume only the state belonging to the same problem/deliberation lineage.

## 5. Model parameters

Model-owned parameters include:

- all HRM/PFC architectural parameters;
- Q-head architecture;
- STR architecture.

In particular, HRM-rl owns:

- model width;
- sequence capacity and input width;
- schema-slot count;
- `layers_h`;
- `cycles_h`;
- `layers_l`;
- `cycles_l`;
- RoPE parameters;
- Q-head dimensions;
- STR dimensions.

Task decoder dimensions, reward values, discount factor, rollout truncation, exploration policy, TD algorithm, loss coefficients, warm-up schedule, optimizer settings, task corpus, device, and precision are outside the model.

## 6. Observables

Stable model-native observables are:

- `theta_summary`;
- `schema_slots`;
- `q_values`;
- `state_value`.

Optional diagnostic traces may expose:

- `z_H`;
- `z_L`;
- value estimates across deliberation steps.

Sampled action, reward, termination, return, and TD target are controller/training observables rather than model observables.

## 7. Conformance

A conforming HRM-rl implementation must satisfy:

- the HRM H/L reasoning core and native slot interface are preserved;
- `q_values` contains exactly one value for `halt` and one for `continue` in canonical order;
- `q_values` has action-value semantics under the resolved deliberation-control return specification;
- `state_value` is one scalar estimate per deliberation state;
- `state_value` is produced by a separate STR critic;
- STR is non-recurrent and is not an additional H/L reasoning process;
- continuation may resume only state belonging to the same problem/deliberation lineage;
- reward, return, and TD targets are not required native forward inputs;
- action sampling/selection remains controller-owned.

## 8. Boundaries and related specifications

Bindings own:

- task-to-model slot construction;
- task-specific decoders from `theta_summary`, `schema_slots`, or other explicitly supported native representations.

The deliberation controller owns:

- policy/action selection;
- execution of `halt` and `continue`;
- interaction with the task runtime;
- preservation of resumable-state lineage.

The RL objective/training protocol owns:

- reward interpretation;
- discounting;
- TD targets;
- Q/value losses;
- warm-up;
- optimizer policy.

Experiments compose these elements with tasks, bindings, corpora, and training/evaluation protocols.

Relevant neighboring documents include:

- HRM;
- HRM-rl deliberation controller;
- RL objective specification;
- MazeHard/Routebind bindings and experiments.
