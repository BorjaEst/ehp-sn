---
title: Configuration validation
authority: normative
status: specified
interface_stability: provisional
serialized_schema_stability: proposed
semantic_resolution_stability: proposed
---

# Configuration validation

This page defines common configuration diagnostics, validation phases, and the implementation gate.

## Stable diagnostic categories

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

Diagnostics within one phase must be reported in deterministic canonical-field order.

## Validation levels

| Level       | Guarantee                                                                                                                          |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `CONFIG`    | Parsing, field ownership, source conflicts, scientific specialization, resource policy, and BOUND resource completeness are valid. |
| `RESOURCES` | `CONFIG` holds and every required bound resource is VERIFIED.                                                                      |
| `BUILD`     | `RESOURCES` holds and runtime components can be constructed without scientific execution.                                          |

## Staleness

A plan becomes semantically stale when an identity-relevant consumed input changes.

Changing unused workspace fields, unused operation-file fields, absolute paths, or diagnostic provenance does not make a plan semantically stale.

## Conformance scenarios

The authoritative implementation and stability gates are defined in [\_index.md](_index.md).

This page owns validation outcomes and diagnostic categories, not project gating.

## Related interfaces

- [Resolution](resolution.md)
- [Files and overrides](files-and-overrides.md)
- [Resource requirements](resource-requirements.md)
- [Python training](../python/training.md)
- [Python evaluation](../python/evaluation.md)
- [Python analysis](../python/analysis.md)

## Non-goals

This page does not define runtime races, execution-time revalidation, artifact repair, or operation-specific scientific compatibility.

## Readiness interpretation

Passing configuration-document review does not by itself authorize implementation of artifact identity, digest verification, or compatibility semantics.

Those behaviors require the upstream artifact and identity specifications named in [\_index.md](_index.md).
