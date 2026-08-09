---
paths:
  - "docs/docs/research/substrates/**/*.md"
  - "packages/ehp-research/src/substrates/**/*.py"
  - "packages/ehp-research/tests/substrates/**/*.py"
  - "tests/architecture/**/*data*.py"
  - "tests/integration/**/*data*.py"
---

# Substrate instructions

Substrates are research-owned reusable, task-neutral domain structures.

## Owned semantics

`docs/authority.md` § "Authority map" assigns "Research substrate semantics and shared schemas" to `ehp_research`, with specification root `docs/docs/research/substrates/`. Consult that specification root for what a substrate may define; do not re-enumerate it here.

`docs/docs/research/substrates/index.md` § "Generic substrate boundary" establishes what a substrate may contain, including intrinsic split membership.

## Excluded semantics

DATA-001 and DATA-002 govern what a substrate must not define: information that exists only because a task poses a problem is task-owned, not substrate-owned.

Diagnostic question (applying DATA-001):

> Would this information still have meaning if no downstream task existed?

If not, it normally does not belong to the substrate.

## Shared research contracts

When several research substrate producers and task consumers require the same task-facing structure, define one research-owned shared contract rather than duplicating semantics.

`docs/docs/research/tasks/index.md` § "Raster topology" establishes DungeonGen and Maze-ND as producers of the shared `raster-topology/v1` task-facing contract; `docs/invariants.md` DATA-005 governs why such a shared contract stays research-owned rather than moving into `ehp_sn`. Consult those rather than re-deriving the example here.

## Identity independence

DATA-002 governs substrate identity independence, including its examples.
Consult it rather than re-enumerating its examples here.

Diagnostic check before adding a field to a substrate's identity computation: would that field's value change, or would it stop being meaningful, if a different downstream task consumed the substrate instead — or if no downstream task existed at all? If so, it is task composition leaking into substrate identity, not an intrinsic property of the substrate, and it does not belong in the identity computation.
