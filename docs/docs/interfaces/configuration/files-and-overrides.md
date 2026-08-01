---
title: Configuration files and overrides
authority: normative
status: specified
interface_stability: provisional
serialized_schema_stability: proposed
semantic_resolution_stability: proposed
---

# Configuration files and overrides

This page defines public TOML documents, canonical field paths, and typed command-line override syntax.

## Public format

The initial public configuration format is TOML.

One operation configuration file may be supplied per invocation.

## Canonical field-path grammar

A canonical path consists of dot-separated ASCII identifiers:

```text
segment("."segment)*
```

Each segment must match:

```text
[A-Za-z_][A-Za-z0-9_-]*
```

Rules:

- paths are case-sensitive;
- Unicode path segments are unsupported;
- a segment must not begin with a number;
- numeric-only segments are unsupported;
- array indices are unsupported;
- arbitrary map traversal is unsupported;
- aliases are unsupported;
- canonical paths must name statically declared schema fields;
- canonical normalization does not change case or punctuation.

Examples:

```text
experiment.training.max_steps
request.runtime.device
analysis.semantic.aggregation
```

Invalid examples:

```text
request.inputs.0
request.MapKey
request."quoted.key"
request..device
```

Quoted TOML keys may be used only where the schema explicitly defines a map-valued table, such as workspace requirement bindings. Those keys are not converted into traversable canonical `--set` paths.

## Candidate schema identifiers

```text
ehp-sn/data-build/v1
ehp-sn/task-build/v1
ehp-sn/train/v1
ehp-sn/evaluate/v1
ehp-sn/analyze/v1
ehp-sn/workspace/v1
```

The identifiers become stable only when their complete serialized field sets and semantic resolution rules are accepted and implemented.

## Parsed result

Parsing an operation file produces one immutable `ParsedOperationConfiguration`.

Parsing must not:

- resolve resources;
- derive seeds;
- construct requests;
- create plans;
- inspect runtime availability.

## `--set` syntax

```console
--set KEY=VALUE
```

`KEY` must be a canonical schema field.

The initial supported value subset is:

```text
string
boolean
integer
finite float
homogeneous array of supported scalar values
```

Unsupported values include:

- dates;
- times;
- date-times;
- inline tables;
- heterogeneous arrays;
- nested arrays;
- `inf`;
- `nan`.

Parsing is schema-directed. The destination field type determines whether the parsed value is accepted.

## Explicit-input repetition

The following are always invalid, even when the repeated values are equal:

```console
--set request.runtime.device='"cpu"' \
--set request.runtime.device='"cpu"'
```

Repeated dedicated options targeting the same canonical field are also invalid.

A typed override and a dedicated argument targeting the same canonical field conflict even when their normalized values are equal.

## Validation rules

The frontend rejects:

- unknown fields;
- malformed paths;
- ambiguous paths;
- unsupported value kinds;
- type-invalid values;
- unsupported schema versions;
- unsupported scientific specialization;
- duplicate TOML keys;
- repeated `--set` paths;
- repeated dedicated options;
- multiple invocation-explicit assignments to one canonical field.

## Compatibility versions

The configuration interface distinguishes:

```text
serialized schema version
semantic resolution version
derivation rule version
```

A serialized schema version covers field names, types, requiredness, and structural representation.

A semantic resolution version covers:

- source application semantics;
- field normalization;
- namespace interpretation;
- identity classification;
- resource precedence;
- replacement policy;
- canonical option mapping;
- specialization interpretation.

A derivation rule version identifies a specific derived-value algorithm such as role-specific seed derivation.

A breaking change to semantic resolution requires a new semantic resolution version even when the serialized field syntax is unchanged.

## Related interfaces

- [Operation schemas](operation-schemas.md)
- [Sources and precedence](sources-and-precedence.md)
- [CLI overview](../cli/_index.md)
- [Python conventions](../python/conventions.md)

## Non-goals

This page does not define resource validation, hash algorithms, execution scheduling, or arbitrary TOML support.

## TOML-to-canonical-path mapping

Nested TOML tables map to canonical paths by joining statically declared table and field names with `.`.

Example:

```toml
[request.runtime]
device = "cpu"
```

maps to:

```text
request.runtime.device
```

Dotted TOML keys are accepted only when they resolve to the same declared canonical path.

Arrays of tables are unsupported in public operation configuration.

Quoted keys are supported only for schema-declared map keys, such as workspace requirement bindings. They do not create traversable canonical paths and cannot be targeted through `--set`.

## CLI resource-selection asymmetry

The initial generic `--set` interface does not traverse workspace binding maps or construct arbitrary resource-binding objects.

Invocation-time resource selection, where supported, must use an operation-specific dedicated option or a statically declared request field.

Python may expose the same resource field through a typed request argument. Operations that do not expose a CLI resource option must document that limitation explicitly.
