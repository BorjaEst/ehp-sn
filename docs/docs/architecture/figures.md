---
title: Figures architecture
authority: descriptive
document_status: specified
---

# Figures architecture

Figures are a cross-cutting scientific-visualization capability used by the existing EHP-SN operations.

They are not an additional scientific lifecycle stage.

```text
data
  ↓
tasks
  ↓
train
  ↓
evaluate
  ↓
analyze
  ↓
report
```

Figure use appears inside those operations where visual communication is useful:

```text
data inspect
tasks inspect
training telemetry
evaluation diagnostics
scientific analysis
report generation
explicit export
Python / notebook exploration
```

The repository-wide requirements are `FIG-001` through `FIG-004` in `docs/invariants.md`.
This page explains the architecture; it does not replace those invariants or the normative framework specifications under [`framework/figures/`](../framework/figures/index.md).

## Scientific boundary

The direction of authority is:

```text
scientific computation
        ↓
authoritative scientific result
        ↓
figure projection
        ↓
visual realization
```

A figure may select, align, structure, encode, render, serialize, and deliver already-authoritative information.

A figure does not establish a new authoritative scientific result.
Model inference, scientific metric calculation, statistical estimation, probe fitting, and hypothesis testing remain owned by the scientific operation that produces the result.

This is a semantic boundary rather than a cost boundary.
An expensive restructuring step may still be figure preparation when it changes no scientific conclusion.
A cheap calculation does not belong in figure code when its output is independently scientific evidence.

## Three semantic placement levels

Figure meaning follows the ordinary EHP-SN ownership model.

```text
ehp_sn.figures
    generic figure mechanics

ehp_research.figures
    reusable scientific figure meaning

experiments/<experiment>/vN/
    joint figure meaning that depends on one experiment composition
```

Framework code may understand concepts such as figure requests, projections, panels, layouts, render profiles, and serialization.

Framework code must not understand research concepts such as TEM, HRM, Arena, MazeHard, place cells, gridness, revisits, or deliberation.

Reusable scientific figures belong to `ehp_research` when their meaning survives independently of one concrete experiment.

A visualization whose meaning depends jointly on a concrete task-model composition belongs to that experiment.
The admitted normative specification root for such figure semantics is `experiments/<experiment>/vN/figures/`; that documentation location does not create runtime filesystem discovery.

## End-to-end flow

The scientific view is fixed before presentation.

```text
authoritative source(s)
        ↓
semantic role bindings
        ↓
input-contract validation
        ↓
authored selection
        ↓
resolved exact selection
        ↓
prepare()
        ↓
provider-defined prepared view
        ↓
FigureProjection
        │
════════╪════════════════════════════
        │ scientific view fixed
        ▼
scientific visual semantics
        ↓
PanelSpecs
        ↓
FigureLayout + explicit bindings
        ↓
Matplotlib Figure / Axes / Artists
        ↓
interactive realization
        or
serialization
        ↓
parent-operation destination
```

The normative projection semantics are defined in [`projection.md`](../framework/figures/projection.md).
Scientific visual encoding is defined in [`visual-semantics.md`](../framework/figures/visual-semantics.md).
Top-level panel placement is defined in [`layout.md`](../framework/figures/layout.md).
Presentation and Matplotlib realization are defined in [`rendering.md`](../framework/figures/rendering.md).
Parent-operation integration is defined in [`integration.md`](../framework/figures/integration.md).

## Projection and realization

A `FigureProjection` identifies the exact scientific view before presentation.

Changing any of the following changes the projection when the value is projection-semantic:

```text
authoritative source
selection policy
selection parameters
resolved selected entities
preparation semantics
semantic preparation parameters
```

Changing presentation does not change the projection:

```text
panel placement
physical width
typography
DPI
serialization format
```

The distinction allows one scientific view to be reused across notebook inspection, telemetry, analysis resources, and publication rendering without pretending that each visual realization is a different scientific result.

## Scientific visual semantics

After projection, the scientific owner decides how the selected information is communicated graphically.

Examples include:

```text
signed error uses a zero-centred diverging mapping
truth and prediction share one quantitative normalization
trajectory identity is shown as line plus start/goal semantics
categorical identity remains consistent across panels
```

Those decisions belong to the figure's visual semantics.

They are distinct from presentation choices such as page width, font family, DPI, margins, and export format.

## Panels and layout

A `PanelSpec` identifies a meaningful top-level visual sub-objective such as:

```text
population
coverage
examples
problem
prediction
reasoning
```

A `FigureLayout` identifies reusable top-level structural regions such as:

```text
primary
secondary
detail
```

The binding is explicit:

```text
population → primary
coverage   → secondary
examples   → detail
```

A panel is not inherently one Matplotlib `Axes`.
One panel may use one axes, multiple axes, a nested `GridSpec`, a table, text, an image, or another suitable realization.

Internal panel layout remains local to the scientific renderer until repeated implementations demonstrate a reusable framework need.

## Matplotlib boundary

EHP-SN does not define a backend-neutral graphics object model.

The path is:

```text
FigureProjection
        ↓
scientific visual semantics
        ↓
layout regions
        ↓
Matplotlib Figure / Axes / Artists
```

Generic Matplotlib helpers may exist for domain-neutral plotting operations, but helpers are libraries rather than new semantic contracts.

The reason the boundary is direct Matplotlib — with no backend-neutral graphics IR — is stated in the rendering specification ([`rendering.md`](../framework/figures/rendering.md)).

## Presentation and serialization

A `RenderProfile` owns non-scientific presentation policy such as physical size, spacing, typography, line defaults, marker defaults, panel-label presentation, accessibility constraints, and venue constraints.

Serialization is a separate realization concern.
A serialization request identifies a format such as PNG, SVG, or PDF together with any realization-affecting serialization parameters.

A mutable `matplotlib.figure.Figure` is normally transient.
Serialized output may be persisted by the requesting operation through the ordinary EHP-SN resource and artifact mechanisms.

## Parent-operation ownership

The figure service does not own when figures run.

The parent operation owns:

```text
diagnostic inference
scheduling
queueing and backpressure
requiredness
failure policy
artifact lifecycle
destination
```

For training, live model state is not exposed to figure code.
The training runtime performs any declared diagnostic inference or capture and hands a stable detached result into the ordinary figure path.

Reports may rerender an existing scientific projection, or reproduce an equivalent projection from committed authoritative sources, but they may not perform new scientific analysis.

## Major non-goals

The figure capability does not introduce:

```text
a figure lifecycle
FigureArtifact as a universal artifact kind
FigureSchedule
FigureComposition
a backend-neutral graphics IR
an EHP Artist hierarchy
a universal scientific selection language
a universal FigureData base class
a parallel figure resource hierarchy
```

Any future addition requires a demonstrated generic requirement rather than symmetry with the rest of the design.
