---
title: Workspace configuration
authority: normative
status: specified
interface_stability: provisional
serialized_schema_stability: proposed
semantic_resolution_stability: proposed
---

# Workspace configuration

A workspace provides local deployment defaults and exact bindings consumed during operation resolution.

## Admission rule

A workspace field is permitted only when it supplies:

- a local deployment default; or
- an exact resource binding consumed during operation resolution.

The workspace must not contain:

- scientific definitions;
- tool-native configuration trees;
- arbitrary environment variables;
- package discovery settings;
- user-interface preferences;
- unrelated project metadata.

## Workspace selection

The initial interface uses explicit workspace selection.

When no workspace is supplied, resolution uses an empty workspace.

## Workspace file

```toml
schema = "ehp-sn/workspace/v1"

[artifact_store]
root = "artifacts"

[cache]
root = ".cache/ehp-sn"

[runtime]
device = "auto"

[tracking]
backend = "local"

[bindings]
"requirement:corpus/arena-training/v1" = "artifact:arena-corpus/default/v1"
```

## Full workspace and effective projection

The full workspace document has a content digest used only for diagnostic provenance.

Resolution also constructs an effective workspace projection containing only:

- consumed workspace defaults;
- consumed resource bindings.

The effective workspace projection may have its own digest.

Identity and staleness rules use the effective projection, not the full workspace document.

Consequences:

- unused workspace fields do not affect semantic identity;
- shadowed workspace values do not affect semantic identity;
- changing unused fields does not make a plan semantically stale;
- changing a consumed default or binding may change identity and stale the plan.

## Semantic provenance

Portable workspace provenance may include:

- source document digest;
- document-relative locator;
- consumed field;
- effective value;
- source class.

Absolute workspace paths belong to diagnostic provenance only.

## Related interfaces

- [Resource requirements](resource-requirements.md)
- [Sources and precedence](sources-and-precedence.md)
- [Identities and provenance](identities-and-provenance.md)
- [Python artifacts](../python/artifacts.md)

## Non-goals

This page does not define artifact commit semantics, storage races, or runtime allocation.

## Authority boundary

The workspace supplies deployment defaults and exact bindings only.

Artifact identity, manifest structure, content digests, and commitment semantics belong to the artifact/framework specifications and must not be invented here.
