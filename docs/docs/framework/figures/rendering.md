---
title: Figure rendering
authority: normative
document_status: specified
capability_status: partial
api_stability: provisional
---

# Figure rendering

This specification defines non-scientific presentation policy and concrete Matplotlib realization after a `FigureProjection` and scientific visual semantics are fixed.

It does not own scientific selection, scientific result calculation, parent-operation scheduling, or artifact lifecycle.

## Realization boundary

The realization path is:

```text
FigureProjection
        ↓
scientific visual semantics
        ↓
FigureLayout + panel-slot binding
        ↓
RenderProfile
        ↓
Matplotlib Figure / Axes / Artists
        ↓
interactive realization
        or
serialization
```

There is deliberately no EHP-owned `FigureComposition`, graphics IR, Artist hierarchy, or generic `RenderEngine` hierarchy.

## `RenderProfile`

A `RenderProfile` identifies versioned non-scientific presentation policy for one intended medium or venue policy.

It may define:

```text
physical width and height
margins
inter-panel spacing
font family
font sizes
line-width defaults
marker-size defaults
panel-label presentation
accessibility constraints
non-semantic palette defaults
venue constraints
```

It must not contain scientific-view selection such as:

```text
cell ID
episode ID
environment ID
checkpoint
split
ranking metric
selection policy
selected cases
```

Those values belong to projection semantics.

## Scientific mappings override presentation defaults

A `RenderProfile` may provide defaults only where they do not change scientific meaning.

If a figure's visual semantics explicitly define a quantitative or categorical mapping, the profile must not silently replace that mapping.

A profile may reject an incompatible realization when an external requirement cannot be satisfied without changing scientific meaning.

## Venue-specific profiles

A venue-specific profile should be introduced only when an actual reporting or publication requirement needs it.

Its identity must distinguish materially different policies.

For example, if a venue has meaningfully different initial-submission and final-production constraints, separate explicit profile identities are preferable to one ambiguous venue name.

Publication helpers or style libraries may assist implementation but do not become policy authority.

## Matplotlib state isolation

Rendering must not depend on uncontrolled ambient Matplotlib state.

The implementation should resolve an effective presentation configuration from:

```text
optional helper defaults
+
RenderProfile
+
explicit framework-controlled overrides
```

and apply it within a temporary Matplotlib style/configuration context where appropriate.

Scientific rendering should normally use explicit object-oriented operations:

```text
ax.plot(...)
ax.imshow(...)
fig.colorbar(...)
```

rather than depending on implicit current-figure/current-axes state.

Backend selection is an outer runtime concern.
A Matplotlib rc-parameter context is not treated as complete backend or process isolation.

## Serialization request

Serialization is distinct from projection and from most presentation semantics.

A serialization request contains at least:

```text
target format
realization-affecting serialization parameters
```

Examples of formats include:

```text
PNG
SVG
PDF
```

Examples of parameters that may affect a realization include format-dependent DPI, bounding-box behavior, transparency, and other explicitly supported serialization options.

The exact public request type is not stabilized until implementation demonstrates which parameters need first-class representation.

Non-visual file metadata and content-integrity metadata remain governed by the owning resource/artifact contracts.

## Interactive realization

A live `matplotlib.figure.Figure` is mutable and process-local.

It is normally treated as a transient realization.

Interactive use does not create a persistent scientific artifact merely because a graphical object exists in memory.

A notebook or inspection caller may display the transient figure without serialization.

## `RealizationIdentity`

Realization identity answers:

> How was this exact `FigureProjection` intentionally communicated?

Conceptually it includes:

```text
ProjectionIdentity
visual-semantics identity/version
FigureLayout identity/version
panel-slot binding
RenderProfile identity/version
serialization request, when serialized
```

A transient interactive realization may omit serialization-specific identity inputs.

Changing only realization inputs must not change `ProjectionIdentity`.

## Rendering-environment provenance

The concrete renderer environment may affect exact output.

Relevant provenance can include values such as:

```text
Matplotlib version
backend/renderer
font-resolution environment
FreeType version where relevant
platform-specific rendering dependencies
```

Those values are recorded when required by the owning reproducibility, resource, cache, or artifact contract.

They are conceptually separate from the intended semantic realization unless another framework contract explicitly makes them identity-bearing for a concrete purpose.

## Semantic and byte reproducibility

Semantic realization determinism and byte-level reproducibility are separate claims.

Equivalent:

```text
projection
visual semantics
layout
binding
profile
serialization request
```

must produce semantically equivalent visual output under a compatible rendering environment.

The framework does not claim byte-identical PNG, SVG, or PDF output across arbitrary environments.

When exact serialized content must be verified, the existing EHP-SN content-integrity mechanism is used.

The figure subsystem does not define a figure-specific digest architecture.

## Generic plotting helpers

The framework may provide domain-neutral Matplotlib helpers.

Helpers may draw already-resolved graphical forms such as:

```text
continuous raster
categorical raster
line
scatter
matrix
trajectory
basic distribution
generic markers
colorbars
```

They must accept scientific mapping decisions rather than inventing research semantics.

No helper becomes a new semantic contract merely because multiple figures call it.
