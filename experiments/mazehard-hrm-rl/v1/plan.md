---
title: MazeHard-HRM-rl v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

## Normative summary

`experiment:mazehard-hrm-rl/v1` is the resolved scientific composition of the `task:mazehard/v1`
task and the `model:hrm-rl/v1` model: a global-route-reasoning experiment in which HRM-rl solves a
fully observed MazeHard problem, deciding its own deliberation length through reinforcement-learned
`halt`/`continue` control, and predicts the reference route.

It declares the compatibility support level, the configured `InputAdapter`/`OutputAdapter` pair,
the deliberation controller and RL objective composition, the task-corpus requirement, the hybrid
training objective, and the evaluation regime. It does not redefine task, model, adapter,
controller, or objective semantics; where this document states a value already owned elsewhere,
that value is repeated for composition clarity, not re-authored.

This document is `draft`. It is a **design exemplar's scientific companion plan**: it references
two reusable building blocks — the HRM-rl deliberation controller and the RL objective
specification — whose specifications do not yet exist (`hrm-rl.md` § 8 lists both as neighboring
documents). This plan records that they are expected to exist as reusable research components, per
`ARCH-016` exemplar-driven discovery, rather than inventing their contracts here.

## 1. Purpose

`mazehard-hrm-rl/v1` exists to test whether HRM's hierarchical PFC reasoning core, when its
halting deliberation is controlled by action-value-based reinforcement learning (`hrm-rl.md`
§ 1) rather than supervised ACT classification, still solves fully observed MazeHard
shortest-route problems whose correctness depends on long-range connectivity (`mazehard.md`
§ 1.2–1.3), evaluated at the same exact-reference, structural-optimality, and token granularity
(`mazehard.md` § 13).

It is the RL-control counterpart to `experiment:mazehard-hrm/v1`, which uses the supervised
halting mechanism of `model:hrm/v1`. The two are distinct canonical identities with distinct
control semantics; neither is a specialization of the other (`experiments.md` § "Semantic
immutability": swapping the model component changes canonical identity). This document does not
speak to `mazehard-hrm/v1`.

## 2. Scope and ownership

### 2.1 Owned by this document

- the canonical experiment identity and its component references;
- the compatibility support declaration for `task:mazehard/v1` × `model:hrm-rl/v1`;
- the configured `InputAdapter`/`OutputAdapter` pair for this binding, including the decoder role
  HRM-rl exposes to the output adapter (task-specific decoding from HRM-rl native representations
  is binding-owned, `hrm-rl.md` § 8, `hrm.md` § 8);
- the selected deliberation controller and RL objective composition (which reusable building
  blocks this experiment connects to govern `halt`/`continue` and Q/value learning);
- the task-corpus requirement this experiment declares;
- the hybrid training protocol (supervised route outcome + reinforcement-learned control);
- named evaluation regimes;
- scientific defaults fixed only by this pairing.

### 2.2 Not owned by this document (`BIND-001`)

Per `BIND-001`, this document must not change: public versus withheld information, task truth,
target meaning, split meaning, or metric meaning. Where §§ 6–9 below reference task, model,
adapter, controller, or objective semantics, the authoritative documents remain so; this document
only selects and composes them.

### 2.3 Authoritative dependencies

| Concern                          | Authoritative specification                                    |
| -------------------------------- | -------------------------------------------------------------- |
| Task semantics                   | `docs/docs/research/tasks/mazehard.md`                         |
| Model semantics                  | `docs/docs/research/models/hrm-rl.md`                          |
| Input adapter contract           | `docs/docs/framework/adapters/raster-sequence-v1.md`           |
| Output adapter contract          | `docs/docs/framework/adapters/raster-prediction-v1.md`         |
| Compatibility declaration schema | `docs/docs/framework/compatibility.md`                         |
| Generic experiment contract      | `docs/docs/interfaces/python/experiments.md`                   |
| Raster topology (transitive)     | `docs/docs/framework/contracts/topology/raster-topology-v1.md` |
| Maze-ND topology (transitive)    | `docs/docs/research/substrates/maze-nd-v1.md`                  |

Two further building blocks are composed by reference but have **no specification yet**: the
deliberation controller and the RL objective (`hrm-rl.md` § 8 lists both as neighboring research
documents). They are recorded as required reusable components per `ARCH-016`, to be specified
under `docs/docs/research/` before their production implementation; their contracts are not
invented by this document or by the design exemplar (`ARCH-014`).

## 3. Identity

| Property                 | Value                           |
| ------------------------ | ------------------------------- |
| Canonical experiment ref | `experiment:mazehard-hrm-rl/v1` |
| Task ref                 | `task:mazehard/v1`              |
| Model ref                | `model:hrm-rl/v1`               |

`model:hrm/v1` (`experiments/mazehard-hrm/v1/plan.md`) is a distinct model with its own binding
and supervised control; this document does not speak to it.

## 4. Compatibility declaration

Per `docs/docs/framework/compatibility.md` § "Support levels":

```yaml
task: task:mazehard/v1
model: model:hrm-rl/v1
support: supported
compatibility_maturity: declared
```

`compatibility_maturity` starts at `declared` because construction and execution do not yet exist
(`packages/ehp-research/src/experiments/`, `.../tasks/mazehard/`, `.../models/`, and the referenced
controller/objective packages are all unimplemented at time of writing).

## 5. Binding: adapter configuration

### 5.1 Input side — `RasterSequenceAdapter` (`raster-sequence-v1`)

Identical to `mazehard-hrm/v1` § 5.1: MazeHard's visible problem (topology, start, goal;
`mazehard.md` § 4.1, § 9.1) is exposed as one categorical raster field over the task's natural
position domain, `P` positions. HRM-rl declares `sequence_capacity = S` (`hrm-rl.md` § 3,
model-owned).

