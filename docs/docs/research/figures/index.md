---
title: Research figures
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Research figures

## Normative summary

`ehp_research.figures` contains reusable scientific visualization capabilities whose scientific meaning remains coherent independently of one concrete experiment.

Research figures implement the generic contracts in `ehp_sn.figures`.

They own reusable scientific source requirements, scientific preparation, domain-specific `FigureData`, and scientific visual-composition semantics.

They do not own generic source resolution, selection mechanics, generic render execution, sinks, artifact commitment, configuration precedence, or workspace experiment composition.

## Placement rule

A figure belongs in `ehp_research.figures` when:

> its scientific interpretation remains meaningful even if the current concrete experiment does not exist.

Examples:

```text
Arena task overview
MazeHard task overview
Dagflow graph overview
HPC place-field summary
MEC grid summary
HRM latent-state dynamics
```

A figure belongs to `experiments/<experiment>/vN/` when its meaning requires a particular cross-component composition.

Examples:

```text
Arena + TEM memory-pathway comparison
MazeHard + HRM reasoning-cycle comparison
MazeHard + HRM-RL deliberation-value comparison
Routebind + HRM joint semantic-spatial reasoning figure
```

## Relationship to framework figures

The framework owns:

```text
FigureSpec contract
FigureInputContract mechanics
source resolution
selection mechanics
FigureProjection envelope
RenderContext
generic visual primitives
rendering realization and serialization
sinks
telemetry mechanics
generic identity/provenance mechanics
reusable contract-level visual helpers and contract views
generic graph primitives / deterministic layouts
```

Research owns:

```text
scientific source-role requirements
research-specific FigureData
scientific preparation
scientific visual-composition semantics
research-specific visual primitives
scientific axes/labels/annotations
reusable scientific FigureSpec instances
```

## Reusable research FigureSpec

A reusable research figure should define:

- canonical figure reference;
- scientific purpose;
- maturity;
- supported framework `FigureUse` values;
- required semantic source roles;
- accepted source schemas/channels/observables;
- supported selection semantics;
- prepared-data schema;
- preparation contract/version;
- scientific visual-composition contract/version;
- scientific labels/interpretation;
- validation/conformance requirements;
- related task/model/analysis specifications.

Generic framework mechanics must be referenced rather than restated.

## FigureData ownership

Research-owned prepared-data types may include:

```text
ArenaOverviewData
MazeHardOverviewData
DagflowOverviewData
HpcPlaceSummaryData
MecGridSummaryData
HrmLatentDynamicsData
```

These names remain illustrative until concrete figure specifications are created.

A research `FigureData` type contains only already-established scientific information required for the declared projection.

It must not become a hidden analysis result container whose quantities are created only because plotting requested them.

## Scientific preparation

Research preparation may:

- retrieve and align resolved scientific entities;
- derive presentation coordinates from already-defined task/topology coordinates;
- map declared categorical identities to established scientific labels;
- assemble already-computed research results into immutable `FigureData`.

It must not:

- rerun model inference;
- compute missing metrics;
- train probes;
- perform statistical tests;
- repair invalid outputs;
- infer privileged information not permitted by the input contract.

If a desired figure needs a scientific quantity that is absent, that quantity must first be produced by the appropriate task/evaluation/analysis authority.

## Scientific visual composition

Research scientific visual composition maps an existing `FigureProjection` into framework visual primitives.

Example:

```text
HpcPlaceSummaryData
        ↓
research visual composition
        ↓
continuous raster panels
field-centre markers
scientific labels
shared colorbar declaration
        ↓
framework visual primitives
        ↓
ehp_sn render execution
```

This is different from backend rendering.

Research code owns the scientific meaning of:

- which prepared variable maps to which mark;
- scientific axes and labels;
- scientific legend semantics;
- domain-specific annotations;
- scientifically meaningful panel relationships.

