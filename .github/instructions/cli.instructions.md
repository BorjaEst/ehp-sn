---
description: "Use when working on the EHP-SN CLI: command surface, orchestration semantics, lifecycle vocabulary, or configuration boundary."
applyTo: "docs/docs/interfaces/cli/**/*.md, packages/ehp-sn/src/cli/**/*.py, packages/ehp-sn/tests/cli/**/*.py"
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

when those semantics are owned elsewhere. Scientific semantics remain owned by framework/research/experiment specifications (CLI-001).

## Lifecycle vocabulary

CLI-002 governs the operation vocabulary. Use the established lifecycle vocabulary unless a demonstrated requirement requires another operation.

`docs/docs/interfaces/cli/index.md` § "Command form" defines the general command form; § "Build vs run" defines the `build`/`run` distinction. Consult those rather than re-deriving them here.

## Stable public configuration boundary

All CLI examples and implementation must conform to the current public configuration interface (CLI-003). Backend-native (Hydra) syntax must not leak into the public surface.
