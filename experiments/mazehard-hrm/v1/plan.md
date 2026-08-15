---
title: MazeHard-HRM v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

## Normative summary

`experiment:mazehard-hrm/v1` is the resolved scientific composition of the `task:mazehard/v1`
task and the `model:hrm/v1` model: a supervised path-labelling experiment in which HRM consumes a
fully observed MazeHard problem and predicts the reference route.

It declares the compatibility support level, the configured `InputAdapter`/`OutputAdapter` pair,
the task-corpus requirement, the training objective, and the evaluation regime. It does not
redefine task, model, or adapter semantics; where this document states a value already owned
elsewhere, that value is repeated for composition clarity, not re-authored.

This document is `draft`. It depends on a specification that is itself `draft` (`maze-nd/v1`). See
"Status and prerequisites".

## 1. Purpose

`mazehard-hrm/v1` exists to reproduce, within EHP-SN, the HRM/Maze-Hard global-spatial-reasoning
comparison described by `docs/docs/research/tasks/mazehard.md` § 1.2–1.3: whether HRM's
hierarchical latent-reasoning core can solve fully observed shortest-route problems whose
correctness depends on long-range connectivity, evaluated at both exact-reference and
structural-optimality granularity (`mazehard.md` § 13).

It is one of two bindings HRM participates in. `hrm.md` § 8 lists Routebind–HRM as a separate
neighboring binding; this document does not speak to it.

## 2. Scope and ownership

### 2.1 Owned by this document

- the canonical experiment identity and its component references;
- the compatibility support declaration for `task:mazehard/v1` × `model:hrm/v1`;
- the configured `InputAdapter`/`OutputAdapter` pair for this binding, including the decoder role
  HRM exposes to the output adapter (`hrm.md` § 8: task-specific decoding from HRM native
  representations is binding-owned, and `docs/authority.md` § "Authority map" assigns assembly of
  a concrete resolved binding to the `ExperimentDefinition`, i.e. to this document);
- the task-corpus requirement this experiment declares;
- training objective composition and named evaluation regimes;
- scientific defaults fixed only by this pairing.

### 2.2 Not owned by this document (`BIND-001`)

Per `BIND-001`, this document must not change: public versus withheld information, task truth,
target meaning, split meaning, or metric meaning. Where §§ 6–9 below reference task or model
semantics, the task (`mazehard.md`) and model (`hrm.md`) documents remain authoritative; this
document only selects and composes them.

### 2.3 Authoritative dependencies

| Concern                          | Authoritative specification                                    |
| -------------------------------- | -------------------------------------------------------------- |
| Task semantics                   | `docs/docs/research/tasks/mazehard.md`                         |
| Model semantics                  | `docs/docs/research/models/hrm.md`                             |
| Input adapter contract           | `docs/docs/framework/adapters/raster-sequence-v1.md`           |
| Output adapter contract          | `docs/docs/framework/adapters/raster-prediction-v1.md`         |
| Compatibility declaration schema | `docs/docs/framework/compatibility.md`                         |
| Generic experiment contract      | `docs/docs/interfaces/python/experiments.md`                   |
| Raster topology (transitive)     | `docs/docs/framework/contracts/topology/raster-topology-v1.md` |
| Maze-ND topology (transitive)    | `docs/docs/research/substrates/maze-nd-v1.md`                  |

## 3. Identity

| Property                 | Value                        |
| ------------------------ | ---------------------------- |
| Canonical experiment ref | `experiment:mazehard-hrm/v1` |
| Task ref                 | `task:mazehard/v1`           |
| Model ref                | `model:hrm/v1`               |

