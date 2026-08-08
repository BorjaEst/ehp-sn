---
applyTo: "docs/docs/research/tasks/**/*.md,packages/ehp-research/src/**/tasks/**/*.py,packages/ehp-research/tests/**/*task*.py,tests/integration/**/*data*.py"
---

# Task instructions

Tasks define scientific problems.

## Task ownership

A task owns:

- one logical task record;
- public information;
- target information;
- privileged or oracle-only information;
- withheld information;
- required parent roles and capabilities;
- task-owned composition semantics;
- case, query, or episode generation;
- oracle/reference truth;
- task-specific validity;
- task metrics and supported scientific claims.

## Excluded semantics

Tasks do not own:

- generic artifact lifecycle;
- generic corpus indexing and manifest mechanics;
- exact user/workspace parent artifact binding;
- model-native tensor representation;
- model tokenization;
- CLI spelling;
- generic execution placement.

## Parent-role model

Use this separation:

```text
task specification
    declares required parent roles and compatibility

task-build configuration
    binds those roles to exact artifact references
    and selects reproducible generation/composition policies

resolved build plan
    records exact selected parent identities and effective configuration

committed TaskCorpus
    materializes all data required by normal consumers
```

Do not hide identity-affecting parent selection in filesystem discovery, import order, or nondeterministic builder behavior.

## Composition

A task may compose multiple independent substrates.

The composition is task build context. It does not automatically become a new substrate.

## Categorical identity

Do not infer identity between categorical domains from equal integer representation.

For example:

```text
Dagflow node ID 4 ≠ observation ID 4
```

unless a task explicitly creates and records a binding between those domains.

## Self-contained corpus

A committed task corpus must satisfy the framework `TaskCorpus` self-containment contract.

Parent substrates and upstream artifacts remain build inputs and provenance, not normal runtime dependencies.
