---
title: Figures
authority: descriptive
document_status: specified
---

# Figures

The figure framework provides generic mechanics for selecting an exact scientific view and realizing it visually without creating new scientific results.

Figures are cross-cutting.
They are requested by the existing EHP-SN operations rather than forming an independent lifecycle.

Repository-wide figure invariants are `FIG-001` through `FIG-004` in `docs/invariants.md`.

## Specification map

The normative framework is split by responsibility:

- [`core.md`](core.md) — `FigureSpec`, provider/catalogue participation, request partition, and framework non-targets.
- [`projection.md`](projection.md) — source roles, input contracts, selection, preparation, `FigureProjection`, and projection identity.
- [`visual-semantics.md`](visual-semantics.md) — `PanelSpec`, scientific graphical meaning, shared quantitative mappings, and figure-level visual coordination.
- [`layout.md`](layout.md) — `FigureLayout`, `PanelSlot`, explicit panel-slot binding, and top-level layout compilation.
- [`rendering.md`](rendering.md) — `RenderProfile`, Matplotlib realization, serialization, realization identity, and rendering-environment provenance.
- [`integration.md`](integration.md) — parent-operation boundary, training telemetry hand-off, persistence ownership, reporting, and notebook equivalence.

The architecture overview is [`architecture/figures.md`](../../architecture/figures.md).

## Conceptual pipeline

```text
authoritative sources
        ↓
semantic role bindings
        ↓
FigureInputContract
        ↓
FigureSelection
        ↓
ResolvedFigureSelection
        ↓
prepare()
        ↓
FigureProjection
        ↓
scientific visual semantics
        ↓
PanelSpecs
        ↓
FigureLayout + panel-slot binding
        ↓
Matplotlib realization
        ↓
interactive output or serialization
        ↓
parent-operation destination
```

## Maturity

The framework specifications are currently specified targets with planned capability status.

They define the intended semantic boundary before the first validated vertical implementation.
They must be revised if the HPC place-summary slice demonstrates that a proposed framework abstraction is unnecessary or insufficient.

A conceptual architectural term does not automatically require a stable public Python class.

## Non-goals

The current framework deliberately does not define:

```text
a figure lifecycle
FigureArtifact
FigureSchedule
FigureComposition
a backend-neutral graphics IR
a universal selection DSL
a universal FigureData superclass
a parallel figure resource system
```

## Downstream scientific figures

Reusable scientific figure semantics belong under `docs/docs/research/figures/` when such specifications exist.

Experiment-joint figure semantics may be normative under `experiments/<experiment>/vN/figures/`.
That repository-authoritative root is outside the normal MkDocs publication tree unless the documentation build explicitly projects it.

Neither documentation location defines runtime discovery.
