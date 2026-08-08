---
applyTo: "docs/docs/research/substrates/**/*.md,packages/ehp-research/src/**/substrates/**/*.py,packages/ehp-research/tests/**/*substrate*.py,tests/architecture/**/*data*.py,tests/integration/**/*data*.py"
---

# Substrate instructions

Substrates are research-owned reusable, task-neutral domain structures.

## Owned semantics

A substrate may define:

- topology;
- connectivity;
- geometry;
- observation fields;
- graph structure;
- reusable source facts;
- intrinsic substrate split membership when scientifically intrinsic;
- family-specific generation or conversion semantics;
- family-specific identity inputs;
- family-specific invariants.

## Excluded semantics

A substrate must not define information that exists only because a task poses a problem, including:

- task queries;
- task-generated starts or goals;
- task-generated trajectories or episodes;
- supervision targets;
- task rewards;
- task metrics;
- model tokenization;
- model-native tensor layouts.

Diagnostic question:

> Would this information still have meaning if no downstream task existed?

If not, it normally does not belong to the substrate.

## Shared research contracts

When several research substrate producers and task consumers require the same task-facing structure, define one research-owned shared contract rather than duplicating semantics.

Example:

```text
DungeonGen ─┐
            ├─→ raster-topology/v1 ─→ Arena / MazeHard / Routebind / Prospect
Maze-ND   ──┘
```

DungeonGen and Maze-ND must not independently redefine shared raster-topology semantics.

Do not move `raster-topology/v1` into `ehp_sn` solely because several `ehp_research` components use it.

## Identity independence

Substrate identity must remain independent of downstream task composition.

Examples:

- an ObsField identity must not contain a topology reference;
- a topology identity must not change because Arena or Routebind uses it;
- Dagflow node IDs must not acquire observation semantics at the substrate layer.
