---
title: Figure visual semantics
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Figure visual semantics

This specification defines the scientific meaning of a graphical realization after a `FigureProjection` has fixed the scientific view.

It does not define scientific selection, top-level physical presentation policy, serialization, or parent-operation scheduling.

## Visual-semantics boundary

Scientific visual semantics answer:

> How should the already-selected authoritative information be encoded so that the intended scientific meaning is communicated correctly?

Examples include:

```text
signed error centred on zero
truth and prediction using one comparable quantitative mapping
trajectory represented with start and goal semantics
categorical identity mapped consistently across panels
```

These are not merely style choices.
Changing them can change the scientific interpretation of the visualization.

Presentation choices such as font family, physical width, DPI, and non-semantic line defaults belong to `RenderProfile`.

## Visual-semantics identity

Every versioned figure definition identifies its visual-semantics version independently from its projection-semantics version.

A visual-semantics change is one that changes the scientific meaning of the graphical encoding while leaving the underlying `FigureProjection` unchanged.

Examples include:

```text
independent normalization → shared quantitative normalization
unsigned magnitude → signed zero-centred mapping
category identity encoded inconsistently → one stable category mapping
```

A mere panel relocation, typography change, DPI change, or serialization-format change is not a visual-semantics change.

A line-style change is semantic only when line style itself encodes scientific meaning.
Otherwise it is presentation policy.

## `PanelSpec`

A `PanelSpec` identifies one stable top-level scientific or communication sub-objective within the figure.

It contains at least:

```text
semantic key
purpose
```

Suitable semantic keys include:

```text
population
coverage
examples
problem
prediction
reasoning
```

Keys such as `a`, `b`, or `c` are presentation labels rather than scientific panel identities.

A `PanelSpec` does not require a public panel-renderer abstraction.
Provider-private functions may render a panel as an implementation detail.

## Panel and axes are different concepts

A panel is a semantic visual unit.

One panel may contain:

```text
one plot
multiple plots
table
text
image
schematic
local guides
annotations
nested layout
```

A panel is therefore not inherently one Matplotlib `Axes`.

Visible panel labels such as `(a)`, `(b)`, and `(c)` are presentation concerns and do not define `PanelSpec` identity.

## Figure-level visual coordination

One figure-level visual authority coordinates cross-panel scientific semantics.

It may establish:

```text
shared normalization
shared categorical mapping
shared scientific scales
figure-level legends or colorbars
cross-panel annotations
scientifically meaningful ordering
```

It may delegate local rendering to provider-private helpers after the shared visual state is established.

This avoids two competing authorities:

```text
figure-level shared semantics
panel-local rendering
```

The panel helper consumes the coordinated semantics; it does not silently redefine them.

## Shared quantitative mappings

A shared colorbar alone does not establish quantitative comparability.

Panels declared quantitatively comparable must share the actual scientific mapping semantics, including every applicable part of:

```text
domain
normalization
colormap meaning
category mapping
```

Where practical, implementations should pass the same resolved normalization/mapping object to all comparable panel renderers rather than reconstructing independent look-alikes.

## Scientifically meaningful transformations

A display transformation belongs here when it changes only how an authoritative value is visually expressed.

Examples may include:

```text
interpolation used only for raster display
visual clipping with explicitly declared display bounds
zero-centred normalization for signed values
```

A transformation belongs upstream in analysis when it estimates or establishes a new scientific quantity.

Borderline operations such as smoothing, thresholding, interpolation, normalization, or binning are classified by purpose, not by operation name.

Scientific display transformations must be explicit in the visual-semantics contract.
They must not be hidden inside generic plotting helpers.

## Visual authority precedence

Three sources may contribute graphical defaults:

```text
plotting/style helper defaults
RenderProfile presentation defaults
explicit scientific visual semantics
```

Their authority order is:

```text
helper defaults
        ↓
RenderProfile
        ↓
explicit scientific visual semantics
```

A lower authority must not silently override a higher one.

A `RenderProfile` or venue constraint may reject a realization that violates an accessibility or publication requirement.
It must not silently reinterpret a scientific mapping.

## Generic helpers

Framework plotting helpers may implement domain-neutral graphical operations.

They do not own scientific meaning.

For example, a generic continuous-raster helper may accept an already-resolved normalization and colormap.
It must not decide that HPC rate maps use a particular scientific scale because "rate map" is a research concept.

Research-specific plotting helpers remain with the scientific owner.

## Relationship to layout

`PanelSpec` answers:

> What does this top-level visual unit mean?

`PanelSlot` answers:

> Where is that unit placed?

The explicit binding is specified by [`layout.md`](layout.md).

Changing only the panel-slot binding changes realization identity but not `ProjectionIdentity` or the underlying `PanelSpec` semantics.
