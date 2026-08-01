---
title: Python interface conventions
authority: normative
status: specified
api_stability: provisional
---

# Python interface conventions

This page defines conventions that apply identically to multiple public Python operations.

## Calling conventions

The primary scientific object may be positional. Invocation-specific options are keyword-only.

```python
training = train(
    experiment,
    seeds=...,
    runtime=...,
    output=...,
)
```

Public signatures do not use ambiguous positional sequences for seeds, runtime, checkpoints, inputs, outputs, or tracking configuration.

## Nominal logical references

Durable semantic identities use nominal reference types:

```python
ExperimentRef
ArtifactRef
CheckpointRef
AnalysisRef
TaskRef
ModelRef
BindingRef
```

Each type has one canonical versioned string form and a parsing capability:

```python
analysis_ref = AnalysisRef.parse("analysis:memory-diagnostics/v1")
```

Public operations may accept either the nominal reference type or its canonical string form. Strings are parsed deterministically before request resolution. A semantic reference parameter does not also accept arbitrary paths or unrelated objects.

Filesystem invocation locations, where supported, use distinct parameters or constructors. For example, a checkpoint path is not silently interpreted as a `CheckpointRef` by an unrestricted `str | Path | object` union.

The complete reference grammar belongs to the framework identity specifications. Python parsing failures are configuration failures.

## Typed values and shortcuts

Convenience strings may represent common typed values only when the normalization is unique and documented:

```text
runtime="cuda"
≡ RuntimeConfiguration(device="cuda")

tracking="local"
≡ the framework-owned local tracking configuration
```

The runtime shortcut does not imply a hardware profile, distributed launch policy, or precision choice. The tracking shortcut does not expose a backend-native client.

An `output` path selects physical placement. It is recorded in invocation provenance but is not portable scientific identity. New immutable artifacts allocate distinct locations rather than overwriting committed output.

## Canonical request model

Each operation has one canonical request type:

```python
TrainingRequest
EvaluationRequest
AnalysisRequest
```

Convenience invocation is exactly request construction followed by normal execution:

```text
train(experiment, **options)
    ≡ train(TrainingRequest(experiment=experiment, **options))
```

The following rules are normative:

- convenience and explicit forms use identical defaults and resolution;
- a request or plan cannot be combined with additional operation fields;
- duplicate semantic values are rejected rather than merged;
- a shortcut and explicit typed value for the same field cannot both be supplied;
- unknown fields are rejected;
- no field changes meaning based on call spelling.

## Request resolution

Unresolved requests may contain canonical strings, nominal references, documented shortcuts, and explicit invocation locations. Resolution produces typed effective values and exact logical identities.

Resolved requests are immutable and contain no unresolved aliases or ambiguous choices. Their identity includes all fields that affect the intended operation, but remains distinct from experiment identity and execution provenance.

## Execution plans

An `ExecutionPlan` is an immutable, portable description of one fully resolved operation. It contains at least:

- operation kind and plan identity;
- request identity and resolved request metadata;
- canonical experiment reference and resolved experiment digest where applicable;
- exact corpus, artifact, checkpoint, and analysis references;
- intended output destination and artifact policy;
- required runtime capabilities;
- identity-affecting fingerprints;
- compatibility decisions and warnings.

A plan does not contain mutable runtime objects, backend clients, open file handles, or live model instances.

Two plans are equal only when their canonical portable plan records are equal. A plan's identity is stable across processes. Plans may be serialized as JSON-compatible metadata records; pickle stability is not guaranteed.

## Validation reports

A `ValidationReport` is immutable and applies to one exact plan identity and one validation level. It contains at least:

- plan identity;
- requested and completed validation level;
- validity outcome;
- completed checks and postconditions;
- warnings and failures;
- volatile fingerprints observed during validation;
- validation timestamp and environment summary where relevant.

A report for another plan, another plan fingerprint, or a lower level cannot satisfy execution requirements.

## Validation levels

The common levels are defined by postconditions:

| Level       | Guaranteed postconditions                                                                                                                                                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `CONFIG`    | All request fields, definitions, specializations, canonical references, and semantic compatibility rules are valid and fully resolvable without requiring external payload access.         |
| `RESOURCES` | `CONFIG` holds, and every required external reference resolves to an available resource whose declared identity, schema, integrity metadata, and destination constraints satisfy the plan. |
| `BUILD`     | `RESOURCES` holds, and the selected public runtime components can be constructed and connected for the planned operation without beginning scientific execution.                           |

`BUILD` does not include a training step, evaluation case, analysis computation, or backend-specific one-batch smoke test unless a future operation specification explicitly adds such a guarantee.

Higher levels include lower-level postconditions.

## Plan execution and staleness

Execution uses the exact resolved scientific inputs represented by the plan or fails. It never silently replans or substitutes another compatible resource.

Execution always rechecks volatile prerequisites, including:

- referenced resource existence and identity fingerprints;
- checkpoint and corpus integrity metadata;
- destination availability and conflict state;
- required runtime capability availability;
- validity of any supplied validation report.

