---
title: Python figures
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Python figures

## Normative summary

The Python figure interface exposes the same figure semantics used by CLI-integrated inspection, telemetry, analysis, and reporting.

Notebook convenience must not create a second plotting architecture or bypass framework contracts.

The conceptual API separates preparation from rendering:

```text
sources
    ↓
prepare_figure(...)
    ↓
FigureProjection
    ↓
render_figure_projection(...)
    ↓
RenderResult
```

Exact import paths and signatures remain provisional until the first implementation vertical slice is accepted.

## API direction

The intended semantic interface is:

```python
projection = prepare_figure(
    figure=figure_ref,
    sources=sources,
    selection=selection,
)

result = render_figure_projection(
    projection,
    context=render_context,
    sink=sink,
)
```

A convenience function may compose both stages:

```python
result = render_figure(
    figure=figure_ref,
    sources=sources,
    selection=selection,
    context=render_context,
    sink=sink,
)
```

For a single-role figure, a future convenience `source=` shorthand may be provided, but the stable semantic model remains named source roles.

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
- visual composition;
- rendering;
- sinks;
- identity/provenance rules.

Notebook code must not silently bypass validation by inspecting undocumented internals.

## Figure references and catalogue

A figure may be selected by:

- canonical figure reference;
- an already-resolved `FigureSpec` obtained from the generic framework catalogue.

The figure API should reuse the generic component/reference catalogue.

A `list_figures()` or `get_figure_spec()` convenience function is permitted only as a thin projection over that generic catalogue, not as a second authority.

## Sources

The Python API may accept framework-native objects capable of resolving declared source roles, conceptually including:

```text
SubstrateArtifact access object
TaskCorpus access object
EvaluationArtifact access object
AnalysisArtifact access object
FigureTelemetrySnapshot
ResolvedFigureSource
```

They resolve to the same `ResolvedFigureSource` contract used by other interfaces.

Raw tensors, arbitrary dictionaries, internal filesystem paths, or implementation objects are not automatically stable figure sources.

## Multi-source figures

Multi-source figures use named roles.

Conceptual example:

```python
sources = {
    "task_case": case_source,
    "prediction": prediction_source,
    "reasoning_trace": trace_source,
}
```

Anonymous positional tuples are not the stable interface.

## Selection

The Python API accepts a typed `FigureSelection` or a typed figure-specific selection compatible with that contract.

Conceptual examples:

```python
selection = RecordSelection(record_id="episode-42")
```

```python
selection = TopKSelection(
    metric="spatial_information",
    k=8,
    tie_break="cell_id_ascending",
)
```

These names remain illustrative.

Python and CLI/configuration forms expressing the same selection semantics must resolve to equivalent `ResolvedFigureSelection`.

Calling code must not manually recreate package-owned deterministic selection logic.

## Preparation

`prepare_figure(...)` returns a framework `FigureProjection` or stable public projection view.

Preparation is:

- read-only with respect to sources;
- deterministic for reproducible projections;
- free of hidden inference;
- free of hidden scientific analysis;
- responsible for resolving exact scientific selection;
- responsible for recording source/projection provenance where available.

For notebook exploration, the projection may remain transient in memory.

## Rendering

`render_figure_projection(...)` accepts an existing `FigureProjection` plus typed `RenderContext`.

Rendering must not repeat or alter scientific selection.

Conceptual example:

```python
context = RenderContext(
    render_profile="interactive",
)
```

Changing only DPI, dimensions, format, typography, or presentation profile must not change projection identity.

## Return contract

The public rendering API should return one framework-controlled result shape rather than changing fundamental return type according to sink/backend.

Conceptually:

```text
RenderResult
├── rendered_figure
├── sink_result
└── diagnostics
```

`rendered_figure` may contain:

- a serializable rendered realization;
- a transient interactive backend handle.

`sink_result` records delivery outcome when a sink is used.

Exact class names and fields remain provisional.

Backend-native objects may be contained in a transient realization but must not replace the framework result envelope as the stable API contract.

## Convenience rendering

`render_figure(...)` semantically composes:

```text
resolve spec
→ resolve/validate sources
→ resolve selection
→ prepare
→ compose
→ render
→ sink
```

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
