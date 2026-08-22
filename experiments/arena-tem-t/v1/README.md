---
title: Arena–TEM-t v1
authority: descriptive
---

# Arena–TEM-t v1

This README is explanatory. The canonical concrete declaration is
[`experiment.toml`](experiment.toml); semantic authority for the selected components lives in the
Arena task specification, the TEM-t model specification, and the referenced adapter contracts.

## Purpose

`experiment:arena-tem-t/v1` is the Arena–TEM-t analogue of `experiment:arena-tem/v1`
([`experiments/arena-tem/v1`](../arena-tem/v1/README.md)): the same sequential-replay,
revisit-conditioned observation-prediction comparison, bound instead to TEM-t's
attention-over-prior-experience mechanism in place of TEM's conjunctive/associative-memory
mechanism. It tests whether the same environment-specific-recall behavioral claim holds under
`tem-t.md`'s reformulation.

It is a distinct experiment from `experiment:arena-tem/v1`: a model swap is a different experiment
(experiments `Semantic immutability`), not a specialization. It keeps the Arena task, the adapter
contracts, and the corpus identical to `arena-tem/v1` so results are comparable across the
TEM/TEM-t swap rather than confounded by a corpus difference.

## What is selected

- **Task:** `task:arena/v1` — sequential replay with revisit-conditioned observation prediction.
- **Model:** `model:tem-t/v1` — Transformer reformulation of TEM (attention over prior experience).
- **Input adapter:** `adapter:relational-sequence/v1` — exposes Arena replay `(observation, action)`
  to TEM-t's native sensory/relation inputs. Configuration is identical to the arena-tem binding,
  because TEM-t declares the same native inputs as TEM.
- **Output adapter:** `adapter:observation-prediction/v1` — maps each selected declared
  sensory-prediction role back to Arena observation-prediction form, `argmax` to the categorical
  label.
- **Sensory-prediction roles:** this binding probes TEM-t's attention mechanism through two
  candidate conditioning roles (structural-only and attention-recall). These roles are tentative
  binding-side reasoning; see [`design/prediction-pathways.md`](design/prediction-pathways.md).

## Corpus

A committed `task:arena/v1` corpus over `dungeongen/v1` (variant `general`) with
`obsfield/v1#categorical-complete` and assignment `categorical-random/v1` — held identical to
`arena-tem/v1`.

This is the shared scientific data-preparation control for the arena-tem / arena-tem-t model swap:
`arena-tem-t/v1` deliberately selects the same Arena corpus as `arena-tem/v1` so the TEM/TEM-t
comparison is not confounded by a corpus difference. The `[corpus]` block here records that the
D1 / D2 / T1 preparation selection is identical to `experiments/arena-tem/v1/experiment.toml`, and
refers to that block as the full preparation specification. The equality is a scientific control
made visible in each experiment's own declaration, not a separate semantic owner.

## Status

`experiment.toml` declares the composition. No construction or execution exists yet; component
specifications (TEM-t, Arena, substrates) remain partly `draft`. The two-pathway taxonomy is new,
undocumented ground with no repository precedent. See [`design/`](design/) for temporary design
reasoning and unresolved questions.
