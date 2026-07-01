# Model Design

<!-- canonical_package: ehp_sn  authority: canonical  status: accepted -->

> Complete parameterized architectures and their model-local contracts.

---

## Normative summary

| Rule                  | Value                                                                                                                                                       |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Neural architectures (`TEMModelV1`, `HRMModelV1`, …); model state (`init_state`, `reset_state`); typed inputs/outputs; architecture config; `trace_views()` |
| **Must not own**      | Task adaptation; loss computation; training loops; rollout execution; metric accumulation; checkpoint selection                                             |
| **Public API**        | `TEMModelV1`, `TEMModelV2`, `HRMModelV1`, `HRMModelV2`, `EHPModelV1`, `build_model`                                                                         |
| **Allowed imports**   | `modules`, `contracts`                                                                                                                                      |
| **Forbidden imports** | `controllers`, `objectives`, `training`, `lightning`, `rollouts`, `evaluation`                                                                              |
| **Layer**             | L2 — Computation                                                                                                                                            |
| **Key invariant**     | Models own architectures, state, and typed I/O contracts; invoked exclusively by adapters, never directly by controllers or rollouts                        |

---

## 1. Canonical contract

Every recurrent model supports seven operations:

1. **Construction**: `model = TEMModelV1(settings)` — creates parameters/buffers, no I/O.
2. **State init**: `state = model.init_state(batch_size, device, dtype)` — no DataModule dependency.
3. **Forward**: `output, next_state = model(inputs, state)` — explicit functional recurrence.
4. **State reset**: `state = model.reset_state(state, reset_mask)` — selective row reset.
5. **Finalisation** (TEM only): `model.finalize_memory(state)` — clamp Hebbian weights at TBPTT boundaries. Optional capability protocol `MemoryFinalizer`.
6. **Dynamics**: `model.set_dynamics(config)` — update runtime neural parameters. Parameter set is family-specific (`TEMDynamics`, `HRMDynamics`, `EHPDynamics`).
7. **Trace views**: `model.trace_views() → object` — expose trace-field specifications for observability. The returned object is a `TraceViewMapping` conceptually owned by `traces`; models return a protocol-compatible object without importing `traces`.

## 2. Distinguish models from modules

| Package   | Role                     | Examples                                             |
| --------- | ------------------------ | ---------------------------------------------------- |
| `modules` | Reusable building blocks | `Attention`, `MLP`, `PathIntegrator`, `HebbianWrite` |
| `models`  | Complete architectures   | `TEMModelV1`, `HRMModelV2`, `EHPModelV1`             |

A module executes one bounded transformation with no family knowledge. A model coordinates multiple transformations with lifecycle and phase semantics.

### Professional foundation

Every concrete model inherits directly from `nn.Module`. There is **no shared `BaseModel`** base class. Project-specific interoperability is expressed through typed input/output objects, configuration dataclasses, and narrow protocols — not inheritance.

### Does not own

| Never in `models`                     | Belongs in             |
| ------------------------------------- | ---------------------- |
| Datasets, batching, data loading      | `data`                 |
| Task-specific input adaptation        | `adapters`             |
| Losses, objectives, training criteria | `objectives`, `loss`   |
| Optimizer or scheduler creation       | `training`             |
| Lightning modules                     | `lightning`            |
| Rollout execution                     | `rollouts`             |
| ACT deliberation loop                 | `controllers`          |
| Environment interaction               | `tasks`                |
| Metric accumulation                   | `metrics`              |
| Checkpoint selection, MLflow lookup   | `evaluation`           |
| Experiment configuration              | `config`, experiments  |
| Reporting or plotting                 | `reporting`, `figures` |

## 3. Inputs, outputs, state — family-specific, not universal

Each family has concrete types (`TEMInputV1`, `TEMOutputV1`, `TEMStateV1`). No universal output with optional fields. Separate model state from controller state and runtime carry:

| Category         | Owner         | Contents                                            |
| ---------------- | ------------- | --------------------------------------------------- |
| Model state      | `models`      | LEC/MEC/HPC/PFC latent state, differentiable memory |
| Controller state | `controllers` | Halted mask, deliberation step count                |
| Runtime carry    | `rollouts`    | Composition of model_state + controller_state       |

## 4. Configuration

Model settings are **per-family frozen dataclasses** (`TEMSettings`, `HRMSettings`, `EHPSettings`), each aligned to the corresponding `config/models/{family}-{version}-base.toml` schema. The union type `ModelSettings = TEMSettings | HRMSettings | EHPSettings` serves as the discriminator for `build_model` dispatch.

Settings contain architecture parameters only. Never: learning rate, optimizer, batch size, checkpoint path, MLflow run ID.

Runtime neural parameters (`eta`, `hebbian_decay`): model owns current values via `set_dynamics(config: FamilyDynamics)`; training owns the schedule.

Three independent version axes: architecture version, checkpoint schema version, configuration schema version.

TODO(spec): typed fields for each per-family settings dataclass are not yet finalised. The TOML configs in `config/models/` are the current authoritative schema.

## 5. Factory

`build_model(settings: ModelSettings) → nn.Module` — explicit `match`-based dispatch over the `ModelSettings` union (`TEMSettings | HRMSettings | EHPSettings`), not a mutable global registry.

## 6. Package structure

```
ehp_sn/models/
├── factory.py, protocols.py
├── tem/ (tem_v1.py, tem_v2.py, _shared.py)
├── hrm/ (hrm_v1.py, hrm_v2.py, _shared.py)
└── ehp/ (ehp_v1.py, _shared.py)
```

## 7. Design contract

> Models own architectures, state, and typed I/O contracts. They are invoked exclusively by adapters (`adapters/`), never directly by controllers or rollouts. They never import from training, evaluation, controllers, or objectives.
