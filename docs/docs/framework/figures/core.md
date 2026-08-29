---
title: Figure framework core
authority: normative
document_status: specified
capability_status: partial
api_stability: provisional
---

# Figure framework core

This specification defines the generic executable figure capability and its participation in framework discovery and orchestration.

It does not define scientific figure meaning, scientific selection algorithms, Matplotlib layout details, or parent-operation scheduling.

## `FigureSpec`

A `FigureSpec` is the registered executable capability for one versioned scientific figure definition.

There is initially no generic EHP runtime type named simply `Figure`.
That name would be ambiguous with the scientific concept and `matplotlib.figure.Figure`.

A `FigureSpec` has three semantically distinct partitions:

```text
projection
    scientific-view semantics

visual
    scientific visual-encoding semantics

defaults
    optional realization defaults
```

The exact Python representation may evolve while the partition remains observable.

### Projection partition

The projection partition identifies the semantics required to construct a `FigureProjection`.

It references:

- the semantic input contract;
- selection semantics and resolver;
- preparation semantics and preparation implementation;
- projection-semantics identity/version.

Projection identity must be constructible without reading visual, default, layout, profile, serialization, or delivery fields.

### Visual partition

The visual partition identifies the scientific meaning of the graphical realization.

It references:

- visual-semantics identity/version;
- `PanelSpec`s;
- cross-panel scientific visual coordination;
- the figure-level visual realization entry point.

The visual partition does not own physical publication dimensions, serialization format, scientific selection, or default placement.

### Defaults partition

A figure may advertise convenience defaults such as:

```text
default FigureLayout reference
default panel-slot binding
default RenderProfile reference
```

when such defaults exist.

Defaults are not projection semantics or scientific visual semantics.
Changing only a default must not alter `ProjectionIdentity` or the identity of the underlying visual-semantics contract.

A caller may override defaults through a concrete `FigureRequest` where the owning interface permits it.

## Canonical figure reference

A `FigureSpec` participates in the framework's canonical component-reference system.

This specification does not invent a parallel figure-reference parser or syntax.
Reference spelling, version structure, and canonicalization reuse the framework reference contract.

If the existing reference framework cannot represent figure components, implementation is blocked by `ARCH-014` until that framework-owned gap is specified.

## Provider contribution

Installed packages may contribute reusable figure definitions through the figure-provider entry-point group:

```text
ehp_sn.figures.providers
```

Each entry point identifies a provider, not an individual figure.
The concrete import target is owned by the contributing package and must refer to an implementation of the framework provider contract.

One provider may contribute multiple `FigureSpec`s.

Provider loading, canonical reference handling, and generic duplicate-resolution mechanics remain owned by the normal framework component-discovery contracts.
The figure framework adds no second plugin system.

Figure participation must satisfy `ARCH-003`:

- contribution uses canonical component references;
- catalogue semantics are independent of provider discovery order;
- conflicting duplicate canonical references are rejected;
- `ehp_sn` does not import a concrete research package by name.

Experiment-local figures use the existing workspace/experiment-resolution path.
The presence of `experiments/<name>/vN/figures/` as a specification root does not define runtime filesystem scanning.

## Catalogue semantics

Figure definitions participate in the normal component-catalogue architecture.

A figure-specific catalogue view may exist for convenience, but it must not become a second authoritative registry with independent identity or lifecycle semantics.

For a given resolved environment, catalogue construction must yield:

```text
one unambiguous FigureSpec per canonical figure reference
```

An ambiguous canonical reference is an error.
There is no first-provider-wins rule.

## `FigureRequest`

A `FigureRequest` represents one requested figure occurrence.

It is an orchestration envelope whose semantics preserve three partitions:

```text
projection request
    sources
    selection
    semantic preparation parameters

realization request
    layout/binding/profile
    serialization request where applicable

delivery policy
    destination/sink reference
    requiredness/failure policy owned by the caller
```

The exact public request type is not stabilized by this specification.
The first implemented vertical slice determines which values require first-class Python contracts.

A `FigureRequest` is not itself one semantic identity domain.
Projection and realization identity are defined separately.

Scheduling and trigger policy do not belong to `FigureRequest` semantics unless an owning operation resolves them into one concrete request occurrence.

## Relationship to scientific owners

The framework defines how a `FigureSpec` participates in selection, preparation, visual realization, and orchestration.

The scientific owner defines the concrete meaning of:

```text
source roles
selection semantics
provider-defined prepared data
PanelSpecs
scientific visual encodings
```

A reusable scientific figure therefore belongs to `ehp_research`.
A figure whose meaning depends jointly on one experiment composition belongs to that experiment.

## Framework non-targets

The core framework does not introduce:

```text
Figure lifecycle
FigureArtifact
FigureSchedule
FigureComposition
backend-neutral graphics IR
universal FigureData base class
universal scientific selection DSL
parallel figure resource hierarchy
```

Any future addition requires a demonstrated framework requirement independent of one research figure.
