---
title: Configuration resolution
authority: normative
document_status: specified
capability_status: partial
api_stability: provisional
---

Resolution transforms frontend inputs into a finalized scientific definition, effective request, BOUND resource records, and immutable execution plan.

This document is the orchestration home in the ownership chain:

```text
Resource requirements
        ↓
Identity
        ↓
Configuration resolution
```

[Resource requirements](resource-requirements.md) owns what a resource requirement and binding is; [Identity](../../framework/identity.md) owns which resolved facts are identity-bearing and how plan identity is composed.
This document applies both: it defines precedence and specialization, applies resource policy, binds resources, and constructs the immutable plan.

## Foundational dependencies

Resolution applies rather than redefines its downstream-owned semantics:

- [Resource requirements](resource-requirements.md) — resource requirement model, candidate selection, and `BOUND`/`VERIFIED` states;
- [Identity](../../framework/identity.md) — identity categories, plan identity, and identity completeness;
- [References](../../framework/references.md) — canonical reference grammar;
- [Digests](../../framework/digests.md) — resource digest and artifact fingerprint semantics;
- [Artifacts](../../framework/artifacts.md) — artifact commitment and immutability.

Resolution may bind resources before the payload is verified.
Identity-sensitive behavior is defined by the framework artifact and identity specifications, which resolution applies rather than redefines.

## Resolution phases

Resolution is specified by phases rather than exact internal discovery order.

```text
PHASE 1 — PARSE
    validate schema and produce ParsedOperationConfiguration

PHASE 2 — CLASSIFY
    map fields to canonical owners and source classes

PHASE 3 — SPECIALIZE
    finalize scientific definitions

PHASE 4 — RESOLVE REQUEST
    apply defaults and invocation-explicit values

PHASE 5 — BIND RESOURCES
    apply requirement-specific resource policy

PHASE 6 — DERIVE
    compute versioned derived values

PHASE 7 — PLAN
    construct resolved request and ExecutionPlan
```

Implementations may combine internal steps, but must preserve:

- phase prerequisites;
- stable diagnostic categories;
- deterministic ordering of reported diagnostics;
- no later phase after a failed prerequisite phase.

Exact internal failure discovery order is not public API.

## Parse phase

The parser produces one immutable `ParsedOperationConfiguration`.

## Sources and precedence

### Source classes

Default-bearing sources:

```text
package_default
workspace_default
workspace_binding
operation_file
```

`operation_file` is the source class for values supplied through `--config PATH`.
The CLI may use the term `--config file` to refer to the same source in its user-facing documentation.

Invocation-explicit sources:

```text
typed_override
dedicated_argument
```

Derived values are not authored sources and do not participate in precedence.

### Normal precedence

For non-resource canonical fields:

```text
package_default
    <
workspace_default
    <
operation_file
    <
invocation-explicit assignment
```

A typed override may replace an operation-file value.
A dedicated argument may replace an operation-file value.

### Invocation-explicit conflict rule

At most one invocation-explicit assignment may target a canonical semantic field at the same precedence level.
Three distinct cases govern repeated field appearance:

| Case                   | Definition                                                                       | Example                                                                     | Result                                                    |
| ---------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------- |
| **Legal override**     | A higher-precedence source replaces a lower-precedence source for the same field | `--device cpu` overriding `operation_file: request.runtime.device = "auto"` | Accepted; lower source recorded as shadowed               |
| **Duplicate explicit** | Two sources at the same invocation level represent the same field                | `--device cpu` and `--set request.runtime.device="cuda"`                    | Rejected; equality of values does not remove the conflict |
| **Conflict**           | Mutually exclusive or semantically incompatible inputs at any level              | `--resume` and `--init-from` together                                       | Rejected                                                  |

Specific rules:

- `--set` plus a dedicated argument at the same invocation level is a duplicate explicit representation;
- repeated `--set` for the same path is invalid;
- repeated dedicated options for the same field are invalid;
- equality of normalized values does not remove a duplicate explicit conflict;
- order does not resolve the conflict.

### Resource sources

Resource candidates do not use the generic precedence chain.
They use the requirement category and replacement policy defined in [Resource requirements](resource-requirements.md).

A fixed definition resource is not a default-bearing source and cannot be replaced.
A replaceable definition default is lower priority than a workspace binding and an explicit permitted request resource.

### Workspace mappings

| Workspace field          | Effective role                                    |
| ------------------------ | ------------------------------------------------- |
| `runtime.device`         | Default for `request.runtime.device`              |
| `runtime.precision`      | Default for `request.runtime.precision`           |
| `tracking.backend`       | Default for `request.tracking.backend`            |
| `artifact_store.root`    | Artifact storage resolver configuration           |
| `bindings.<requirement>` | Resource candidate governed by requirement policy |

