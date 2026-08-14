---
title: Python interface
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Python interface

The EHP-SN Python interface exposes supported scientific workflows to notebooks, scripts, tests, and research applications.

It defines the public programming model: the objects callers construct, how requests are resolved into immutable plans, how plans are validated and executed, what operations return, and how committed artifacts are passed downstream. Exact implementation signatures beyond the contracts fixed here belong to the generated API reference.

## Primary workflow

```python
from ehp_sn import evaluate, train
from ehp_sn.protocols import TrainingProtocol
from ehp_sn.reproducibility import SeedConfiguration
from ehp_research.experiments.arena_tem import arena_tem_v1

experiment = arena_tem_v1(
    training=TrainingProtocol(max_steps=50_000),
)

training = train(
    experiment,
    seeds=SeedConfiguration.from_master(42),
    runtime="cuda",
    tracking="local",
    output="runs/arena-tem-v1",
)

evaluation = evaluate(
    experiment,
    checkpoint=training.best_checkpoint,
    regime="test",
    seeds=SeedConfiguration.from_master(43),
)

metrics = evaluation.metrics
# Immutable mapping from metric identifiers to aggregate MetricResult values.
# Per-case values and large arrays remain artifact resources.
print(metrics)
```

`runtime="cuda"` normalizes to a runtime configuration with `device="cuda"`. It does not select a named hardware profile.

The training request resolves the experiment's task-corpus requirement to one exact corpus artifact before execution. The resolved corpus identity is recorded in the plan, result metadata, and committed run manifest.

## Canonical analysis contract

The initial Python interface executes one versioned analysis per call:

```python
from ehp_sn import analyze

analysis = analyze(
    "analysis:memory-diagnostics/v1",
    inputs=[evaluation.artifact],
)
```

The first argument is an `AnalysisRef` or its canonical string form. `inputs` is an ordered sequence whose cardinality and accepted artifact kinds are declared by the analysis definition. One call returns one `AnalysisResult` and commits at most one analysis artifact. The initial interface does not accept an `analyses=[...]` batch argument. Multiple analyses are orchestrated with ordinary Python iteration.

## Programming model

```text
ExperimentDefinition
    immutable scientific composition and declared data requirements

Request
    one unresolved or partially resolved invocation

ExecutionPlan
    immutable, fully resolved operation and identity fingerprints

ValidationReport
    immutable checks for one exact plan and validation level

TrainingResult / EvaluationResult / AnalysisResult
    portable metadata plus typed references and lazy artifact-backed views

ArtifactManifest
    authoritative durable record
```

An `ExperimentRef` identifies a package-owned experiment specification. A resolved experiment retains that reference and also has a digest of its complete effective scientific definition. Supported scientific specialization changes the resolved digest even when the canonical experiment reference remains unchanged.

## Canonical request construction

Each operation has one canonical request type. Convenience calls are syntax for constructing that request and then following the same resolution, validation, execution, and publication path.

```text
train(experiment, **options)
    ≡ train(TrainingRequest(experiment=experiment, **options))
```

Passing a request or plan together with additional operation fields is invalid. The interface never merges duplicate values from two sources or applies different semantics based on call spelling.

## Plan, validate, execute

The explicit lifecycle is:

```python
request = TrainingRequest(...)
plan = plan_training(request)
report = validate_training(plan, level="resources")
result = train(plan, validation=report)
```

Exact helper names remain provisional, but the semantics are normative:

- plans are immutable and identify exact resolved scientific inputs;
- validation reports apply to one plan identity and one validation level;
- execution never silently replans;
- volatile prerequisites are rechecked at execution time;
- stale plans or reports fail before scientific execution begins;
- convenience execution internally records the exact plan that was executed.

## Package ownership

```text
ehp_sn
    workflow operations
    request resolution and validation
    execution services
    artifacts, references, results, and provenance
    input/output adapters

ehp_research
    concrete experiments
    substrates and tasks
    models; resolved task-model bindings
    metrics and analyses
```

## Result chaining

Returned references are accepted directly by compatible downstream operations:

```python
checkpoint = training.best_checkpoint

if checkpoint is not None:
    evaluation = evaluate(
        experiment,
        checkpoint=checkpoint,
        regime="test",
    )

artifact = evaluation.artifact
```

Checkpoint references identify checkpoint resources owned by committed training-run artifacts. They preserve the parent run identity and checkpoint resource identity.

