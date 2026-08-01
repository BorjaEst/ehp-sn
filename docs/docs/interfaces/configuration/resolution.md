---
title: Configuration resolution
authority: normative
status: specified
interface_stability: provisional
serialized_schema_stability: proposed
semantic_resolution_stability: proposed
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
- [Sources and precedence](sources-and-precedence.md)
- [Resource requirements](resource-requirements.md)
- [Validation](validation.md)

## Non-goals

This page does not define exact hash algorithms, runtime allocation, execution-time revalidation, or persistence commit.

## Foundational dependencies

Resolution may bind resources before the payload is verified, but identity-sensitive behavior depends on existing artifact and operation identity specifications.

When those specifications are absent, configuration may still parse and classify inputs, but it must not invent resource identity or digest semantics.
