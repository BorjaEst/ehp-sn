---
title: Configuration sources and precedence
authority: normative
status: specified
interface_stability: provisional
serialized_schema_stability: proposed
semantic_resolution_stability: proposed
---

# Configuration sources and precedence

This page defines source classes, normal precedence, and invocation-explicit conflicts.

## Source classes

Default-bearing sources:

```text
package_default
workspace_default
workspace_binding
operation_file
```

Invocation-explicit sources:

```text
typed_override
dedicated_argument
```

Derived values are not authored sources and do not participate in precedence.

## Normal precedence

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

## Invocation-explicit conflict rule

At most one invocation-explicit assignment may target a canonical semantic field.

Therefore:

- `--set` plus a dedicated argument conflict;
- repeated `--set` for the same path is invalid;
- repeated dedicated options for the same field are invalid;
- equality of normalized values does not remove the conflict;
- order does not resolve the conflict.

## Resource sources

Resource candidates do not use the generic precedence chain.

They use the requirement category and replacement policy defined in [Resource requirements](resource-requirements.md).

A fixed definition resource is not a default-bearing source and cannot be replaced.

A replaceable definition default is lower priority than a workspace binding and an explicit permitted request resource.

## Workspace mappings

| Workspace field          | Effective role                                    |
| ------------------------ | ------------------------------------------------- |
| `runtime.device`         | Default for `request.runtime.device`              |
| `runtime.precision`      | Default for `request.runtime.precision`           |
| `tracking.backend`       | Default for `request.tracking.backend`            |
| `artifact_store.root`    | Artifact storage resolver configuration           |
| `bindings.<requirement>` | Resource candidate governed by requirement policy |

## Source equivalence

Frontend source class does not affect semantic identity when effective semantic values are equal.

A value supplied through TOML, Python, workspace default, `--set`, or a dedicated option contributes the same semantic value after canonicalization.

Source class remains provenance.

## Diagnostic categories

Stable categories include:

```text
unknown_field
malformed_path
unsupported_value_kind
type_mismatch
duplicate_explicit_input
repeated_override
repeated_dedicated_option
resource_policy_violation
```

## Related interfaces

- [Operation schemas](operation-schemas.md)
- [Files and overrides](files-and-overrides.md)
- [Workspace](workspace.md)
- [Resource requirements](resource-requirements.md)

## Non-goals

This page does not define resource verification, digest algorithms, or execution-time allocation.

## Rationale for strict conflicts

EHP-SN intentionally rejects last-write-wins behavior.

Silent merge semantics are unsuitable for reproducibility-sensitive scientific operations because they obscure which explicit user instruction was intended.

Defaults may be replaced. Explicit invocation instructions may not compete.
