---
title: Routebind–HRM v1
authority: descriptive
---

# Routebind–HRM v1

This README is explanatory. The canonical concrete declaration is
[`experiment.toml`](experiment.toml); semantic authority for the selected components lives in the
Routebind task specification, the HRM model specification, and the referenced adapter contracts.

## Purpose

`experiment:routebind-hrm/v1` tests whether HRM's hierarchical latent-reasoning core can combine
fully observed spatial structure with a corpus-stable but unobserved semantic transition law
(`task:routebind/v1`) learned parametrically across corpus cases (`routebind.md` § 1.2), evaluated
primarily on behavioral route validity (`valid_semantic_spatial_route_rate`) and secondarily on
physical-cost optimality, rather than on field-similarity alone (`routebind.md` § 13.4).

`hrm.md` § 8 and `docs/docs/interfaces/cli/index.md` already name `experiment:routebind-hrm/v1` as
a canonical worked example; this directory provides that example's declaration.

## What is selected

- **Task:** `task:routebind/v1` — a fully observed spatial–semantic prospective routing task:
  visible topology and observations, hidden semantic transition law.
- **Model:** `model:hrm/v1` — the Hierarchical Reasoning Model (HRM), a latent recurrent
  reasoning core. `model:hrm-rl/v1` is a distinct model (reinforcement-learned deliberation
  control) and out of scope here.
- **Input adapter:** `adapter:raster-overlay-sequence/v1` — exposes Routebind's four public
  per-position channels (traversability, observation identity, `start_flag`, `goal_flag`) as one
  combined categorical sequence to HRM's ordered native slot sequence (`S = P` at the reference
  profile).
- **Output adapter:** `adapter:raster-field-prediction/v1` — two independent instances map the
  binding's decoder over HRM's native `schema_slots` back to Routebind's two continuous target
  fields, one per field: `target_trajectory` and `target_waypoint` (`routebind.md` § 8.5), value
  range `[0, 1]`, identity copy.
- **Decoder:** a binding-owned decoder over HRM's `schema_slots` (`hrm.md` § 8: task-specific
  decoding from HRM native representations is binding-owned). It reads `schema_slots` — not
  `theta_summary` — since per-position field prediction needs `P` independent outputs, and declares
  an explicit `slot_preservation` guarantee. See
  [`design/adapters.md`](design/adapters.md) for the candidate rationale and the open review point
  on where the decoder's slot-preservation role belongs.

## Corpus

A committed `task:routebind/v1` corpus built over `dungeongen/v1` (variant `general`) with
`obsfield/v1#categorical-complete` and assignment `categorical-random/v1`, and a
`specific`-status `dagflow/v1` semantic-graph source. The explicit graph-node-to-observation
binding protocol is left open (`routebind.md` § 15).

## Status

`experiment.toml` declares the composition. No construction or execution exists yet; component
specifications (Routebind, HRM, the two raster adapter contracts, DungeonGen, ObsField) remain
partly `draft`. See [`design/`](design/) for temporary design reasoning and unresolved questions.
