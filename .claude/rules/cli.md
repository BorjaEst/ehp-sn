---
paths:
  - "docs/docs/interfaces/cli/**/*.md"
  - "packages/ehp-sn/src/cli/**/*.py"
  - "packages/ehp-sn/tests/cli/**/*.py"
---

# CLI instructions

The `ehp-sn` CLI is the public operational control surface over framework and installed research definitions.

## Orchestration, not semantic ownership

CLI commands orchestrate framework and research semantics. They do not become the semantic owner merely because they invoke an operation.

Prefer wording such as:

- `exposes`;
- `orchestrates`;
- `resolves`;
- `validates`;
- `invokes`;
- `produces`;
- `executes`.

Avoid statements such as:

```text
data owns manifests
tasks owns task semantics
evaluate owns metric definitions
```

when those semantics are owned elsewhere.

Example:

```text
ehp-sn data
    orchestrates substrate operations

ehp_research substrate definition
    defines family-specific scientific semantics

ehp_sn
    defines generic artifact lifecycle and validation mechanics
```

## Lifecycle vocabulary

CLI-002 governs the operation vocabulary.
Use the established lifecycle vocabulary unless a demonstrated requirement requires another operation.

`docs/docs/interfaces/cli/_index.md` § "Command form" defines the general command form; § "Build vs run" defines the `build`/`run` distinction.
Consult those rather than re-deriving them here.

## Configuration boundary

All CLI examples and implementation must conform to the current public configuration interface.

Use EHP-SN-owned `--config`, typed `--set`, and dedicated options where specified.

Do not expose Hydra-native syntax as the stable CLI contract.

## Discovery

ARCH-003 governs this.

CLI catalogue commands discover installed definitions through the framework-owned registration/discovery mechanism.

## CLI/Python equivalence

CONFIG-004 governs CLI/Python semantic equivalence. Consult it rather than re-enumerating its convergence list here.
