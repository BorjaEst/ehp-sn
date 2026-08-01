---
title: Evaluation interface
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Evaluation interface

The Python evaluation interface evaluates one compatible checkpoint under one named regime declared by an experiment.

A successful call returns only after an immutable evaluation artifact containing the declared outputs has been committed.

## Canonical call forms

Convenience form:

```python
evaluation = evaluate(
    experiment,
    checkpoint=training.best_checkpoint,
    regime="test",
    seeds=SeedConfiguration.from_master(43),
)
```

Explicit request form:

```python
request = EvaluationRequest(
    experiment=experiment,
    checkpoint=training.best_checkpoint,
    regime="test",
    seeds=SeedConfiguration.from_master(43),
)

evaluation = evaluate(request)
```

Explicit planned execution:

```python
plan = plan_evaluation(request)
report = validate_evaluation(plan, level="resources")
evaluation = evaluate(plan, validation=report)
```

The convenience form constructs one canonical `EvaluationRequest`. A request or plan cannot be combined with additional evaluation fields. Duplicate or ambiguous values are rejected.

## Public types and capabilities

| Capability                   | Public contract                                                                        | Status                                           |
| ---------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Execute evaluation           | `evaluate(experiment_or_request_or_plan, *, validation=None, ...) -> EvaluationResult` | Established target; overload details provisional |
| Represent one invocation     | `EvaluationRequest`                                                                    | Established public concept                       |
| Represent resolved execution | `ExecutionPlan`                                                                        | Established public concept                       |
| Report validation            | `ValidationReport`                                                                     | Established public concept                       |
| Resolve a request            | `plan_evaluation(request)`                                                             | Proposed helper symbol                           |
| Validate a plan              | `validate_evaluation(plan, level=...)`                                                 | Proposed helper symbol                           |
| Return success               | `EvaluationResult`                                                                     | Stable result type contract                      |

## Request and regime ownership

An `EvaluationRequest` contains:

- experiment definition or `ExperimentRef`;
- `CheckpointRef`;
- selected named regime;
- optional permitted evaluation-corpus override;
- declared evaluation seed roles;
- runtime configuration;
- output root;
- optional diagnostic case bound.

The regime owns corpus or split requirements, case selection, metrics, validity rules, trace requirements, and recording policy. Invocation options select a regime but do not redefine its scientific meaning.

## Corpus and checkpoint resolution

Corpus resolution follows deterministic precedence:

1. explicitly permitted request corpus;
2. exact regime-declared reference;
3. configured workspace binding;
4. otherwise fail.

The plan records exact corpus reference, digest, and split identity. Automatic selection among arbitrary compatible artifacts is prohibited.

The checkpoint must be a `CheckpointRef` or an explicitly separate invocation-location argument where supported. Validation resolves the parent training-run artifact and checks model family, experiment compatibility, lineage, and integrity.

## Seed roles

Evaluation resolves only roles declared by the regime and runtime contract, such as case sampling or stochastic evaluation behavior. Unsupported explicit roles are rejected. Corpus-generation seeds belong to corpus identity.

## Evaluation plan

The immutable `ExecutionPlan` contains:

- plan and request identities;
- canonical experiment reference and resolved digest;
- checkpoint and parent run identities;
- corpus reference, digest, and split;
- selected regime and purpose;
- metric, validity, trace, prediction, and case-recording declarations;
- role-specific seeds;
- runtime requirements;
- output and artifact policy;
- identity-affecting fingerprints.

Planning runs no inference and contains no live model or backend objects.

## Validation guarantees

Evaluation uses the shared levels:

