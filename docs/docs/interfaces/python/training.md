---
title: Training interface
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Training interface

The Python training interface resolves, plans, validates, and executes one training invocation from an experiment definition.

Training consumes one exact resolved experiment and task-corpus artifact. A successful call returns only after a committed training-run artifact exists.

## Canonical call forms

Convenience form:

```python
training = train(
    experiment,
    seeds=SeedConfiguration.from_master(42),
    runtime="cuda",
    tracking="local",
    output="runs/arena-tem-v1",
)
```

Explicit request form:

```python
request = TrainingRequest(
    experiment=experiment,
    seeds=SeedConfiguration.from_master(42),
    runtime=RuntimeConfiguration(device="cuda"),
    tracking=LocalTrackingConfiguration(),
    output=ArtifactDestination("runs/arena-tem-v1"),
)

training = train(request)
```

Explicit planned execution:

```python
plan = plan_training(request)
report = validate_training(plan, level="resources")
training = train(plan, validation=report)
```

The convenience form is exactly request construction followed by the same planning, validation, execution, and publication path. Passing a request or plan together with additional training fields is invalid. Duplicate or ambiguous values are rejected rather than merged.

## Public types and capabilities

| Capability                   | Public contract                                                                   | Status                                           |
| ---------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------ |
| Execute training             | `train(experiment_or_request_or_plan, *, validation=None, ...) -> TrainingResult` | Established target; overload details provisional |
| Represent one invocation     | `TrainingRequest`                                                                 | Established public concept                       |
| Represent resolved execution | `ExecutionPlan`                                                                   | Established public concept                       |
| Report validation            | `ValidationReport`                                                                | Established public concept                       |
| Resolve a request            | `plan_training(request)`                                                          | Proposed helper symbol                           |
| Validate a plan              | `validate_training(plan, level=...)`                                              | Proposed helper symbol                           |
| Return success               | `TrainingResult`                                                                  | Stable result type contract                      |

## Request fields

A `TrainingRequest` contains:

- experiment definition or `ExperimentRef`;
- optional permitted corpus override;
- master and supported role-specific seeds;
- runtime configuration;
- tracking configuration;
- output root;
- optional `resume` checkpoint;
- optional `init_from` checkpoint.

Requests are immutable after construction. Unknown fields and conflicting representations of the same field are rejected.

## Corpus resolution

Resolution uses this order:

1. explicit request corpus, when the experiment permits replacement;
2. exact corpus declared by the resolved experiment;
3. configured workspace binding;
4. otherwise fail.

The plan records the exact corpus `ArtifactRef`, content digest, schema compatibility, and resolution source. Automatic selection among arbitrary compatible artifacts is prohibited.

## Seed roles

`SeedConfiguration.from_master(42)` derives only roles declared by the training protocol and runtime contract, such as initialization, training-order sampling, stochastic model operations, and worker derivation.

Unsupported explicit roles are rejected. Corpus-generation seeds belong to corpus identity, not the training request.

## Training plan

The immutable training `ExecutionPlan` contains:

- plan and request identities;
- canonical experiment reference and resolved digest;
- exact corpus reference and digest;
- effective training protocol;
- resolved role-specific seeds;
- resume or initialization identity;
- runtime requirements;
- output root and planned artifact policy;
- compatibility decisions;
- identity-affecting fingerprints.

Planning performs no training step, creates no committed output, and contains no live runtime objects.

## Validation guarantees

