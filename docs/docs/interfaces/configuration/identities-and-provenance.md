---
title: Configuration identities and provenance
authority: normative
status: specified
interface_stability: provisional
serialized_schema_stability: proposed
semantic_resolution_stability: proposed
---

# Configuration identities and provenance

This page defines configuration-level semantic inputs to identity and separates semantic provenance from diagnostic provenance.

## Equality invariant

Two configurations with equal effective semantic values and equal exact scientific resource identities must have equal scientific-invocation identity, regardless of whether values came from TOML, Python, workspace defaults, `--set`, or dedicated arguments.

## Identity inputs

Configuration contributes:

- canonical target identity;
- finalized scientific-definition digest;
- canonical effective semantic field values;
- requirement identities;
- exact selected scientific resource identities;
- identity-relevant normalization rule IDs;
- identity-relevant derivation rule IDs;
- semantic resolution version.

Configuration does not contribute:

- absolute source file paths;
- current working directory;
- CLI token positions;
- original textual spelling;
- frontend source class when effective values are equal;
- unused workspace fields;
- shadowed workspace fields;
- unused operation-file fields.

## Resource identity

A resource may contribute:

- logical reference;
- immutable version;
- content digest;
- requirement identity.

The exact combination is declared by the owning operation and artifact identity contract.

Workspace paths never contribute to scientific identity.

## Semantic provenance

Semantic provenance is portable and may include:

- canonical field;
- effective typed value;
- source class;
- source document identity or digest;
- document-relative locator;
- normalization rule ID;
- derivation rule ID;
- identity classification;
- consumed workspace projection identity.

## Diagnostic provenance

Diagnostic provenance is local and non-portable. It may include:

- absolute filesystem path;
- CLI token position;
- original textual spelling;
- complete replaced values;
- local environment details.

Diagnostic provenance must not affect scientific or operational identity.

## Workspace provenance

The full workspace digest is diagnostic provenance only.

The effective workspace projection contains only consumed defaults and bindings. Its digest may contribute to operational request or plan identity when those consumed values do.

## Unused and shadowed values

Unused and shadowed values:

- do not affect effective semantic identity;
- do not affect scientific-invocation identity;
- do not stale a plan when changed;
- may remain in diagnostics.

## Related interfaces

- [Workspace](workspace.md)
- [Resolution](resolution.md)
- [Operation schemas](operation-schemas.md)
- [Python artifacts](../python/artifacts.md)
- [Python conventions](../python/conventions.md)

## Non-goals

This page does not define canonical serialization or hash algorithms.

## Resource identity authority

Resource identity contribution is governed exclusively by the rule in [Resource requirements](resource-requirements.md):

> The owning operation identity specification and artifact identity specification declare which resource identity components contribute to each identity category.

This page does not independently redefine that selection.

Source document digests are semantic provenance only. They do not contribute to scientific-invocation identity unless the document itself is a declared scientific input.

## Missing upstream authorities

This page defines which configuration values are candidates for identity participation.

The canonical serialization, digest algorithms, artifact identity contract, and reference grammar must be supplied by the future framework artifact and identity specifications. Until then, identity participation remains a design contract rather than an executable hashing contract.
