# Training Architecture

<!-- canonical_package: ehp_sn  authority: canonical  status: draft -->

> Canonical design for `ehp_sn.training` — owns **training execution policy**.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                                              |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Training-step composition; backward policy (accumulation, clipping, stepping); TBPTT boundary decisions; checkpoint emission policy; optimizer/scheduler construction; `TrainingState`             |
| **Must not own**      | Model architecture; loss mathematics; rollout execution; task semantics; metric formulas; Lightning lifecycle                                                                                      |
| **Public API**        | `LossTerm`, `TrainStepOutput`, `TrainingUnit`, `TrainingState`, `TrainingConfig`, `GradientConfig`, `OptimizerSpec`, `TrainingRuntime` (protocol, consumer-owned)                                  |
| **Allowed imports**   | `rollouts` (R: contracts, StepRecord), `objectives` (R: ObjectiveResult), `models` (R: state types and `nn.Module` protocol only), `contracts` (R), `types` (R); **P:** `data`, `tasks`, `metrics` |
| **Forbidden imports** | `lightning`, `evaluation`, `figures`, `reporting`                                                                                                                                                  |
| **Layer**             | L3 — Runtime Execution                                                                                                                                                                             |
| **Key invariant**     | Training owns when and how optimization occurs; never owns what the model computes or why a loss is scientifically valid; remains backend-independent — never imports `lightning`                  |

---

## 1. Canonical responsibility

Training owns **when and how** optimization occurs; it does not own **what** the model computes or **why** a loss is scientifically valid.

```
batch/rollout → training unit → named losses + metrics + next carry
                                    ↓
                               backward → gradient policy → optimizer update → scheduler → checkpoint/logging
```

## 2. Ownership boundaries

### Training owns

| Responsibility                    | Examples                                                            |
| --------------------------------- | ------------------------------------------------------------------- |
| Training-step composition         | `LossTerm`, `TrainStepOutput`, `TrainingUnit`                       |
| Backward execution                | Accumulation, backward call, gradient clipping, nonfinite detection |
| TBPTT boundary policy             | When autograd detachment occurs                                     |
| Checkpoint emission policy        | When and at what frequency                                          |
| Optimizer/scheduler construction  | `OptimizerSpec`, `ParameterGroupSpec`                               |
| Distributed loss normalization    | `SumOverBatch`                                                      |
| Family-specific runtime schedules | `resolve_tem_runtime`, HRM validation config                        |

### Carry/TBPTT division

| Owner      | Responsibility                                      |
| ---------- | --------------------------------------------------- |
| `training` | When a TBPTT truncation boundary occurs             |
| `rollouts` | How a generic carry tree is transformed             |
| `models`   | Model-specific boundary hooks (`finalize_memory()`) |

### Backward/optimizer division

| Operation                                         | Owner                |
| ------------------------------------------------- | -------------------- |
| Construct scalar differentiable objective         | `objectives`         |
| Decide accumulation, backward, clipping, stepping | `training`           |
| Translate into Lightning hooks                    | `lightning`          |
| Execute PyTorch autograd primitive                | Called by `training` |

### Checkpoint division

| Concern                             | Owner                |
| ----------------------------------- | -------------------- |
| Serializable model/optimizer state  | `models`, `training` |
| When to emit                        | `training`           |
| Lightning callback/file integration | `lightning`          |
| Selecting/loading for evaluation    | `evaluation`         |

### What training does NOT own

| Concern                                     | Owner                           |
| ------------------------------------------- | ------------------------------- |
| Neural network definitions                  | `models`                        |
| Environment interaction, temporal execution | `rollouts`                      |
| Task rules and targets                      | `tasks`                         |
| Loss mathematics                            | `objectives` / `loss`           |
| Metric definitions and aggregation          | `metrics`                       |
| Dataset and dataloader construction         | `data`                          |
| Logger implementations                      | `logging` / `lightning.loggers` |
| Offline evaluation recipes                  | `evaluation`                    |
| Trace schemas and capture                   | `traces`                        |
| Figures and visualizations                  | `figures`                       |
| Lightning lifecycle implementation          | `lightning`                     |
| Experiment-specific model assembly          | `experiments`                   |

### Forbidden dependencies

`models ↛ training`, `objectives ↛ training`, `rollouts ↛ training`, `tasks ↛ training`, `metrics ↛ training`, `training ↛ lightning`, `training ↛ experiments`, `training ↛ evaluation`, `training ↛ figures`, `training ↛ traces`.

`training` may import from `models` (through narrow contracts only), `objectives` (through `TrainStepOutput`), and `rollouts` (through carry types). It must never import from `lightning` — Lightning integration lives in `ehp_sn.lightning`, which imports `ehp_sn.training`, not the reverse.

---

## 3. Core contracts

### `LossTerm` and `TrainStepOutput`

`LossTerm.value` is a **local sum** over the local batch — the only supported representation for backward-participating losses. `LossTerm.normalizer` records contributing units (positive scalar). Training computes backward loss as a per-term weighted normalized sum: `sum(term.weight * term.value / term.normalizer)`.

`TrainStepOutput` carries `losses: Mapping[str, LossTerm]`, `metrics: Mapping[str, float | Tensor]`, and carry. At least one `LossTerm` must have `backward=True`.

### `TrainingUnit`

Bridges scientific computation and training infrastructure: `train_step(batch, carry, state) → TrainStepOutput`. Does **not** call `.backward()`, `optimizer.step()`, or `scheduler.step()`.

### `TrainingState`

Mutable runtime counters: `batch_step`, `optimizer_step`, `samples_seen`, `epoch`.

---

## 4. Configuration

- `TrainingConfig`: batch size, gradient accumulation steps, max epochs.
- `GradientConfig`: max norm, norm type, clip value.
- `PrecisionConfig`: amp enabled, dtype.
- `OptimizerSpec`: algorithm, parameter groups, options.
- `SchedulerSpec`: algorithm, options.

---

## 5. Package structure

```
ehp_sn/training/
├── contracts.py, state.py, config.py, carry.py
├── distributed.py, optim.py, gradients.py
├── tem.py, hrm.py  (see relocation plan)
└── units/  (VariationalReplayTrainingUnit, ACTSupervisedTrainingUnit)
```

**Relocation plan:** `tem.py`/`hrm.py` mix training-owned and non-training concerns. Split by ownership: runtime schedules stay; ~~`ValidationRuntimeConfig` → `contracts/validation.py`~~ **(done)**; `load_weights_from_checkpoint` → `models/loading.py` (not started, Q3 2026); `VALID_INIT_GROUPS` → `models/loading.py` (not started, Q3 2026).

---

## 6. Design contract

> `ehp_sn.training` owns training execution policy. It composes `TrainingUnit` implementations that bridge rollout records to objective computation, applies backward policy, and emits checkpoints.

- `training` may import `torch.nn.Module` and model state dataclasses for carry manipulation and checkpoint hydration. It must **never** import concrete architecture classes or construct model instances.
- Training must remain backend-independent — it never imports from `lightning`.
- `objectives` define _what_ is optimized; `training` defines _how_ and _when_.
