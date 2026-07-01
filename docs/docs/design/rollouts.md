# Rollout Architecture

<!-- canonical_package: ehp_sn  authority: canonical  status: accepted -->

> Canonical design for `ehp_sn.rollouts` — the repository's **temporal execution kernel**.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                                                             |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Temporal iteration; carry mechanism (init, propagation, reset, freeze, detach); `StepBoundary` aggregation; `StopReason`; `StepRecord`                                                                            |
| **Must not own**      | Model architecture; control policies; loss construction; task semantics; backward calls; optimizer steps                                                                                                          |
| **Public API**        | `RecurrentRunner`, `SingleStepRunner`, `StepController` (protocol, consumer-owned), `StepRecord`, `StepBoundary`, `RolloutResult`, `StopReason`, `Source` (protocol), `StepSink`                                  |
| **Allowed imports**   | `contracts` (R), `types` (R); **P:** `utils`                                                                                                                                                                      |
| **Forbidden imports** | `lightning`, `training`, `evaluation`, `models`, `objectives`, `traces`, `diagnostics`, `adapters`, `data`, `tasks`                                                                                               |
| **Layer**             | L3 — Runtime Execution                                                                                                                                                                                            |
| **Key invariant**     | Rollouts owns temporal execution of controllers against step sources; invokes controllers through the consumer-owned `StepController` protocol without importing controller, data, task, or model implementations |

---

## 1. Canonical responsibility

Rollouts owns the transformation:

```
source state → step input → controller.step(input, carry) → output + next carry
                                                                    ↓
                                              boundary handling / collection / stop decision
```

The module invokes a controller through the `StepController` protocol. It does not implement controller algorithms, define task semantics, own gradient context, or call the adapter directly. The canonical execution chain is `rollout runner → controller.step() → adapter(model, task_input, model_state)`.

### Per-step flow

```
runner
  ├─ controller.step(carry, batch, context)
  │    ├─ adapter.prepare_inputs(task_input)
  │    ├─ adapter.forward(model, model_input, model_state)
  │    │    └─ model(input, model_state) → output, next_model_state
  │    ├─ adapter.postprocess(output)
  │    └─ returns next_carry + controller_output
  │
  ├─ task_runtime.step(action)
  │    └─ mutates opaque environment state
  │
  ├─ receives StepFeedback
  │
  └─ on terminated/truncated slots:
       ├─ task_runtime.reset(mask)
       └─ carry updater: freeze / reset masked slots
```

The same episode-boundary mask coordinates both operations, but each subsystem performs its own reset according to its own state semantics:

| Subsystem        | Reset action                            | Data touched                            |
| ---------------- | --------------------------------------- | --------------------------------------- |
| `TaskRuntime`    | `reset(reset: RuntimeReset)`            | Internal environment state per slot     |
| Controller carry | `CarryUpdater.reset_where(carry, mask)` | Model state + controller state per slot |

The reset mask does not transfer ownership of environment state to `rollouts`. It only tells each owner which vectorized slots must discard and recreate their internal state.

For EHP, a rollout represents one of: supervised step, fixed recurrent sequence, Arena trajectory, TEM replay episode, HRM ACT deliberation, TBPTT chunk, or (future) online environment interaction.

### Carry / TBPTT division of ownership

| Owner      | Responsibility                                           |
| ---------- | -------------------------------------------------------- |
| `training` | When a TBPTT truncation boundary occurs                  |
| `rollouts` | How a generic carry tree is transformed at that boundary |
| `models`   | Model-specific boundary hooks (e.g. `finalize_memory()`) |

### What rollouts does NOT own

| Concern                                   | Owner                                                     |
| ----------------------------------------- | --------------------------------------------------------- |
| Model architecture                        | `models`                                                  |
| Control policies and deliberation         | `controllers`                                             |
| Task observations, rewards, transitions   | `contracts.task_runtime`, task packages                   |
| Loss construction                         | `objectives`                                              |
| Scientific metrics                        | `metrics`                                                 |
| Training loops, `.backward()`, optimizers | `lightning`, `training`                                   |
| MLflow, Zarr, filesystem paths            | `evaluation`, `traces`                                    |
| Trace registries, figure creation         | `traces`, `figures`                                       |
| Gradient mode                             | Caller (`torch.inference_mode()` / `torch.enable_grad()`) |

