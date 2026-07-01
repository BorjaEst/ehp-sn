# Controller Architecture

<!-- canonical_package: ehp_sn  authority: canonical  status: accepted -->

> `ehp_sn.controllers` — one-step, task-agnostic control transitions over recurrent model execution.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                                                                      |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | One-step control transitions; halt/continue/action decisions; slot-lifecycle management; controller-family outputs                                                                                                         |
| **Must not own**      | Model architecture; task semantics; loss computation; rollout iteration; optimizer steps                                                                                                                                   |
| **Public API**        | `BridgeAdapter` (protocol, consumer-owned), `ControllerOutput`, `ACTController`, `DeliberationQHaltingController`, `RLController`, `ReplayTrajectoryController`, `ControllerState`, `DeliberationContext`, `ReplayContext` |
| **Allowed imports**   | `contracts` (R), `types` (R); **P:** `adapters` (`BridgeOutput` dataclass types only), `policies`, `utils`                                                                                                                 |
| **Forbidden imports** | `models` (direct), `tasks` (direct), `training`, `lightning`, `evaluation`, `objectives`                                                                                                                                   |
| **Layer**             | L2 — Computation                                                                                                                                                                                                           |
| **Key invariant**     | Controller delegates model invocation to the adapter; never calls `model(input, state)` directly                                                                                                                           |

---

## 1. Canonical invocation position

```
rollout runner → controller.step(carry, batch, context)
    → adapter(model, task_input, model_state) → model(input, model_state)
    → adapter.postprocess(output) → bridge_output
    → control decision (halt/continue/action)
→ (carry, controller_output)
```

## 2. One-transition contract

\[(C\_{n+1}, O_n) = \operatorname{step}(C_n, B_n, \Omega)\]

| Symbol     | Meaning                  | Type                                                      |
| ---------- | ------------------------ | --------------------------------------------------------- |
| \(C_n\)    | Controller carry         | Opaque `CarryT` (invariant)                               |
| \(B_n\)    | Current batch            | Per-family input type                                     |
| \(\Omega\) | Execution context        | Typed per family (`DeliberationContext`, `ReplayContext`) |
| \(O_n\)    | Controller-family output | `QHaltingInteractionRecord`, etc.                         |

Concrete controllers structurally match the `StepController` protocol defined in `rollouts/contracts.py` (consumer-owned). Controllers never define this protocol themselves; the canonical signature is:

```python
def step(self, step_input: SourceItemT, carry: CarryT, *,
         options: Mapping[str, Any] | None = None) -> tuple[ControllerOutputT, CarryT]: ...
```

`initial_state()` is a controller-internal convenience, not part of the protocol. Carry initialisation is provided by an injected `CarryInitializer` at the rollouts level.

Typed execution contexts per family:

````python
@dataclass(frozen=True)
class DeliberationContext:
    allow_halt: bool = True
    explore: bool = True
    halt_action: int | None = None
    max_halt_steps: int | None = None

@dataclass(frozen=True)
class ReplayContext:
    allow_halt: bool = True
``` |

## 3. Two time axes

| Axis | Meaning | Convention |
|------|---------|------------|
| \(t\) | Environment/physical time | One env transition per step |
| \(k\) | Internal deliberation time | Multiple internal steps per env step |

The runtime advances \(t\). A deliberation controller advances \(k\).

## 4. Controller families

| Controller | Backbone protocol | Primary axis | Key decision |
|------------|-------------------|-------------|--------------|
| `ACTController` | `ACTRolloutBackbone` | k (deliberation) | Halt/continue via Q-logit collapse |
| `DeliberationQHaltingController` | `QHaltingRolloutBackbone` | k → t at halt | Continue/halt + task runtime advance |
| `RLController` | Actor-critic backbone | t (environment) | Action selection via policy |
| `ReplayTrajectoryController` | Replay backbone | t (replay cursor) | Cursor advancement |

## 5. Model/controller composition

> The backbone computes decision variables. The controller applies decision semantics.

| Backbone computes | Controller applies |
|-------------------|-------------------|
| Halt/continue logits | Done masks via threshold + exploration |
| Policy logits | Action sampling or greedy selection |
| Value estimate | Recording into interaction record |

## 6. Package structure

````

ehp_sn/controllers/
├── contracts.py # BridgeAdapter protocol (consumer-owned), ControllerOutput, DeliberationContext, ReplayContext
├── \_base.py # BaseController (optional base class)
├── state.py # ControllerState
├── records.py # Interaction records
├── policies.py # Action-selection and halt-decision functions
├── deliberation/ (act.py, q_halting.py)
├── online/ (actor_critic.py)
└── replay/ (trajectory.py)

```

## 7. Design contract

> Controllers own one-step control transitions. They delegate model invocation to adapters through the `BridgeAdapter` protocol (consumer-owned in `controllers/contracts.py`). The `StepController` protocol is consumer-owned by rollouts (`rollouts/contracts.py`); concrete controllers structurally match it. Controllers never import model architectures, task implementations, or adapter implementations directly. The runner owns repeated invocation; the controller owns the semantics of one transition. Concrete adapter instances are injected at composition time. `initial_state()` is a controller-internal convenience, not part of the `StepController` protocol — carry initialisation belongs to the composition root or an injected `CarryInitializer`.
```
