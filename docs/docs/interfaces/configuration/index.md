---
title: Configuration interface
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Configuration interface

The EHP-SN configuration interface defines how package-owned defaults, an optional explicit workspace, one operation configuration file, and explicit invocation values are resolved into a typed request and immutable execution plan.

Within this documentation section, **must**, **must not**, **should**, and **may** express normative requirements.

Configuration is a frontend input mechanism. It does not replace scientific definitions, requests, plans, or artifact manifests, and it does not expose Hydra as the public configuration language.

## Sub-aspects of this page's stability

This page's single `api_stability` frontmatter value covers three sub-aspects that must each stabilize before it can be promoted from `provisional` to `stable`. These are descriptive sub-aspects, not a separate formal vocabulary or separate frontmatter fields:

| Sub-aspect                    | Meaning                                                                         |
| ----------------------------- | ------------------------------------------------------------------------------- |
| interface stability           | Stability of the public behavioral contract                                     |
| serialized-schema stability   | Stability of TOML and serialized record structures                              |
| semantic-resolution stability | Stability of precedence, normalization, binding, derivation, and interpretation |

All three remain provisional until the implementation and stability gates below are satisfied.

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
    --config config/train/arena-tem.toml \
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
    --config config/train/arena-tem.toml \
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

## Backend boundary

The public configuration boundary separates EHP-SN-owned semantics from implementation tools.

```text
public TOML or typed Python input
    ↓
ParsedOperationConfiguration
    ↓
EHP-SN resolver
    ↓
optional backend translation
    ↓
typed resolved request and BOUND resources
    ↓
ExecutionPlan
```

### Backend restrictions

Backends must not own:

- public field-path grammar;
- public `--set` value subset;
- source classification;
- explicit-input conflict rules;
- namespace ownership;
- resource precedence;
- semantic resolution version;
- identity inputs;
- semantic provenance.

### Option registry

The dedicated-option registry must be generated from, or conformance-checked against:

- authoritative operation field schemas;
- authoritative CLI option definitions.

It must not become a second authority.

### Missing-contract rule

A backend must not compensate for absent framework specifications by inventing artifact identity, digest, manifest, reference, or compatibility semantics.

When an upstream contract is missing, the implementation must fail explicitly or remain limited to parsing and non-identity resolution.

## Upstream dependencies

Configuration identity and resolution depends on framework reference documents:

- [References](../../framework/references.md) — canonical reference grammar, version semantics
- [Identity](../../framework/identity.md) — identity categories, equality invariants
- [Digests](../../framework/digests.md) — resource digest and artifact fingerprint semantics, integrity verification
- [Artifacts](../../framework/artifacts.md) — artifact schema, commitment, immutability
- [Manifests](../../framework/manifests.md) — manifest structure, declared resources
- [Checkpoints](../../framework/checkpoints.md) — checkpoint identity, capability levels
- [Provenance](../../framework/provenance.md) — portable vs diagnostic provenance

Configuration must reference these authorities. It must not reproduce or invent their semantics.

## Implementation gate

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
- [Resource requirements](resource-requirements.md)
- [Resolution](resolution.md)
- [Identities and provenance](identities-and-provenance.md)

## Related interfaces

- [CLI overview](../cli/index.md)
- [Python overview](../python/index.md)
- [Python conventions](../python/conventions.md)
- [Python experiments](../python/experiments.md)
- [Python artifacts](../python/artifacts.md)

## Non-goals

This interface does not define artifact digest algorithms, atomic persistence, runtime allocation, execution-time revalidation, artifact reuse, checkpoint lineage, or backend class layout.
