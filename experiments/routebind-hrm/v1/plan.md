---
title: Routebind-HRM v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

## Normative summary

`experiment:routebind-hrm/v1` is the resolved scientific composition of the `task:routebind/v1`
task and the `model:hrm/v1` model: a supervised spatial–semantic routing experiment in which HRM
consumes a fully observed Routebind problem (visible topology and observations, hidden semantic
law) and predicts continuous trajectory and waypoint fields.

It declares the compatibility support level, the configured `InputAdapter`/`OutputAdapter` pair,
the task-corpus requirement, the training objective, and the evaluation regime. It does not
redefine task, model, or adapter semantics.

This document is `draft`. Unlike `mazehard-hrm/v1/plan.md`, it cannot reuse an existing adapter
pair — see "Adapter gap" below — so it depends on two new framework adapter specifications
authored alongside it (`raster-overlay-sequence-v1.md`, `raster-field-prediction-v1.md`, both
themselves `draft`) in addition to `routebind.md`'s own upstream substrate chain. See "Status and
prerequisites".

## Adapter gap

`routebind.md`'s shape does not fit either adapter pair used by the other three experiment specs
in this repository:

- Routebind's public input (`routebind.md` §4.1, §9.1) is four simultaneous per-position channels
  — traversability, observation identity, `start_flag`, `goal_flag` — not one categorical channel.
  `raster-sequence-v1.md` §1 explicitly excludes this: "Combining separate scientific roles such as
  passability, start, and goal into one category is outside this adapter."
- Routebind's targets (`routebind.md` §8.5, §9.1) are two continuous-valued fields
  `target_trajectory`, `target_waypoint` ∈ [0, 1] per position, not categorical labels or scores —
  outside `raster-prediction-v1.md` §2.1's `prediction_kind: categorical labels or categorical
