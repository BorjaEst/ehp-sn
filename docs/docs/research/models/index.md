---
title: Research models
authority: descriptive
document_status: draft
---

# Research models

This section holds background documentation for published model architectures the project is
interested in experimenting with. Each page summarizes one model's origin, the computational
idea it contributes, and how it relates to the other models documented here.

These pages are descriptive. They ground later work in a citable source and a shared
understanding of what each architecture claims, but they do not define:

- how a model binds to a task's public, target, or withheld information;
- a model's concrete tensor interface, parameterization, or training procedure;
- a canonical component identity or version for the model;
- the generic framework contract a model implementation would conform to.

Each model page covers:

- **Overview** — what the model is and why it is relevant here.
- **Origin** — the paper or source it is grounded in, with its `references.bib` citation key.
- **Core idea** — the computational mechanism, described self-containedly.
- **Relation to other models here** — how it connects to the other entries in this catalogue.
- **Related work** — adjacent papers worth knowing about, noted but not incorporated into the
  model's own description.
- **Notes for this project** — why the model is of interest, without committing to how or
  whether it will be integrated.

## Current catalogue

| Model | Origin | Status |
| ----- | ------ | ------ |
| [TEM](tem.md) | Whittington et al., "The Tolman-Eichenbaum Machine" (2020) | Written |
| [TEM-t](tem-t.md) | Whittington, Warren & Behrens, "Relating transformers to models and neural representations of the hippocampal formation" (2022) | Written |
| [HRM](hrm.md) | Wang et al., "Hierarchical Reasoning Model" (2025) | Written |
| HRM-rl | Hierarchical Reasoning Model with RL-trained halting | Planned, not yet written |
| EHP | Entorhinal Hippocampal Prefrontal — this project's own integrated model | Planned, not yet written |

Further models will be added here as they are written.

## Related specifications

- [Research](../index.md)
