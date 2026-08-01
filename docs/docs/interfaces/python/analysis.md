---
title: Analysis interface
authority: normative
status: specified
api_stability: provisional
---

# Analysis interface

The Python analysis interface executes one versioned scientific post-hoc analysis over an ordered set of committed artifacts.

The canonical initial contract is singular: one analysis identity, one request, one validation boundary, one result, and at most one committed analysis artifact per call.

## Canonical signature and cardinality

```python
from ehp_sn import analyze

result = analyze(
    "analysis:memory-diagnostics/v1",
    inputs=[evaluation.artifact],
)
```

Canonical argument model:

```python
def analyze(
    analysis: AnalysisRef | str | AnalysisRequest | ExecutionPlan,
    *,
    inputs: Sequence[ArtifactRef | Artifact] | None = None,
    validation: ValidationReport | None = None,
    **request_options,
) -> AnalysisResult:
    ...
```

The exact overload spelling may be refined in generated API reference, but these semantics are fixed:

- a canonical string is parsed as one versioned `AnalysisRef`;
- `inputs` is ordered and its cardinality is validated against the analysis definition;
- a request or plan cannot be combined with `inputs` or other request fields;
- one call returns one `AnalysisResult`;
- one call commits at most one analysis artifact;
- `analyses=[...]` batching is not accepted by the initial interface;
- multiple analyses use ordinary iteration or future separate orchestration.

## Canonical request and planned execution

```python
request = AnalysisRequest(
    analysis=AnalysisRef.parse("analysis:memory-diagnostics/v1"),
    inputs=(evaluation.artifact,),
)

plan = plan_analysis(request)
report = validate_analysis(plan, level="resources")
result = analyze(plan, validation=report)
```

Convenience invocation constructs the same `AnalysisRequest` and follows the same plan, validation, execution, and publication path.

## Analysis definition ownership

The selected analysis definition owns:

- canonical versioned `AnalysisRef`;
- accepted artifact kinds;
- input cardinality and ordering;
- required metrics, cases, predictions, and traces;
- semantic parameters;
- rendering parameters;
- derived tables, figures, and resources;
- deterministic identity and reuse policy.

The initial stable target accepts one committed evaluation artifact for memory diagnostics. Other cardinalities are valid only when explicitly declared.

## Analysis plan

The immutable `ExecutionPlan` contains:

- plan and request identities;
- canonical `AnalysisRef`;
- ordered input `ArtifactRef` values and content digests;
- required `ResourceRef` values;
- semantic and rendering parameters kept as distinct fields;
- output root and artifact policy;
- scientific-result and artifact-identity fingerprints;
- validation requirements and compatibility decisions.

Planning performs no derived computation or rendering and never infers missing inputs from directories.

## Validation guarantees

| Level       | Additional guarantee                                                                                                                                                                   |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CONFIG`    | Analysis reference, input cardinality, ordering, semantic parameters, and rendering parameters are valid.                                                                              |
| `RESOURCES` | All input manifests and required recorded resources resolve with required integrity and schemas; destination constraints are valid.                                                    |
| `BUILD`     | Analysis implementation, resource readers, derived-output writers, and renderer components can be constructed and connected without computing scientific results or rendering figures. |

Execution rechecks input identities, content digests, resource integrity metadata, destination state, and renderer availability. A changed identity-affecting input raises `StalePlanError`; analysis never silently substitutes another artifact or resource.

## Execution boundary

Analysis may load recorded resources, compute declared derived quantities, produce tables and figure-ready data, render declared figures, and commit one analysis artifact.

Analysis must not rerun model inference, rerun evaluation, reconstruct missing traces silently, or recompute absent primary evaluation outputs.

## Scientific and rendering identity

```text
scientific_result_id
    analysis version
    + ordered scientific input identities and digests
    + semantic analysis parameters

analysis_artifact_id
    scientific_result_id
    + rendering parameters
    + renderer identity
```

Changing semantic parameters changes both identities. Changing only format, DPI, labels, theme, selected figures, or renderer version changes artifact identity while potentially retaining scientific-result identity.

Both identities are recorded in the plan, result, and manifest.

## `AnalysisResult`

`AnalysisResult` is immutable and returned only after publication succeeds.

| Attribute              | Type                      | Behavior                                                                         |
| ---------------------- | ------------------------- | -------------------------------------------------------------------------------- |
| `status`               | `OperationStatus`         | Successful terminal status.                                                      |
| `artifact`             | `ArtifactRef`             | Authoritative committed analysis artifact.                                       |
| `plan`                 | `ExecutionPlan`           | Exact executed plan or portable equivalent.                                      |
| `validation`           | `ValidationReport`        | Report used for execution.                                                       |
| `scientific_result_id` | identity value            | Identity of scientific derivation independent of rendering-only changes.         |
| `tables`               | `tuple[ResourceRef, ...]` | Immutable references to declared table resources; empty when none are produced.  |
| `figures`              | `tuple[ResourceRef, ...]` | Immutable references to declared figure resources; empty when none are produced. |
| `derived`              | `tuple[ResourceRef, ...]` | Other declared derived resources.                                                |

A capability not defined by the analysis raises `CapabilityUnavailableError`; a defined collection with zero outputs is an empty tuple. Large table or figure payloads are opened through the artifact rather than embedded in the result.

`to_record()` returns JSON-compatible metadata and references.

## Publication failure

If scientific derivation or rendering completes but commitment fails, `analyze()` raises `PublicationError` and returns no `AnalysisResult`.

The exception may expose computation-completed state, request and plan identities, diagnostics, and non-authoritative staging or recovery information. Such information is not a committed analysis artifact.

## Interruption

On `KeyboardInterrupt`:

- cleanup runs deterministically;
- `KeyboardInterrupt` is re-raised;
- no successful result is returned;
- source artifacts remain unchanged;
- staging and diagnostic records remain non-authoritative;
- the operation is not automatically resumed.

## Exceptions

`analyze()` may raise:

- `ConfigurationError` for invalid analysis reference, options, cardinality, or parameters;
- `CompatibilityError` for incompatible artifact kinds or ordering;
- `ResourceError`, `ArtifactNotFoundError`, or `ArtifactIntegrityError` for missing or invalid recorded inputs;
- `ValidationError` or `StalePlanError`;
- `CapabilityUnavailableError` for absent required artifact capabilities;
- `OutputConflictError`;
- `ExecutionError` for scientific derivation or rendering failure;
- `PublicationError`.

## Reuse

Reuse requires matching analysis version, ordered input identities and digests, semantic parameters, and—at artifact level—rendering parameters and renderer identity. Reuse never changes source artifacts.

## Side effects

Analysis may read committed resources, create staging state, compute derived outputs, render figures, and commit one immutable analysis artifact.

## Current scope

Analysis and rendering remain one operation initially, but semantic and rendering parameters are distinct in requests, plans, results, and manifests. Generic bulk analysis, asynchronous handles, and remote futures are not part of the initial interface.

## Related interfaces

- [Python interface overview](_index.md)
- [Evaluation](evaluation.md)
- [Artifacts](artifacts.md)
- [Shared conventions](conventions.md)
- [CLI analysis](../cli/analyze.md)
- [Framework semantics](../../framework/_index.md)

## Non-goals

Analysis does not own training, inference, primary evaluation, checkpoint selection, report packaging, generic batching, or arbitrary notebook exploration.
