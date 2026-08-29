---
title: Figure layout
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Figure layout

This specification defines reusable top-level panel-placement topology for figure realization.

It does not define scientific panel meaning, internal panel rendering, physical publication size, typography, or serialization.

## `FigureLayout`

A `FigureLayout` identifies one versioned top-level structural topology.

It defines only structural information required to place independently meaningful panels, such as:

```text
top-level rows and columns
PanelSlots
row spans
column spans
relative track ratios
structural ordering
```

It does not define:

```text
scientific panel meaning
physical millimetres or inches
DPI
font family
font size
serialization format
venue identity
```

Those concerns belong to scientific visual semantics or `RenderProfile` as appropriate.

## `PanelSlot`

A `PanelSlot` is a named top-level structural region within a `FigureLayout`.

Reusable structural names may include:

```text
primary
secondary
detail
supporting
```

A slot name describes placement rather than scientific meaning.

A `PanelSlot` is not inherently one Matplotlib `Axes`.

A slot may be realized through:

```text
one Axes
multiple Axes
nested GridSpec
SubFigure
another suitable Matplotlib region
```

## Scientific panel and structural slot

A scientific panel and a structural slot are separate identities.

For example:

```text
PanelSpecs:
    population
    coverage
    examples

PanelSlots:
    primary
    secondary
    detail
```

A binding may be:

```text
population → primary
coverage   → secondary
examples   → detail
```

The same layout can therefore be reused by an unrelated scientific figure with different `PanelSpec` keys.

## Binding validation

The initial framework contract requires explicit binding.

For a layout in which every declared slot is required:

- each required `PanelSpec` is bound exactly once;
- each required `PanelSlot` receives exactly one panel;
- unknown panel keys are rejected;
- unknown slot keys are rejected;
- duplicate bindings are rejected;
- missing required panels are rejected;
- missing required slots are rejected.

A validated mapping is sufficient.
A public `PanelBinding` class is not required unless implementation demonstrates an additional invariant that the mapping cannot express.

## No implicit optional-slot system

The initial layout model does not define generic optional or responsive slots.

Prefer explicit versioned layouts when topology differs materially:

```text
summary/v1
summary-with-detail/v1
```

rather than one implicit topology whose structure changes according to hidden conditions.

Responsive or optional topology may be introduced later only after repeated concrete requirements demonstrate that explicit layouts are insufficient.

## Layout identity

Layout identity describes structural topology.

Changing any of the following changes layout identity when the value is part of the layout specification:

```text
slot set
slot ordering
row/column topology
slot spans
relative track ratios
structural nesting exposed by the layout contract
```

Changing scientific selection, typography, physical dimensions, or serialization format does not change layout identity.

## Panel-slot binding and realization identity

Panel-slot binding participates in realization identity.

These are different realizations:

```text
population → primary
coverage   → secondary
```

and:

```text
coverage   → primary
population → secondary
```

even when the projection, panel semantics, and layout topology are otherwise unchanged.

The binding does not contribute to `ProjectionIdentity`.

## Matplotlib compilation

The framework may compile:

```text
FigureLayout
+
panel-slot binding
+
RenderProfile geometry
```

into Matplotlib structural objects such as:

```text
GridSpec
SubplotSpec
```

The framework does not need a parallel hierarchy such as:

```text
PanelRegion
LayoutRegionHandle
FigureRegion
```

when Matplotlib structural objects already provide the required implementation boundary.

## Internal panel layout

The top-level layout boundary ends at the structural region assigned to a `PanelSpec`.

Scientific rendering code may subdivide that region locally.

For example, an `examples` panel assigned to one `SubplotSpec` may create:

```text
2 × 4 nested GridSpec
```

for eight example plots.

Internal subdivision remains provider-local until multiple semantically independent implementations demonstrate a reusable layout contract.

## Layout versus presentation

`FigureLayout` owns topology.

`RenderProfile` owns physical and presentation policy.

Conceptually:

```text
FigureLayout
    structural ratios and slots

        +

RenderProfile
    physical dimensions and spacing policy

        ↓

Matplotlib
    concrete coordinates and objects
```

A rendering backend may combine these values in one API.
The EHP-SN semantic boundary remains separate.