### Source equivalence

Frontend source class does not affect semantic identity when effective semantic values are equal.
A value supplied through TOML, Python, workspace default, `--set`, or a dedicated option contributes the same semantic value after canonicalization.
Source class remains provenance.

## Request resolution

For non-resource fields, the effective value follows normal precedence:

```text
package_default
< workspace_default
< operation_file
< one invocation-explicit assignment
```

This restates the normal precedence for request fields specifically; it does not add a second source model.
Sources, precedence, and conflict handling are defined above.

## Resource binding

Resource binding follows the requirement category and request policy, not the generic source order.
It applies, rather than redefines, the selection and precedence model owned by [Resource requirements](resource-requirements.md).

## Planning

Planning consumes resolved configuration, BOUND resources, and the identity rule to construct the immutable authoritative plan.

### Planning completeness

At the end of configuration resolution:

- every required requirement is BOUND;
- every `one` requirement has one exact logical reference;
- every `optional-one` requirement has either one exact reference or an explicit absent record;
- no requirement is merely DECLARED;
- verification may remain pending.

This is the minimum completeness required for planning.

### Authoritative immutable plan

Planning produces an immutable, authoritative framework plan in which all scientific build choices required before execution are resolved.
The plan is a plan of intention only: it performs no generation, stages nothing, mutates no artifact, and commits nothing.

Execution must not later invent unresolved scientific choices.
Every scientific choice the build requires is either resolved in the plan or declared absent by it, before execution begins.

### Producer/framework ownership boundary

The framework and the producer split responsibility for a plan:

```text
producer (ehp_research)
    declares family-specific identity-bearing scientific inputs
    and resource requirements that characterize the build

framework (ehp_sn)
    resolves generic resource requirements to the concrete
    bindings the plan needs,
    applies the plan-identity rule from
    Identity § "PlanId",
    and constructs the immutable authoritative plan
```

The framework must not know producer-specific configuration types or family-specific fields.
It carries the producer-effective configuration opaquely and never inspects its fields.
Producer-specific semantics remain downstream and are owned by the corresponding `ehp_research` specifications.

### Identity handoff

Resolution supplies canonical resolved inputs and BOUND resource records to the identity mechanism defined by [Identity](../../framework/identity.md) § "PlanId".
Source file paths, CLI positions, and frontend spelling are excluded.

Resolution does not redefine which fields contribute to identity.
Which producer-specific values are identity-bearing, how bound resources contribute, and when identity is complete are decided by [Identity](../../framework/identity.md).
In particular, whether a plan may be considered identity-complete at `BOUND` or requires `VERIFIED`-state evidence is governed by Identity § "Identity completeness and verification".

### Implemented substrate-planning slice

This section records the settled semantics and implemented scope demonstrated by current substrate planning.
It does not extend to execution, artifact staging or publication, validation, inspection, or unrelated planned framework contracts.

The generic planning mechanics live in `ehp_sn` (the `ehp_sn.planning` package).
Normative semantics remain in the owning specifications, including this document.

The implemented framework surface covers:

- producer-owned planning input resolution for the selected authoritative definition;
- resolution of declared resource requirements to exact bound resources;
- application of the plan-identity rule from [Identity](../../framework/identity.md) § "PlanId";
- construction of the immutable framework plan.

The implementation is deliberately limited to the framework surface demonstrated by current substrate planning.
It does not imply implementation of producer execution, artifact staging or publication, validation, inspection, or unrelated planned framework contracts.
Broader resolution semantics above remain `capability_status: partial` where only a subset is satisfied by code.

## Plan and validation relationship

Validation observes and reports facts about an immutable plan.
It does not complete or transform a partially resolved plan.

```text
authored request
    → resolved immutable plan
    → validation report bound to plan ID
    → freshness check
    → execution of the same plan
```

### Plan-to-validation binding

A validation report is bound to a plan through the framework-derived `PlanId` defined by [Identity](../../framework/identity.md) § "PlanId".
The binding is deterministic: the report records the `PlanId` derived from the canonical identity projection of the same immutable plan it observed.

The central invariant is:

```text
report.plan_id == plan_id(plan)
```

This cleanly separates two independent questions:

```text
Does this report describe this plan?
        → plan_id equality

Are its observations still usable?
        → freshness
```

This corresponds directly to the separation of plan staleness, validation staleness, and execution blocking below: `plan_id` equality answers "did validation observe this plan?", while freshness answers "are those observations still current?".

