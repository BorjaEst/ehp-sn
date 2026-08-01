---
title: Configuration resolution
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Configuration resolution

Resolution transforms frontend inputs into a finalized scientific definition, effective request, BOUND resource records, and immutable execution plan.

## Validation phases

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

`operation_file` is the source class for values supplied through `--config PATH`. The CLI may use the term `--config file` to refer to the same source in its user-facing documentation.

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

At most one invocation-explicit assignment may target a canonical semantic field at the same precedence level. Three distinct cases govern repeated field appearance:

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

Resource candidates do not use the generic precedence chain. They use the requirement category and replacement policy defined in [Resource requirements](resource-requirements.md).

A fixed definition resource is not a default-bearing source and cannot be replaced. A replaceable definition default is lower priority than a workspace binding and an explicit permitted request resource.

### Workspace mappings

| Workspace field          | Effective role                                    |
| ------------------------ | ------------------------------------------------- |
| `runtime.device`         | Default for `request.runtime.device`              |
| `runtime.precision`      | Default for `request.runtime.precision`           |
| `tracking.backend`       | Default for `request.tracking.backend`            |
| `artifact_store.root`    | Artifact storage resolver configuration           |
| `bindings.<requirement>` | Resource candidate governed by requirement policy |

### Source equivalence

Frontend source class does not affect semantic identity when effective semantic values are equal. A value supplied through TOML, Python, workspace default, `--set`, or a dedicated option contributes the same semantic value after canonicalization. Source class remains provenance.

## Request source application

For non-resource fields:

```text
package_default
< workspace_default
< operation_file
< one invocation-explicit assignment
```

## Resource binding

Resource binding follows the requirement category and request policy, not the generic source order.

See [Resource requirements](resource-requirements.md).

## Planning completeness

At the end of configuration resolution:

- every required requirement is BOUND;
- every `one` requirement has one exact logical reference;
- every `optional-one` requirement has either one exact reference or an explicit absent record;
- no requirement is merely DECLARED;
- verification may remain pending.

This is the minimum completeness required for planning.

## Plan and validation relationship

Validation observes and reports facts about an immutable plan. It does not complete or transform a partially resolved plan.

```text
authored request
    → resolved immutable plan
    → validation report bound to plan ID
    → freshness check
    → execution of the same plan
```

Under this model:

- logical resources are BOUND before the plan is complete;
- physical accessibility and integrity are VERIFIED in the validation report;
- validation does not mutate the plan;
- volatile conditions do not change plan identity;
- execution records the actual allocation and physical resolutions.

## Validation

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

Diagnostics within one phase must be reported in implementation-deterministic order: stable across repeated runs of the same implementation version for the same inputs. Cross-implementation canonical ordering is not required.

### Validation levels

| Level       | Guarantee                                                                                                                          |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `CONFIG`    | Parsing, field ownership, source conflicts, scientific specialization, resource policy, and BOUND resource completeness are valid. |
| `RESOURCES` | `CONFIG` holds and every required bound resource is VERIFIED.                                                                      |
| `BUILD`     | `RESOURCES` holds and runtime components can be constructed without scientific execution.                                          |

### Staleness and execution readiness

Three distinct concepts govern correctness after planning:

| Concept               | Definition                                                       | Example                                                    | Consequence                                             |
| --------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------- |
| **Plan stale**        | An identity-bearing plan dependency changed                      | Workspace binding changed; corpus digest no longer matches | New plan required; `StalePlanError`                     |
| **Validation stale**  | An observed external condition may have changed                  | GPU became unavailable; destination became occupied        | Re-validate; if conditions restored, plan remains valid |
| **Execution blocked** | Current environmental state incompatible with the unchanged plan | Temporary resource contention                              | Retry may succeed; plan identity unchanged              |

A plan describes intended execution and is immutable after construction. A validation report records observations about mutable external state at a point in time.

Changing unused workspace fields, unused operation-file fields, absolute paths, or diagnostic provenance does not affect any of these conditions.

## Runtime `auto` resolution

`device = "auto"` is a policy, not a physical allocation. Its normative semantics are:

| Property             | Value                                                       |
| -------------------- | ----------------------------------------------------------- |
| Allowed device kinds | `[cuda, cpu]`                                               |
| Preference           | Ordered: first available from the allowed list              |
| Fallback             | Permitted within the allowed list                           |
| CPU fallback         | Permitted when no accelerator is available                  |
| Distributed          | Forbidden unless an explicit distributed policy is supplied |
| Availability check   | Observed during `RESOURCES` validation                      |
| Execution choice     | Must match the validation observation unless re-validated   |

The resolved device is recorded in execution provenance. It does not affect scientific identity. Changing only the resolved device (when `auto` produces a different allocation) changes request identity but not experiment identity.

Plans containing `device = "auto"` are exact execution descriptions only when combined with their validation report, which records the observed allocation.

## Identity inputs

Resolution passes canonical semantic values to identity computation.

Source file paths, CLI positions, and frontend spelling are excluded.

Normalization rule IDs and derivation rule IDs are included when changing them could change an effective semantic value.

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

## Foundational dependencies

Resolution may bind resources before the payload is verified, but identity-sensitive behavior depends on framework artifact and identity specifications:

- [References](../../framework/references.md) — canonical reference grammar
- [Identity](../../framework/identity.md) — identity categories and equality invariants
- [Digests](../../framework/digests.md) — content digest semantics
- [Artifacts](../../framework/artifacts.md) — artifact commitment and immutability

When those specifications are absent, configuration may still parse and classify inputs, but it must not invent resource identity or digest semantics.
