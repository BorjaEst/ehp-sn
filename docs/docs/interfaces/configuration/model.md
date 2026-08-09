---
title: Configuration model
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Configuration model

This page defines the semantic objects involved in configuration and the ownership of configurable values.

## Definition defaults

Definition defaults are package-owned scientific values supplied by experiments, analyses, tasks, models, bindings, and protocols.

Resources associated with a definition are classified by [Resource requirements](resource-requirements.md) as fixed, replaceable defaults, or absent.

## Workspace

Workspace settings provide local deployment defaults and exact bindings for package-declared resource requirements.

They must not redefine scientific task, model, binding, protocol, metric, regime, or analysis semantics.

### Admission

A workspace field is permitted only when it supplies a local deployment default or an exact resource binding consumed during operation resolution.

The workspace must not contain scientific definitions, tool-native configuration trees, arbitrary environment variables, package discovery settings, user-interface preferences, or unrelated project metadata.

### Workspace file

```toml
schema = "ehp-sn/workspace/v1"

[artifact_store]
root = "artifacts"

[cache]
root = ".cache/ehp-sn"

[runtime]
device = "auto"

[tracking]
backend = "local"

[bindings]
"requirement:corpus/arena-training/v1" = "artifact:arena-corpus/default/v1"
```

### Effective projection

Two distinct digests are defined:

| Digest                       | Scope                                                  | Role                                                         |
| ---------------------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| `workspace_document_digest`  | Digest of the complete selected workspace file         | Diagnostic provenance only; identifies the authored document |
| `effective_workspace_digest` | Digest of only consumed normalized fields and bindings | Identity-bearing; contributes to plan identity               |

Resolution constructs an effective workspace projection containing only consumed workspace defaults and consumed resource bindings.

Identity and staleness rules use the effective projection, not the full workspace document:

- unused workspace fields do not affect semantic identity;
- shadowed workspace values do not affect semantic identity;
- changing unused fields changes `workspace_document_digest` but not `effective_workspace_digest` or plan identity;
- changing a consumed default or binding changes `effective_workspace_digest` and may change identity and stale the plan.

## Operation configuration

An operation configuration is a typed, partial frontend document used while resolving one operation.

It is a serialized frontend envelope whose fields are dispatched to their semantic owners. It is not a complete request and not a universal semantic `Config` object.

## Parsed operation configuration

`ParsedOperationConfiguration` is the transient result of parsing one operation file.

Required behavior:

- typed;
- operation-specific;
- partial;
- immutable after parsing;
- schema-validated.

It is not a request, scientific definition, execution plan, resolved-resource record, or reproduction record.

## Namespace assignment

Namespace assignment follows public semantics.

| Namespace      | Meaning                                                                              |
| -------------- | ------------------------------------------------------------------------------------ |
| `experiment.*` | Supported specialization that changes the resolved experiment definition             |
| `analysis.*`   | Supported semantic specialization of the selected analysis                           |
| `request.*`    | Invocation-specific intent that does not redefine the selected scientific definition |

Examples:

- `experiment.training.max_steps` belongs under `experiment.*` when training duration is part of the declared scientific protocol.
- `request.runtime.device` belongs under `request.*` because it is execution policy.
- `request.checkpoint` belongs under `request.*` because it selects an invocation input.
- optimizer family belongs under `experiment.*` only when the experiment owns it as scientific protocol.

## Request

A request represents one intended operation invocation.

It combines a finalized scientific target with invocation-specific values and authored resource inputs.

## Resolved request

A resolved request contains:

- a finalized immutable scientific definition;
- typed effective request values;
- canonical logical references;
- BOUND resource records;
- derived values;
- semantic provenance;
- no unresolved aliases or ambiguous choices.

The authoritative resource state definitions are in [Resource requirements](resource-requirements.md).

## Execution plan

An `ExecutionPlan` is an immutable, serializable, backend-independent description of an execution. It may contain logical or local placement requirements and is not necessarily relocatable between machines.

At planning time, every required resource must satisfy the BOUND postcondition defined by `resource-requirements.md`.

## Scientific-specialization invariant

```text
canonical scientific definition
    +
supported specialization
    ↓
immutable resolved scientific definition
    ↓
request construction
```

## Related interfaces

- [Resource requirements](resource-requirements.md)
- [Identities and provenance](identities-and-provenance.md)
- [Resolution](resolution.md)

## Non-goals

This page does not define artifact commit semantics, storage races, or runtime allocation.

A request must never contain pending experiment or analysis mutations.

## Authored and resolved resources

Authored request input:

```toml
[request]
corpus = "artifact:arena-corpus/default/v1"
```

Resolved records are owned by `resource-requirements.md` and the plan/provenance schema. This page does not redefine their states or serialized fields.

## Related interfaces

- [Python experiments](../python/experiments.md)
- [Python conventions](../python/conventions.md)
- [Python artifacts](../python/artifacts.md)
- [Python training](../python/training.md)
- [Python evaluation](../python/evaluation.md)
- [Python analysis](../python/analysis.md)

## Non-goals

This page does not define resource states, digest algorithms, storage validation, runtime scheduling, or execution-time revalidation.

## Foundational dependencies

This model depends on the authoritative artifact and identity specifications: [References](../../framework/references.md), [Identity](../../framework/identity.md), [Digests](../../framework/digests.md), and [Data artifacts](../../framework/data-artifacts.md). Resource references, manifest identity, digest semantics, and compatibility declarations are defined there; this page applies them rather than redefining them.
