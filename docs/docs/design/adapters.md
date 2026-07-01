# Adapter Design

<!-- canonical_package: ehp_sn  authority: canonical  status: accepted -->

> A narrow composition layer for exactly one supported task–model pairing. The sole coupling point between tasks and models.

---

## Normative summary

| Rule                  | Value                                                                                                                                                 |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Task→model input encoding; model invocation; model→task output decoding; compatibility validation; model-state lifecycle delegation                   |
| **Must not own**      | Target extraction; loss calculation; metric computation; action selection; rollout iteration; checkpoint resolution                                   |
| **Public API**        | Per-pairing `BridgeOutput` dataclasses, `build_*_bridge` builders; implements `BridgeAdapter` protocol (consumer-owned by `controllers/contracts.py`) |
| **Allowed imports**   | `models` (R), `tasks` (R: `TaskSpec`, task input/output schemas), `modules` (P), `contracts` (R), `types` (R)                                         |
| **Forbidden imports** | `training`, `lightning`, `evaluation`, `objectives`, `controllers`, `rollouts`                                                                        |
| **Layer**             | L2 — Computation                                                                                                                                      |
| **Key invariant**     | Adapter is the sole coupling point between tasks and models; controllers delegate model invocation to the adapter                                     |

---

## 1. Canonical invocation position

```
rollout runner → controller.step(carry, batch, context)
    → adapter(model, task_input, model_state)
        → model(input, model_state) → output, next_model_state
    → adapter.postprocess(output) → bridge_output
→ (carry, controller_output)
```

| Concern                                           | Owner         |
| ------------------------------------------------- | ------------- |
| Repeated temporal iteration                       | `rollouts`    |
| Control decision and one-step transition          | `controllers` |
| Task-to-model translation and physical model call | `adapters`    |
| Neural computation                                | `models`      |

### Concrete pairings (one adapter per task–model pair)

```
ArenaTaskInput × TEMV1 → ArenaTEMV1BridgeOutput
ArenaTaskInput × TEMV2 → ArenaTEMV2BridgeOutput
MazeHardTaskInput × HRMV1 → MazeHardHRMV1BridgeOutput
MazeHardTaskInput × HRMV2 → MazeHardHRMV2BridgeOutput
GoaltraceTaskInput × HRMV1 → GoaltraceHRMV1BridgeOutput
RoutebindTaskInput × HRMV1 → RoutebindHRMV1BridgeOutput
SeqMazeTaskInput × HRMV1 → SeqMazeHRMV1BridgeOutput
SeqMazeTaskInput × HRMV2 → SeqMazeHRMV2BridgeOutput
```

HRM v1 pairings carry `task` and `control` fields. HRM v2 pairings carry `task`, `policy` (Q-values), and `critic` (state-value). TEM v1/v2 pairings carry `task`, `learning` (a `TEMLearningState`), and optional `diagnostics`.

Execution boundary:

```
task-native input → prepare_inputs → model-native input → model step → model-native output → postprocess → task-facing bridge output
```

## 2. Five responsibilities

1. **Validate compatibility** — at construction time: observation vocabulary ↔ decoder output, graph nodes ↔ token capacity, input dimension ↔ model dimension, requested heads available.
2. **Encode task inputs** (`prepare_inputs`) — task-native → model-native. Produces token embeddings, spatial encodings, masks, sequence packing.
3. **Invoke the model** — `model_output, next_state = self.model(model_input, state)`.
4. **Decode model outputs** (`postprocess`) — model-native → task-facing bridge result. May combine with model-native control values.
5. **Expose stable bridge contract** — `BridgeOutput(task, control, policy?, critic?, learning?, diagnostics?)`.

## 3. Bridge output anatomy

| Field         | Meaning                        | Required by        | Optional          |
| ------------- | ------------------------------ | ------------------ | ----------------- |
| `task`        | Prediction per task contract   | Objectives, traces | Never             |
| `control`     | Action logits (ACT)            | Controllers        | Per regime        |
| `policy`      | Q-values (RL)                  | Controllers        | Per regime        |
| `critic`      | State value (RL)               | Controllers        | Per regime        |
| `learning`    | Tensors required by objectives | Objectives         | Pairing-dependent |
| `diagnostics` | Observability data             | Figures            | Always optional   |

Prefer concrete output types per pairing (`MazeHardHRMV1BridgeOutput`, `ArenaTEMBridgeOutput`), never a generic one with optional-everything.

```python
# Good — concrete, no invalid states
@dataclass(frozen=True)
class MazeHardHRMV1BridgeOutput:
    task: MazeHardTaskOutput
    control: ControlOutput

@dataclass(frozen=True)
class MazeHardHRMV2BridgeOutput:
    task: MazeHardTaskOutput
    policy: PolicyOutput
    critic: CriticOutput

@dataclass(frozen=True)
class ArenaTEMV1BridgeOutput:
    task: ArenaTaskOutput
    learning: TEMLearningState
```

```python
# Avoid — invalid states are possible
@dataclass
class GenericBridgeOutput:
    task: TaskOutput | None = None
    control: ControlOutput | None = None
    policy: PolicyOutput | None = None
    critic: CriticOutput | None = None
```

## 4. State ownership

Model defines state type/semantics. Adapter delegates lifecycle: `init_state(batch_size, device, dtype)`, `reset_state(state, reset_mask)`. Adapter-owned recurrent state must be explicit (`AdapterState(model, decoder)`).

## 5. Encoders and decoders

**Encoders** own: embeddings, input projections, role/positional encoding, model-required masks. Must not own: target extraction, loss masks for objectives.

**Decoders** own: task-specific heads, slot selection, reshaping, bounded transforms, task-output construction. Must not own: loss functions, target comparison, metrics, controller decisions.

## 6. Pairing modules (composition roots)

Each pairing module (`goaltrace.py`, `mazehard.py`) is a composition root containing the concrete adapter, local compatibility validation, and a builder function. No generic orchestration superclass.

## 7. Builder functions

One builder per pairing: `build_{task}_{family}_{version}_bridge(*, model, task_spec, config) → BridgeAdapter`. Centralizes dimension derivation, encoder/decoder selection, compatibility checks, stable defaults.

## 8. Package structure

```
ehp_sn/adapters/
├── contracts.py          # BridgeOutput dataclass definitions (producer-owned). Also: ControlOutput, PolicyOutput, CriticOutput, TEMLearningState. BridgeAdapter protocol is consumer-owned by controllers (controllers/contracts.py)
├── tem/  (config.py, contracts.py, encoders.py, decoders.py, arena.py, traces.py)
└── hrm/  (config.py, contracts.py, encoders.py, decoders.py, goaltrace.py, mazehard.py, routebind.py, seqmaze.py)
```

## 9. Design contract

> The adapter is the sole execution-time coupling point between tasks and models. Controllers delegate model invocation to it through the `BridgeAdapter` protocol (defined by controllers). Objectives consume its `BridgeOutput` (producer-owned by adapters). No other package may couple tasks to models directly at execution time.