This experiment configures:

- `S = P`, so `RIN-CMP-001` (`P <= S`) holds with zero representation-only padding; for the
  canonical `30 × 30` reference-reproduction profile (`mazehard.md` § 9.2), `P = S = 900`.
- `category_mapping`: an explicit injective mapping from MazeHard's public per-position category
  domain (traversable/blocked, start, goal; `mazehard.md` § 4.1; equivalently
  `{wall, free, start, goal}` under § 8.3, excluding the target-only `path` class) to HRM-rl's
  model-owned categorical input vocabulary.
- no `sequence_mask` for the reference profile (`padding_count = 0`).

The `reset` input (`hrm-rl.md` § 3, "starts a new problem") is emitted at problem start so that
independent MazeHard problems do not share problem-scoped reasoning state (`hrm-rl.md` § 4).

### 5.2 Decoder role — HRM-rl native output to task-prediction interface

`HRM-rl` native outputs include `theta_summary`, `schema_slots`, `q_values`, and `state_value`
(`hrm-rl.md` § 3 and § 6). Task-specific answer prediction is binding-owned (`hrm-rl.md` § 8).

This experiment declares the decoder role reads `schema_slots` (per-slot native representation),
not `theta_summary`, `q_values`, or `state_value` (the latter two feed the controller, not route
prediction):

- this HRM-rl instantiation's schema-slot count is set to `S` (equal to `sequence_capacity`, per
  § 5.1), one schema slot per input slot;
- the decoder projects each schema slot to a categorical distribution over MazeHard's target
  vocabulary `{wall, free, start, goal, path}` (`mazehard.md` § 8.3);
- the decoder's output role declares `slot_preservation`: output slot `s` corresponds to the same
  task position as input slot `s`.

### 5.3 Output side — `RasterPredictionAdapter` (`raster-prediction-v1`)

- source role: the § 5.2 decoder output over `schema_slots`, `prediction_kind: categorical
scores` (a 5-way distribution per slot);
- `position_to_slot` / `slot_to_position`: reused unchanged from § 5.1 (`p ↦ p`);
- score-to-label conversion: `argmax` over the 5-class distribution at each position, since
  `mazehard.md` § 8.3's target `y*` is a single mutually-exclusive categorical label per position;
- `category_mapping`: identity or an explicit injective mapping mirroring § 5.1.

### 5.4 What this binding must not do

Per `ADAPT-002` and both adapters' own § 7 "Information and semantic boundaries": no part of this
binding may consume `optimal_cost`, `reference_path`, or any other target/oracle field
(`mazehard.md` § 9.1) as model input. The deliberation controller consumes `q_values`/`state_value`
produced by the model, not task oracle fields; reward for RL control is composed from the outcome
supervision in evaluation (§ 7, § 8), not fed through the adapters. Scoring against `y*` happens
entirely in evaluation.

## 6. Task-corpus requirement

This experiment declares a requirement for one committed `task:mazehard/v1` corpus release built
over one `maze-nd/v1` `source-topology` release, at the canonical reference-reproduction profile
(`30 × 30`, `P = 900`; `mazehard.md` § 9.2).

