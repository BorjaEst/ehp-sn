---
title: Figure configuration
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Figure configuration

## Normative summary

Figure configuration classifies figure-specific values used by existing EHP-SN operations.

It does **not** create a top-level figure operation and does not yet define one universal figure TOML schema.

Generic configuration precedence, canonical field-path grammar, explicit-input conflicts, workspace admission, resource binding, provenance classes, and identity mechanics remain authoritative in the existing configuration specifications and are not redefined here.

This document owns only the figure-specific specialization of those rules.

## Scope

This page defines figure-specific configurable concerns:

- invocation of a figure capability;
- named source-role binding when operation-local source selection is permitted;
- scientific selection parameters;
- render/presentation parameters;
- telemetry schedules;
- sinks/destinations;
- requiredness/failure policy;
- figure-specific identity classification;
- operation integration.

It does not define:

- generic precedence;
- generic conflict rules;
- generic provenance mechanics;
- generic workspace semantics;
- arbitrary dynamic maps;
- arrays-of-table support;
- one final figure TOML structure;
- backend-native plotting option trees;
- figure identity hashing;
- artifact commitment.

## Namespace specialization

Figure fields use the existing configuration namespaces:

```text
experiment.*
analysis.*
request.*
```

No new top-level `figure.*` namespace is established.

The generic namespace criteria remain authoritative.

This page adds the following figure-specific clarification:

> Ownership of a figure definition is not the same as ownership of one request to render it.

For example:

```text
experiments/mazehard-hrm/v1
    may own:
        figure:mazehard-hrm-reasoning/v1 semantics

request
    normally owns:
        whether to render it now
        which permitted entities to show
        cadence
        render profile
        sink
```

A figure being experiment-local therefore does **not** automatically make its rendering request an `experiment.*` field.

## Figure configuration classes

### Figure capability declaration

A scientific definition may declare that a figure capability exists or that a projection is a defined output of an analysis/experiment.

Examples:

```text
analysis defines a standard place-summary projection
experiment defines an experiment-local joint reasoning figure
```

The owning definition determines the figure's scientific semantics.

Whether the current invocation renders that capability is normally downstream/request policy unless the scientific definition explicitly makes the projection itself a required scientific output.

### Invocation figure request

Examples:

```text
render one compatible inspect figure
enable optional training diagnostic figure
request one report realization
export one selected projection
```

These are normally `request.*` concerns.

### Scientific selection

Selection determines which scientific entities appear in a projection.

Examples:

```text
record ID
environment ID
top-k cells by an existing metric
case subset
reasoning-cycle subset
```

Selection is distinct from rendering.

Its namespace/identity class depends on the owning operation:

```text
analysis-owned canonical scientific selection
    → analysis.* when it changes the analysis definition

one invocation's inspection/export selection
    → request.*
```

### Presentation configuration

Presentation values include:

```text
render profile
size
dpi
typography
layout constraints
output format
```

They belong to realization/request or report-profile semantics.

They do not redefine scientific result or projection identity.

### Telemetry schedule

Telemetry schedule values include conceptually:

```text
figure ref
trigger
probe selection
maximum items
render profile
sink
requiredness
bounded buffering policy
```

These are request-level operational semantics unless another authority explicitly defines a scientific diagnostic output requirement.

Cadence itself does not become experiment science merely because an experiment-local figure is being rendered.

### Sink/destination

Examples:

```text
telemetry logger
explicit export path
report slot
staged artifact resource role
```

These are delivery/placement concerns.

A filesystem destination does not define scientific projection identity.

## No final universal TOML schema yet

This document intentionally does not stabilize structures such as:

```toml
[[request.figures]]
...
```

or:

```toml
[request.figures.foo]
...
```

The current configuration interface does not provide arbitrary arrays-of-tables or dynamic traversable maps as a generic stable mechanism.

A serialized figure schema must be introduced by a concrete operation only after its exhaustive field catalogue is known.

Likely first vertical slices are:

