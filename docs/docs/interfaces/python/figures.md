---
title: Python figures
authority: normative
document_status: draft
capability_status: partial
api_stability: provisional
---

# Python figures

## Normative summary

The Python figure interface exposes the same figure semantics used by CLI-integrated inspection (`data inspect --figure`), and — through the same service — by telemetry, analysis, evaluation, and reporting.

Notebook convenience must not create a second plotting architecture or bypass framework contracts.

The public API separates preparation from realization into two stages, plus one convenience that composes them:

```text
exact resolved source
    ↓
prepare_figure(...)
    ↓
FigureProjection
    ↓
render_figure_projection(...)   transient Matplotlib Figure
   or
realize_projection(...)         persistent serialized RealizedFigure
```

Exact import paths and signatures remain provisional (`api_stability: provisional`) until a second substantially different operation confirms the surface (Phase 5A–5C).

## Public surface

The supported Python surface lives in `ehp_sn.figures`. Its parameter structure follows the implementation that survived `data inspect` (Phase 5D § 7.2):

```python
from ehp_sn.figures import (
    FigureSource,
    prepare_figure,
    render_figure_projection,
    realize_projection,
    render_figure,
)

source = FigureSource(
    artifact_ref="artifact:dg/v1",
    record_id="sha256:1a61…",
    schema_ref="raster-topology/v1",
    content=record_content,
)

projection = prepare_figure(registry, figure_ref, source)

# transient interactive realization
mpl_figure = render_figure_projection(projection, registry=registry)

# persistent serialized realization
policy = resolve_serialization_policy(format="svg", dpi=100)
realized = realize_projection(projection, serialization=policy, registry=registry)
```

`registry` is the ordinary figure catalogue (`effective_figure_registry()`, or a caller-constructed `ComponentRegistry`). `source` is the single exact resolved source the parent operation already resolved — the figure layer never re-selects it.

A convenience composes the canonical prepare + realize path; it never implements a parallel path:

```python
mpl_figure = render_figure(registry, figure_ref, source)
realized   = render_figure(registry, figure_ref, source, serialization=policy)
```

## No second semantic system

Python and configured operation paths must use the same:

- figure references;
- `FigureSpec`s;
- input-contract validation;
- source-role semantics;
- source resolution;
- deterministic selection;
- preparation contracts;
- `FigureProjection`;
- scientific visual semantics;
- realization and serialization;
- projection/realization identity/provenance rules.

For equivalent semantic requests, the CLI (`data inspect --figure`) and Python must normalize to the same canonical figure reference, the same source-role identity, the same authored + resolved selection, the same projected view, and the same `ProjectionIdentity` (Phase 5D § 7.5). Presentation divergence is allowed: different `RenderProfile` or serialization may yield a different `RealizationIdentity` while preserving `ProjectionIdentity` (Phase 5D § 7.6).

The Python API has no private duplicate catalogue, no notebook-specific selection logic, and no alternate identity derivation (Phase 5D § 7.8). It is a façade over the same generic figure service the CLI uses.

Notebook code must not silently bypass validation by inspecting undocumented internals.

## Figure references and catalogue

A figure may be selected by:

- canonical figure reference;
- an already-resolved `FigureSpec` obtained from the generic framework catalogue.

The figure API reuses the generic `ComponentRegistry` (`effective_figure_registry()`), the same catalogue the CLI resolves against. There is no second authoritative figure catalogue.

## Sources

A Python caller supplies an exact resolved source through `FigureSource`, the public counterpart of the service's exact source surface:

```text
artifact_ref   committed artifact's canonical reference  (artifact:…/vN)
record_id      exact record identity                     (sha256:…)
schema_ref     framework-owned logical contract          (raster-topology/v1)
content        stable logical contents
```

`FigureSource` is structurally identical to the service's exact source contract, so the canonical `prepare_figure` consumes it without any source-type branch.

Raw tensors, arbitrary dictionaries, internal filesystem paths, or implementation objects are not automatically stable figure sources unless they satisfy the recorded source contract.

## Multi-source figures

Multi-source figures use named roles. A figure declares its semantic roles through its `FigureInputRequirement`s; each role is bound to one exact source. Anonymous positional tuples are not the stable interface.

For the currently realized single-role service surface, one exact source is bound to the figure's single declared role. Multi-source role binding is validated and exercised by evaluation/experiment figures in later slices.

## Selection

