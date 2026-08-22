---
title: MazeHard–HRM v1
authority: descriptive
---

# MazeHard–HRM v1

This README is explanatory. The canonical concrete declaration is
[`experiment.toml`](experiment.toml); semantic authority for the selected components lives in the
MazeHard task specification, the HRM model specification, and the referenced adapter contracts.

## Purpose

`experiment:mazehard-hrm/v1` reproduces, within EHP-SN, the HRM/MazeHard global-spatial-reasoning
comparison described by `docs/docs/research/tasks/mazehard.md` § 1.2–1.3: whether HRM's
hierarchical latent-reasoning core can solve fully observed shortest-route problems whose
correctness depends on long-range connectivity, evaluated at both exact-reference and
structural-optimality granularity (`mazehard.md` § 13).

It is one of two bindings HRM participates in. `hrm.md` § 8 lists Routebind–HRM as a separate
neighboring binding; this document does not speak to it.

## What is selected

- **Task:** `task:mazehard/v1` — a fully observed static shortest-route prediction task over
  finite raster maze topologies.
- **Model:** `model:hrm/v1` — the Hierarchical Reasoning Model (HRM), a latent recurrent
  reasoning core.
- **Input adapter:** `adapter:raster-sequence/v1` — exposes MazeHard's categorical per-position
  field to HRM's ordered native slot sequence.
- **Output adapter:** `adapter:raster-prediction/v1` — maps the binding's decoder over HRM's
  native `schema_slots` back to MazeHard's per-position path label, `argmax` to the categorical
  label.
- **Decoder:** a binding-owned decoder over HRM's `schema_slots` (hrm.md § 8: task-specific
  decoding from HRM native representations is binding-owned). It is assembled here and projects
  each schema slot to MazeHard's target vocabulary with an explicit `slot_preservation` guarantee.
  See [`design/output-decoding.md`](design/output-decoding.md) for the candidate rationale and
  the open review point on where the decoder's slot-preservation role belongs.

## Corpus

A committed `task:mazehard/v1` corpus over one `maze-nd/v1` source-topology release, at the
canonical reference-reproduction profile (`30 × 30`, `P = 900`; `mazehard.md` § 9.2).

This is the **shared scientific data-preparation control** for the mazehard-hrm / mazehard-hrm-rl
control-semantics swap. `mazehard-hrm-rl/v1` selects the same MazeHard corpus definition
intentionally, so the HRM/HRM-rl comparison (supervised vs RL deliberation control) is not
confounded by a corpus difference. The control-semantics swap is the _only_ scientific difference
between the two.

The upstream preparation DAG is:

```text
D3 maze-nd/v1#source-topology → T2 task:mazehard/v1 corpus → [mazehard-hrm, mazehard-hrm-rl]
```

The `[corpus]` block in `experiment.toml` records the exact selection-level build requirements each
preparation target needs (D3 Maze-ND, T2 MazeHard corpus), referencing research-owned definitions by
canonical reference and identifying the unresolved research/framework gaps (notably the Maze-ND
authoritative source, connectivity and selection policies, and the MazeHard admission profile) that
must be fixed before Phase 2. It does not redefine substrate, task, or framework semantics
(`ARCH-002`).

## Status

`experiment.toml` declares the composition. No construction or execution exists yet; component
specifications (MazeHard, HRM, Maze-ND) remain partly `draft`. See [`design/`](design/) for
temporary design reasoning and unresolved questions.