---

## 2. Package structure

```
ehp_sn/rollouts/
├── contracts.py       # Protocols: Source, StepController, StepSink, Runner
├── configuration.py   # RolloutConfig, CollectionConfig, TBPTTConfig
├── records.py         # StepBoundary, StepRecord, RolloutResult, SourceContext
├── runtime.py         # SingleStepRunner, RecurrentRunner
├── sources.py         # RepeatSource, DemandDrivenReplaySource
├── collection.py      # NullSink, RecordSink, CompositeSink
├── masking.py         # Batch-slot mask operations
└── errors.py          # Typed exception hierarchy
```

---

## 3. Core contracts

### 3.1 `StepController` — one logical control transition

```python
class StepController(Protocol[SourceItemT, CarryT, ControllerOutputT]):
    def step(self, step_input: SourceItemT, carry: CarryT, *,
             options: Mapping[str, Any] | None = None) -> tuple[ControllerOutputT, CarryT]: ...
```

This protocol is defined locally in `rollouts/contracts.py` (consumer-owned). The controller delegates model invocation to an adapter and owns the control decision. Rollouts never imports `controllers` — concrete `StepController` instances are injected by composition roots (`experiments/`, builders).

### 3.2 `Source` — temporal input producer

Sources receive a `SourceContext` projection — not the full controller carry:

| Field        | Type        | Meaning                        |
| ------------ | ----------- | ------------------------------ |
| `step_index` | `int`       | Current step                   |
| `active`     | `(B,) bool` | Slots eligible to execute      |
| `halted`     | `(B,) bool` | Controller-deliberation halt   |
| `terminated` | `(B,) bool` | Task-level natural episode end |
| `truncated`  | `(B,) bool` | Task-level truncation          |

```python
class Source(Protocol[SourceItemT]):
    def next(self, context: SourceContext) -> SourceStep[SourceItemT] | None: ...
```

`CarryAwareSource` exists for the minority (e.g. `DemandDrivenReplaySource`) that need read-only carry access. Prefer plain `Source`. Implementations of `Source` (in `data/`, evaluation, etc.) structurally match this protocol. Neither rollouts nor the implementation package needs to import the other.

### 3.3 `StepSink` — observer of rollout execution

Lifecycle: `on_start` → `on_step` (per step) → `on_complete(result)` on normal termination, `on_error(error)` on failure. Sinks must not alter execution semantics.

### 3.4 `Runner` and carry operations

```python
class Runner(Protocol[CarryT, ControllerOutputT]):
    def run(self, *, source, controller, initial_carry, carry_updater,
            sink=None, collection=None, options=None) -> RolloutResult[CarryT]: ...
```

- `SingleStepRunner`: exactly one step. `RecurrentRunner`: 0..N steps with halt/termination/truncation/limit support.
- `CarryUpdater` (in `contracts/carry.py`): `reset_where(carry, mask)`, `freeze_where(previous, updated, mask)`.
- `CarryDetacher`: `detach(carry)`.
- `HaltedCarry`: exposes `halted: Tensor` property.
- `RunnerState[CarryT]` (in `rollouts/contracts.py`): opaque wrapper around the controller carry. The runner only accesses runner-owned bookkeeping; the controller carry is opaque. Concrete `ControllerState` types are embedded by controllers, not exposed through the protocol.

---

## 4. Configuration

### `RolloutConfig`

| Field                            | Purpose          | Exceeded behaviour           |
| -------------------------------- | ---------------- | ---------------------------- |
| `max_steps: int \| None`         | Expected horizon | Returns `STEP_LIMIT_REACHED` |
| `hard_max_steps: int \| None`    | Safety guard     | Raises `ExecutionLimitError` |
| `stop_when_all_halted: bool`     | —                | —                            |
| `stop_when_all_terminated: bool` | —                | —                            |

Both budgets inclusive: `max_steps=N` permits steps 0..N-1.

### `CollectionConfig` (invocation-level)

`snapshot_carry: bool = False`, `output_selector: Callable | None = None`.

### `TBPTTConfig`

`chunk_length: int`, `detach_between_chunks: bool = True`.

