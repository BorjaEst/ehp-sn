---
title: Arena–TEM v1
authority: descriptive
---

# Arena–TEM v1

This README is explanatory. The canonical concrete declaration is
[`experiment.toml`](experiment.toml); semantic authority for the selected components lives in the
Arena task specification, the TEM model specification, and the referenced adapter contracts.

## Purpose

`experiment:arena-tem/v1` reproduces, within EHP-SN, the TEM environment-specific-memory comparison
`arena.md` §1.1 describes as its "reference Arena–TEM evaluation": whether a recurrent
relational-memory model can acquire structured, environment-specific state from sequential
experience and use it to predict observations at revisited positions, with different model
sensory-prediction roles probing different degrees of reliance on acquired state versus the current
sensory observation.

## What is selected

- **Task:** `task:arena/v1` — sequential replay with revisit-conditioned observation prediction.
- **Model:** `model:tem/v1` — Tolman–Eichenbaum Machine.
- **Input adapter:** `adapter:relational-sequence/v1` — exposes Arena replay `(observation, action)`
  to TEM's native sensory/relation inputs.
- **Output adapter:** `adapter:observation-prediction/v1` — maps TEM's declared sensory-prediction
  roles back to Arena observation-prediction form, `argmax` to the categorical label.
- **Sensory-prediction roles:** this experiment selects TEM's declared sensory-prediction output
  roles (posterior, sensory-recall, structural-prior/path-integration); it does not define them.

## Corpus

A committed `task:arena/v1` corpus over `dungeongen/v1` (variant `general`) with
`obsfield/v1#categorical-complete` and assignment `categorical-random/v1`.

## Status

`experiment.toml` declares the composition. No construction or execution exists yet; component
specifications (TEM, Arena, substrates) remain partly `draft`. See [`design/`](design/) for
temporary design reasoning and unresolved questions.
