---
applyTo: "docs/docs/interfaces/configuration/**/*.md,config/**/*.md,config/**/*.toml,packages/ehp-sn/src/**/*config*.py,packages/ehp-sn/src/**/*resolution*.py,packages/ehp-sn/tests/**/*config*.py,packages/ehp-sn/tests/**/*resolution*.py"
---

# Configuration instructions

Configuration defines public frontend resolution and resource-binding semantics.

## Resolution model

Use this model:

```text
scientific definition
    declares values and resource requirements

workspace / operation configuration / explicit invocation values
    provide configurable values and exact permitted resource bindings

resolution
    finalizes scientific specialization
    resolves request values
    creates BOUND resource records

validation
    establishes evidence that required resources are VERIFIED

execution
    consumes the immutable resolved plan
```

## Resource selection

Exact scientific resources that affect reproducibility must be selected through explicit, recordable resolution.

For task-corpus generation, parent roles should be represented as declared resource requirements and exact bindings.

For multi-parent tasks, distinguish roles such as:

```text
topology
observation_field
semantic_graph
acquired_memory
```

Do not replace resource requirements with arbitrary implicit filesystem lookup.

## Ownership boundary

Configuration must not redefine:

- task semantics;
- substrate semantics;
- model architecture;
- generic artifact identity algorithms;
- manifest semantics.

Configuration may determine which exact permitted resource satisfies a declared requirement.

## Backend boundary

Hydra may be an implementation backend.

Hydra's native override DSL, Defaults List, interpolation semantics, or tool-native configuration trees are not automatically public EHP-SN configuration semantics.

Public CLI and Python configuration must resolve through the same EHP-SN-owned semantic model.

## Reproducibility

Identity-affecting values, selected exact resources, normalization rules, and derivation rules must be represented in resolved configuration/provenance according to the authoritative identity specifications.

Do not depend on user shell history or hidden randomness for scientific build selection.
