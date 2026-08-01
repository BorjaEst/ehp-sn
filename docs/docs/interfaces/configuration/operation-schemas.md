---
title: Operation configuration schemas
authority: normative
status: specified
interface_stability: provisional
serialized_schema_stability: proposed
semantic_resolution_stability: proposed
---

# Operation configuration schemas

Each operation interface must own or generate its exhaustive field catalogue before the corresponding serialized schema is stable.

## Required catalogue fields

Every field must declare:

| Property                    | Meaning                                 |
| --------------------------- | --------------------------------------- |
| Path                        | Canonical field path                    |
| Type                        | Exact public type                       |
| Required                    | Authored requiredness                   |
| Default                     | Default-bearing source, if any          |
| Owner                       | Definition or request owner             |
| Namespace rationale         | Why the field belongs under that prefix |
| File                        | Accepted in operation file              |
| `--set`                     | Accepted as typed override              |
| Dedicated option            | CLI mapping, if any                     |
| Identity class              | Identity participation                  |
| Semantic resolution version | Interpretation contract                 |
| Derivation rule             | Versioned derivation, if applicable     |
| Resume/reuse class          | Compatibility effect                    |
| Provenance class            | Portable source behavior                |

## Namespace criteria

A field belongs under `experiment.*` or `analysis.*` only when changing it produces a different resolved scientific definition.

A field belongs under `request.*` when it selects invocation inputs, runtime policy, placement, diagnostics, or other operational intent without redefining the scientific target.

## CLI registry authority

The dedicated-option registry must be generated from, or conformance-checked against:

- the authoritative operation field catalogue;
- the authoritative CLI option specification.

It must not become a second authority.

## Stability rule

A candidate schema is not stable until:

- its exhaustive catalogue exists;
- canonical paths satisfy the grammar;
- source classes are defined;
- option mappings are conformance-tested;
- identity classifications are fixed;
- semantic resolution version is fixed;
- parser and resolver tests pass.

## Related interfaces

- [Files and overrides](files-and-overrides.md)
- [Sources and precedence](sources-and-precedence.md)
- [Python training](../python/training.md)
- [Python evaluation](../python/evaluation.md)
- [Python analysis](../python/analysis.md)

## Non-goals

This page does not duplicate operation-owned scientific compatibility rules.

## Deferred namespaces

Data-build and task-build configuration is not generalized through `definition.*` in the initial interface. Each operation must first establish a concrete public schema before a shared namespace is introduced.

## First concrete schema

The first complete catalogue must be `ehp-sn/train/v1`.

Training is the required initial proof because it exercises:

- scientific specialization;
- request-owned seeds and runtime policy;
- corpus requirements and bindings;
- output placement;
- checkpoint and resume compatibility;
- identity and provenance classification.

Evaluation and analysis schemas follow after the training catalogue validates the common schema model.
