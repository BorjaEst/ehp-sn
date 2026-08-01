---
title: Configuration backend integration
authority: normative
status: specified
interface_stability: provisional
serialized_schema_stability: proposed
semantic_resolution_stability: proposed
---

# Configuration backend integration

This page defines the boundary between the public configuration interface and implementation tools.

## Public boundary

```text
public TOML or typed Python input
    ↓
ParsedOperationConfiguration
    ↓
EHP-SN resolver
    ↓
optional backend translation
    ↓
typed resolved request and BOUND resources
    ↓
ExecutionPlan
```

## Backend restrictions

Backends must not own:

- public field-path grammar;
- public `--set` value subset;
- source classification;
- explicit-input conflict rules;
- namespace ownership;
- resource precedence;
- semantic resolution version;
- identity inputs;
- semantic provenance.

## Option registry

The dedicated-option registry must be generated from, or conformance-checked against:

- authoritative operation field schemas;
- authoritative CLI option definitions.

It must not become a second authority.

## Backend-specific conformance

The authoritative implementation gate is defined in [\_index.md](_index.md).

Backend integration additionally must demonstrate:

1. no backend-native value crosses a public boundary;
2. backend translation preserves canonical field paths and semantic provenance;
3. direct Python use does not require Hydra;
4. backend translation does not introduce hidden defaults;
5. operation and CLI registries remain conformance-checked against their authoritative specifications.

## Related interfaces

- [Operation schemas](operation-schemas.md)
- [Files and overrides](files-and-overrides.md)
- [Sources and precedence](sources-and-precedence.md)
- [Python conventions](../python/conventions.md)
- [CLI overview](../cli/_index.md)

## Non-goals

This page does not prescribe backend class layout, Hydra launcher configuration, runtime scheduling, or persistence implementation.

## Missing-contract rule

A backend must not compensate for absent framework specifications by inventing artifact identity, digest, manifest, reference, or compatibility semantics.

When an upstream contract is missing, the implementation must fail explicitly or remain limited to parsing and non-identity resolution.