scores` requirement.

Both gaps are genuine, reusable framework-representational patterns (multi-channel raster input,
continuous raster-field output), not Routebind- or HRM-specific, so per `docs/authority.md` they
belong under `docs/docs/framework/adapters/` (`ehp_sn`-owned). This experiment is their first
worked composition, but the contracts themselves name neither Routebind nor HRM in their normative
bodies.

## 1. Purpose

`routebind-hrm/v1` exists to test whether HRM's hierarchical latent-reasoning core can combine
visible spatial structure with a corpus-stable but unobserved semantic transition law
(`routebind.md` §1.2), evaluated primarily on behavioral route validity
(`valid_semantic_spatial_route_rate`) and secondarily on physical-cost optimality, rather than on
field-similarity alone (`routebind.md` §13.4).

This is the one binding the repository already names as a canonical worked example
(`hrm.md` §8; `docs/docs/interfaces/cli/index.md`'s `experiment:routebind-hrm/v1`) but had no
written content for — the same gap `mazehard-hrm` and `arena-tem` filled earlier in this pass.

## 2. Scope and ownership

### 2.1 Owned by this document

- the canonical experiment identity and its component references;
- the compatibility support declaration for `task:routebind/v1` × `model:hrm/v1`;
- the configured `InputAdapter`/`OutputAdapter` pair for this binding, including the decoder role
  HRM exposes to the two output-adapter instances (same reasoning as `mazehard-hrm/v1/plan.md`
  §5.2: task-specific decoding from HRM native representations is binding-owned per `hrm.md` §8);
- the task-corpus requirement this experiment declares;
- training objective composition;
- scientific defaults fixed only by this pairing.

### 2.2 Not owned by this document (`BIND-001`)

Per `BIND-001`, this document must not change: public versus withheld information, task truth,
target meaning, split meaning, or metric meaning. `routebind.md`'s oracle/target semantics (§8) and
metrics (§13) remain authoritative and unmodified here.

### 2.3 Authoritative dependencies

| Concern                              | Authoritative specification                                          |
| ------------------------------------ | -------------------------------------------------------------------- |
| Task semantics                       | `docs/docs/research/tasks/routebind.md`                              |
| Model semantics                      | `docs/docs/research/models/hrm.md`                                   |
| Input adapter contract               | `docs/docs/framework/adapters/raster-overlay-sequence-v1.md`         |
| Output adapter contract              | `docs/docs/framework/adapters/raster-field-prediction-v1.md`         |
| Compatibility declaration schema     | `docs/docs/framework/compatibility.md`                               |
| Generic experiment contract          | `docs/docs/interfaces/python/experiments.md`                         |
| Raster topology (transitive)         | `docs/docs/framework/contracts/topology/raster-topology-v1.md`       |
| Categorical field (transitive)       | `docs/docs/framework/contracts/observations/categorical-field-v1.md` |
| Directed semantic graph (transitive) | `docs/docs/research/substrates/dagflow-v1.md`                        |
| DungeonGen (transitive)              | `docs/docs/research/substrates/dungeongen-v1.md`                     |
| ObsField (transitive)                | `docs/docs/research/substrates/obsfield-v1.md`                       |

## 3. Identity

| Property                 | Value                         |
| ------------------------ | ----------------------------- |
| Canonical experiment ref | `experiment:routebind-hrm/v1` |
| Task ref                 | `task:routebind/v1`           |
| Model ref                | `model:hrm/v1`                |

`model:hrm-rl/v1` (`docs/docs/research/models/hrm-rl.md`) is a distinct model and out of scope for
`routebind-hrm/v1`, same reasoning as `mazehard-hrm/v1/plan.md` §3.

## 4. Compatibility declaration

```yaml
task: task:routebind/v1
model: model:hrm/v1
support: supported
compatibility_maturity: declared
```

`compatibility_maturity` starts at `declared`: no construction or execution exists yet.

## 5. Binding: adapter configuration

### 5.1 Input side — `RasterOverlaySequenceAdapter` (`raster-overlay-sequence-v1`)

Routebind's four public channels (`routebind.md` §4.1, §9.1) over `P` positions are exposed as one
combined categorical sequence. HRM declares `sequence_capacity = S` (`hrm.md` §3, model-owned).

This experiment configures:

- `S = P`, same reasoning as `mazehard-hrm/v1/plan.md` §5.1: `sequence_capacity` set to exactly
  Routebind's natural position count for the selected corpus profile, so no representation-only
  padding is needed for the reference profile;
- the four declared channels: traversability (`wall`/`free`), observation identity (cardinality
  equal to the corpus vocabulary size), `start_flag` (binary), `goal_flag` (binary, marking
  `C_goal`);
- `channel_combination_mapping`: an explicit injective mapping from the four-channel tuple to
  HRM's model-owned categorical input vocabulary. The exact mapping is an implementation choice
  deferred to the HRM implementation's declared input vocabulary; this document requires only
  injectivity (`ROV-MAP-002`), same discipline as `mazehard-hrm/v1/plan.md` §5.1's
  `category_mapping`.

Neither the semantic graph, its binding, nor any privileged field (`routebind.md` §4.3) is a
declared channel — `RasterOverlaySequenceAdapter` §7 forbids consuming anything the source
task-data interface does not declare public.

### 5.2 Decoder role — HRM native output to two continuous task-prediction interfaces

Same reasoning as `mazehard-hrm/v1/plan.md` §5.2: the decoder reads `schema_slots` (the per-slot
native representation), not `theta_summary`, since per-position field prediction needs `P`
independent outputs. This HRM instantiation's schema-slot count is set to `S` (equal to
`sequence_capacity`), one schema slot per input slot.

This experiment declares **two** independent decoder roles, one per Routebind target field
(`routebind.md` §8.5):

| Role               | Reads                            | `value_range` | Target field        |
| ------------------ | -------------------------------- | ------------- | ------------------- |
| `trajectory-field` | schema slots, bounded projection | `[0, 1]`      | `target_trajectory` |
| `waypoint-field`   | schema slots, bounded projection | `[0, 1]`      | `target_waypoint`   |

Each role's output slot `s` corresponds to the same task position as input slot `s`, an explicit
`slot_preservation` guarantee required by `RasterFieldPredictionAdapter`'s `RFP-IF-002`. Decoder
network architecture (projection width, activation used to bound the output to `[0, 1]`) is an
implementation choice within `hrm.md`'s model-owned parameter space, not fixed here.

### 5.3 Output side — `RasterFieldPredictionAdapter` (`raster-field-prediction-v1`)

Two independent adapter instances, one per §5.2 role, matching that adapter's single-channel-per-
instance design (§1):

- **trajectory instance**: source = `trajectory-field` role, `prediction_kind: continuous scores`,
  `value_range: [0, 1]`; target = Routebind's `target_trajectory` field, same `value_range`.
- **waypoint instance**: source = `waypoint-field` role, same `prediction_kind`/`value_range`;
  target = Routebind's `target_waypoint` field.

Both reuse the §5.1 position-slot correspondence unchanged (`p ↦ p`). Neither instance rescales,
thresholds, or otherwise transforms values beyond the identity copy `RasterFieldPredictionAdapter`
§3 defines.

### 5.4 What this binding must not do

Per `ADAPT-002` and both adapters' own §7: no part of this binding may consume the hidden semantic
graph, its binding, `optimal_cost`, `valid_route_count`, or any other privileged/withheld field
(`routebind.md` §4.3–4.5, §9.1) as model input. Scoring against the oracle route set happens
entirely in evaluation (§8 below), not inside either adapter.

## 6. Task-corpus requirement

This experiment declares a requirement for one committed `task:routebind/v1` corpus release built
over:

- **topology parent**: `dungeongen/v1`, variant `general` — same substrate choice and reasoning as
  `arena-tem/v1/plan.md` §6 (procedural, no external-source semantics).
- **observation-field parent**: `obsfield/v1`, variant `categorical-complete`, assignment protocol
  `categorical-random/v1` — same choice as `arena-tem/v1/plan.md` §6.
- **semantic-graph-source parent**: `dagflow/v1` — already `document_status: specified`, the only
  non-`draft` substrate in the catalogue. The explicit graph-node-to-observation binding protocol
  (`routebind.md` §6.5) is a corpus-profile choice, not fixed by this document — `routebind.md`
  §15 itself leaves this open.

Per `docs/docs/interfaces/python/experiments.md` § "Task-corpus requirements", this document
declares the requirement; it does not select a concrete local artifact.

## 7. Training protocol

- **Objective**: supervised regression loss (for example weighted MSE or BCE-style, an
  implementation choice not fixed here) between each predicted field ($\hat f_{\mathrm{traj}}$,
  $\hat f_{\mathrm{wp}}$, `routebind.md` §8.5) and its stored target (`target_trajectory`,
  `target_waypoint`) at every position.
- **Halting term**: HRM's supervised ACT halt/continue mechanism (`hrm.md` §1, §3) contributes its
  own supervised halting loss term, composed with the two field-regression losses. Composition
  weighting across three loss terms is an open issue (§9), not invented here.
- **Padding**: excluded from the loss when the corpus profile requires representation-only slots
  (§5.1), consistent with `raster-overlay-sequence-v1.md` `ROV-MAP-003`.
- Optimizer, learning rate, batch size, training duration, and relative loss weighting are outside
  both HRM (`hrm.md` §5) and this document's current scope.

## 8. Evaluation regimes and metrics

Named evaluation regimes and metrics are taken directly from `routebind.md` §13 and must not be
redefined here (`BIND-001`) — unlike `arena-tem/v1/plan.md`, no per-pathway metric specialization
is needed, since `routebind.md` §14's binding boundary is generic and does not anticipate
model-specific evaluation pathways the way `arena.md` did for TEM:

| Regime / metric                               | Source                                                                                                  |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `valid_semantic_spatial_route_rate` (primary) | `routebind.md` §13.1                                                                                    |
| Optimality ratio `ρ_cost`                     | `routebind.md` §13.2                                                                                    |
| Representational field-error diagnostics      | `routebind.md` §13.3 (secondary — a low field error does not by itself establish route validity, §13.4) |

This experiment's only addition is which decoded representation feeds these metrics: the §5.3
output-adapter product (two continuous fields in canonical position order), decoded into a route
by whatever deterministic decoding procedure the evaluation regime defines — that procedure itself
is an open issue (§9), since `routebind.md` §13.1's route-validity metric presumes a decoded route,
not a raw field, and this document does not yet fix the field-to-route decoding rule.

## 9. Status and prerequisites

This document records, rather than resolves, the following blockers:

- **The two adapters this binding depends on are themselves new and `draft`**:
  `raster-overlay-sequence-v1.md` and `raster-field-prediction-v1.md` were authored alongside this
  document in the same pass and have no independent implementation or validation history, unlike
  the four adapters the other three experiment specs reuse.
- **`dungeongen/v1` and `obsfield/v1` are still `draft`**, each with their own remaining open
  issues (generator dependency/reference protocol for DungeonGen; hex/finite-shape/enumeration,
  topology-to-ambient mapping, and vocabulary-identity contracts for ObsField) — not resolved by
  this document.
- **`routebind.md`'s own open issues** (§15): the first Routebind corpus must choose one explicit
  graph-node-to-observation binding protocol; the framework representation of a corpus-level
  semantic law sourced from an intrinsically split Dagflow artifact needs documenting in the
  corpus/profile specification; named corpus profiles must define actual cost/depth distributions.
- **The field-to-route decoding rule needed by §8's primary metric is not yet fixed** — this is a
  genuine gap this document surfaces rather than resolves: `routebind.md` §13.1 defines route
  validity over a _decoded route_, but this binding only produces continuous fields (§5.3). A
  deterministic decoding procedure (for example greedy field-guided search, or a declared
  threshold-and-trace rule) needs specifying before `valid_semantic_spatial_route_rate` is
  computable for this binding — likely evaluation-protocol content this document does not yet own
  a home for.
- **Training-protocol numeric defaults** (§7) are not yet fixed anywhere in the authority chain for
  this pairing.

## Related specifications

- [Routebind v1](../../../docs/docs/research/tasks/routebind.md)
- [HRM](../../../docs/docs/research/models/hrm.md)
- [Raster multi-channel overlay to sequence adapter v1](../../../docs/docs/framework/adapters/raster-overlay-sequence-v1.md)
- [Sequence to continuous raster field adapter v1](../../../docs/docs/framework/adapters/raster-field-prediction-v1.md)
- [Compatibility](../../../docs/docs/framework/compatibility.md)
- [Experiments](../../../docs/docs/interfaces/python/experiments.md)
- [DungeonGen v1](../../../docs/docs/research/substrates/dungeongen-v1.md)
- [ObsField v1](../../../docs/docs/research/substrates/obsfield-v1.md)
