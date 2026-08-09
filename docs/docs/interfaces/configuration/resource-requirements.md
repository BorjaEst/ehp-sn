---
title: Resource requirements
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Resource requirements

Resource requirements define package-owned resource roles and deterministic selection of exact logical resources.

## Initial surface

The initial interface supports only:

- exact requirement reference;
- resource kind;
- accepted schema IDs;
- cardinality `one` or `optional-one`;
- fixed resource or replaceable default;
- exact workspace binding;
- exact explicit request resource;
- package-owned compatibility validator when schema equality is insufficient.

It does not define a general-purpose compatibility language.

## Resource categories

A requirement declares exactly one definition-owned resource category:

```text
fixed
default
none
```

### Fixed resource

A fixed resource is an exact definition-owned resource.

It must be used directly.

It cannot be replaced by a workspace binding or request resource.

### Definition-provided default

A default resource is an exact replaceable definition-owned fallback.

For a replaceable requirement, precedence is:

```text
explicit permitted request resource
    ↓
workspace binding
    ↓
definition-provided default
    ↓
failure or optional absence
```

### No definition resource

When no definition resource exists:

```text
explicit permitted request resource
    ↓
workspace binding
    ↓
failure or optional absence
```

## Request policy

`request_policy` is one of:

```text
forbidden
allowed
required
```

Rules:

- `forbidden` rejects an explicit request resource;
- `allowed` permits an explicit request resource;
- `required` requires an explicit request resource and bypasses workspace/default candidates.

A fixed resource always implies `request_policy="forbidden"`.

## Requirement declaration

A minimal declaration contains:

```text
ref
resource_kind
accepted_schema_ids
cardinality
definition_resource_category
definition_resource_ref
request_policy
compatibility_validator_id
description
```

`compatibility_validator_id` is optional and package-owned. It identifies a versioned validator but does not serialize a callable.

## Resource states

```text
DECLARED
BOUND
VERIFIED
```

### DECLARED

The requirement exists, but no exact resource has been selected.

### BOUND

Exactly one logical resource reference has been selected, or an optional requirement is absent.

For a bound resource, the record includes:

- requirement reference;
- exact logical resource reference;
- resolution source;
- definition resource category;
- request policy.

BOUND does not guarantee resource existence, accepted schema metadata, or integrity.

### VERIFIED

`RESOURCES` validation has confirmed:

- resource existence;
- accepted schema;
- required manifest metadata;
- integrity evidence required by the operation.

The configuration docs define the state transition, not storage validation internals.

## Optional absence

For `optional-one`, absence is represented by an explicit state record:

```toml
[resolved_resources.optional_diagnostics]
state = "BOUND"
requirement = "requirement:artifact/optional-diagnostics/v1"
presence = "absent"
```

This is preferable to omitting the record because it preserves the fact that the optional requirement was deliberately resolved.

## Resource identity contribution

At scientific-invocation identity level, a selected scientific resource contributes:

- canonical logical reference;
- immutable version when part of the reference;
- resource digest when the resource contract declares content identity necessary and VERIFIED evidence is available;
- requirement identity.

The operation or artifact identity specification determines whether the logical reference alone is sufficient before verification.

## Related interfaces

- [Configuration model](model.md)
- [Resolution](resolution.md)
- [Python artifacts](../python/artifacts.md)
- [Python training](../python/training.md)
- [Python evaluation](../python/evaluation.md)

## Non-goals

This page does not define artifact lookup, download, commit, storage integrity algorithms, or operation-specific compatibility.

## Identity authority

Configuration supplies the following candidate identity components:

- requirement reference;
- exact logical resource reference;
- immutable version when encoded by the reference;
- verified resource digest when required by the resource contract.

The owning operation identity specification and artifact identity specification declare which components contribute to scientific invocation, plan, result, and artifact identity.

Configuration resolution must not decide this dynamically. The applicable identity rule must be declared before resolution begins.

If the required artifact or operation identity specification does not exist, identity-sensitive implementation of that resource requirement is blocked.

## Implementation dependency

Resource parsing and precedence may be implemented independently of the specific operation and artifact identity contracts that consume them.

The following behavior is defined by the owning operation and artifact identity specifications, per [Identity](../../framework/identity.md), [Digests](../../framework/digests.md), and [Data artifacts](../../framework/data-artifacts.md), not by this page:

- deciding whether logical reference alone is identity-complete;
- requiring or interpreting resource digests;
- assigning verification evidence;
- computing identity-sensitive plan fields;
- determining resource compatibility beyond declared schema acceptance.