## Result and artifact authority

A normal result object is returned only after authoritative artifact commitment succeeds. Result objects are immutable, contain portable metadata and logical references, and may expose lazy artifact-backed collections. Large predictions, traces, arrays, and per-case values are not embedded in serialized result metadata.

Result objects may be converted to a JSON-compatible metadata record through the operation's documented serialization capability. Pickle compatibility is not part of the stable interface. The committed artifact manifest remains authoritative if in-memory result metadata and durable state are compared.

## Interruption and publication

`KeyboardInterrupt` remains distinguishable and is re-raised after deterministic cleanup. It is not wrapped as an ordinary execution failure.

An interrupted operation never returns a successful result or presents uncommitted staging output as a committed artifact. Only checkpoints already committed before interruption are eligible for resume. Automatic checkpoint-on-interrupt is not part of the initial contract.

If scientific computation completes but artifact publication fails, the operation raises `PublicationError` and returns no successful result. Recoverable diagnostic or staging information exposed by the exception is explicitly non-authoritative.

## Public-interface status

The following symbols are established interface targets:

| Symbol              | Descriptive label                                  |
| ------------------- | -------------------------------------------------- |
| `train`             | Established target                                 |
| `evaluate`          | Established target                                 |
| `analyze`           | Established target; one-analysis-per-call contract |
| `TrainingProtocol`  | Established target                                 |
| `SeedConfiguration` | Established target                                 |
| `arena_tem_v1`      | Established target                                 |

Planning, validation, and artifact-loading helper names remain provisional unless marked otherwise in their owning pages.

## Per-symbol descriptive labels

The labels below are descriptive narrative, not a formal maturity vocabulary: they describe where one public symbol currently sits on the path toward this page's single `api_stability` value, at finer grain than that one page-level field expresses. They do not constitute a second canonical dimension, and a symbol's normative status is `authority: normative` plus this page's `api_stability`, not the label itself.

| Descriptive label       | Meaning                                                                                                |
| ----------------------- | ------------------------------------------------------------------------------------------------------ |
| **Established target**  | The operation's role, workflow position, argument model, and observable behavior are normative.        |
| **Established concept** | The semantic object and responsibilities are normative; the final concrete type name may still change. |
| **Required capability** | The behavior must be exposed, although a non-core helper spelling may change.                          |
| **Proposed symbol**     | A candidate spelling used to make the programming model concrete.                                      |
| **Implemented**         | Code exists for the documented capability.                                                             |
| **Validated**           | Acceptance tests confirm the implementation against this contract.                                     |

`authority: normative` applies to behavior, stable public fields fixed by these pages, and ownership boundaries. `api_stability: provisional` permits changes to explicitly provisional helpers during implementation; it does not permit changing the canonical request, result, interruption, publication, or one-analysis-per-call semantics without revising this specification.

## Extension scope

EHP-SN is intended to support custom tasks, models, adapters, bindings, metrics, analyses, and experiment factories. Public registration, plugin, resolver, inheritance, and custom-component protocols remain provisional until Arena–TEM and MazeHard–HRM demonstrate the shared contract. No stable extension base classes are defined here.

## Current execution scope

The public workflow API is synchronous. Study orchestration remains reducible to ordinary requests. The initial interface does not define asynchronous job handles, remote futures, callback protocols, generic bulk operations, or backend-specific study objects.

## Documentation boundaries

- These pages own cross-object Python behavior and supported programming patterns.
- Generated API reference owns exact implemented signatures, overloads, and low-level per-symbol details.
- Framework specifications own cross-interface identity, compatibility, reproducibility, and serialized artifact semantics.
- CLI documentation owns shell syntax, process presentation, and exit codes.
- Scientific documentation owns task, model, metric, and protocol meaning.

## Interface documents

- [Experiments](experiments.md)
- [Training](training.md)
- [Evaluation](evaluation.md)
- [Artifacts](artifacts.md)
- [Shared conventions](conventions.md)
- [Analysis](analysis.md)

## Python and CLI equivalence

Equivalent Python and CLI invocations produce scientifically and operationally equivalent resolved requests and plans, excluding documented frontend metadata. Backend or frontend differences must not alter experiment, data, checkpoint, seed, regime, validation, or artifact-policy semantics.

## Non-goals

This page does not define backend integrations, artifact-format layouts, concrete extension protocols, asynchronous orchestration, or exhaustive generated API entries.