If an identity-affecting input or validated prerequisite changed, execution raises `StalePlanError` before scientific execution. The caller must create and validate a new plan.

Convenience calls internally create, validate, and record the exact plan that was executed.

## Structured results

Successful operations return immutable result objects:

```python
TrainingResult
EvaluationResult
AnalysisResult
```

A successful result is returned only after authoritative artifact publication succeeds. Result objects contain portable metadata, nominal references, and optional lazy artifact-backed accessors. They do not embed large predictions, traces, arrays, or per-case datasets.

All result types provide:

- `status`, equal to the successful terminal status;
- `artifact`, the committed authoritative `ArtifactRef`;
- `plan`, the executed `ExecutionPlan` or its portable record;
- `validation`, the validation report used for execution;
- `to_record()`, returning JSON-compatible portable metadata.

Pickle compatibility is not part of the stable contract. Reconstructing rich lazy views in another process requires loading the authoritative artifact through the documented artifact loader.

## Optional and unavailable outputs

The interface uses one consistent policy:

- an optional singular reference that was not produced is `None`;
- a supported collection with zero members is an empty immutable collection;
- a capability not supported by the operation, regime, analysis, or artifact kind raises `CapabilityUnavailableError` when accessed;
- a declared resource that should exist but is missing or invalid raises `ResourceError` or `ArtifactIntegrityError`;
- large resources are represented by lazy or bounded handles rather than materialized automatically.

Capability queries must be available through the result or artifact metadata so callers can avoid exception-driven discovery.

## Identity categories

| Identity                | Python representation                           | Used for                                                        |
| ----------------------- | ----------------------------------------------- | --------------------------------------------------------------- |
| Experiment identity     | `ExperimentRef` plus resolved experiment digest | Scientific definition comparison and compatibility              |
| Request identity        | Resolved request identity                       | Invocation comparison and plan construction                     |
| Plan identity           | `ExecutionPlan.id`                              | Validation binding and stale-plan detection                     |
| Execution provenance    | Result and manifest provenance                  | Reproducibility, runtime record, and audit                      |
| Artifact identity       | `ArtifactRef`                                   | Durable selection, downstream inputs, and destination conflicts |
| Artifact content digest | Manifest content digest                         | Integrity and byte/content-level verification                   |

Equal experiments do not imply equal results. Scientific equivalence does not imply byte-identical artifacts. Runtime configuration is not part of experiment identity, but runtime and environment provenance remain part of reproducibility records.

## Backend-independent boundary

Stable scientific contracts do not expose Hydra `DictConfig`, Lightning Fabric objects, MLflow run objects, backend checkpoint dictionaries, distributed-framework strategy instances, Typer contexts, or backend-native exceptions as required semantic values.

Backend-specific objects may exist behind adapters. Backend exceptions may be chained as causes, but callers can handle normal failures through EHP-SN exception types and structured fields.

## Exception hierarchy

The stable public hierarchy is semantic:

```text
EhpSnError
├── ConfigurationError
├── CompatibilityError
├── ResourceError
│   ├── ArtifactNotFoundError
│   └── ArtifactIntegrityError
├── ValidationError
│   └── StalePlanError
├── ExecutionError
├── OutputConflictError
├── PublicationError
└── CapabilityUnavailableError
```

All `EhpSnError` instances expose:

- `category`;
- `operation` where applicable;
- an actionable message;
- structured `details`;
- related request, plan, or artifact references when available.

`PublicationError` additionally exposes whether scientific computation completed and may expose diagnostic or staging information. Such information is not an authoritative artifact and must not be passed downstream as one.

`KeyboardInterrupt` is not wrapped in `ExecutionError`. It is re-raised after cleanup. A future programmatic cancellation API may define a separate cancellation exception; none is part of the initial interface.

## Publication and successful return

The commit boundary is part of every executing call:

```text
scientific computation succeeds
    ↓
manifest and resources are finalized
    ↓
authoritative artifact is atomically committed
    ↓
successful result is returned
```

If publication fails, no successful result is returned. The operation raises `PublicationError`. An external tracker entry, staging directory, or diagnostic record does not substitute for a committed artifact.

## Interruption

For `train()`, `evaluate()`, and `analyze()`:

- `KeyboardInterrupt` remains distinguishable and is re-raised;
- deterministic cleanup runs before control returns to the caller;
- no uncommitted directory is presented as a completed artifact;
- an optional diagnostic interruption record may be written but is non-authoritative;
- only checkpoints committed before interruption may be resumed;
- automatic checkpoint-on-interrupt is not part of the initial contract;
- interruption does not return a successful result object.

## Synchronous execution

The initial public API is synchronous. A call returns only after success, failure, or interruption. Internal distributed execution does not change this caller contract.

## Python and CLI equivalence

Equivalent Python and CLI invocations produce scientifically and operationally equivalent resolved requests and plans, excluding documented frontend metadata. Backend or frontend differences must not alter experiment, data, checkpoint, seed, regime, validation, or artifact-policy semantics.

## Non-goals

This page does not define artifact-format schemas, backend implementation, extension inheritance, asynchronous job handles, generic batch orchestration, or operation-specific scientific fields.
