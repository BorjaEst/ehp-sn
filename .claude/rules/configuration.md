---
paths:
  - "docs/docs/interfaces/configuration/**/*.md"
  - "config/**/*.md"
  - "config/**/*.toml"
  - "packages/ehp-sn/src/configuration/**/*.py"
  - "packages/ehp-sn/tests/configuration/**/*.py"
---

# Configuration instructions

Configuration defines public frontend resolution and resource-binding semantics.

## Resolution model

Resolution turns a scientific definition and configurable values into a finalized specialization, resolved request values, and bound resources; validation then establishes evidence that those resources are usable; execution consumes the immutable resolved plan.
`docs/docs/interfaces/configuration/resolution.md` § "Plan and validation relationship" and § "Validation" define the exact state machine and its terminology.
Consult it rather than restating the model here.

## Resource selection

Exact scientific resources that affect reproducibility must be selected through explicit, recordable resolution.

For task-corpus generation, parent roles should be represented as declared resource requirements and exact bindings.

Per-task parent-role sections in `docs/docs/research/tasks/` — for example `prospect.md` § "6.1 Build-time parent roles" and `routebind.md` § "6.1 Parent roles" — define the role vocabulary for multi-parent tasks.
Consult those rather than re-enumerating role names here.

Do not replace resource requirements with arbitrary implicit filesystem lookup.

## Ownership boundary

ARCH-002 and `docs/authority.md` § "Authority map" govern this: a semantic contract has one normative owner, and configuration must not become a second normative home for semantics owned elsewhere. Consult the authority map for which package/specification owns a given concept before defining configuration behavior that touches it.

Configuration may determine which exact permitted resource satisfies a declared requirement.

## Backend boundary

CONFIG-002 and CLI-003 govern this. Hydra may be an implementation backend.

Hydra's native override DSL, Defaults List, interpolation semantics, or tool-native configuration trees are not automatically public EHP-SN configuration semantics.

Public CLI and Python configuration must resolve through the same EHP-SN-owned semantic model.

## Reproducibility

CONFIG-003 and CONFIG-004 govern this. Identity-affecting values, selected exact resources, normalization rules, and derivation rules must be represented in resolved configuration/provenance according to the authoritative identity specifications.

Do not depend on user shell history or hidden randomness for scientific build selection.