```text
training telemetry
analysis/report rendering
```

They must share the semantic classes in this document rather than invent incompatible local meanings.

## Canonical field paths

Every future public figure field must satisfy the existing canonical field-path grammar and belong to an authoritative operation schema.

The figure subsystem must not expose a stable path such as:

```text
request.figures.0.matplotlib.rcParams.foo
```

Backend-specific presentation settings, if exposed, must be explicitly typed and clearly separated from portable figure semantics.

Generic precedence and duplicate-explicit-input behavior apply unchanged; this document defines no figure-specific exception.

## Source-role configuration

When one operation permits explicit figure-source selection, each source binds to a named figure role.

Conceptually:

```text
task_case
    → task/evaluation case resource

prediction
    → prediction resource

reasoning_trace
    → trace resource

analysis
    → derived analysis resource
```

Bindings must use canonical framework reference/resource mechanisms.

Figure configuration must not rely on an internal storage path when the framework resource surface can resolve the semantic role.

## Selection configuration

A reproducible configured selection must satisfy the deterministic-selection contract from `framework/figures/projection.md`.

Where configurable, this includes:

```text
candidate population
filter
order
cardinality
tie-break
missing/non-finite policy
figure-specific seed role
```

If the `FigureSpec` fixes part of the policy, operation configuration may change only explicitly supported selection parameters.

## Telemetry configuration

Training/evaluation telemetry must resolve:

```text
FigureSchedule
    ↓ trigger
concrete FigureRequest
```

Future operation fields must distinguish:

- schedule/trigger policy;
- exact resolved probe selection;
- render profile;
- sink;
- requiredness;
- bounded buffering/backpressure policy.

The actual public field catalogue remains provisional.

## Figure-specific identity classification

Figure configuration must classify values into existing framework identity categories.

At minimum the specialization distinguishes:

```text
projection input
render-realization input
operational telemetry input
placement
diagnostic provenance only
```

Typical classification:

| Value                                 | Figure-specific identity effect                                           |
| ------------------------------------- | ------------------------------------------------------------------------- |
| Exact selected scientific entity      | Projection identity                                                       |
| Top-k selection semantics             | Projection identity                                                       |
| Preparation semantic parameter        | Projection identity                                                       |
| Visual-composition semantic parameter | Render-realization identity unless another scientific spec says otherwise |
| DPI                                   | Render-realization identity                                               |
| SVG vs PNG                            | Render-realization identity                                               |
| Telemetry cadence                     | Operational request/plan identity                                         |
| Buffer/drop policy                    | Operational request/plan identity                                         |
| Filesystem export path                | Placement; not scientific projection identity                             |
| Absolute local source path            | Diagnostic provenance only                                                |

The generic identity and provenance authorities remain definitive.

## Operation integration

Figure configuration is consumed by existing operations:

```text
data inspect
    request-level inspection figure

tasks inspect
    request-level corpus figure

train run
    request-level FigureSchedule

evaluate run
    optional request-level diagnostics

analyze run
    analysis-defined scientific results/projection capabilities
    + request-level realization

report build
    report-profile presentation selection
    + request-level placement/export
```

Exact fields belong to the corresponding operation schemas and reference this common classification.

## Stability gate

A stable serialized figure configuration contract requires:

1. one implemented vertical slice;
2. an exhaustive operation field catalogue;
3. deterministic selection semantics;
4. fixed figure-specific identity classification;
5. clear separation of selection, visual composition, rendering, and sink;
6. telemetry buffering/failure policy where applicable;
7. CLI/Python equivalence tests;
8. no backend-native configuration trees in public resolved records.

Until these conditions are met, serialized figure configuration remains provisional.

## Related specifications

- [`Configuration interface`](index.md)
- [`Configuration model`](model.md)
- [`Files and overrides`](files-and-overrides.md)
- [`Resolution`](resolution.md)
- [`Identities and provenance`](identities-and-provenance.md)
- [`Framework figures`](../../framework/figures/index.md)
