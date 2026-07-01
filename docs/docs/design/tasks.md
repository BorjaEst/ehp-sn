# Tasks Design

<!-- canonical_package: ehp_sn  authority: canonical  status: accepted -->

> `ehp_sn.tasks` — the task-domain layer: what problem is being solved, what constitutes a valid instance, what information is exposed, how success is interpreted.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Task identity, semantic contracts, target derivation, runtime transitions, scoring declarations                                                                                                         |
| **Must not own**      | Model architecture; controller implementation; training loops; metric formulas; rollout scheduling                                                                                                      |
| **Public API**        | `TaskKey`, `TaskSpec`, `TaskRuntime`, `TaskScoringSpec`, `TaskStepEvaluator` (legacy)                                                                                                                   |
| **Allowed imports**   | `contracts`, `types`, `numpy`, `torch`                                                                                                                                                                  |
| **Forbidden imports** | `models`, `controllers`, `objectives`, `metrics`, `rollouts`, `training`, `lightning`, `reporting`, `figures`                                                                                           |
| **Layer**             | L1 — Domain Primitives                                                                                                                                                                                  |
| **Key invariant**     | Tasks define what the problem is; they never know how a model solves it                                                                                                                                 |
| **Transitional**      | T$1: Per-family integration modules (`builder.py`) may import `data` for corpus construction. Target: these modules move to `ehp_sn/build/` by Q4 2026. Pure `tasks/` modules have zero `data` imports. |

### Dependency rules

**Allowed:**
| Dependency | Rationale |
|-----------|-----------|
| stdlib | — |
| `numpy` | Corpus builder and oracle math |
| `torch` | Tensor-valued contracts |
| `ehp_sn.types` | Shared type aliases |
| `ehp_sn.contracts` | Cross-package protocols |

**Forbidden:**
| Dependency | Rationale |
|-----------|-----------|
| `ehp_sn.models` | Tasks must be model-agnostic |
| `ehp_sn.controllers` | Controllers consume tasks, not vice versa |
| `ehp_sn.objectives` | Objectives consume task targets |
| `ehp_sn.metrics` | Metrics measure results |
| `ehp_sn.rollouts` | Rollouts consume task runtimes |
| `ehp_sn.training` | Training imports targets, not identity |
| `ehp_sn.reporting` | Reporting consumes evaluated results |
| `ehp_sn.figures` | Figures consume evaluated results |
| `lightning` | Training-layer concern |
| `mlflow` | Infrastructure |

Per-family integration modules may depend outward in controlled ways: `builder.py` → `ehp_sn.data`, `providers.py` → `ehp_sn.evaluation.contracts`, `traces.py` → `ehp_sn.traces` contracts, `runtime.py` → `ehp_sn.contracts`.

### Current state assessment

**What exists and is correct:** Per-family vertical modules ✅, `contracts.py` typed dataclasses ✅, `runtime.py` batch keys ✅, `evaluation.py` MetricSpec ✅, `supervision.py` learning structs ✅, `providers.py` EvaluationSourceProvider ✅, `reward.py` stateless projectors ✅, `capabilities/replay.py` ✅, `scoring.py` central aggregation ✅, channel group constants ✅, structured task identity (`TaskKey`) ✅, `TaskDefinition` protocol ✅, `StaticTaskRuntime` protocol ✅.

**Resolved:** `ValidationRuntimeConfig` relocated from `training/` to `contracts/validation.py`.

---

## 1. Task identity

```python
TaskKey(namespace="ehp", family="arena", variant="structural")
TaskMode: STATIC | SEQUENTIAL | INTERACTIVE
TaskTrait: VARIABLE_LENGTH | DELIBERATIVE | REPLAYABLE | STRUCTURED_OUTPUT | MEMORY_CONDITIONED
```

`TaskMode` is mutually exclusive. `TaskTrait` values are orthogonal.

## 2. Task families

| Family      | Mode       | Traits                        |
| ----------- | ---------- | ----------------------------- |
| `arena`     | SEQUENTIAL | VARIABLE_LENGTH, REPLAYABLE   |
| `mazehard`  | SEQUENTIAL | VARIABLE_LENGTH, DELIBERATIVE |
| `goaltrace` | STATIC     | STRUCTURED_OUTPUT             |
| `routebind` | STATIC     | STRUCTURED_OUTPUT             |
| `seqmaze`   | SEQUENTIAL | VARIABLE_LENGTH, DELIBERATIVE |