| Level       | Additional guarantee                                                                                                                                                 |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CONFIG`    | Experiment, regime, checkpoint metadata requirements, seed roles, diagnostic bounds, and declared outputs are semantically valid.                                    |
| `RESOURCES` | Checkpoint, corpus, split, metrics, validity rules, trace implementations, runtime prerequisites, and destination constraints resolve and satisfy required metadata. |
| `BUILD`     | Model, task, binding, metric, trace, and runtime components can be constructed and connected without executing an evaluation case.                                   |

Execution rechecks volatile resource identities, integrity metadata, destination state, and runtime capabilities.

## Execution consistency

`evaluate(plan, validation=report)` executes the exact plan or fails. It never silently substitutes another checkpoint, corpus, split, regime, case bound, or seed allocation.

A changed identity fingerprint or stale prerequisite raises `StalePlanError` before inference begins.

## Complete and diagnostic evaluation

```python
diagnostic = evaluate(
    experiment,
    checkpoint=training.best_checkpoint,
    regime="test",
    max_cases=32,
)
```

A bounded call is a distinct diagnostic evaluation unless the regime explicitly declares that bound complete. It has a distinct request, plan, execution, and artifact identity and cannot satisfy complete-regime or reference-result requirements.

## Metric result model

`evaluation.metrics` is an immutable `Mapping[str, MetricResult]` containing aggregate results declared by the selected regime.

`MetricResult` is portable metadata with stable attributes:

| Attribute  | Type                                             | Meaning                                          |
| ---------- | ------------------------------------------------ | ------------------------------------------------ | --------------------------------------------- |
| `name`     | `str`                                            | Canonical metric identifier.                     |
| `value`    | JSON-compatible scalar or small structured value | Aggregate result suitable for direct inspection. |
| `count`    | `int                                             | None`                                            | Number of contributing cases when meaningful. |
| `unit`     | `str                                             | None`                                            | Declared unit when applicable.                |
| `metadata` | immutable mapping                                | Small declared contextual fields.                |

Per-case metric values, confidence samples, predictions, traces, and large arrays remain artifact resources and are not embedded in the mapping.

## `EvaluationResult`

`EvaluationResult` is immutable and returned only after publication succeeds.

| Attribute                   | Type                                   | Behavior                                                              |
| --------------------------- | -------------------------------------- | --------------------------------------------------------------------- |
| `status`                    | `OperationStatus`                      | Successful terminal status.                                           |
| `artifact`                  | `ArtifactRef`                          | Authoritative committed evaluation artifact.                          |
| `plan`                      | `ExecutionPlan`                        | Exact executed plan or portable equivalent.                           |
| `validation`                | `ValidationReport`                     | Validation report used for execution.                                 |
| `metrics`                   | immutable `Mapping[str, MetricResult]` | Aggregate declared metrics; empty only when the regime declares none. |
| `purpose`                   | `EvaluationPurpose`                    | `complete` or `diagnostic`.                                           |
| `satisfies_complete_regime` | `bool`                                 | Whether this result satisfies the complete selected regime.           |
| `cases`                     | `CaseCollection`                       | Lazy or bounded case accessor when supported.                         |
| `traces`                    | `TraceCollection`                      | Lazy or bounded trace accessor when supported.                        |
| `predictions`               | `PredictionCollection`                 | Lazy or bounded prediction accessor when supported.                   |

If the regime does not support cases, traces, or predictions, accessing that capability raises `CapabilityUnavailableError`. If supported but zero records were retained, the accessor represents an empty collection. Missing declared resources raise `ResourceError` or `ArtifactIntegrityError`.

`to_record()` returns JSON-compatible portable metadata without materializing large resources.

## Publication failure

If inference and metric aggregation complete but authoritative commitment fails, `evaluate()` raises `PublicationError` and returns no `EvaluationResult`.

The exception exposes operation, request and plan identities, whether computation completed, structured diagnostics, and optional non-authoritative staging or recovery information.

## Interruption

On `KeyboardInterrupt`:

- cleanup runs deterministically;
- `KeyboardInterrupt` is re-raised;
- no successful result or committed evaluation artifact is reported unless commitment completed before interruption;
- staging and diagnostic records remain non-authoritative;
- evaluation is not automatically resumed.

## Exceptions

`evaluate()` may raise:

- `ConfigurationError`;
- `CompatibilityError`;
- `ResourceError`, `ArtifactNotFoundError`, or `ArtifactIntegrityError`;
- `ValidationError` or `StalePlanError`;
- `OutputConflictError`;
- `ExecutionError` for inference or aggregation failure;
- `PublicationError`;
- `CapabilityUnavailableError` when optional accessors are used on unsupported outputs.

## Related interfaces

- [Experiments](experiments.md)
- [Training](training.md)
- [Artifacts](artifacts.md)
- [Analysis](analysis.md)
- [Shared conventions](conventions.md)
- [Framework semantics](../../framework/_index.md)
