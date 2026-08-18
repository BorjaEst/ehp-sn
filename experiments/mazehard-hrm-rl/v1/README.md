---
title: MazeHard–HRM-rl v1
authority: descriptive
---

# MazeHard–HRM-rl v1

This README is explanatory. The canonical concrete declaration is
[`experiment.toml`](experiment.toml); semantic authority for the selected components lives in the
MazeHard task specification, the HRM-rl model specification, and the referenced adapter contracts.
Unresolved design reasoning — in particular the spec-pending deliberation controller and RL
objective — lives in [`design/controller-and-rl.md`](design/controller-and-rl.md).

## Purpose

`experiment:mazehard-hrm-rl/v1` tests whether HRM's hierarchical PFC reasoning core, when its
halting deliberation is controlled by action-value-based reinforcement learning (`hrm-rl.md` § 1)
rather than supervised ACT classification, still solves fully observed MazeHard shortest-route
problems whose correctness depends on long-range connectivity (`mazehard.md` § 1.2–1.3), evaluated
at the same exact-reference, structural-optimality, and token granularity (`mazehard.md` § 13).

It is the RL-control counterpart to `experiment:mazehard-hrm/v1`, which uses the supervised halting
mechanism of `model:hrm/v1`. The two are distinct canonical identities with distinct control
semantics; neither is a specialization of the other. This document does not speak to
`mazehard-hrm/v1`.

## What is selected

- **Task:** `task:mazehard/v1` — a fully observed static shortest-route prediction task over
  finite raster maze topologies.
- **Model:** `model:hrm-rl/v1` — HRM with reinforcement-learned deliberation control; a PFC+
  STR architecture whose stable native outputs include `q_values` and `state_value` alongside
  `theta_summary` and `schema_slots` (`hrm-rl.md` § 1–3).
- **Input adapter:** `adapter:raster-sequence/v1` — exposes MazeHard's categorical per-position
  field to HRM-rl's ordered native slot sequence (`S = P = 900` at the reference profile), with a
  `reset` at problem start.
- **Output adapter:** `adapter:raster-prediction/v1` — maps the binding's decoder over HRM-rl's
  native `schema_slots` back to MazeHard's per-position path label, `argmax` to the categorical
  label.
- **Decoder:** a binding-owned decoder over HRM-rl's `schema_slots` (`hrm-rl.md` § 8: task-specific
  decoding from HRM-rl native representations is binding-owned). It reads `schema_slots` — not
  `theta_summary`, `q_values`, or `state_value`, the latter two feeding the controller rather than
  route prediction. See [`design/controller-and-rl.md`](design/controller-and-rl.md) for the
  candidate rationale.
- **Deliberation controller:** this experiment _selects_ the reusable deliberation controller that
  governs `halt`/`continue` from `q_values`/`state_value` (`hrm-rl.md` § 8). Its specification is
  **missing** (ARCH-014/ARCH-016, `hrm-rl.md` § 8); this experiment composes it by reference and
  does not invent its contract. See the design note.
- **RL objective:** this experiment _selects_ the reusable RL objective owning reward
  interpretation, discounting, TD targets, Q/value losses, warm-up, and optimizer policy
  (`hrm-rl.md` § 8). Its specification is likewise **missing**; this experiment composes it by
  reference and does not invent its contract. See the design note.

## Corpus

A committed `task:mazehard/v1` corpus over one `maze-nd/v1` source-topology release, at the
canonical reference-reproduction profile (`30 × 30`, `P = 900`; `mazehard.md` § 9.2).

## Status

`experiment.toml` declares the composition and the hybrid (supervised route + RL-control) objective.
No construction or execution exists yet; component specifications (MazeHard, HRM-rl, Maze-ND) remain
partly `draft`, and the deliberation controller and RL objective specifications are not yet written
(ARCH-016). See [`design/`](design/) for temporary design reasoning and unresolved questions.