## 3. Semantic protocols (segregated)

- `TaskDefinition`: immutable metadata (`TaskSpec`).
- `InstanceValidator`: validate an instance.
- `InputProjector[InstanceT, InputT]`: derive model-facing inputs.
- `TargetProjector[InstanceT, TargetT]`: derive reference targets.
- `OutputDecoder[OutputT, DecodedT]`: interpret raw model outputs.
- `ActionConstrainedTask[InstanceT]`: legal-action masks as boolean tensors.

Consumers request only the protocols they need. Families implement what applies.

## 4. Task runtime protocols

- `TaskRuntime` (in `contracts/`, semantically task-owned): step-based environment boundary for SEQUENTIAL and INTERACTIVE tasks. Mutable environment state is internal; callers advance via `step(action) -> StepFeedback` and signal resets via `reset(RuntimeReset)`.
- `StaticTaskRuntime` (in `contracts/`, semantically task-owned): single-shot evaluation boundary for STATIC tasks. Provides `evaluate(instance, prediction) -> dict[str, Any]`.

## 4. Per-family structure

```
tasks/<family>/
├── contracts.py (domain DTOs), spec.py (FAMILY_KEY, FAMILY_SPEC)
├── targets.py, runtime.py, supervision.py, evaluation.py
├── reward.py, validation.py, decoding.py
├── builder.py (corpus I/O), providers.py (evaluation cases)
└── capabilities/ (replay, ...)
```

Integration modules (`builder.py`, `providers.py`, `traces.py`, `runtime.py`) may depend outward in controlled ways — each outward dependency must be justified in the module docstring, listed in the family's `__init__.py`, and tracked as a transitional exception (T$1 for `data` imports in builders). Target: pure `tasks/` modules have zero outward domain imports beyond `contracts` and `types`.

## 5. Scoring metadata

`MetricSpec` and `TaskScoringSpec` are declarative DTOs. Recommended home: `contracts/scoring.py` (neutral — tasks and metrics both import from contracts). Canonical aggregation in `scoring.py` as a migration bridge.

## 6. Design contract

> Tasks own the semantic definition of every problem. They remain independent of model architecture, controller implementation, and training loops. `TaskRuntime` (in `contracts/`, semantically task-owned) is the execution-time boundary for value-control controllers.

## 7. TaskRuntime encapsulation

`TaskRuntime` SHALL encapsulate mutable environment state. Callers SHALL advance the runtime through `step(action)` and reset selected runtime slots through `reset(reset)`. Environment state SHALL NOT be passed through controller carry or exposed as a task-specific argument to controller interfaces.

### State ownership domains

```
Controller carry
    = model state (models)
    + controller state (controllers)

TaskRuntime internal state
    = environment transition state (tasks)
```

These may advance in the same rollout iteration, but they are not the same state channel.

### Design invariants

1. **Controllers remain task-agnostic.** They consume normalized adapter outputs and produce actions or decisions. They do not manipulate Arena positions, graph cursors, episode simulators, or task-specific transition objects.

2. **Carry remains a decision-system abstraction.** It contains data required to continue model computation and controller deliberation. Environment mechanics belong to the runtime, even when `rollouts` coordinates resets for both.

3. **Reset masks coordinate without merging.** A reset mask does not transfer ownership of environment state to `rollouts`. It only tells the runtime which vectorized slots must discard and recreate their internal state. In parallel, `rollouts` applies the same episode-boundary mask to the controller carry. Each subsystem performs its own reset according to its own semantics.

### Rejected alternative

A functional `next_env_state, feedback = step(env_state, action)` would require environment state to become an explicit rollout-owned value, broadening public contracts substantially. That is useful for pure functional simulation or JAX-style transformations, but inconsistent with the current object-oriented `TaskRuntime` contract.

### Decision record

| Decision                                       | Resolution                                                      |
| ---------------------------------------------- | --------------------------------------------------------------- |
| `TaskRuntime.step` state parameter             | Rejected                                                        |
| Environment-state ownership                    | Internal to `TaskRuntime`                                       |
| Controller carry contents                      | Model state plus controller state only                          |
| Episode-boundary coordination                  | `rollouts` propagates reset masks to both owners                |
| Task-specific environment types in controllers | Forbidden                                                       |
| Adapter access to environment state            | Forbidden unless represented as ordinary task observation/input |
