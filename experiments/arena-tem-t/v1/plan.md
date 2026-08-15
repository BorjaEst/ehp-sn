---
title: Arena-TEM-t v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

## Normative summary

`experiment:arena-tem-t/v1` is the resolved scientific composition of the `task:arena/v1` task and
the `model:tem-t/v1` model: the same sequential-replay, revisit-conditioned observation-prediction
experiment as `experiment:arena-tem/v1` (`experiments/arena-tem/v1/plan.md`), bound instead to
TEM-t's attention-over-prior-experience mechanism in place of TEM's conjunctive/associative-memory
mechanism.

Unlike `arena-tem`, no part of this binding has any existing repository precedent: no adapter
worked example, CLI reference, or `arena.md`/`tem-t.md` clause names an Arena–TEM-t pathway split.
This document is where that split is first declared.

This document is `draft` for the same upstream reasons as `arena-tem/v1/plan.md` (§9 there), plus
the fact that its own central content — the pathway taxonomy — is new, undocumented ground.

## 1. Purpose

Same scientific question as `arena-tem/v1/plan.md` §1 (`arena.md` §1.2: environment-specific
recall from sequential experience, probed via revisit-conditioned observation prediction), bound to
a Transformer-attention memory mechanism instead of TEM's original mechanism, to test whether the
same behavioral claim holds under `tem-t.md`'s reformulation.

## 2. Scope and ownership

### 2.1 Owned by this document

Same categories as `arena-tem/v1/plan.md` §2.1, substituting `model:tem-t/v1` for `model:tem/v1`
throughout, plus: the Arena–TEM-t pathway taxonomy (§5.2 below) — genuinely new content with no
Arena or TEM-t precedent to select among, unlike `arena-tem`'s pathways which `arena.md` already
named.

### 2.2 Not owned by this document (`BIND-001`)

Identical to `arena-tem/v1/plan.md` §2.2: this document must not change Arena's public/withheld
split, task truth, target meaning, split meaning, or `A_obs^rev`/secondary metric meaning.

### 2.3 Authoritative dependencies

Identical to `arena-tem/v1/plan.md` §2.3, with `docs/docs/research/models/tem-t.md` in place of
`tem.md` as model semantics.

## 3. Identity

| Property                 | Value                       |
| ------------------------ | --------------------------- |
| Canonical experiment ref | `experiment:arena-tem-t/v1` |
| Task ref                 | `task:arena/v1`             |
| Model ref                | `model:tem-t/v1`            |

Distinct canonical identity from `experiment:arena-tem/v1` — not a specialization of it
(`experiments.md` § "Semantic immutability": a model swap is a different experiment).

## 4. Compatibility declaration

```yaml
task: task:arena/v1
model: model:tem-t/v1
support: supported
compatibility_maturity: declared
```

Same rationale as `arena-tem/v1/plan.md` §4: no construction or execution exists yet.

## 5. Binding: adapter configuration

### 5.1 Input side — `RelationalSequenceAdapter` (`relational-sequence-v1`)

Identical configuration to `arena-tem/v1/plan.md` §5.1: TEM-t declares the same native inputs
(`sensory_id`, `relation_id`, `reset`, `sequence_mask`; `tem-t.md` §3) as TEM, so the adapter's
resolved configuration — step-identity-preserving `t ↦ t`, injective observation/relation
mappings, reset emitted at step 0 — carries over unchanged. Not re-derived here.

### 5.2 Prediction pathways — TEM-t native output to task-prediction interface

Neither `arena.md` nor `tem-t.md` names an Arena–TEM-t pathway split. This document declares one,
grounded in `tem-t.md`'s own architecture and 8-step schedule (§4: reset → encode sensory+relation
→ update `g_t` → construct query `q_t` → select eligible `K_<t`/`V_<t` → attend → predict → insert
current experience for later steps).

**Why two pathways, not three:** TEM's three-way split (§5.2 of `arena-tem/v1/plan.md`) exploits a
real architectural seam TEM has and TEM-t does not: TEM separates a conjunctive representation
`p_t` (structure + sensory, pre-memory) from a subsequent associative-memory read, so a
prior/posterior/recall trichotomy has three distinct representations to attach to. TEM-t's
architecture diagram (`tem-t.md` normative summary) constructs the attention query directly from "relation-dependent
structural state + sensory/content state" as one combined step feeding one retrieval mechanism
(attention over `K_<t`/`V_<t`) — there is no second, separate memory-read stage to distinguish a
`posterior` role from a `sensory-recall` role. The only architecturally meaningful seam is whether
the query incorporates current sensory evidence (`x_t`) at all.

| Pathway            | `prediction_conditioning`                                                                                                                                                            | Current observation access                                                                                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `structural-only`  | query `q_t` constructed from `g_t` alone (excluding `x_t`), attends over eligible `K_<t`/`V_<t`                                                                                      | none — the query itself excludes current sensory evidence, the TEM-t analogue of `structural-prior/path-integration`                                                         |
| `attention-recall` | query `q_t` constructed from `g_t` and `x_t` together (the architecture's default per `tem-t.md`'s normative summary), attends over eligible `K_<t`/`V_<t`, subject to `tem-t.md`'s anti-leakage rule | yes — the current step's own experience is inserted into memory only at schedule step 8, strictly after this step's retrieval (step 6), so no leakage occurs within one step |

