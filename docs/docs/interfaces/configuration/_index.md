---
title: Configuration interface
authority: normative
status: specified
interface_stability: provisional
serialized_schema_stability: proposed
semantic_resolution_stability: proposed
---

# Configuration interface

The EHP-SN configuration interface defines how package-owned defaults, an optional explicit workspace, one operation configuration file, and explicit invocation values are resolved into a typed request and immutable execution plan.

Within this documentation section, **must**, **must not**, **should**, and **may** express normative requirements.

Configuration is a frontend input mechanism. It does not replace scientific definitions, requests, plans, or artifact manifests, and it does not expose Hydra as the public configuration language.

## Stability dimensions

| Field                           | Meaning                                                                         |
| ------------------------------- | ------------------------------------------------------------------------------- |
| `interface_stability`           | Stability of the public behavioral contract                                     |
| `serialized_schema_stability`   | Stability of TOML and serialized record structures                              |
| `semantic_resolution_stability` | Stability of precedence, normalization, binding, derivation, and interpretation |

All three remain provisional or proposed until the implementation and stability gates below are satisfied.

## Primary model

```text
explicit target
    +
optional explicit workspace
    +
optional operation configuration
    +
invocation-explicit values
    ↓
ParsedOperationConfiguration
    ↓
resolved scientific definition
    ↓
resolved request
    ↓
BOUND resource records
    ↓
immutable ExecutionPlan
```

The selected target remains explicit:

```console
ehp-sn train plan experiment:arena-tem/v1 \
    --workspace config/workspace.toml \
    --config config/training/arena-tem.toml \
    --device cpu
```

## Supported public namespaces

```text
experiment.*
analysis.*
request.*
```

`definition.*` is not part of the initial public configuration contract. It may be introduced only after a concrete data-build or task-build schema demonstrates the need.

## End-to-end training example

### Workspace

```toml
schema = "ehp-sn/workspace/v1"

[artifact_store]
root = "artifacts"

[runtime]
device = "auto"

[bindings]
"requirement:corpus/arena-training/v1" = "artifact:arena-corpus/default/v1"
```

### Operation configuration

```toml
schema = "ehp-sn/train/v1"

[experiment.training]
max_steps = 100000
validation_interval = 1000

[request.seeds]
master = 42

[request.runtime]
precision = "bf16-mixed"

[request.output]
destination = "runs/arena-tem"
```

### Invocation

```console
ehp-sn train plan experiment:arena-tem/v1 \
    --workspace config/workspace.toml \
    --config config/training/arena-tem.toml \
    --device cpu
```

### Effective resolution

```text
experiment.training.max_steps
    value: 100000
    source: operation_file

request.seeds.master
    value: 42
    source: operation_file

request.runtime.device
    value: cpu
    source: dedicated_argument
    shadowed:
        value: auto
        source: workspace_default

requirement:corpus/arena-training/v1
    state: BOUND
    ref: artifact:arena-corpus/default/v1
    source: workspace_binding
```

The result is a finalized experiment definition, one resolved request, one BOUND corpus record, and one immutable execution plan.

## CLI and Python equivalence

When CLI and Python inputs represent the same canonical target and the same values expressible by the public configuration schemas, they must produce equivalent:

- finalized scientific definitions;
- effective request values;
- resource bindings;
- derived values;
- identity-relevant plan fields.

Equivalent inputs need not have identical frontend serialization or diagnostic provenance.

## Repository readiness

The configuration specification is internally coherent and ready to guide implementation design, but configuration implementation is blocked until its upstream framework contracts exist.

Required upstream specifications:

```text
docs/framework/artifacts.md
    artifact manifest contract
    logical artifact references
    content-digest semantics
    verification evidence
    commitment authority

docs/framework/identity.md
    canonical reference grammar
    version semantics
    identity categories
    compatibility declarations

one complete training configuration schema
    exhaustive field catalogue
    exact types and defaults
    namespace ownership
    CLI mappings
    identity and compatibility classes
```

Configuration documents must reference these authorities once they exist. They must not reproduce or invent their semantics.

The intended documentation order is:

```text
architecture and framework foundations
    ↓
artifact and identity specifications
    ↓
complete training operation schema
    ↓
configuration implementation
    ↓
evaluation and analysis schemas
    ↓
stability review
```

## Consolidated implementation gate

### Specification prerequisites

Before implementation begins:

1. artifact and resource reference semantics have an authoritative specification;
2. artifact manifest and content-digest semantics have an authoritative specification;
3. one complete operation schema exists, beginning with training;
4. resource states have one authoritative definition in `resource-requirements.md`;
5. canonical field-path and `--set` rules are fixed;
6. source precedence and explicit-input conflicts are fixed.

### Implementation acceptance

The first vertical slice must demonstrate:

1. one complete training configuration;
2. one workspace with one resource binding;
3. equivalent CLI and Python resolution;
4. one conflicting explicit-input case;
5. one shadowed workspace value;
6. one fixed resource;
7. one replaceable default resource;
8. semantic provenance independent of absolute file paths;
9. `DECLARED → BOUND → VERIFIED` resource progression;
10. no backend-native values in public records.

### Stability prerequisites

Before any stability field becomes stable:

1. training, evaluation, and analysis schemas are complete;
2. serialized schemas and semantic resolution versions are fixed;
3. operation-specific field catalogues are authoritative;
4. resource identity contribution is delegated to existing artifact and operation identity specifications;
5. all related-interface links resolve to existing documents;
6. end-to-end conformance tests pass.

## Alternatives considered

### Last-write-wins merging

Rejected because silent replacement obscures scientific intent and weakens reproducibility.

### Hydra-native public syntax

Rejected because backend syntax must not own EHP-SN semantics.

### Multiple configuration files and inheritance

Deferred because they introduce ordering, composition, and provenance complexity without a demonstrated initial requirement.

### General-purpose `--set`

Rejected. The initial interface accepts only statically declared schema fields and a restricted scalar value subset.

## Interface documents

- [Configuration model](model.md)
- [Files and overrides](files-and-overrides.md)
- [Operation schemas](operation-schemas.md)
- [Sources and precedence](sources-and-precedence.md)
- [Workspace](workspace.md)
- [Resource requirements](resource-requirements.md)
- [Resolution](resolution.md)
- [Identities and provenance](identities-and-provenance.md)
- [Validation](validation.md)
- [Backend integration](backend-integration.md)

## Related interfaces

- [CLI overview](../cli/_index.md)
- [Python overview](../python/_index.md)
- [Python conventions](../python/conventions.md)
- [Python experiments](../python/experiments.md)
- [Python artifacts](../python/artifacts.md)

## Non-goals

This interface does not define artifact digest algorithms, atomic persistence, runtime allocation, execution-time revalidation, artifact reuse, checkpoint lineage, or backend class layout.