Validation may add observations to the report, but it must never add identity-bearing state to the plan.
A validation observation does not become a plan-identity input and is never folded back into the immutable plan.
For example, an expected resource digest necessary to identify a resource scientifically must already be part of the BOUND intention before validation; validation only confirms or contradicts it as a `VERIFIED` observation.

Under this model:

- logical resources are BOUND before the plan is complete;
- physical accessibility and integrity are VERIFIED in the validation report;
- validation does not mutate the plan;
- volatile conditions do not change plan identity;
- execution records the actual allocation and physical resolutions.

## Validation

### ValidationReport contract

Beyond the plan-to-validation binding above, a `ValidationReport` has a deliberately narrow semantic contract:

```text
ValidationReport
    plan_id
    validation_level
    outcome
    observations / evidence
    diagnostic information
    observation provenance / time where relevant
```

The report's `plan_id` must equal `plan_id(plan)` for the plan it observed.
Its `validation_level` records the highest validation level satisfied.
Its observations are volatile evidence about mutable external state; they are never folded into the immutable plan.

Execution against a validated plan requires:

```text
execute(P, R)

requires:

R.plan_id == plan_id(P)
R.level >= required_level
R is successful
R's volatile observations remain fresh
```

Freshness is deliberately not part of `PlanId`.
For example, a plan with `device = "auto"` keeps the same `plan_id` when CUDA becomes unavailable; the validation report merely becomes stale.
The framework does not need to solve every future freshness mechanism before a resource-empty plan can execute.

### Diagnostic categories

```text
parse_error
schema_mismatch
unknown_field
malformed_path
unsupported_value_kind
type_mismatch
duplicate_explicit_input
repeated_override
repeated_dedicated_option
namespace_violation
resource_policy_violation
resource_unbound
resource_unverified
```

Diagnostics within one phase must be reported in implementation-deterministic order: stable across repeated runs of the same implementation version for the same inputs.
Cross-implementation canonical ordering is not required.

### Validation levels

| Level       | Guarantee                                                                                                                         |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `CONFIG`    | Parsing, field ownership, source conflicts, scientific specialization, resource policy, and BOUND resource completeness are valid |
| `RESOURCES` | `CONFIG` holds and every required bound resource is VERIFIED                                                                      |
| `BUILD`     | `RESOURCES` holds and runtime components can be constructed without scientific execution                                          |

### Staleness and execution readiness

Three distinct concepts govern correctness after planning:

| Concept               | Definition                                                       | Example                                                    | Consequence                                             |
| --------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------- |
| **Plan stale**        | An identity-bearing plan dependency changed                      | Workspace binding changed; corpus digest no longer matches | New plan required; `StalePlanError`                     |
| **Validation stale**  | An observed external condition may have changed                  | GPU became unavailable; destination became occupied        | Re-validate; if conditions restored, plan remains valid |
| **Execution blocked** | Current environmental state incompatible with the unchanged plan | Temporary resource contention                              | Retry may succeed; plan identity unchanged              |

A plan describes intended execution and is immutable after construction.
A validation report records observations about mutable external state at a point in time.

Changing unused workspace fields, unused operation-file fields, absolute paths, or diagnostic provenance does not affect any of these conditions.

## Special resolution policies

### Runtime `auto` resolution

`device = "auto"` is a policy, not a physical allocation.
Its normative semantics are:

| Property             | Value                                                       |
| -------------------- | ----------------------------------------------------------- |
| Allowed device kinds | `[cuda, cpu]`                                               |
| Preference           | Ordered: first available from the allowed list              |
| Fallback             | Permitted within the allowed list                           |
| CPU fallback         | Permitted when no accelerator is available                  |
| Distributed          | Forbidden unless an explicit distributed policy is supplied |
| Availability check   | Observed during `RESOURCES` validation                      |
| Execution choice     | Must match the validation observation unless re-validated   |

The resolved device is recorded in execution provenance.
It does not affect scientific identity.
Changing only the resolved device (when `auto` produces a different allocation) changes request identity but not experiment identity.

Plans containing `device = "auto"` are exact execution descriptions only when combined with their validation report, which records the observed allocation.

## CLI and Python equivalence

For public-schema-representable inputs, equivalence requires equal:

- canonical target;
- finalized definitions;
- effective semantic values;
- BOUND resource records;
- derived values;
- identity-relevant plan fields.

Serialized frontend representation and diagnostic provenance may differ.

## Related interfaces

- [Files and overrides](files-and-overrides.md)
- [Resource requirements](resource-requirements.md)
- [Identities and provenance](identities-and-provenance.md)
- [Identity](../../framework/identity.md)
