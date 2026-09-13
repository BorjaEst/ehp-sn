---
title: Resource requirements
authority: normative
document_status: specified
capability_status: partial
api_stability: provisional
---

Resource requirements define package-owned resource roles and deterministic selection of exact logical resources.

This document owns the resource requirement model, candidate selection and precedence, and the resource states.
It is the most upstream of the ownership chain:

```text
Resource requirements
        ↓
Identity
        ↓
Configuration resolution
```

It defines WHAT a resource requirement and binding is.
It does not define which facts constitute identity — that belongs to [Identity](../../framework/identity.md) — and it does not define how requirements are applied to construct a plan — that belongs to [Resolution](resolution.md).

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

## Requirement model

### Resource categories

A requirement declares exactly one definition-owned resource category:

```text
fixed
default
none
```

#### Fixed resource

A fixed resource is an exact definition-owned resource.

It must be used directly.

It cannot be replaced by a workspace binding or request resource.

#### Definition-provided default

A default resource is an exact replaceable definition-owned fallback.

#### No definition resource

When no definition resource exists, candidate selection proceeds without a definition fallback.

### Request policy

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

### Requirement declaration

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

`compatibility_validator_id` is optional and package-owned.
It identifies a versioned validator but does not serialize a callable.

## Candidate selection and precedence

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

When no definition resource exists:

```text
explicit permitted request resource
    ↓
workspace binding
    ↓
failure or optional absence
```

Selection is deterministic and recordable.
Resource selection determinism is definition and planning semantics; registration only makes a definition discoverable and does not change a definition's resource semantics.

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

### Optional absence

For `optional-one`, absence is represented by an explicit state record:

```toml
[resolved_resources.optional_diagnostics]
state = "BOUND"
requirement = "requirement:artifact/optional-diagnostics/v1"
presence = "absent"
```

This is preferable to omitting the record because it preserves the fact that the optional requirement was deliberately resolved.

## Identity boundary

Resource resolution can provide these facts about a resolved requirement:

- requirement reference;
- selected logical resource reference;
- immutable version when part of the reference;
- verification digest or evidence when `VERIFIED` evidence is available.

This document does not decide whether or how those facts contribute to identity.
[Identity](../../framework/identity.md) decides that: it identifies which canonical resolved facts are identity-bearing and how they compose into plan identity, including how the `BOUND`/`VERIFIED` distinction affects identity completeness.

Resource parsing and precedence may be implemented independently of the identity contracts that consume them.
If the required artifact or operation identity specification does not exist, identity-sensitive use of a resource requirement is blocked.

## Non-goals

This page does not define:

- which facts are identity-bearing or compose plan identity — see [Identity](../../framework/identity.md);
- artifact lookup, download, commit, or storage integrity algorithms;
- operation-specific compatibility;
- how requirements are applied to construct a plan — see [Resolution](resolution.md).

## Implemented scope: substrate planning resource resolution

This section records only the implemented slice of resource requirements, as demonstrated by current substrate planning.
It does not claim that every future workspace or resource-resolution feature described on this page is implemented.

Implemented:

- producer planning semantics may declare resource requirements for the selected authoritative definition;
- framework planning resolves those requirements to the concrete bindings the plan needs;
- a requirement is either resolved to one exact resource, or fails cleanly when it cannot be bound;
- bound resources are represented in the immutable framework plan.

The implemented substrate-planning slice supports only the candidate sources exercised by the current substrate planners: an exact definition-provided reference with cardinality `one` or `optional-one`, bound with resolution source `definition`.
The broader `fixed`/`default`/workspace/request precedence and `request_policy` model on this page remains planned unless explicitly stated otherwise.

The implemented surface covers requirement declaration and resolution to bound resources (`BOUND`).
It does not implement workspace persistence backends, download, commit, storage integrity, `VERIFIED` evidence assignment, or the broader resolution machinery that other pages describe.

## Related interfaces

- [Configuration model](model.md)
- [Resolution](resolution.md)
- [Identity](../../framework/identity.md)
- [Python artifacts](../python/artifacts.md)
- [Python training](../python/training.md)
- [Python evaluation](../python/evaluation.md)
