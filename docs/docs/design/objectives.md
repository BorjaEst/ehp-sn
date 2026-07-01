# Objectives Design

<!-- canonical_package: ehp_sn  authority: canonical  status: draft -->

> `ehp_sn.objectives` owns the **differentiable scoring layer** between model/runtime outputs and optimization.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                                                                                                                                                                           |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Task scoring (token CE, field MSE); scoring of adapter-bridged controller values (halt BCE on `BridgeOutput.control`, Q-value MSE on `BridgeOutput.policy`, value MSE on `BridgeOutput.critic`); coefficient application; mask-aware reduction; `ObjectiveResult`, `TaskStepEvaluation` (consumes `RatioStat` from `contracts`) |
| **Must not own**      | Model execution; rollout traversal; optimizer steps; `.backward()` calls; metric accumulation; checkpointing                                                                                                                                                                                                                    |
| **Public API**        | `ObjectiveResult`, `ObjectiveContext`, `ACTSupervisedScorer`, `TEMObjective`, `HybridRLObjective`, `TaskStepEvaluation`                                                                                                                                                                                                         |
| **Allowed imports**   | `loss` (R), `adapters` (R: `BridgeOutput` types only), `contracts` (R), `types` (R)                                                                                                                                                                                                                                             |
| **Forbidden imports** | `metrics`, `models`, `controllers`, `rollouts`, `tasks`, `training`, `lightning`, `evaluation`, `figures`                                                                                                                                                                                                                       |
| **Layer**             | L2 — Computation                                                                                                                                                                                                                                                                                                                |
| **Key invariant**     | Objectives consume `BridgeOutput` from adapters; they never import controller or task implementations directly; they never call `.backward()`, step optimizers, or accumulate metrics                                                                                                                                           |

---

## 1. Ownership boundaries

| Owns                                                                                                                                              | Does not own                        | Owner               |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------- |
| Task scoring (token CE, field MSE)                                                                                                                | Model forward execution             | `models`            |
| Adapter-bridged controller scoring (halt BCE on `BridgeOutput.control`, Q-value MSE on `BridgeOutput.policy`, value MSE on `BridgeOutput.critic`) | Recurrent state evolution           | `controllers`       |
| Coefficient application                                                                                                                           | Rollout traversal                   | `rollouts`          |
| Mask-aware reductions                                                                                                                             | Optimizer construction/stepping     | `training`          |
| Objective-specific validation                                                                                                                     | `.backward()` calls                 | `training` (policy) |
| `ObjectiveResult` contracts                                                                                                                       | Logging backends                    | `logging`           |
| Task-to-objective adaptation                                                                                                                      | Evaluation metric accumulation      | `metrics`           |
| —                                                                                                                                                 | Target generation from raw datasets | `data`              |
| —                                                                                                                                                 | Experiment selection                | `experiments`       |
| —                                                                                                                                                 | Checkpointing                       | `training` (policy) |

Forbidden dependencies: `objectives ↛ controllers`, `objectives ↛ tasks`, `objectives ↛ lightning`, `objectives ↛ metrics`, `objectives ↛ models`. Dependency direction is strictly `loss ← objectives ← training/lightning`.

**Controller scoring resolution:** Objectives scores adapter-bridged controller values (halt BCE on `BridgeOutput.control`, Q-value MSE on `BridgeOutput.policy`, value MSE on `BridgeOutput.critic`) but forbids importing `controllers`. This is consistent: controller output values reach objectives through `BridgeOutput` fields (owned by adapters), not through direct controller imports.

## 2. Four-level architecture

````
Level 1: loss primitives (ehp_sn.loss) — pure tensor→tensor functions
Level 2: atomic objectives — wrap one primitive with masking/reduction (e.g. TokenPredictionObjective, HaltClassificationObjective)
Level 3: task adaptation — TaskStepEvaluator decouples composites from task modality. This is the central architectural innovation: task evaluators adapt heterogeneous task outputs into a common TaskStepEvaluation, so composite objectives operate on a uniform interface regardless of task family.
Level 4: composite objectives — combine terms into training criterion

## 3. Core contracts

