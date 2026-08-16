---
title: Arena-TEM v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

## Normative summary

`experiment:arena-tem/v1` is the resolved scientific composition of the `task:arena/v1` task and
the `model:tem/v1` model: a sequential replay experiment in which TEM acquires environment-specific
associative memory from action-observation experience and predicts observations, evaluated
primarily on revisit-conditioned accuracy.

It declares the compatibility support level, the configured `InputAdapter`/`OutputAdapter` pair,
the three TEM prediction pathways `arena.md` §1.1/§14 already anticipate but leave binding-owned,
the task-corpus requirement, the training objective, and the evaluation regime. It does not
redefine task, model, or adapter semantics.

This document is `draft`. It depends on specifications that are themselves `draft`
(`dungeongen/v1`, `obsfield/v1`). See "Status and prerequisites".

## 1. Purpose

`arena-tem/v1` exists to reproduce, within EHP-SN, the TEM environment-specific-memory comparison
`docs/docs/research/tasks/arena.md` describes as its "reference Arena–TEM evaluation" (§1.1):
whether a recurrent relational-memory model can acquire structured, environment-specific state from
sequential experience and use it to predict observations at revisited positions
(`arena.md` §1.2), with different TEM prediction pathways probing different degrees of reliance on
that acquired state versus the current sensory observation (§1.1, §14).

This is the experiment `docs/docs/interfaces/python/experiments.md`, `docs/docs/framework/references.md`,
and the CLI docs already use pervasively as their worked example (`experiment:arena-tem/v1`,
resolved through `ExperimentRef.parse`/`resolve_experiment`) — this document is the first time its
actual scientific content is specified; none of those interface docs define it.

## 2. Scope and ownership

### 2.1 Owned by this document

- the canonical experiment identity and its component references;
- the compatibility support declaration for `task:arena/v1` × `model:tem/v1`;
- the configured `InputAdapter`/`OutputAdapter` pair for this binding;
- the three named TEM prediction pathways `arena.md` §1.1/§14 refer to but does not itself define
  (`posterior`, `sensory-recall`, `structural-prior/path-integration`) and their corresponding
  pathway metrics `A_post`, `A_rec^rev`, `A_PI^rev` (named but not defined by `arena.md` §13.2,
  which explicitly assigns their definition to "Model/binding-specific Arena–TEM evaluation");
- the topology and observation-field substrate choice for this experiment's corpus requirement;
- training objective composition;
- scientific defaults fixed only by this pairing.

### 2.2 Not owned by this document (`BIND-001`)

Per `BIND-001`, this document must not change: public versus withheld information, task truth,
target meaning, split meaning, or metric meaning. `arena.md`'s primary metric `A_obs^rev` and
secondary metrics (§13.1–13.2) remain authoritative and unmodified here; this document only adds
the pathway-specific specializations `arena.md` itself defers to the binding.

### 2.3 Authoritative dependencies

| Concern                          | Authoritative specification                                          |
| -------------------------------- | -------------------------------------------------------------------- |
| Task semantics                   | `docs/docs/research/tasks/arena.md`                                  |
| Model semantics                  | `docs/docs/research/models/tem.md`                                   |
| Input adapter contract           | `docs/docs/framework/adapters/relational-sequence-v1.md`             |
| Output adapter contract          | `docs/docs/framework/adapters/observation-prediction-v1.md`          |
| Compatibility declaration schema | `docs/docs/framework/compatibility.md`                               |
| Generic experiment contract      | `docs/docs/interfaces/python/experiments.md`                         |
| Raster topology (transitive)     | `docs/docs/framework/contracts/topology/raster-topology-v1.md`       |
| Categorical field (transitive)   | `docs/docs/framework/contracts/observations/categorical-field-v1.md` |
| DungeonGen (transitive)          | `docs/docs/research/substrates/dungeongen-v1.md`                     |
| ObsField (transitive)            | `docs/docs/research/substrates/obsfield-v1.md`                       |

## 3. Identity