Training supports the shared levels from [Python interface conventions](conventions.md#validation-levels).

Training-specific postconditions are:

| Level       | Additional guarantee                                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `CONFIG`    | Experiment, corpus requirement, seed roles, resume/init exclusivity, protocol, and component compatibility are valid.                |
| `RESOURCES` | Corpus and checkpoint references resolve with required metadata; device and destination prerequisites are available.                 |
| `BUILD`     | Task, binding, model, objective, and selected runtime components can be constructed and connected without executing a training step. |

A validation report is bound to the exact plan identity. Execution rechecks volatile resource, checkpoint, destination, and runtime conditions.

## Execution consistency

`train(plan, validation=report)` executes the exact plan or fails. It never silently resolves another corpus, substitutes another checkpoint, changes seeds, or allocates a materially different request.

If an identity-bearing plan dependency changed, execution raises `StalePlanError` before the first training step and the caller must create and validate a new plan. If a validation observation is no longer current (volatile resource, checkpoint, destination, or runtime condition changed), re-validation may restore executability without changing plan identity.

When `train(request)` or the convenience form is used, the implementation internally creates and records the exact plan used for execution.

## Resume and initialization

```python
resumed = train(
    experiment,
    resume=previous.last_checkpoint,
)

new_run = train(
    experiment,
    init_from=previous.best_checkpoint,
    seeds=SeedConfiguration.from_master(99),
)
```

- `resume` continues the same lineage.
- `init_from` starts a new lineage.
- They are mutually exclusive.
- Resume validates parent run identity, committed checkpoint resource, resolved experiment digest, corpus identity, model structure, optimizer compatibility, and completed-step history.

Only checkpoints committed before an interruption are resumable.

## `TrainingResult`

`TrainingResult` is immutable and returned only after publication succeeds.

Stable public attributes:

| Attribute         | Type                        | Behavior                                                                               |
| ----------------- | --------------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `status`          | `OperationStatus`           | Always the successful terminal status for a returned result.                           |
| `artifact`        | `ArtifactRef`               | Authoritative committed training-run artifact.                                         |
| `plan`            | `ExecutionPlan`             | Exact executed plan or portable equivalent.                                            |
| `validation`      | `ValidationReport`          | Report used to authorize execution.                                                    |
| `checkpoints`     | `tuple[CheckpointRef, ...]` | Immutable collection of committed checkpoint references; empty if none were committed. |
| `best_checkpoint` | `CheckpointRef              | None`                                                                                  | Selected best checkpoint, or `None` when the protocol defines no best-selection result. |
| `last_checkpoint` | `CheckpointRef              | None`                                                                                  | Latest committed resumable checkpoint, or `None`.                                       |
| `run`             | `RunRecord`                 | Portable run identity and terminal metadata; not a backend-native run object.          |

`to_record()` returns JSON-compatible portable metadata. It does not embed checkpoint payloads, telemetry streams, or large arrays. Rich resources are reopened through `artifact` in another process.

Accessing a checkpoint capability not defined by the protocol is represented by `None` for the singular optional attributes. `checkpoints` remains an empty tuple when no checkpoint was produced.

## Publication failure

A normal `TrainingResult` is returned only after the run manifest and declared resources are committed.

If training computation completes but publication fails, `train()` raises `PublicationError` and returns no result. The exception exposes:

- `operation="train"`;
- related request and plan identities;
- `computation_completed`;
- structured publication diagnostics;
- optional staging or recovery information.

Staging information is non-authoritative and cannot be used as an `ArtifactRef` or `CheckpointRef`.

## Interruption

On `KeyboardInterrupt`:

- deterministic cleanup runs;
- `KeyboardInterrupt` is re-raised, not wrapped;
- no successful result is returned;
- no staging directory is presented as committed output;
- checkpoints already committed before interruption remain valid;
- automatic checkpoint-on-interrupt is not part of the initial contract;
- an optional diagnostic interruption record is non-authoritative.

## Exceptions

`train()` may raise these stable semantic exception types:

- `ConfigurationError` for invalid request fields or unsupported specialization;
- `CompatibilityError` for incompatible experiment, corpus, checkpoint, runtime, or resume state;
- `ResourceError` for unavailable or invalid corpus, checkpoint, device, or destination resources;
- `ValidationError` for unmet validation postconditions;
- `StalePlanError` when an identity-bearing plan dependency changed since validation;
- `OutputConflictError` for unsafe destination conflicts;
- `ExecutionError` for failures after scientific execution begins;
- `PublicationError` when authoritative commitment fails.

All expose the structured fields defined by the shared exception contract.

## Related interfaces

- [Experiments](experiments.md)
- [Artifacts](artifacts.md)
- [Evaluation](evaluation.md)
- [Shared conventions](conventions.md)
- [Framework semantics](../../framework/_index.md)