### `ObjectiveResult`

```python
@dataclass(frozen=True)
class ObjectiveResult:
    loss: Tensor          # scalar, differentiable
    contributions: dict[str, Tensor]  # signed, weighted — must sum to loss
    terms: dict[str, Tensor]         # (B,) or (B,S) unreduced — ephemeral
    diagnostics: dict[str, Tensor]   # detached observability only
````

**Invariants:** `loss == sum(contributions.values())`. Terms are ephemeral — discard after reduction. Diagnostics are detached.

### `ObjectiveContext`

```python
@dataclass(frozen=True)
class ObjectiveContext:
    global_step: int
    stage: Stage  # TRAIN | VALIDATE | TEST | PREDICT
```

Algorithmic conditions (warmup, coefficient annealing) are communicated via **resolved scalar fields** in regime-specific context, not inferred from stage.

### `TaskStepEvaluation`

Bridge between task-specific evaluators and task-agnostic ACT scorer:

```python
@dataclass(frozen=True)
class TaskStepEvaluation:
    task_loss_per_sample: Tensor     # (B,) — per-sample, internally normalized
    task_loss_count: Tensor          # (B,) — contributing elements per sample
    completion_target: Tensor        # (B,) — float [0,1], readiness to halt
    metrics: dict[str, RatioStat]    # sufficient statistics
```

`continuation_target` is derived (`1 - completion_target`), not stored independently.

## 4. Composite objectives

| Composite             | Regime             | Composition                                               | Entry Point                                 |
| --------------------- | ------------------ | --------------------------------------------------------- | ------------------------------------------- |
| `ACTSupervisedScorer` | ACT (HRM v1)       | `c_task·task_sum + c_halt·halt_BCE + c_continue·cont_BCE` | `evaluate_step(record, *, inputs, context)` |
| `TEMObjective`        | TEM (v1, v2)       | `obs_nll + latent_consistency + reg`                      | `evaluate_step(record, *, inputs, context)` |
| `HybridRLObjective`   | Hybrid RL (HRM v2) | `token_CE + c_v·V_MSE + c_q·Q_MSE`                        | `compute_step(batch, *, context)`           |

## 5. Masking and normalization policies

| Objective             | Mask source                           | Normalization                                  | Gradient-scale contract                      |
| --------------------- | ------------------------------------- | ---------------------------------------------- | -------------------------------------------- |
| TEM                   | `protocol_mask` (revisit eligibility) | Masked mean over eligible                      | ~constant per eligible sample                |
| ACT                   | `TaskStepEvaluation.task_loss_count`  | `sum / count` (task); `sum(masked_BCE)` (halt) | Scales with active count                     |
| Hybrid RL/Token       | `ignore_index=-100`                   | Per-sequence mean, batch sum                   | Independent of tokens; grows with batch      |
| Field                 | `mask (B,N)`                          | Per-sample mean, batch sum                     | Independent of valid nodes; grows with batch |
| Q-Value / State-Value | None                                  | Raw MSE sum                                    | Grows linearly with batch                    |

## 6. Package structure

```
ehp_sn/objectives/
├── contracts.py        # ObjectiveResult, ObjectiveContext, TaskStepEvaluation
├── atomic.py           # TokenPredictionObjective, HaltClassificationObjective, FieldMSEObjective
├── composites.py       # ACTSupervisedScorer, TEMObjective, HybridRLObjective
├── task_evaluators/    # Per-family TaskStepEvaluator implementations
│   ├── arena.py, mazehard.py, goaltrace.py, routebind.py, seqmaze.py
├── reduction.py        # Masked reductions, gradient normalization
└── validation.py       # Objective-specific input validation
```

## 7. Design contract

> `ehp_sn.objectives` owns the differentiable scoring layer. Atomic objectives wrap loss primitives with typed validation, masking, and reduction. Task evaluators adapt heterogeneous outputs into `TaskStepEvaluation`. Composite objectives combine terms into the final training criterion. Objectives consume `BridgeOutput` from adapters; they never import controller or task implementations directly. Objectives never call `.backward()`, step optimizers, or accumulate metrics.