Per `docs/docs/interfaces/python/experiments.md` § "Task-corpus requirements", this document
declares the requirement; it does not select a concrete local artifact. It does **not** fix the
Maze-ND source revision, fingerprint, connectivity policy, or selection/deduplication order —
those are `maze-nd/v1`'s own open issues (§ 9) and must be resolved there, not invented here.

## 7. Training protocol

This is the experiment's central scientific addition: a **hybrid** protocol that composes a
supervised route outcome objective with a reinforcement-learned deliberation-control objective.

- **Route outcome (supervised)**: supervised cross-entropy over the 5-class target vocabulary at
  every output position, matching `mazehard.md` § 13.1's exact-reference-accuracy target. The
  route decoder is trained against `reference_labels`/`reference_path` (`mazehard.md` § 9.1).
- **Deliberation control (RL)**: HRM-rl's `halt`/`continue` is controlled by the selected
  deliberation controller (`hrm-rl.md` § 8: policy/action selection, execution of `halt` and
  `continue`, interaction with the task runtime, preservation of resumable-state lineage). The
  selected RL objective owns reward interpretation, discounting, TD targets, Q/value losses,
  warm-up, and optimizer policy (`hrm-rl.md` § 8), interpreted under the resolved
  deliberation-control return specification (`hrm-rl.md` § 1).

This document selects the reusable controller and RL objective building blocks by reference; it
does not author their contract. Because their specifications do not yet exist, this experiment
records them as required reusable components per `ARCH-016`, to be specified before their
implementation.

- **Padding/ignore positions**: none for the reference profile (§ 5.1).
- Optimizer, learning rate, batch size, and training duration are outside both HRM-rl (`hrm-rl.md`
  § 5) and this document's current scope; they are experiment-level scientific defaults still to
  be fixed once an implementation exists to validate them against (§ 9).

## 8. Evaluation regimes and metrics

Named evaluation regimes and metrics are taken directly from `mazehard.md` § 13 and must not be
redefined here (`BIND-001`):

| Regime / metric                   | Source               |
| --------------------------------- | -------------------- |
| Exact solution accuracy (primary) | `mazehard.md` § 13.1 |
| Token accuracy (diagnostic)       | `mazehard.md` § 13.2 |
| `any_valid_optimal_path_rate`     | `mazehard.md` § 13.3 |
| Aggregation                       | `mazehard.md` § 13.4 |

This experiment additionally evaluates the learned deliberation policy: the distribution of
reasoning steps (`halt` step) and the value estimates the controller attains, as diagnostics
distinct from route accuracy. These are this experiment's composition-level observables, not
task-level metrics redefined from `mazehard.md`.

The decoded representation feeding the route metrics is the § 5.3 output-adapter product (per-
position labels in `{wall, free, start, goal, path}`, in canonical task-position order).

## 9. Status and prerequisites

This document records, rather than resolves, the following blockers:

- **`maze-nd/v1` is still `draft`** (same three unresolved policy choices as `mazehard-hrm/v1` § 9:
  authoritative source revision/fingerprint, `preserve` vs `reject` connectivity policy,
  selection-before-or-after-deduplication order). None are decided here.
- **The deliberation controller and RL objective specifications are missing.** `hrm-rl.md` § 8
  lists both as neighboring documents; neither exists yet under `docs/docs/research/`. This
  experiment's § 7 composes them by reference. Per `ARCH-014`, this document and the design
  exemplar must not invent their canonical contracts; the controller's policy/action-selection
  and Q/value-learning semantics and the RL objective's reward/TD semantics are reusable research
  concepts that must be specified before their production implementation.
- **Training-protocol numeric defaults** (§ 7): route-loss vs RL-return composition weighting,
  discounting, TD algorithm, optimizer, learning rate, batch size, and training duration are not
  fixed anywhere in the authority chain for this pairing.
- **Research-registration guarantees** (`ARCH-003`): registering this experiment's task/model/
  adapter components with framework discovery must not rely on any registration property beyond
  what `ARCH-003` guarantees.

## Related specifications

- [MazeHard v1](../../../docs/docs/research/tasks/mazehard.md)
- [HRM-rl](../../../docs/docs/research/models/hrm-rl.md)
- [Raster categorical to sequence adapter v1](../../../docs/docs/framework/adapters/raster-sequence-v1.md)
- [Categorical sequence to raster adapter v1](../../../docs/docs/framework/adapters/raster-prediction-v1.md)
- [Compatibility](../../../docs/docs/framework/compatibility.md)
- [Experiments](../../../docs/docs/interfaces/python/experiments.md)
- [Maze-ND v1](../../../docs/docs/research/substrates/maze-nd-v1.md)