Selection is declared and resolved by the figure's projection partition through its deterministic `select` resolver. A Python caller does not author selection separately from `FigureSource` on the current service surface: where a figure performs scientific selection, `prepare_figure` resolves the exact `ResolvedFigureSelection` (authored semantics/version + parameters + exact resolved identities) and carries it on the `FigureProjection`.

Python and CLI/configuration forms expressing the same selection semantics must resolve to equivalent `ResolvedFigureSelection`. Calling code must not manually recreate package-owned deterministic selection logic.

## Preparation

`prepare_figure(...)` returns a framework `FigureProjection`.

Preparation is:

- read-only with respect to sources;
- deterministic for reproducible projections;
- free of hidden inference;
- free of hidden scientific analysis;
- responsible for resolving exact scientific selection;
- responsible for recording source/projection provenance.

For notebook exploration, the projection may remain transient in memory.

## Rendering

`render_figure_projection(...)` accepts an existing `FigureProjection` and realizes it as a transient Matplotlib Figure; the caller owns the interactive Figure's lifetime.

`realize_projection(...)` accepts an existing `FigureProjection` plus an explicit resolved serialization policy (`ResolvedSerializationPolicy`) and produces a `RealizedFigure` holding the semantic `RealizationIdentity`, a content digest, and separate rendering-environment provenance. The framework owns the persistent Figure lifecycle and releases it on every exit path.

Rendering must not repeat or alter scientific selection. Changing only DPI, dimensions, format, typography, or presentation profile must not change `ProjectionIdentity` (it may change `RealizationIdentity`).

Presentation policy is expressed through the explicit, versioned `RenderProfile`; serialization policy through `ResolvedSerializationPolicy`. Neither is inferred from ambient Matplotlib state or filenames.

## Return contract

The two realization entry points each return one framework-controlled result shape:

- transient: a Matplotlib `Figure` (interactive; caller owns lifetime);
- persistent: a `RealizedFigure` (serialized bytes + `RealizationIdentity` + `ContentDigest` + rendering-environment provenance).

A transient backend handle and a serialized realization are distinct outcomes of the same `FigureProjection`; neither replaces the projection as the scientific-view boundary.

## Convenience rendering

`render_figure(...)` semantically composes the canonical:

```text
resolve figure spec through the catalogue
→ validate the source against the declared input requirement
→ resolve selection (when declared) and prepare
→ FigureProjection
→ realize (transient or persistent per the serialization argument)
```

It implements no parallel path; `ProjectionIdentity` and `RealizationIdentity` are identical to calling the stages directly.

Its result must be equivalent to explicit preparation plus rendering with the same inputs.

## Sinks

Python may request semantic sink roles such as:

```text
ephemeral display
explicit export
staged artifact/report sink
```

Training/evaluation telemetry sinks are normally controlled by the parent execution operation rather than arbitrary notebook calls.

Filesystem export path is placement and does not change scientific projection identity.

## Error model

The Python interface should expose controlled framework errors for at least:

```text
unknown or ambiguous figure
input-contract mismatch
missing source role
unsupported source schema/capability
invalid or non-reproducible selection
preparation failure
visual-composition failure
render failure
sink failure
committed-artifact mutation attempt
```

Exact exception names remain provisional.

Backend-specific exceptions should be translated/wrapped at the stable framework boundary unless explicitly documented as backend-specific provisional behavior.

## Read-only semantics

The Python figure API must not implicitly:

- append to a committed artifact;
- update a TaskCorpus;
- modify an EvaluationArtifact;
- alter a checkpoint/model;
- persist new scientific analysis into an immutable artifact.

Persistence requires an owning staged operation or explicit presentation export.

## CLI/Python equivalence

When Python and operation configuration express the same:

- figure reference;
- exact source identities;
- selection semantics;
- render context;

they must resolve to equivalent projection and realization semantics.

Frontend-specific diagnostics and in-memory handles may differ.

## Non-goals

This page does not define:

- scientific figure meaning;
- deterministic selection algorithms;
- projection hashing;
- plotting-backend APIs;
- telemetry buffering;
- CLI option syntax;
- report package structure.

## Related specifications

- [`Framework figures`](../../framework/figures/index.md)
- [`Figure configuration`](../configuration/figures.md)
- [`Python conventions`](conventions.md)
- [`Python analysis`](analysis.md)
- [`Python training`](training.md)
- [`Python evaluation`](evaluation.md)