Both roles are declared TEM-t outputs, not adapter- or binding-computed (`tem-t.md` §8: bindings
"must not construct relational state, attention memory, or associative retrieval").
`prediction_timing = current_step` for both, matching Arena's target timing requirement
(`observation-prediction-v1.md` §2.2).

### 5.3 Output side — `ObservationPredictionAdapter` (`observation-prediction-v1`)

Same configuration shape as `arena-tem/v1/plan.md` §5.3, applied independently to the two §5.2
pathways: source `prediction_kind: categorical scores`, step correspondence reused unchanged from
§5.1, `argmax` score-to-label conversion against Arena's single-label target `y_t^* = o_t`.

### 5.4 What this binding must not do

Same as `arena-tem/v1/plan.md` §5.4: no privileged/withheld Arena field (`is_revisit`,
`trajectory_position`) may reach model input; the `structural-only` pathway's current-observation
exclusion is enforced by the query-construction declaration in §5.2, not by an adapter withholding
data the model otherwise received; scoring happens entirely in evaluation (§8), not in either
adapter.

## 6. Task-corpus requirement

Identical to `arena-tem/v1/plan.md` §6: `dungeongen/v1` (variant `general`) as topology parent,
`obsfield/v1` (variant `categorical-complete`, `categorical-random/v1` protocol) as
observation-field parent — held identical across both bindings deliberately, so results are
comparable across the TEM/TEM-t model swap rather than confounded by a corpus difference. Not
re-derived here.

## 7. Training protocol

- **Objective**: supervised cross-entropy between each pathway's predicted observation
  distribution and `y_t^* = o_t`, same shape as `arena-tem/v1/plan.md` §7.
- **Reset/memory-scope alignment**: governed by `tem-t.md`'s reset semantics ("a reset initializes
  both structural state and sequence-scoped attention memory," §4) and Arena's `episode_start`;
  per `arena.md` §14 this belongs to the experiment's training protocol, not fixed further here.
- **Padding**: excluded from the loss, consistent with `relational-sequence-v1.md` `SIN-MAP-004`.
- Optimizer, learning rate, batch size, training duration, and pathway-loss weighting are open
  issues, not invented here, same as `arena-tem/v1/plan.md` §7.

## 8. Evaluation regimes and metrics

`arena.md` §13's primary/secondary metrics apply unmodified (`BIND-001`), identical to
`arena-tem/v1/plan.md` §8.

This binding's addition — new metric names, deliberately distinct from `arena-tem`'s `A_post` /
`A_rec^rev` / `A_PI^rev`, since those denote TEM's specific mechanism and reusing them here would
misattribute a different computation to the same name:

| Metric         | Definition                                                                                |
| -------------- | ----------------------------------------------------------------------------------------- |
| `A_struct^rev` | `A_obs^rev` (`arena.md` §13.1), computed over the `structural-only` pathway's predictions |
| `A_attn^rev`   | `A_obs^rev`, computed over the `attention-recall` pathway's predictions                   |

Same aggregation rule (`arena.md` §13.3) and same undefined-for-zero-revisit reporting requirement.

## 9. Status and prerequisites

Everything in `arena-tem/v1/plan.md` §9 applies identically (`dungeongen/v1` and `obsfield/v1`
still `draft` with their own remaining open issues, though the shared `raster-topology/v1` /
`categorical-field/v1` / `ambient-domain/v1` framework-contract blocker they both depended on has
since been promoted to `specified`; Arena's own deferred split/novelty policy; unfixed training
numeric defaults) — not restated here.

Additionally, specific to this document:

- **The §5.2 pathway taxonomy is new, undocumented ground with no repository precedent** — no
  adapter example, no `arena.md` clause, no `tem-t.md` clause anticipates it, unlike `arena-tem`'s
  pathways which `arena.md` §1.1/§14 already named. If implementation reveals a better split (for
  example, if TEM-t's actual attention mechanism supports a third distinguishable role this
  document's reading of `tem-t.md`'s architecture diagram did not anticipate), that is a design
  revision to _this_ document, not evidence it was wrong to attempt a taxonomy before
  implementation existed.
- **The two-pathway-vs-three-pathway architectural argument in §5.2** is this document's own
  reasoning from `tem-t.md`'s architecture description, not a restatement of settled authority —
  `tem-t.md` does not itself state that it supports only two prediction pathways.

## Related specifications

- [Arena v1](../../../docs/docs/research/tasks/arena.md)
- [TEM-t](../../../docs/docs/research/models/tem-t.md)
- [Arena-TEM v1](../../arena-tem/v1/plan.md)
- [Observation-relation sequence to sensory-relation sequence adapter v1](../../../docs/docs/framework/adapters/relational-sequence-v1.md)
- [Sensory-prediction sequence to observation sequence adapter v1](../../../docs/docs/framework/adapters/observation-prediction-v1.md)
- [Compatibility](../../../docs/docs/framework/compatibility.md)
- [Experiments](../../../docs/docs/interfaces/python/experiments.md)
- [DungeonGen v1](../../../docs/docs/research/substrates/dungeongen-v1.md)
- [ObsField v1](../../../docs/docs/research/substrates/obsfield-v1.md)