The framework owns rendering-realization policy (`RenderProfile`) and serialization, and may provide domain-neutral Matplotlib drawing helpers; Matplotlib itself owns the concrete graphics object model.

## Research-specific visual primitives

`ehp_research.figures` may define reusable scientific primitives built from framework primitives.

Examples:

```text
place-field rate-map view
place-field-centre overlay
grid autocorrelation view
RSA matrix semantics
maze route support
semantic transition overlay
Arena replay trajectory semantics
HRM deliberation trajectory semantics
```

A research primitive must have reusable scientific meaning independent of one experiment.

## References and naming

Reusable scientific figures use canonical framework figure references, conceptually:

```text
figure:arena-task-overview/v1
figure:mazehard-task-overview/v1
figure:hpc-place-summary/v1
figure:hrm-latent-dynamics/v1
```

The exact reference grammar remains owned by `framework/references.md`.

Research figure names must not use experiment names merely to host an experiment-local figure.

## Registration and discovery

`ehp_research.registration` exposes reusable research figures through the generic framework registration/discovery mechanism.

It must not register experiment-local joint figures.

The framework must not directly import `ehp_research.figures`.

Generic duplicate-reference and catalogue conflict rules remain owned by the framework registry/discovery authority.

## Supported uses

A research figure declares compatibility with a framework `FigureUse` contract.

Examples:

```text
Arena task overview
    INSPECTION
    REPORT
    EXPLORATION

HRM latent dynamics
    TELEMETRY
    ANALYSIS
    REPORT
    EXPLORATION
```

Supported use does not determine render profile, destination, cadence, or fatality.

## Relationship to tasks

Task figures may visualize task-owned semantics such as:

- public inputs;
- targets;
- privileged information when the requesting context permits it;
- trajectories;
- routes;
- queries;
- task annotations.

Visualization must preserve the task information regime. Researcher-visible privileged information must not leak into model inputs merely because the same figure displays it.

## Relationship to models

Model figures consume declared model-native outputs, observables, and traces.

They must not depend on undocumented implementation tensors.

A visualization requiring a new scientifically meaningful internal quantity must first establish that observable in the applicable model/trace specification.

## Relationship to analyses

Figures over derived scientific quantities consume analysis results rather than recomputing them.

Example:

```text
AnalysisArtifact
    spatial_information
    rate_maps
    field_centres
        ↓
HPC place-summary figure
    select
    prepare
    compose
    render
```

The figure explains/presents the result; it does not establish the result.

## Relationship to experiments

Experiment-local figures may reuse framework primitives and reusable research primitives.

Example:

```text
MazeHard problem view
    reusable research

HRM latent-dynamics view
    reusable research

MazeHard + HRM joint reasoning figure
    experiment-local
```

## Documentation policy

This index establishes the reusable research-figure boundary.

Individual specifications such as:

```text
arena-task-overview-v1.md
hrm-latent-dynamics-v1.md
```

should be added only when the corresponding figure capability is actually specified.

The project should not pre-create files for hypothetical figures.

## Conformance

A reusable research figure conforms when:

1. its scientific meaning is independent of one concrete experiment;
2. it declares semantic sources through framework input contracts;
3. its selection follows framework deterministic-selection rules;
4. its preparation performs no hidden analysis or inference;
5. its `FigureData` semantics are defined;
6. its visual composition maps only already-prepared science to framework primitives;
7. generic rendering/sink mechanics remain framework-owned;
8. registration uses generic discovery;
9. generic identity, provenance, artifact, and configuration mechanics are referenced rather than redefined.

## Related specifications

- [`Framework figures`](../../framework/figures/index.md)
- [`Figure projection`](../../framework/figures/projection.md)
- [`Figure rendering`](../../framework/figures/rendering.md)
- [`Figure integration`](../../framework/figures/integration.md)
- [`Research tasks`](../tasks/index.md)
- [`Research models`](../models/index.md)
- [`Python figures`](../../interfaces/python/figures.md)