`model:hrm-rl/v1` (`docs/docs/research/models/hrm-rl.md`) is a distinct model and is explicitly
out of scope for `mazehard-hrm/v1`. A future `mazehard-hrm-rl/v1` experiment, if warranted, is a
separate canonical identity, not a specialization of this one (`experiments.md` § "Semantic
immutability": supported specialization does not include swapping the model component).

## 4. Compatibility declaration

Per `docs/docs/framework/compatibility.md` § "Support levels":

```yaml
task: task:mazehard/v1
model: model:hrm/v1
support: supported
compatibility_maturity: declared
```

`compatibility_maturity` starts at `declared` because construction and execution do not yet exist
(`packages/ehp-research/src/experiments/`, `.../tasks/mazehard/`, `.../models/` are all
unimplemented at time of writing). It advances to `implemented`, `validated`, and `reference`
under `docs/docs/framework/compatibility.md` § "Compatibility maturity" as evidence accrues; this
document is not updated to restate that ladder, only its current position.

## 5. Binding: adapter configuration

### 5.1 Input side — `RasterSequenceAdapter` (`raster-sequence-v1`)

MazeHard's visible problem (topology, start, goal; `mazehard.md` § 4.1, § 9.1) is exposed as one
categorical raster field over the task's natural position domain, `P` positions. HRM declares
`sequence_capacity = S` (`hrm.md` § 3, model-owned).

This experiment configures:

- `S = P`, i.e. HRM's `sequence_capacity` is set to exactly MazeHard's natural position count for
  the selected corpus profile, so `RIN-CMP-001` (`P <= S`) holds with zero representation-only
  padding. For the canonical `30 × 30` reference-reproduction profile (`mazehard.md` § 9.2),
  `P = S = 900`, matching the reference manuscript's interface size.
- `category_mapping`: an explicit injective mapping from MazeHard's public per-position category
  domain (traversable/blocked, start, goal — per `mazehard.md` § 4.1; equivalently `{wall, free,
start, goal}` under § 8.3's labeling, excluding the target-only `path` class) to HRM's
  model-owned categorical input vocabulary. The exact mapping (integer IDs or otherwise) is an
  implementation choice deferred to the HRM implementation's declared input vocabulary; it is not
  authored here beyond requiring injectivity (`RIN-MAP-002`).
- no `sequence_mask` is required for the reference profile (`padding_count = 0`); a corpus profile
  with `P < S` would require one, per `raster-sequence-v1.md` § 3.

This is exactly the adapter's own § 12 "Non-normative MazeHard–HRM-style composition" worked
example, made this experiment's actual, binding configuration rather than an illustration.

### 5.2 Decoder role — HRM native output to task-prediction interface

`hrm.md` § 3 gives HRM's stable native outputs as `theta_summary`, `schema_slots`, and
`halt_logits`; none is a task-specific prediction. Per `hrm.md` § 8, attaching a task-specific
decoder to a native representation is binding-owned, and per `docs/authority.md` this binding is
assembled here.

This experiment declares the decoder role as follows:

- the decoder reads `schema_slots` (the per-slot native representation), not `theta_summary` (a
  single summary vector cannot carry `P` independent per-position predictions);
- this HRM instantiation's schema-slot count is set to `S` (equal to `sequence_capacity`, per
  § 5.1), one schema slot per input slot;
- the decoder projects each schema slot to a categorical distribution over MazeHard's target
  vocabulary `{wall, free, start, goal, path}` (`mazehard.md` § 8.3);
- the decoder's output role explicitly declares `slot_preservation`: output slot `s` corresponds
  to the same task position as input slot `s` under the § 5.1 correspondence. This is a declared
  guarantee of this binding, required by `raster-prediction-v1.md` `ROUT-IF-002` — equal slot
  cardinality between input and output alone is not sufficient evidence (`ROUT-CMP-001`).

Decoder network architecture (projection width, activation, initialization) is an implementation
choice within `hrm.md`'s model-owned parameter space and is not fixed by this document.

### 5.3 Output side — `RasterPredictionAdapter` (`raster-prediction-v1`)

- source role: the § 5.2 decoder output over `schema_slots`, `prediction_kind: categorical
scores` (a 5-way distribution per slot);
- `position_to_slot` / `slot_to_position`: reused unchanged from § 5.1 (`p ↦ p`), per
  `raster-prediction-v1.md` § 3 ("For the compatible `v1` raster input adapter this is...");
- score-to-label conversion: this experiment's task-prediction interface explicitly requires
  `argmax` over the 5-class distribution at each position, since `mazehard.md` § 8.3's target `y*`
  is a single categorical label per position and mutually exclusive — the exact condition under
  which `raster-prediction-v1` `v1` supports `argmax` (§ 3 "Scores to labels");
- `category_mapping`: identity or an explicit injective mapping from the decoder's label indices
  to `{wall, free, start, goal, path}`, mirroring § 5.1's input-side mapping.

This is the adapter's own § 12 "Non-normative HRM–MazeHard-style composition" example, likewise
made concrete and binding for this experiment.

### 5.4 What this binding must not do

Per `ADAPT-002` and both adapters' own § 7 "Information and semantic boundaries": no
part of this binding may consume `optimal_cost`, `reference_path`, or any other target/oracle
field (`mazehard.md` § 9.1) as model input; no part may perform route repair, connectivity
correction, or threshold tuning on the decoded prediction. Scoring against $y^*$ happens entirely
in evaluation (§ 8 below), not inside either adapter.

## 6. Task-corpus requirement

This experiment declares a requirement for one committed `task:mazehard/v1` corpus release built
over one `maze-nd/v1` `source-topology` release, at the canonical reference-reproduction profile
(`30 × 30`, `P = 900`; `mazehard.md` § 9.2).

Per `docs/docs/interfaces/python/experiments.md` § "Task-corpus requirements", this document
declares the requirement; it does not select a concrete local artifact. The exact corpus reference
resolves at request time through the framework's declared precedence.

This experiment does **not** fix the Maze-ND source revision, fingerprint, connectivity policy, or
selection/deduplication order — those are `maze-nd/v1`'s own open issues (§ 9 below) and must be
resolved in that specification, not invented here.

## 7. Training protocol

- **Objective**: supervised cross-entropy over the 5-class target vocabulary at every supervised
  output position, matching `mazehard.md` § 13.1's exact-reference-accuracy target.
- **Halting term**: HRM's supervised ACT halt/continue mechanism (`hrm.md` § 1, § 3) contributes
  its own supervised halting loss term, composed with the route-prediction cross-entropy. The
  exact composition weighting is an open issue (§ 9) — `hrm.md` does not fix it, and inventing a
  specific coefficient here would assert unowned authority.
- **Padding/ignore positions**: none for the reference profile (§ 5.1, `padding_count = 0`); a
  non-reference profile with `P < S` must exclude padding-only slots from the loss, consistent
  with `raster-sequence-v1.md` `RIN-MAP-003`.
- Optimizer, learning rate, batch size, and training duration are outside both HRM (`hrm.md` § 5)
  and this document's current scope; they are experiment-level scientific defaults still to be
  fixed once an implementation exists to validate them against (§ 9).

## 8. Evaluation regimes and metrics

Named evaluation regimes and metrics are taken directly from `mazehard.md` § 13 and must not be
redefined here (`BIND-001`):

| Regime / metric                   | Source               |
| --------------------------------- | -------------------- |
| Exact solution accuracy (primary) | `mazehard.md` § 13.1 |
| Token accuracy (diagnostic)       | `mazehard.md` § 13.2 |
| `any_valid_optimal_path_rate`     | `mazehard.md` § 13.3 |
| Aggregation                       | `mazehard.md` § 13.4 |

This experiment's only addition is which decoded representation feeds these metrics: the § 5.3
output-adapter product (per-position labels in `{wall, free, start, goal, path}`, in canonical
task-position order), evaluated against the corpus's stored `reference_labels` / `reference_path`
/ `optimal_cost` fields (`mazehard.md` § 9.1).

## 9. Status and prerequisites

This document records, rather than resolves, the following blockers:

- **`maze-nd/v1` is still `draft`.** `raster-topology/v1` (the shared schema `maze-nd/v1` sits on)
  has since been promoted to `specified`, removing that dependency blocker, but `maze-nd/v1` itself
  still carries three unresolved policy choices (authoritative source revision/fingerprint,
  `preserve` vs `reject` connectivity policy, selection-before-or-after-deduplication order). None
  of these are decided by this document; § 6 above deliberately declares only a corpus
  _requirement_, not a concrete release.
- **Training-protocol numeric defaults** (§ 7): halting-loss weighting, optimizer, learning rate,
  batch size, and training duration are not yet fixed anywhere in the authority chain for this
  pairing. They should be fixed once an implementation exists to validate them against, not
  invented in this specification.
- **`docs/decisions.md` DEC-006** (open, indirectly relevant): general research-registration
  properties (determinism, import-order independence beyond duplicate resolution) are not settled
  authority. Registering this experiment's task/model/adapter components with framework discovery
  must not rely on those properties beyond what `ARCH-003` already guarantees.

## Related specifications

- [MazeHard v1](../../../docs/docs/research/tasks/mazehard.md)
- [HRM](../../../docs/docs/research/models/hrm.md)
- [Raster categorical to sequence adapter v1](../../../docs/docs/framework/adapters/raster-sequence-v1.md)
- [Categorical sequence to raster adapter v1](../../../docs/docs/framework/adapters/raster-prediction-v1.md)
- [Compatibility](../../../docs/docs/framework/compatibility.md)
- [Experiments](../../../docs/docs/interfaces/python/experiments.md)
- [Maze-ND v1](../../../docs/docs/research/substrates/maze-nd-v1.md)
