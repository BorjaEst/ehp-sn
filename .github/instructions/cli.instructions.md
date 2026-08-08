---
applyTo: "docs/docs/interfaces/cli/**/*.md,packages/ehp-sn/src/**/*cli*.py,packages/ehp-sn/tests/**/*cli*.py"
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
- `materializes`;
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

Use the established operation vocabulary unless a demonstrated requirement requires another operation:

```text
list
show
plan
validate
build
run
inspect
```

The general command form is:

```text
ehp-sn COMMAND OPERATION [TARGET] [OPTIONS]
```

`build` materializes data-like immutable artifacts.

`run` executes computational protocols.

## Configuration boundary

All CLI examples and implementation must conform to the current public configuration interface.

Use EHP-SN-owned `--config`, typed `--set`, and dedicated options where specified.

Do not expose Hydra-native syntax as the stable CLI contract.

## Discovery

CLI catalogue commands discover installed definitions through the framework-owned registration/discovery mechanism.

The CLI/framework must not import `ehp_research` by name to populate the catalogue.

## CLI/Python equivalence

Equivalent CLI and Python inputs must converge on the same semantic constructors, resource binding rules, validation, and execution plans.