| Property                 | Value                     |
| ------------------------ | ------------------------- |
| Canonical experiment ref | `experiment:arena-tem/v1` |
| Task ref                 | `task:arena/v1`           |
| Model ref                | `model:tem/v1`            |

`model:tem-t/v1` (`docs/docs/research/models/tem-t.md`) is a distinct model with its own binding —
see `experiments/arena-tem-t/v1/plan.md`. This document does not speak to it, consistent with
`experiments.md` § "Semantic immutability" treating a model swap as a different canonical identity.

## 4. Compatibility declaration

Per `docs/docs/framework/compatibility.md` § "Support levels":

```yaml
task: task:arena/v1
model: model:tem/v1
support: supported
compatibility_maturity: declared
```

`compatibility_maturity` starts at `declared`: no construction or execution exists yet
(`packages/ehp-research/src/experiments/`, `.../tasks/arena/`, `.../models/` are all unimplemented
at time of writing).

## 5. Binding: adapter configuration

### 5.1 Input side — `RelationalSequenceAdapter` (`relational-sequence-v1`)

Arena's replay `(observation[t], action[t])` for `t ∈ {0..T-1}` (`arena.md` §9.1) is exposed as one
observation/relation task sequence. TEM declares native inputs `sensory_id`, `relation_id`, `reset`,
`sequence_mask` (`tem.md` §3).

This experiment configures:

- `task_step_to_model_step(t) = t`, matching both the adapter's fixed `v1` correspondence and
  Arena's own temporal-canonicalization rule (`arena.md` §7.4);
- `observation_mapping`: an explicit injective mapping from Arena's public observation vocabulary
  to TEM's `sensory_id` domain;
- `relation_mapping`: an explicit injective mapping from Arena's grid4 (+ optional `STAY`) action
  vocabulary (`arena.md` §7.2) to TEM's `relation_id` domain;
- reset representation: emitted at task step `0`, satisfying `SIN-CMP-002` and matching TEM's
  `reset` input, which "initializes environment/sequence-specific model state" (`tem.md` §3) —
  this is also where Arena's `episode_start` (`arena.md` §9.1) enters the model;
- no `sequence_mask` required when the corpus uses fixed episode length `T`; required when episode
  length varies and fixed-capacity storage pads shorter episodes.

This is exactly the adapter's own §12 "Non-normative Arena–TEM-style composition" worked example,
made this experiment's actual, binding configuration.

### 5.2 Prediction pathways — TEM native output to task-prediction interface

`tem.md` §3 states the stable task-facing output is "the declared sensory-prediction role." Unlike
HRM's binding-owned decoder (`hrm.md` §8), TEM keeps conjunction and memory retrieval inside the
model (`tem.md` §7–§8), and `observation-prediction-v1.md` §2.1 confirms "the selected source role
is supplied by binding/experiment composition" — i.e. TEM itself must declare the candidate
sensory-prediction roles; this binding's job is to select and name which declared role plays which
Arena–TEM pathway, not to construct new decoding. `arena.md` §1.1 and §14 already name three
pathways for "the reference Arena–TEM evaluation" — `posterior`, `sensory-recall`, and
`structural-prior/path-integration` — as properties of this binding, not of the Arena task or of
generic TEM. Neither `arena.md` nor `tem.md` defines what distinguishes them; that is this
document's job.

This experiment declares three named sensory-prediction roles, each a distinct `model-output role`
satisfying `observation-prediction-v1.md` §2.1's requirements (`model_step_identity`,
`step_preservation`, `prediction_kind`, `source_vocabulary`, `prediction_timing`,
`prediction_conditioning`), grounded in TEM's own 8-step inference schedule (`tem.md` §4, steps
2–6: structural update → sensory encoding → conjunction → memory/inference → prediction):

