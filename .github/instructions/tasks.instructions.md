---
description: "Use when working on scientific tasks: problem meaning, parent-role model, categorical identity, or task boundaries."
applyTo: "docs/docs/research/tasks/**/*.md, packages/ehp-research/src/tasks/**/*.py, packages/ehp-research/tests/tasks/**/*.py, tests/integration/**/*data*.py"
---

# Task instructions

Tasks define scientific problems.
`docs/docs/research/tasks/index.md` is the specification root.

## Task ownership

TASK-001 defines what a task owns; BIND-001 bounds bindings and defines what tasks do not own.
Consult those invariants rather than re-enumerating their contents here.

When code or a specification under these paths starts doing something a binding should do instead — such as adapting task output to a model-native representation, or altering any of the properties BIND-001 requires a binding to preserve — that is a BIND-001 boundary violation, not a task detail; stop and route the concern to where bindings are defined rather than absorbing it here.

If code or a specification under these paths starts implementing generic corpus index mechanics, split-inheritance rules, lineage-relation mechanics, or validation/loading orchestration that does not depend on this task's scientific problem meaning, that is drifting into framework territory; stop and route it to `docs/docs/framework/corpora.md` § "Framework and research ownership".

## Parent-role model

```text
task specification  →  declares required parent roles and compatibility
task-build configuration  →  binds those roles to exact artifact references
resolved build plan  →  records exact selected parent identities and effective configuration
committed TaskCorpus  →  materializes all data required by normal consumers
```

DATA-003 governs the forbidden-dependency list for identity-affecting parent selection.
Consult it rather than re-enumerating that list here.

## Categorical identity

`docs/docs/research/tasks/index.md` § "Directed semantic graph" and `docs/invariants.md` DATA-002 establish that Dagflow node IDs are not observation IDs absent an explicit task-owned binding.
Consult those rather than re-deriving the example here.

When a task composes Dagflow output with ObsField output, check every place that maps a Dagflow node ID to an observation ID for an explicit, task-recorded binding — a matching integer value alone is not evidence that the two IDs denote the same thing.

## Self-contained corpus

A committed task corpus must satisfy the framework `TaskCorpus` self-containment contract.
DATA-004 governs the build-input/provenance versus runtime-dependency distinction; consult it rather than re-stating it here.