---

## 5. Records

### `StepBoundary` — aggregated boundary signals

Five `(B,) bool` tensors with defined temporal ordering:

```
pre-step source facts:  valid, episode_start
         ↓
controller transition
         ↓
post-step facts:        halted, terminated, truncated
         ↓
next-step eligibility
```

Derived masks (properties): `task_done`, `controller_done`, `requires_reset`, `eligible_for_replacement`. No conflated `finished`.

### `StepRecord` and `RolloutResult`

`StepRecord(step_index, sampled_input, executed_input, output, boundary, carry_snapshot?)` — one executed step.

`RolloutResult(final_carry, stop_reason, stats)` — does **not** contain step records (sink-owned).

### `StopReason`

`SINGLE_STEP_COMPLETED | ALL_HALTED | ALL_TERMINATED | ALL_TRUNCATED | SOURCE_EXHAUSTED | STEP_LIMIT_REACHED`

---

## 6. Critical execution invariants

### Freeze ordering

> Freeze slots that were inactive **before** execution, not slots that became inactive **because of** this execution.

A slot active at step _t_ that halts during step _t_ produced a valid carry update. Single post-step `freeze_where(previous, proposed, mask=~active_before)`. No pre-step freeze.

### Stop quantification

Stop conditions apply to a configurable stop population, not all batch slots. Padded/irrelevant slots excluded.

### Memory safety

1. Full carry sequence never retained by default.
2. Snapshots detached, immutable, diagnostic-only.
3. Runner never accumulates records internally.
4. Output selector runs before sink delivery.
5. `snapshot_carry` defaults to `False`.
6. Gradient mode is caller-owned (`torch.inference_mode()` / `torch.enable_grad()`).

---

## 7. Masking vocabulary

Distinct masks, distinct purposes:

| Function                     | Returns                              | Semantics                               |
| ---------------------------- | ------------------------------------ | --------------------------------------- |
| `execution_mask(boundary)`   | `~halted & ~terminated & ~truncated` | Slots eligible for next step            |
| `loss_mask(boundary)`        | `valid`                              | Slots contributing to current-step loss |
| `replacement_mask(boundary)` | `halted \| terminated \| truncated`  | Slots eligible for episode replacement  |

`valid` is per-timestep (in `loss_mask` but NOT in `execution_mask`).

---

## 8. Sources and collection

| Source                     | Protocol           | Use                            |
| -------------------------- | ------------------ | ------------------------------ |
| `RepeatSource`             | `Source`           | Evaluation — yields same batch |
| `DemandDrivenReplaySource` | `CarryAwareSource` | Partial-reset training         |

Sinks: `NullSink` (no-op), `RecordSink` (materialize), `CompositeSink` (tuple of sinks). `TrainingLossSink` is training-owned, not in rollouts.

---

## 9. Error handling

| Exception              | Condition                                                            |
| ---------------------- | -------------------------------------------------------------------- |
| `ExecutionLimitError`  | `hard_max_steps` exceeded (safety violation, NOT normal termination) |
| `InvalidBoundaryError` | Boundary mask invariants violated                                    |
| `CarryShapeError`      | Carry batch dimensions incompatible                                  |
| `StepExecutionError`   | `controller.step()` raised (preserves original as `__cause__`)       |

---

## 10. Design contract

> `ehp_sn.rollouts` owns temporal execution of controllers against step sources. Rollouts is invoked _by_ training and evaluation; it never imports them. Runners coordinate source consumption, controller invocation (via the locally-defined `StepController` protocol), carry propagation, boundary aggregation, stopping, and sink-driven record emission.

- Controllers, objectives, metrics, tracing, storage, and training orchestration remain external.
- `StepController` protocol is defined locally in `rollouts/contracts.py` (consumer-owned). The runner accepts any structurally-matching object without importing controller implementations.
- Carry opaque except through `CarryUpdater` and `HaltedCarry.halted`.
- `valid`, `halted`, `terminated`, `truncated` are distinct with defined temporal ordering.
- `max_steps` → `STEP_LIMIT_REACHED`; `hard_max_steps` → `ExecutionLimitError`.
- Rollout-to-score adaptation lives in `training/rollout_scoring.py`, not in rollouts.