| Pathway                             | `prediction_conditioning`                                                                                                                    | Current observation access                                                                                         |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `structural-prior/path-integration` | emitted from `g_t` alone, computed at schedule step 2, before the current step's sensory identity is encoded                                 | none — structurally impossible by timing, not by input withholding                                                 |
| `posterior`                         | emitted from `p_t` after the full conjunctive + memory/inference computation (schedule steps 4–5)                                            | yes — `p_t` is built from `x_t`, which is derived from the current step's `sensory_id`                             |
| `sensory-recall`                    | emitted from content retrieved from associative memory `M_{t-1}` keyed by `g_t`, i.e. what a prior visit to this structural state associated | yes, per `arena.md` §14, though its distinguishing signal is memory retrieval rather than current sensory evidence |

All three conditions are declared, not computed by this document — TEM's own implementation must
expose them as its "declared sensory-prediction role(s)" at the corresponding schedule points;
this binding only selects and names them (`tem.md` §8: bindings "must not implement TEM
embeddings, structural-state updates, conjunctive computation, memory retrieval, or memory
updates"). This interpretation is this document's own declared design decision, not restated
authority — see "Status and prerequisites."

`prediction_timing = current_step` for all three pathways, satisfying `observation-prediction-v1.md`
§2.2's exact-match requirement against Arena's target timing.

### 5.3 Output side — `ObservationPredictionAdapter` (`observation-prediction-v1`)

For each of the three §5.2 pathways, independently:

- source role: the named pathway's declared sensory-prediction output,
  `prediction_kind: categorical scores` over TEM's sensory vocabulary;
- `task_step_to_model_step` / `model_step_to_task_step`: reused unchanged from §5.1 (`t ↦ t`);
- `category_mapping`: identity or explicit injective mapping from TEM's sensory-prediction indices
  back to Arena's observation vocabulary, mirroring §5.1's input-side mapping;
- score-to-label conversion: `argmax`, since Arena's target `y_t^* = o_t` (`arena.md` §4.2) is a
  single categorical label and `observation-prediction-v1` `v1` supports `argmax` when the target
  explicitly requires it (§3 "Scores to labels").

This reuses the adapter's own §12 "Non-normative TEM–Arena-style composition" worked example,
applied independently to each of the three pathways.

### 5.4 What this binding must not do

Per `ADAPT-002` and both adapters' own §7 "Information and semantic boundaries": no part of this
binding may consume `is_revisit`, `trajectory_position`, or any other privileged/withheld field
(`arena.md` §9.1, §4.3–4.4) as model input; the `structural-prior/path-integration` pathway's
current-observation exclusion is enforced by TEM's own schedule timing (§5.2), not by an adapter
hiding data the model otherwise received. Scoring against `y_t^*` happens entirely in evaluation
(§8 below), not inside either adapter.

## 6. Task-corpus requirement

This experiment declares a requirement for one committed `task:arena/v1` corpus release built over:

- **topology parent**: `dungeongen/v1`, variant `general` (`dungeongen-v1.md` — the only variant;
  procedurally generated, no external-source semantics, a natural fit for a reproduction setting
  not tied to an external benchmark, unlike Maze-ND). This is this document's own substrate choice,
  not dictated by `arena.md`, which requires only the `raster-topology/v1` capability (§6.1–6.2).
- **observation-field parent**: `obsfield/v1`, variant `categorical-complete`, assignment protocol
  `categorical-random/v1` (`obsfield-v1.md` — the only currently-specified assignment protocol).

Per `docs/docs/interfaces/python/experiments.md` § "Task-corpus requirements", this document
declares the requirement; it does not select a concrete local artifact.

This experiment does **not** fix DungeonGen's generator dependency, acceptance policy, or
ObsField's `distribution`/`base_seed` parameters — those are concrete-release decisions belonging
to the corpus profile, not invented here.

## 7. Training protocol

- **Objective**: supervised cross-entropy between each pathway's predicted observation
  distribution and `y_t^* = o_t` at every valid replay step, for whichever pathway(s) this
  experiment trains jointly or separately (a training-time choice, not fixed by this document).
- **Reset/episode alignment**: governed by TEM's reset semantics and 8-step schedule (`tem.md` §4)
  and Arena's `episode_start` (`arena.md` §9.1); per `arena.md` §14, "recurrent unrolling and state
  reset belong to the experiment's training protocol, not to either adapter" — this document is
  where that belongs, and it is not yet fixed beyond reusing TEM's declared reset contract.
- **Padding/ignore positions**: any representation-only padding steps (§5.1) are excluded from the
  loss, consistent with `relational-sequence-v1.md` `SIN-MAP-004`.
- Optimizer, learning rate, batch size, training duration, and relative pathway-loss weighting are
  outside both TEM (`tem.md` §5) and this document's current scope — open issues, not invented
  here.

## 8. Evaluation regimes and metrics

Named evaluation regimes and metrics are taken directly from `arena.md` §13 and must not be
redefined here (`BIND-001`):

| Regime / metric                                    | Source                         |
| -------------------------------------------------- | ------------------------------ |
| Revisit-conditioned observation accuracy (primary) | `arena.md` §13.1 (`A_obs^rev`) |
| Overall / first-visit accuracy (secondary)         | `arena.md` §13.2               |
| Aggregation                                        | `arena.md` §13.3               |

This binding's addition, per `arena.md` §13.2's explicit deferral ("Model/binding-specific
Arena–TEM evaluation may additionally report the pathway metrics `A_post`, `A_rec^rev`, `A_PI^rev`"):
each is `A_obs^rev`'s exact definition (`arena.md` §13.1), computed independently over the §5.2
pathway named `posterior`, `sensory-recall`, and `structural-prior/path-integration` respectively —
not a new metric shape, a per-pathway specialization of the existing one, using the same
undefined-for-zero-revisit reporting rule.

## 9. Status and prerequisites

This document records, rather than resolves, the following blockers:

- **`dungeongen/v1` and `obsfield/v1` are still `draft`.** `raster-topology/v1`,
  `categorical-field/v1`, and `ambient-domain/v1` (the framework contracts both substrates and
  `arena.md` itself depended on) have since been promoted to `specified`, removing that shared
  dependency blocker from all three — `arena.md`'s own §15 no longer lists it either. Each
  substrate still carries its own remaining open issues, unresolved by this document: DungeonGen's
  generator dependency/reference protocol is unfixed (`dungeongen-v1.md` § "Open issues"); ObsField's
  exact hex/finite-shape/enumeration contract, topology-to-ambient-position mapping contract, and
  vocabulary-reference/identity contract remain unresolved (`obsfield-v1.md` § "Open issues").
- **Arena's own split/novelty policy** (`arena.md` §10.3) is left to the concrete corpus profile,
  not invented here.
- **The §5.2 pathway interpretation is this document's own declared design decision**, reasoned
  from TEM's documented 8-step schedule but not itself restated authority from `tem.md` or a
  citation to Whittington et al. (2020)'s exact posterior/prior/recall formulation. If
  implementation or closer reading of the reference paper reveals a different split is more
  faithful, that is a revision to _this_ document (per `tem.md`'s own instruction that deviations
  "must be documented at the affected rule"), not evidence this document was wrong to attempt one.
- **Training-protocol numeric defaults** (§7) are not yet fixed anywhere in the authority chain for
  this pairing.

## Related specifications

- [Arena v1](../../../docs/docs/research/tasks/arena.md)
- [TEM](../../../docs/docs/research/models/tem.md)
- [Observation-relation sequence to sensory-relation sequence adapter v1](../../../docs/docs/framework/adapters/relational-sequence-v1.md)
- [Sensory-prediction sequence to observation sequence adapter v1](../../../docs/docs/framework/adapters/observation-prediction-v1.md)
- [Compatibility](../../../docs/docs/framework/compatibility.md)
- [Experiments](../../../docs/docs/interfaces/python/experiments.md)
- [DungeonGen v1](../../../docs/docs/research/substrates/dungeongen-v1.md)
- [ObsField v1](../../../docs/docs/research/substrates/obsfield-v1.md)
