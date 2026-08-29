---
title: Figure operation integration
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Figure operation integration

This specification defines the boundary between the generic figure capability and the EHP-SN operations that request figures.

It does not define the scientific semantics of a concrete figure or the scheduling policy of a particular operation.

## Parent-operation authority

The requesting operation or runtime owns:

```text
when a figure request exists
diagnostic inference
scheduling and triggers
queueing and backpressure
requiredness
failure policy
artifact lifecycle
destination ownership
```

The generic figure framework consumes a concrete figure request and produces a projection and visual realization.

It does not acquire an independent lifecycle, scheduler, scientific inference path, or artifact lifecycle.

This boundary implements `FIG-004`.

## Request hand-off

A parent operation provides or resolves the inputs required for one concrete figure occurrence.

Conceptually, the request may contain:

```text
figure reference

projection request
    source-role bindings
    authored selection
    semantic preparation parameters

realization request
    layout reference or override
    panel-slot binding
    RenderProfile reference or override
    serialization request when applicable

delivery policy
    destination/sink reference
    requiredness/failure policy
```

The exact Python request type is not stabilized until the first vertical implementation proves which values require first-class contracts.

Scheduling policy is not part of a concrete figure occurrence.
A schedule or trigger resolves into one concrete `FigureRequest`.

## Stable source hand-off

A parent operation must hand the figure path stable point-in-time sources.

Committed artifacts naturally satisfy this requirement when their resource contract provides immutable content.

Live or mutable execution state must first be detached, snapshotted, or otherwise stabilized.

The generic figure service must not retain a callback that can reacquire mutable scientific state later.

## Training telemetry

Training is operationally special because diagnostic visualization may observe a live scientific process.

The boundary is:

```text
training runtime
        ↓
declared diagnostic capture/inference
        ↓
stable detached diagnostic result
        ↓
FigureRequest
        ↓
ordinary figure pipeline
```

Figure code must not receive:

```text
live model object
optimizer
gradient graph
mutable recurrent state
scientific RNG object
```

The training operation owns model mode, gradient control, state isolation, RNG handling, device synchronization, and any required diagnostic inference.

## Diagnostic inference

When a requested diagnostic case is not already represented in current scientific outputs, any required inference belongs to the parent scientific operation.

Correct:

```text
training/evaluation operation
    performs declared diagnostic inference
        ↓
stable result
        ↓
figure pipeline
```

Incorrect:

```text
figure renderer
    calls model.forward()
```

The latter would violate `FIG-002`, `FIG-003`, and `FIG-004`.

## Scheduling and bounded telemetry

A recurring policy such as:

```text
render after every validation cycle
```

belongs to training or evaluation execution policy.

It creates concrete figure-request occurrences.

Queue size, memory budget, blocking behavior, coalescing, dropping, failure reporting, and shutdown behavior belong to the operation/runtime that schedules optional diagnostic work.

The figure framework exposes no `FigureSchedule` semantic abstraction.

Optional telemetry must not require an unbounded queue.

## Requiredness and failure

Requiredness is request/operation policy rather than `FigureSpec` semantics.

The same figure may be:

```text
optional in training telemetry
optional in evaluation diagnostics
required in report generation
required in an explicit export command
```

The parent operation decides the consequence of failure.

A `FigureSpec` therefore does not contain one universal `fatal` or `required` flag.

## Destination and sinks

A parent operation owns the destination.

A small `FigureSink` protocol may exist when implementation benefits from one common delivery boundary.

Potential destinations include:

```text
ephemeral display
telemetry logger
staged artifact resource
report package
explicit export target
```

A sink must not acquire independent artifact identity, staging, commit, or scientific lifecycle semantics that already belong to the parent operation.

## Artifact immutability

Figure integration does not weaken existing artifact immutability.

Allowed:

```text
artifact staging
        ↓
prepare projection
render/serialize
write staged resource
validate
commit
```

Forbidden:

```text
committed scientific artifact
        ↓
append new figure resource
```

A later realization should instead be written to a new owning destination such as a report or explicit export.

## Reports

A report may:

```text
reuse an existing FigureProjection
        +
report layout/profile
        ↓
new realization
```

or:

```text
committed authoritative sources
        ↓
same projection semantics
        ↓
equivalent FigureProjection
        ↓
report realization
```

A report may not perform new inference, metric calculation, fitting, or scientific statistical analysis merely to produce a figure.

Presentation may change.
Science may not.

## Python and notebooks

Python/notebook use reuses the same scientific path.

Conceptually:

```text
prepare_figure(...)
    → FigureProjection

render_figure_projection(...)
    → Matplotlib Figure
```

A convenience API may combine the two operations.

Notebook use must not implement a parallel selector, preparation path, or scientific interpretation.

The supported public Python surface belongs under `docs/docs/interfaces/python/` only after implementation exists.

## CLI operations

There is no standalone figure lifecycle command merely because figures exist.

Implemented figure controls belong to the CLI documentation of the operation that owns them:

```text
data
tasks
train
evaluate
analyze
report
```

A future standalone export operation would require separate interface and architectural justification.

## Configuration

This specification does not define a figure-specific public configuration language.

A future configuration model must preserve the semantic partition:

```text
scientific selection
    → projection request

presentation
    → realization request

schedule/trigger
    → parent operation

destination
    → parent operation
```

Speculative TOML structures must not become de-facto configuration contracts.
