---
title: Figure projection
authority: normative
document_status: specified
capability_status: partial
api_stability: provisional
---

# Figure projection

This specification defines how a figure obtains one exact scientific view from authoritative scientific sources.

The projection boundary ends before visual realization.

## Source roles

A figure consumes semantic source roles rather than anonymous positional tuples.

Conceptually:

```text
role
    what a source means to this figure

source identity
    which exact authoritative resource satisfies that role
```

Example roles may include:

```text
task_case
prediction
reasoning_trace
analysis
```

Role names and their scientific meanings belong to the figure's semantic owner.

The figure framework does not create source subclasses such as `TaskCorpusFigureSource` or `AnalysisFigureSource`.
A role is bound to an existing resolved EHP-SN resource or another framework-admitted stable source representation.

## `FigureInputContract`

A `FigureInputContract` declares semantic information requirements for each source role.

It may constrain:

```text
required semantic contract
required channels/capabilities
role cardinality
```

It must not specify physical storage paths such as Zarr groups, Parquet files, or filesystem locations.

The contract reuses existing EHP-SN scientific and resource contracts.
It does not establish a parallel figure schema system.

## Stable point-in-time sources

Every source participating in selection or preparation must represent a stable point-in-time scientific state for the duration of projection.

A source that can change concurrently must be detached, snapshotted, committed, or otherwise stabilized before crossing the projection boundary.

Read-only access alone is insufficient when another execution path can mutate the backing state.

This requirement applies to training telemetry and to any other live or mutable source.

## `FigureSelection`

`FigureSelection` represents authored scientific-view selection intent.

The framework does not require one universal selection representation.
A scientific owner may define domain-specific selection semantics such as:

```text
top K entities by an existing metric
fixed episode identities
worst cases by an existing error metric
first K successful trials
```

The framework must not introduce a generic metric/filter/query AST without demonstrated cross-domain need.

## `ResolvedFigureSelection`

`ResolvedFigureSelection` records the exact entities selected for exact source identities.

Both authored and resolved selection are provenance.

Two different authored policies that resolve to the same entity IDs remain different projection provenance.

## Deterministic selection

A deterministic selector must define every ordering or eligibility rule that can affect the result.

Depending on the selector, this includes:

```text
candidate population
eligibility/filter
ordering
cardinality
tie breaking
missing values
non-finite values
duplicate identity handling
```

Selection must not accidentally depend on:

```text
filesystem order
mapping iteration order
worker completion order
shard order
serialization order
provider discovery order
```

The scientific owner defines domain-specific selection semantics.
The framework verifies only generic reproducibility requirements.

## Stochastic selection

Stochastic figure selection is permitted only when required by the scientific view.

Its random stream must be independent of:

```text
training RNG
task RNG
evaluation RNG
model RNG
controller RNG
```

The selection provenance retains:

```text
selection semantics
selection parameters
figure-selection seed
resolved identities
```

Figure execution must never advance a scientific RNG stream.

## `prepare()`

`prepare()` converts validated authoritative sources plus an exact resolved selection into a provider-defined prepared scientific view.

It may:

```text
retrieve selected authoritative values
align channels
reorder selected entities
slice existing histories
reshape arrays
construct plotting coordinates
associate IDs with existing labels or metrics
construct representation masks
```

It must not:

```text
run model inference
estimate an authoritative scientific quantity
compute a new authoritative metric
fit a model or probe
perform hypothesis testing
perform new scientific statistical estimation
```

The decision rule is semantic:

```text
creates independently authoritative scientific evidence
    → upstream scientific operation

chooses or structures authoritative information for the view
    → selection / preparation

determines data-to-visual graphical meaning
    → visual semantics
```

## Borderline transformations

Operations such as smoothing, interpolation, normalization, thresholding, or binning are classified by purpose rather than by name.

A transformation used to estimate an authoritative scientific quantity belongs upstream.

A transformation used only to express already-authoritative information visually belongs to visual semantics.

Such transformations must be explicit and versioned by the semantic owner that uses them.
They must not be hidden inside generic plotting helpers.

## Provider-defined prepared data

The prepared view is domain-specific.

Examples may include:

```text
ArenaOverviewData
HpcPlaceSummaryData
HrmLatentDynamicsData
```

No universal `FigureData` superclass or `x/y/labels/metadata` payload is required.

The framework transports provider-defined prepared data opaquely where practical.

The generic contract does not require eager copying or one materialization strategy.
Prepared data may use immutable values, stable resource references, or stable read-only views as appropriate.

Once incorporated into a `FigureProjection`, the prepared scientific view is immutable by contract.
Renderers must not mutate it, and its backing scientific state must remain stable for the projection lifetime.

## `FigureProjection`

A `FigureProjection` is the provenance-bearing boundary representing one exact scientifically defined view before presentation.

Conceptually it carries:

```text
projection-semantics identity/version
resolved source-role bindings and source identities
authored selection semantics and parameters
resolved selected identities
preparation semantics/version
semantic preparation parameters
provider-defined prepared scientific view
scientific provenance
```

A projection may be transient or persisted by an owning operation.
Persistence is not inherent.

A `FigureProjection` is not a PNG, SVG, PDF, or Matplotlib Figure.

The framework contract does not require the projection to copy all prepared arrays into a new materialization.
It requires a stable immutable prepared view with fixed provenance for the projection lifetime.

## Projection identity

`ProjectionIdentity` is determined by semantic/provenance inputs:

```text
projection-semantics identity/version
exact authoritative source identities
authored selection semantics/version
selection parameters
resolved selected identities
preparation semantics/version
semantic preparation parameters
```

Therefore these changes create a new projection:

```text
different authoritative source
different selection policy
different selected entities
different preparation semantics
different semantic preparation parameter
```

These do not change projection identity:

```text
different panel placement
different physical size
different typography
different DPI
different serialization format
```

Projection identity must be computable without reading the visual, default, layout, profile, serialization, or delivery portions of the figure definition or request.

Projection identity is not proof that persisted prepared bytes are identical.
When persisted content needs integrity verification, the owning EHP-SN resource/artifact integrity mechanism remains authoritative.
